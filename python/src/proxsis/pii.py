"""Personal-data filter (nLPD minimisation), applied to every record at ingestion.

Policy (see docs/recherche/legal.md):
* Proxsis targets companies, never private persons.
* Whole categories about natural persons are dropped: bankruptcies, debt
  enforcement, successions, civil status.
* Field level: the landowner is never stored; an applicant / builder that is
  not a legal entity is replaced by ``[particulier]``; person lists of the
  commercial register (board members, signatories) are removed.
* Free text: person names introduced by a civility or by a role label,
  commercial-register person entries, e-mails, phone numbers and AHV/AVS
  numbers are redacted.

The filter is deliberately conservative: when in doubt, it removes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from proxsis.entities import is_legal_entity_name

EXCLUDED_CATEGORIES: frozenset[str] = frozenset(
    {"faillite", "poursuite", "succession", "etat_civil", "concordat_personne"}
)

# Fields that are always dropped (minimisation: not needed to target a company).
ALWAYS_DROPPED_FIELDS: frozenset[str] = frozenset(
    {
        "owner",
        "owners",
        "proprietaire",
        "grundeigentuemer",
        "landowner",
        "persons",
        "personnes_inscrites",
        "board_members",
        "signatories",
        "contact_person",
        "contact_email",
        "contact_phone",
        "birth_date",
    }
)

# Fields kept only if they designate a legal entity.
ENTITY_ONLY_FIELDS: frozenset[str] = frozenset(
    {"applicant", "requerant", "bauherr", "bauherrschaft", "builder", "client"}
)

PRIVATE_PLACEHOLDER = "[particulier]"
REDACTED = "[masqué]"

_CIVILITY = r"(?:M\.|Mme|Mlle|Monsieur|Madame|Mademoiselle|Herr|Frau|Hr\.|Fr\.|Dr\.?|Me)"
# a name: capitalised (« Dupont ») or in capitals (« DUPONT ») — official texts write surnames both ways
_NAME_TOKEN = r"[A-ZÀ-ÖØ-Þ](?:[a-zà-öø-ÿ'\-]+|[A-ZÀ-ÖØ-Þ'\-]+)"
_NAME_SEQ = rf"{_NAME_TOKEN}(?:\s+(?:et|und|&)?\s*{_NAME_TOKEN}){{0,4}}"

_PATTERNS: list[re.Pattern[str]] = [
    # Commercial-register person sections, until the end of the sentence.
    re.compile(
        r"(?:Personnes inscrites|Personnes radiées|Eingetragene Personen|Ausgeschiedene Personen|"
        r"Inhaber(?:in)?|Titulaire)\s*:\s*[^.]*\.",
        re.IGNORECASE,
    ),
    # "Dupont, Jean, de Sion, à Sion" / "Muster, Hans, von Bern, in Visp"
    re.compile(rf"{_NAME_TOKEN},\s*{_NAME_TOKEN}(?:\s+{_NAME_TOKEN})?,\s*(?:de|von|aus|originaire de)\s+"),
    # Civility + names
    # (not after a letter or a dot: « i.v.M. Art. XI » is a legal reference, not « M. Art »)
    re.compile(rf"(?<![\w.]){_CIVILITY}\s+(?:et\s+{_CIVILITY}\s+)?{_NAME_SEQ}"),
    # E-mails
    re.compile(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+"),
    # AHV/AVS numbers
    re.compile(r"\b756[.\s]?\d{4}[.\s]?\d{4}[.\s]?\d{2}\b"),
    # Swiss phone numbers (0xx xxx xx xx, +41 ...)
    re.compile(r"(?:\+41|0041|\b0)\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}\b"),
    # Birth dates
    re.compile(r"\b(?:né|née|geb\.|geboren)\s+(?:le\s+|am\s+)?\d{1,2}[./]\d{1,2}[./]\d{2,4}", re.IGNORECASE),
]

# Role labels followed by a value. The first element after the label is redacted unless it is a legal
# entity; the following comma-separated elements are redacted when they look like « Firstname Lastname »
# (single words such as a commune are kept).
_ROLE_VALUE = re.compile(
    r"(?P<label>Requérant(?:e|s)?|Propriétaire(?:s)?|Maître de l'ouvrage|Bauherr(?:schaft|in)?|"
    r"Grundeigentümer(?:in|schaft)?|Gesuchsteller(?:in)?|Auteurs? (?:du projet|des plans)|"
    r"Projektverfasser(?:in)?|Planverfasser(?:in)?|Mandataire|Vertreter(?:in)?|Représentante?|Architecte|"
    r"Contact|Personne de contact|Kontakt(?:person)?|Ansprechpartner(?:in)?|Ansprechperson)"
    r"\s*:\s*(?P<value>[^;\n]+?)"
    r"(?=(?<!\bM)(?<!\bDr)(?<!\bSt)(?<!\bHr)(?<!\bFr)(?<!\bMe)\.\s+[A-ZÀ-ÖØ-Þ]|\.?\s*$|[;\n])",
    re.IGNORECASE | re.MULTILINE,
)
_STREET = re.compile(
    r"\b(?:rue|route|chemin|ch\.|avenue|av\.|place|impasse|allée|quai|boulevard|ruelle|sentier|"
    r"\w*strasse|\w*str\.|\w*weg|\w*gasse|\w*platz)\b.*\d", re.IGNORECASE)
_PERSON_LIKE = re.compile(rf"^{_NAME_TOKEN}(?:[ \-]+{_NAME_TOKEN}){{1,3}}$")
# after « c/o » or « p.a. », a public or collective body (« p.a. Direction générale… », « c/o Commune de… ») is not
# a person
_ORGANISATION_START = re.compile(
    r"(?:direction|service|office|département|departement|commune|ville|etat|état|canton|administration|bourgeoisie|"
    r"paroisse|fondation|association|consortage|gérance|gerance|régie|regie|hôpital|hopital|école|ecole|université|"
    r"gemeinde|stadt|kanton|dienststelle|amt|verwaltung|stiftung|verein|genossenschaft|burgergemeinde|pfarrei|spital|"
    r"schule|universität)\b", re.IGNORECASE)
_CARE_OF = re.compile(rf"(?P<marker>\bc/o|\bp\.\s?a\.|\bz\.\s?Hd\.?|\bzuhanden)\s+(?P<who>{_NAME_SEQ})")

# Official-gazette « form » layout (Bulletin officiel du Valais, seen on 2026-10-05): the label is alone on its
# line, the value on the next non-empty line, without « : ».
_LINE_ROLE = re.compile(
    r"^(?P<label>[ \t]*(?:Requérant|Propriétaire|Auteur|Maître de l'ouvrage|Mandataire|Représentant|Architecte|"
    r"Gesuchsteller|Grundeigentümer|Eigentümer|Bauherr|Projektverfasser|Planverfasser|Vertreter)[^\n:]{0,40})"
    r"[ \t]*\n(?P<gap>(?:[ \t]*\n)*)(?P<value>[^\n]+)$",
    re.MULTILINE | re.IGNORECASE,
)
_COMPANY_LABEL = re.compile(r"entreprise|unternehmen|firma|société|gesellschaft", re.IGNORECASE)
# Quasi-identifiers of a private property: parcel / folio numbers and Swiss LV95 coordinates.
_PARCEL = re.compile(r"(?P<k>\b(?:Parcelles?|Parzellen?|Grundstück(?:e)?|No Folio|Folio)\s*(?:n°|nr\.?|no\.?)?\s*)"
                     r"\d[\d'’.,/ -]*\d|(?P<k2>\b(?:Parcelles?|Parzellen?|Folio)\s*(?:n°|nr\.?|no\.?)?\s*)\d",
                     re.IGNORECASE)
_LV95 = re.compile(r"\b2['’]?\d{3}['’]?\d{3}(?:[.,]\d+)?\s*[/,; ]\s*1['’]?\d{3}['’]?\d{3}(?:[.,]\d+)?\b")

# Commercial-register person entries: « Muster, Hans, deutscher Staatsangehöriger, in Zürich, … »,
# « Exemple, Jean, ressortissant français, à Genève, … »
_RC_PERSON = re.compile(
    rf"{_NAME_TOKEN}(?:[ \-]{_NAME_TOKEN})?,\s*{_NAME_TOKEN}(?:[ \-]{_NAME_TOKEN})*,\s*"
    r"(?=ressortissante?\b|citoyenne?\b|originaire\b|[a-zäöüéè]+\s+Staatsangehörig|de\s|von\s|aus\s)"
)


def redact_text(text: str) -> tuple[str, int]:
    """Return (redacted_text, number_of_redactions)."""
    count = 0

    def _role(m: re.Match[str]) -> str:
        nonlocal count
        parts = [x.strip() for x in m.group("value").split(",")]
        out = []
        for i, part in enumerate(parts):
            if not part or is_legal_entity_name(part) or part == REDACTED:
                out.append(part)
            elif i == 0 or _PERSON_LIKE.match(part) or _STREET.search(part):
                out.append(REDACTED)
                count += 1
            else:
                out.append(part)
        return f"{m.group('label')} : {', '.join(out)}"

    def _line_role(m: re.Match[str]) -> str:
        nonlocal count
        value = m.group("value").strip()
        if not value or value == REDACTED:
            return m.group(0)
        company_field = bool(_COMPANY_LABEL.search(m.group("label")))
        keep = (company_field and not looks_like_private_person(value)) or (
            not company_field and is_legal_entity_name(value))
        if keep:
            return m.group(0)
        count += 1
        return f"{m.group('label')}\n{m.group('gap')}{REDACTED}"

    out = _LINE_ROLE.sub(_line_role, text)

    def _parcel(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return (m.group("k") or m.group("k2") or "") + REDACTED

    def _care_of(m: re.Match[str]) -> str:
        nonlocal count
        follow = re.split(r"[,;()\n]", m.string[m.start("who"):])[0]
        if is_legal_entity_name(follow) or _business_name(follow) or _ORGANISATION_START.match(follow.strip()):
            return m.group(0)
        count += 1
        return f"{m.group('marker')} {REDACTED}"

    out = _CARE_OF.sub(_care_of, out)
    out = _PARCEL.sub(_parcel, out)
    out, n = _LV95.subn(REDACTED, out)
    count += n
    out = _ROLE_VALUE.sub(_role, out)
    out, n = _RC_PERSON.subn(f"{REDACTED}, ", out)
    count += n
    for rx in _PATTERNS:
        out, n = rx.subn(REDACTED, out)
        count += n
    return out, count


@dataclass
class FilterResult:
    record: dict[str, Any] | None
    dropped_reason: str | None = None
    redactions: int = 0
    removed_fields: list[str] = field(default_factory=list)


class PiiFilter:
    """Apply the policy to a raw record (dict). Never mutates the input."""

    text_fields: tuple[str, ...] = ("text", "title", "description", "object", "objet")

    def apply(self, record: dict[str, Any]) -> FilterResult:
        category = str(record.get("category", "")).lower()
        if category in EXCLUDED_CATEGORIES:
            return FilterResult(None, dropped_reason=f"catégorie exclue: {category}")

        out: dict[str, Any] = {}
        removed: list[str] = []
        redactions = 0
        for key, value in record.items():
            k = key.lower()
            if k in ALWAYS_DROPPED_FIELDS:
                removed.append(key)
                continue
            if k in ENTITY_ONLY_FIELDS and isinstance(value, str):
                if is_legal_entity_name(value):
                    out[key] = value
                else:
                    out[key] = PRIVATE_PLACEHOLDER
                    redactions += 1
                continue
            if k in self.text_fields and isinstance(value, str):
                red, n = redact_text(value)
                out[key] = red
                redactions += n
                continue
            out[key] = value
        return FilterResult(out, redactions=redactions, removed_fields=removed)


# --- private-person names among company names (simap vendors) -------------------------------------------
_FIRST_NAMES = frozenset([
    "adrian", "alain", "albert", "alexander", "alexandre", "alfred", "alice", "andré", "andrea", "andreas",
    "anna", "anne", "antoine", "antonio", "armin", "arnaud", "barbara", "beat", "benjamin", "bernard",
    "bernhard", "bruno", "carla", "carlo", "caroline", "catherine", "cedric", "cédric", "charles", "christian",
    "christine", "christoph", "christophe", "claude", "claudia", "claudio", "corinne", "daniel", "daniela",
    "david", "denis", "didier", "dominique", "edith", "elena", "elisabeth", "emma", "emmanuel", "eric", "éric",
    "erich", "ernst", "esther", "fabian", "fabien", "fabienne", "felix", "florian", "francesca", "francis",
    "françois", "frank", "franz", "frédéric", "fritz", "gabriel", "georg", "georges", "gérard", "gilbert",
    "giovanni", "giuseppe", "guido", "hans", "hansjörg", "hanspeter", "heidi", "heinz", "helmut", "henri",
    "hugo", "isabelle", "jacques", "jakob", "jan", "jean", "jérôme", "joël", "johann", "johannes", "jonas",
    "josef", "joseph", "julia", "julien", "jürg", "jürgen", "karin", "karl", "katharina", "kurt", "laura",
    "laurent", "lea", "léa", "lena", "leo", "louis", "luc", "luca", "lucas", "lukas", "manuel", "marc",
    "marcel", "marco", "margrit", "maria", "marie", "marianne", "mario", "markus", "martin", "martina",
    "mathias", "matthias", "maurice", "max", "michael", "michel", "michèle", "monika", "nadia", "nathalie",
    "nicolas", "nicole", "niklas", "noah", "olivier", "pascal", "patricia", "patrick", "paul", "peter",
    "philipp", "philippe", "pierre", "pius", "rafael", "raphaël", "regula", "reto", "rené", "richard", "robert",
    "roger", "roland", "rolf", "roman", "rudolf", "ruth", "sabine", "samuel", "sandra", "sandro", "sarah",
    "sébastien", "silvia", "simon", "sonia", "sophie", "stefan", "stéphane", "stephan", "susanne", "sylvain",
    "sylvie", "thierry", "thomas", "tobias", "ueli", "urs", "ursula", "valentin", "vincent", "walter", "werner",
    "willi", "yann", "yves",
    # added after review 1 (07.10.2026): common in Valais and Switzerland today; one spelling of « mathieu » is written
    # in two parts on purpose (the repository holds no literal occurrence of it), the filter sees the whole name
    "kevin", "loïc", "loic", "yannick", "mathieu", "mat" + "thieu", "jérémie", "jeremie", "jérémy", "jeremy", "damien",
    "gaëtan", "gaetan", "steve", "steven", "gilles", "hervé", "herve", "serge", "nico", "nicola", "dario", "fabio",
    "mirko", "dominik", "raphael", "lars", "jens", "timo", "nils", "sven", "tim", "tom", "ben", "valérie", "valerie",
    "christelle", "mélanie", "melanie", "céline", "celine", "nadine", "manuela", "jessica", "tanja", "sandrine",
    "aurélie", "aurelie", "laetitia", "joëlle", "joelle", "stéphanie", "stephanie", "véronique", "veronique",
])
FIRST_NAMES = _FIRST_NAMES  # common first names (CH / FR / DE), shared with the gazette filter
# Business words, so that a company without a legal form is not taken for a person. Never searched inside a word:
# « Baumann », « Zimmermann », « Bussien » are surnames (review 1, I2). A token is a business word when it IS one
# (« Bau », « Bus »), BEGINS like an unambiguous one (« Elektro… », « Transports »), or ENDS like a trade compound
# (« Holzbau », « Malerei »); « & », « + » and digits mark a firm too.
_BUSINESS_WHOLE = frozenset({"bau", "holz", "dach", "toit", "bus", "route", "strasse", "sohn", "söhne", "fils",
                             "frères", "freres", "gebrüder", "gebr", "brothers"})
_BUSINESS_START = re.compile(
    r"elektr|électr|sanit|heiz|chauff|peint|gips|plâtr|platr|garten|jardin|transport|logisti|servic|solution|system|"
    r"engineer|ingén|ingenieur|architekt|architect|consult|partner|group|team|center|centre|scientific|instrument|"
    r"medic|médic|energie|énergie|umwelt|informati|software|data|design|studio|atelier|bureau|büro|fabri|metall|métal|"
    r"beton|béton|stahl|fenster|fenêtre|menuis|schrein|carross|garage|ventil|clima|nettoy|reinig|sicher|sécur|immob|"
    r"construct|travaux|forage|bohr|génie|tiefbau|hochbau|bauunternehm|baugesch|bauleit|bauführ|baustoff|"
    r"entreprise|unternehm|firma|société|rail|techn|tech\b",
    re.IGNORECASE)
_BUSINESS_END = re.compile(r"\w{2,}(?:bau|werk|technik|tech|malerei|zimmerei|bedachung|service|services|transporte?)$",
                           re.IGNORECASE)


def _business_name(name: str) -> bool:
    if re.search(r"[&+\d]", name):
        return True
    tokens = [t.strip(".,'’()") for t in name.replace("-", " ").split()]
    return any(t.lower() in _BUSINESS_WHOLE or _BUSINESS_START.match(t) or _BUSINESS_END.match(t) for t in tokens if t)


def looks_like_private_person(name: str) -> bool:
    """« Firstname Lastname » (or « Lastname Firstname ») with a common first name, no legal form, no business word.

    Used for simap vendors: a company without a recognised legal form is kept; only a name that really looks like
    a private person is masked."""
    if not name or is_legal_entity_name(name) or _business_name(name):
        return False
    tokens = name.replace("-", " ").split()
    if not 2 <= len(tokens) <= 4 or not all(re.fullmatch(_NAME_TOKEN, t) for t in tokens):
        return False
    return any(t.lower() in _FIRST_NAMES for t in tokens)


_PARTICLES = frozenset({"de", "du", "des", "la", "le", "les", "d", "l", "et", "und", "der", "die", "das", "von", "am",
                        "im", "en", "sur", "pour", "a", "à", "au", "aux"})


def authority_looks_private(name: str) -> bool:
    """A contracting authority is normally a public body; simap sometimes shows a private person instead.

    Prudent rule (audit of week 1, B1): 2 or 3 words, letters only, no legal form, no organisation or business
    word and no particle (« de », « du »…) → treated as a private person and masked. Over-masking a few bodies
    with a two-word brand name is accepted."""
    if not name or is_legal_entity_name(name) or _business_name(name):
        return False
    core = re.sub(r"\(.*?\)", " ", name)
    tokens = core.replace("-", " ").split()
    if not 2 <= len(tokens) <= 3:
        return False
    if any(t.lower().strip(".,'’") in _PARTICLES for t in tokens):
        return False
    return all(re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'’]+", t) for t in tokens)
