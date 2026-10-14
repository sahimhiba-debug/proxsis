"""Personal-data filter of the Bulletin officiel import (fail closed), applied to each publication BEFORE anything is
written. Each party of the roles (requérant, propriétaire, maître d'ouvrage, auteur des plans) is classified:
companies (legal form) and public or collective bodies (communes, bourgeoisies, fondations, paroisses, consortages,
authorities, associations) are kept; anything else is treated as a natural person and replaced by ``[masqué]`` — in
the role, in the title and in the whole text. Parcels and coordinates are masked too. A last sweep stops the import
(``PersonalDataFound``) if a person marker survives. Kept in one module so that it can be reviewed in one reading.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from dataclasses import field as dc_field
from typing import Any

from proxsis.entities import legal_form_at_end
from proxsis.gazette_pdf import ROLE_FIELDS
from proxsis.pii import FIRST_NAMES, REDACTED, redact_text

# Week-2 audit, B2. A party value is cut into pieces (lines, commas, « c/o », « p.a. », « représenté par »,
# « z. Hd. », « Domicile: », any « label: »…) and each piece is classified ON ITS OWN. A piece is kept only if it is
# itself an organisation; persons, addresses, functions (« président ») and unknown text are masked. Free text
# (titles, other fields) is masked word by word: a capitalised word is kept only if it is a known word — frequent
# in the index titles, a construction word, a locality — and never if it is a first name or a word of a masked
# party anywhere in the import.


class PersonalDataFound(Exception):
    """Raised by the sweep BEFORE anything is written. ``findings`` carry ids, fields and reasons, never values."""

    def __init__(self, findings: list[dict[str, str]]):
        super().__init__(f"{len(findings)} donnée(s) personnelle(s) possible(s) après filtre : import arrêté")
        self.findings = findings


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("’", "'"))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def _fw(word: str) -> str:
    """Folded word without its elision (« d'Habitation » → « habitation »)."""
    return _fold(re.sub(r"^(?:[dlDL]|qu)['’]", "", word))


_FIRST = frozenset(_fold(n) for n in FIRST_NAMES)
# words that are never a name: articles, places of the canton, construction vocabulary (FR / DE), legal forms
_BASE = frozenset(_fold(w) for w in """
les la le l du des de d au aux en sur sous pour avec et un une am im zum zur auf bei mit und der die das den dem von
vom nach fur ob unter ober saint sainte st ste nord sud est ouest ost west valais wallis suisse schweiz oberwallis
haut-valais bas-valais rhone
sa ag sarl gmbh snc kg sagl
commune municipalite ville bourgeoisie paroisse consortage fondation association etat canton service departement
administration office gemeinde einwohnergemeinde burgergemeinde munizipalgemeinde stadtgemeinde pfarrei
kirchgemeinde kanton staat dienststelle verein stiftung genossenschaft alpgenossenschaft
construction transformation renovation agrandissement demolition amenagement amenagements installation pose
remplacement creation realisation assainissement extension surelevation changement mise reconstruction
modification modifications ameliorations amelioration correction regularisation reamenagement raccordement
equipement deplacement isolation habillage refection rehaussement implantation abattage defrichement
immeuble immeubles chalet chalets maison maisons villa habitation habitations logement logements appartement
appartements halle hangar garage garages couvert piscine annexe batiment batiments entrepot atelier depot ecole
creche ems hotel restaurant cafe commerce bureau bureaux parking place places route routes chemin rue avenue
mur murs toiture toit facade facades fenetres balcon terrasse cave grange raccard mazot ecurie etable remise
cabane abri jardin cloture portail acces pont canal conduite conduites station antenne panneaux solaires
photovoltaique photovoltaiques pompe chaleur citerne silo serre vigne vignes cave alpage alpages buvette
cuisine salle salles vestiaires local locaux magasin centre foyer eglise chapelle cimetiere home colonie camping
zone zones parcelle parcelles rez etage etages combles sous-sol attique lucarne lucarnes velux cheminee
ascenseur escalier fosse step reseau eau eaux usees claires electricite gaz chauffage bois beton metal
neubau umbau anbau ausbau abbruch sanierung erweiterung renovation errichtung erstellung umnutzung aufstockung
einbau ersatz rueckbau ruckbau instandsetzung verlegung anpassung anpassungen anschluss abriss wiederaufbau
mehrfamilienhaus einfamilienhaus zweifamilienhaus doppeleinfamilienhaus wohnhaus wohnhauser haus hauser
ferienhaus ferienwohnung wohnung wohnungen halle lagerhalle werkhalle garage garagen stall scheune stadel
speicher remise carport einstellhalle tiefgarage gebaude hotel restaurant schule kindergarten turnhalle
werkstatt buro gewerbe industrie lager efh mfh zfh dfh pv pv-anlage photovoltaikanlage solaranlage
warmepumpe schwimmbad pool balkon terrasse dach fenster fassade zufahrt strasse mauer stutzmauer platz weg
kirche kapelle friedhof alphutte hutte chalet maiensass antenne mobilfunkanlage reservoir leitung leitungen
wasserleitung kanalisation brucke wald rebberg reben keller dachgeschoss dachfenster lukarne lukarnen
parzelle parz nr gst swisscom salt sunrise
art artikel al abs ziff lit rpg rpv lat oat lc oc lcat baug bauv
""".split())  # noqa: SIM905 — a word list reads better as text
_SUFFIX_OK = re.compile(r"(?:haus|hauser|halle|hallen|anlage|anlagen|gebaude|bau|bauten|garage|garagen|stall|"
                        r"scheune|stadel|wohnung|wohnungen|mauer|dach|fassade|zone|platz|leitung|leitungen|heizung|"
                        r"pumpe|terrasse|balkon|lift|zimmer|raum|keller|becken|brucke|sanierung|erweiterung|umbau|"
                        r"neubau|abbruch|ersatz|umnutzung|einbau|ausbau|anbau|aufstockung|unterstand|uberdachung|"
                        r"parkplatz|parkplatze|zufahrt|strasse|weg|schutz|geschoss|arbeiten|treppe|wechsel|seite|"
                        r"hauses)$"
                        # German and French noun endings, long words only (short surnames such as « Jung » excluded)
                        r"|^.{4,}(?:ung|ungen|tion|tionen|heit|keit|schaft|ierung|lage)$|^.{6,}ment$|^.{3,}gang$")
# after these words a capitalised word is often an owner's name: only known words are kept
_TRIGGERS = frozenset(_fold(w) for w in """efh mfh zfh dfh haus wohnhaus einfamilienhaus zweifamilienhaus ferienhaus
chalet villa maison mazot raccard familie famille fam chez propriete""".split())  # noqa: SIM905
_PARTICLES_SKIP = frozenset({"de", "du", "des", "d", "l", "von", "vom", "zum", "zur", "la", "le", "les"})
_PRIVATE_COLLECTIVE = re.compile(
    r"\b(hoirie|erbengemeinschaft|ppe|copropri[ée]t[ée]|stockwerkeigent\w*|soci[ée]t[ée] simple|"
    r"einfache gesellschaft|fondation de famille|familienstiftung|famille|familie|fam\.)", re.IGNORECASE)
_ARTICLE = r"(?:(?:la|le|les|l['’]|die|der|das)\s*)?"
# public authorities and bodies under public law: kept, only first names and party words are masked inside
_PUBLIC_START = re.compile(
    rf"^{_ARTICLE}(?:commune|municipalit[ée]|ville\b|bourgeoisie|burgergemeinde|burgerschaft|gemeinde|"
    r"einwohnergemeinde|munizipalgemeinde|stadtgemeinde|stadt\b|paroisse|pfarrei|kirchgemeinde|[ée]glise|kirche|"
    r"[ée]tat du valais|etat du valais|canton|kanton|staat wallis|"
    r"conf[ée]d[ée]ration|office|bundesamt|service|dienststelle|d[ée]partement|departement|administration|"
    r"commission|syndicat|triage|forstrevier|r[ée]gie|cff\b|sbb\b|ofrou\b|astra\b|armasuisse|"
    r"h[ôo]pital|spital|[ée]cole|schule|centre scolaire|association intercommunale|zweckverband|direction\b|"
    r"haute[- ][ée]cole|hes-so|hevs\b)", re.IGNORECASE)
# bodies that can carry a person's or a family's name: kept, but every word is checked (strict)
_ASSOCIATION_START = re.compile(
    rf"^{_ARTICLE}(?:consortage|geteilschaft|alpgenossenschaft|fondation|stiftung|association|verein|"
    r"soci[ée]t[ée] de d[ée]veloppement|club|ski-club|"
    r"soci[ée]t[ée] coop[ée]rative|coop[ée]rative|genossenschaft|consortium|amicale)", re.IGNORECASE)
_SEP = re.compile(
    r"\s*(?:[,;()\[\]\n]|\s/\s|\bc/o\b|\bp\.\s?a\.|\bpar\b|\brepr[ée]sent[ée]e?s?\b|\bvertreten\s+durch\b|"
    r"\bz\.\s?h(?:d|nd)?\.|\bzuhanden\b|\bà\s+l['’]att(?:ention)?\.?(?:\s+de)?|\batt\.|\bbei\b|"
    r"\b[\w'’.-]+\s*:|\bche[-‐]?\d{3}\.?\d{3}\.?\d{3}\b|"
    r"\s+(?:et|und)\s+(?!(?:fils|cie|co|söhne|sohn|partner|partenaires|associ[ée]s)\b))\s*", re.IGNORECASE)
# « 3930 Visp » (an address, never part of a company: « Construction 2000 SA » is not an NPA) and « X SA - Rue … »
_NPA_PLACE = re.compile(r"\b[1-3]\d{3}\s+(?!(?:SA|AG|S\.A\.|Sàrl|SARL|GmbH)\b)[A-ZÀ-ÖØ-Þ][\w'’\-]*(?:\s+\([A-Z]{2}\))?")
_DASH = re.compile(r"\s[-–—]\s")
# words that may follow the legal form in a company name (« Exemple SA Immobilier »)
_COMPANY_TAIL = re.compile(r"(?:\s+(?:immobili[eè]re?|immobilier|immobilien|constructions?|holding|groupe?|group|"
                           r"services?|"
                           r"management|invest|partners?|bau|holzbau|architecture|architektur|ing[ée]nierie|"
                           r"engineering|suisse|schweiz|valais|wallis)){1,2}\s*$", re.IGNORECASE)
_BARE_FORM = re.compile(r"^(?:s\.?\s?a\.?|a\.?\s?g\.?|s[àa]rl|s\.?\s?[àa]\s?r\.?\s?l\.?|gmbh|g\.?\s?m\.?\s?b\.?\s?h\.?|"
                        r"sagl|snc|kg)"
                        r"(?:\s+(?:en formation|en liquidation|in gründung|in liquidation))?$", re.IGNORECASE)
_WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ][\w'’\-]*")
# a number of 3 digits or more is a parcel, a PPE unit or a lot unless it is a year or a quantity with its unit
_UNIT = (r"(?:m2|m²|m3|m³|m|km|cm|mm|kw|kwp|kwh|kv|kva|mw|mwh|gwh|ha|l|litres?|places?|logements?|appartements?|"
         r"wohnungen|zimmer|"
         r"parkplätze|plätze|lits|betten|chf|fr\.?|francs|%|pièces?|chambres?|personnes?|t|tonnes?|mètres?|meter|"
         r"jahre|ans|élèves|schüler|sièges|sitzplätze|véhicules|fahrzeuge|kg)")
_LONG_NUMBER = re.compile(rf"(?<![\w.,'’/-])(?!(?:19|20)\d\d\b)\d{{3,6}}(?:['’]\d{{3}})?"
                          rf"(?![\w.'’/-]|,\d|\s*{_UNIT}\b)", re.IGNORECASE)
_PRICE_BEFORE = re.compile(r"(?:CHF|Fr\.)\s*$")
# a reference to a law article keeps its number (« Art. 24 RPG », « al. 2 »)
_LAW_REF = re.compile(r"(?i)\b(?:art|artikel|al|abs|ziff|lit|let|rs|sr)\.?\s*$")
# capitalised words followed by a house number anywhere in a title (« an der Sonnmatte 12 (EFH 13) », « Sonnmatte 12 und
# 14 »): the numbers are masked, and so are the words that are not known (a street name), never a quantity or a year
_HOUSE = re.compile(
    r"(?P<words>(?:(?:[A-ZÀ-ÖØ-Þ][\w'’\-]*\.?|\[masqué\])\s+){1,3})"
    r"(?P<num>(?!(?:19|20)\d\d\b)\d{1,4}(?:\s?[a-zA-Z](?![a-zA-Z]))?"
    r"(?:\s*(?:und|et|/|-|–)\s*\d{1,4}(?:\s?[a-zA-Z](?![a-zA-Z]))?)*)\b"
    rf"(?!\s*(?i:{_UNIT})\b)(?![.,]\d)")
# street + number, masked in free text like the parcel (« Route de X 12 », « Bahnhofstrasse 3a »)
_STREET_ADDR = re.compile(
    r"\b(?:rue|route|chemin|ch\.|avenue|av\.|place|impasse|all[ée]e|quai|boulevard|ruelle|sentier|promenade|"
    r"[\wäöü]*strasse|[\wäöü]*str\.|[\wäöü]*weg|[\wäöü]*gasse|[\wäöü]*platz)\b[^,;\n\d]{0,40}?\d+\s?[a-zA-Z]?\b",
    re.IGNORECASE)
# a civility or an « attention of » marker: the words that follow are a person, whatever their frequency
_ADDRESSEE = re.compile(
    r"(?P<m>(?:\b(?:Monsieur|Madame|Mademoiselle|Herrn?|Frau|Mme|Mlle|Dr\.?|zuhanden|(?:Domicile|Wohnsitz|Wohnort)"
    r"\s*:)|\bz\.\s?H(?:d|nd)?\.|\bc/o\b|\bp\.\s?a\.|\bà\s+l['’]att(?:ention)?\.?(?:\s+de)?|(?<![\w.])M\.))"
    r"(?P<n>(?:\s*(?:[A-ZÀ-ÖØ-Þ][\w'’\-]*\.?|von|van|de|du|der|di)(?=[\s,;.)]|$)){1,4})")
_SWEEP_MARKERS = re.compile(
    r"(?:\b(?:Domicile|Wohnsitz|Wohnort)\s*:|\bc/o\b|\bp\.\s?a\.|\bz\.\s?Hd\.|\bzuhanden\b|"
    r"\b(?:Monsieur|Madame|Mademoiselle|Herrn?|Frau|Mme|Mlle)\b|(?<![\w.])M\.)\s*(?!\[masqué\])[A-ZÀ-ÖØ-Þ]"
    r"|\bnée? le\b|\bgeb\.\s")
_SWEEP_ROLE_IN_TITLE = re.compile(r"\b(?:Requérant|Gesuchsteller|Propriétaire|Grundeigentümer|Projektverfasser|"
                                  r"Planverfasser|Domicile|Wohnsitz)\b", re.IGNORECASE)
_SWEEP_NPA = re.compile(r"\b[1-3]\d{3}\s+[A-ZÀ-ÖØ-Þ]")


@dataclass
class FilterContext:
    """Built in memory over the WHOLE import before anything is filtered (never written)."""

    person_words: set[str] = dc_field(default_factory=set)  # folded words of every masked party
    title_vocab: set[str] = dc_field(default_factory=set)   # folded words seen in >= 3 index titles
    text_vocab: set[str] = dc_field(default_factory=set)    # folded words seen in >= 5 publications' other fields
    localities: set[str] = dc_field(default_factory=set)    # folded localities and communes (and their words)
    title_words: set[str] = dc_field(default_factory=set)   # every folded word read (index titles, corpus)


def _pieces(value: str) -> list[str]:
    lines = [x.strip() for x in (value or "").split("\n") if x.strip()]
    merged: list[str] = []
    for line in lines:  # a legal form wrapped alone on the next line belongs to the name above
        if merged and _BARE_FORM.match(line) and not legal_form_at_end(merged[-1]):
            merged[-1] += " " + line
        else:
            merged.append(line)
    out: list[str] = []
    for line in merged:
        line = _NPA_PLACE.sub(lambda m: "\n" + m.group(0) + "\n", line)
        right = _DASH.split(line)[-1]
        if not (legal_form_at_end(right) and not re.search(r"\d", right)):  # « X Planung - Architektur AG » is one name
            line = _DASH.sub("\n", line)
        for part in line.split("\n"):
            out += [_trim(p) for p in _SEP.split(part)]
    return [p for p in out if p and re.search(r"\w", p)]


def _trim(piece: str) -> str:
    p = piece.strip(" -–—:/")
    return p if re.search(r"\b\w\.$", p) else p.strip(" .")  # « Exemple S.A. » keeps its dot


def _company_end(piece: str) -> bool:
    return bool(legal_form_at_end(piece) or legal_form_at_end(_COMPANY_TAIL.sub("", piece)))


_GLUE_PARTICLES = frozenset({"de", "du", "des", "d", "l", "la", "le", "les", "et", "und", "von", "&", "+", "y", "e"})
# words that describe a trade, not a brand: a company name made of them (+ legal form) is not a separate company
_GENERIC = frozenset(_fold(w) for w in """construction constructions bau holzbau hochbau tiefbau architekt architekten
architecte architectes planung
ingenieur ingenieure ingénieur ingénieurs
architecture architektur ingenieure ingenieurs ingenieurbuero engineering immobilier immobiliere immobilien invest
gestion services service partner partners partenaires sia groupe group holding bureau atelier entreprise unternehmung
bauunternehmung fils cie sohne sohn et und""".split())  # noqa: SIM905


def _distinctive(words: list[str]) -> bool:
    """At least one word that is neither a legal form, a particle, a trade word nor a construction word."""
    return any(_fold(w) not in _GENERIC | _BASE | _GLUE_PARTICLES and not _BARE_FORM.match(w)
               and not legal_form_at_end(w) for w in words)


def _glued_person(piece: str) -> int:
    """« Ottmar Beispiel mls architekten sia ag »: capitalised names (2 or more, not template words) glued before a
    company written in lower case. Returns the number of leading words to mask (0 if none)."""
    toks = piece.split()
    n = 0
    while n < len(toks) and toks[n][:1].isupper() and _fold(toks[n]) not in _BASE and not legal_form_at_end(toks[n]):
        n += 1
    if n >= 2 and n < len(toks) and toks[n][:1].islower() and _fold(toks[n]) not in _GLUE_PARTICLES \
            and _company_end(" ".join(toks[n:])) and _distinctive(toks[n:]):
        return n
    return 0


def _classify_piece(piece: str) -> str:
    """« entreprise » | « public » | « association » | « personne » for ONE piece."""
    p = piece.strip()
    if not p or _PRIVATE_COLLECTIVE.search(p):
        return "personne"
    if _company_end(p) and not _ASSOCIATION_START.match(p):
        return "entreprise"
    if re.search(r"\d", p):
        return "personne"  # an address (street number, NPA) is never a body
    if _PUBLIC_START.match(p):
        return "public"
    if _ASSOCIATION_START.match(p):
        return "association"
    return "personne"


def classify_party(name: str) -> str:
    """« entreprise », « public » (communes, bourgeoisies, fondations, paroisses, consortages, authorities,
    associations) or « personne » (everything else, masked)."""
    kind = _classify_piece(name)
    return "public" if kind == "association" else kind


def _person_words(piece: str) -> set[str]:
    """Capitalised words of a masked party piece (not addresses, not template words) for masking elsewhere."""
    if re.search(r"\d", piece):
        return set()
    out = set()
    for w in _WORD.findall(piece):
        core = re.sub(r"^(?:[dlDL]|qu)['’]", "", w)
        f = _fold(core)
        if core[:1].isupper() and len(f) >= 2 and f not in _BASE and not _PRIVATE_COLLECTIVE.fullmatch(core):
            out.add(f)
            out.update(x for x in f.split("-") if len(x) >= 2 and x not in _BASE)
    return out


def _mask_words(text: str, ctx: FilterContext, vocab: set[str] | None) -> tuple[str, int]:
    """Mask capitalised words that are, or may be, names. ``vocab`` None = only first names and party words
    (public bodies); otherwise a capitalised word must be known (vocab, construction words, localities)."""
    count = 0
    trigger_left = 0
    last_end = 0

    def known(f: str) -> bool:
        parts = [x for x in f.split("-") if x]
        return (f in _BASE or f in ctx.localities or (vocab is not None and f in vocab) or bool(_SUFFIX_OK.search(f))
                or (bool(parts) and all(x in _BASE or x in ctx.localities or (vocab is not None and x in vocab)
                                        for x in parts)))

    def repl(m: re.Match[str]) -> str:
        nonlocal count, trigger_left, last_end
        word = m.group(0)
        if re.search(r"[,;:()/]", m.string[last_end:m.start()]):
            trigger_left = 0  # « Umbau Haus X, Lens »: the commune after the comma is not the owner
        last_end = m.end()
        prefix = re.match(r"^(?:[dlDL]|qu)['’]", word)
        core = word[prefix.end():] if prefix else word
        f = _fold(core)
        after_trigger = trigger_left > 0
        if f in _PARTICLES_SKIP and core[:1].islower():
            return word
        trigger_left = max(trigger_left - 1, 0)
        if f in _TRIGGERS:
            trigger_left = 2
        if not core or not core[0].isupper():
            return word
        parts = [x for x in f.split("-") if x]
        if f in ctx.localities and not after_trigger and len(core) > 1:
            return word
        mask = (len(core) == 1 or f in ctx.person_words or any(x in ctx.person_words for x in parts) or f in _FIRST
                or any(x in _FIRST for x in parts))  # an initial (« J.-P. D. ») is a person
        if not mask and after_trigger:  # right after « Haus », « Chalet »…: even a place name may be the owner's
            mask = not (f in _BASE or bool(_SUFFIX_OK.search(f)))
        if not mask and vocab is not None:
            mask = not known(f)
        if mask:
            count += 1
            return (prefix.group(0) if prefix else "") + REDACTED
        return word

    def addressee(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return f"{m.group('m')} {REDACTED}"

    def street(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return REDACTED

    def long_number(m: re.Match[str]) -> str:
        nonlocal count
        before, after = m.string[:m.start()], m.string[m.end():]
        if _PRICE_BEFORE.search(before) or _LAW_REF.search(before):
            return m.group(0)
        if len(m.group(0)) == 4 and re.match(r"\s+[A-ZÀ-ÖØ-Þ][a-zà-ÿ]", after):
            return m.group(0)  # a postcode before its locality (« 1950 Sion ») is not a person's address
        count += 1
        return REDACTED

    def house(m: re.Match[str]) -> str:
        nonlocal count
        words = m.group("words").split()
        if _LAW_REF.search(m.group("words")):
            return m.group(0)
        count += 1
        kept = [w if w == REDACTED or (known(_fold(w.rstrip("."))) and _fold(w.rstrip(".")) not in ctx.person_words)
                else REDACTED for w in words]
        return " ".join(kept) + " " + REDACTED

    text = _ADDRESSEE.sub(addressee, text)
    if vocab is not None:
        text = _STREET_ADDR.sub(street, text)
        text = _HOUSE.sub(house, text)
        text = _LONG_NUMBER.sub(long_number, text)
    out = _WORD.sub(repl, text)
    red, n = redact_text(out)  # civilities, role labels, parcels, coordinates
    return _collapse(red), count + n


def _collapse(text: str) -> str:
    return re.sub(rf"(?:{re.escape(REDACTED)}[\s,\-–]*)+{re.escape(REDACTED)}", REDACTED, text)


def build_context(pubs: list[dict[str, Any]], index_titles: list[str], localities: list[str]) -> FilterContext:
    """One context for the whole import: a word of a masked party is masked in EVERY publication."""
    from collections import Counter

    ctx = FilterContext()
    for loc in localities:
        f = _fold(loc)
        ctx.localities.add(f)
        ctx.localities.update(x for x in re.split(r"[\s/]+", f) if len(x) >= 3 and x not in _PARTICLES_SKIP)
    for p in pubs:
        for values in p.get("roles", {}).values():
            for value in values:
                for piece in _pieces(value):
                    if _classify_piece(piece) == "personne":
                        ctx.person_words |= _person_words(piece)
        for values in p.get("champs", {}).values():  # « z. Hd. Herr X » in a contact point, « Domicile: … »
            for v in values:
                for m in _ADDRESSEE.finditer(v or ""):
                    ctx.person_words |= _person_words(m.group("n"))
    ctx.person_words -= ctx.localities
    title_count: Counter[str] = Counter()
    for t in index_titles:
        title_count.update({_fold(re.sub(r"^(?:[dlDL]|qu)['’]", "", w)) for w in _WORD.findall(t or "")})
    text_count: Counter[str] = Counter()
    for p in pubs:
        words: set[str] = set()
        for k, values in p.get("champs", {}).items():
            if k not in {"coordonnees", "parcelle"}:
                for v in values:
                    words |= {_fold(re.sub(r"^(?:[dlDL]|qu)['’]", "", w)) for w in _WORD.findall(v or "")}
        text_count.update(words)
    ctx.title_words = set(title_count) | set(text_count)
    for p in pubs:  # every word read in the corpus: a fragment left by a cut word appears nowhere on its own
        ctx.title_words |= {_fw(w) for w in _WORD.findall(p.get("titre") or "")}
    bad = ctx.person_words | _FIRST
    ctx.title_vocab = {w for w, n in title_count.items() if n >= 3} - bad
    ctx.text_vocab = ({w for w, n in text_count.items() if n >= 5} | ctx.title_vocab) - bad
    return ctx


def filter_publication(pub: dict[str, Any], ctx: FilterContext | None = None
                       ) -> tuple[dict[str, Any], list[dict[str, str]]]:
    ctx = ctx or build_context([pub], [], [])
    masks: list[dict[str, str]] = []
    companies: list[str] = []
    publics: list[str] = []
    roles: dict[str, list[str]] = {}
    cut = {fld: [_pieces(v) for v in pub["roles"].get(fld, [])] for fld in ROLE_FIELDS}
    alone = {p for vs in cut.values() for ps in vs for p in ps
             if _classify_piece(p) == "entreprise" and len(p.split()) >= 2 and _distinctive(p.split())}

    def unglue(piece: str) -> list[str]:
        """A person glued before a company: the company cited alone elsewhere, or a lower-case brand."""
        for q in sorted(alone, key=len, reverse=True):
            if q != piece and piece.endswith(" " + q):
                return [piece[: -len(q)].strip(), q]
        n = _glued_person(piece)
        return [" ".join(piece.split()[:n]), " ".join(piece.split()[n:])] if n else [piece]

    for fld in ROLE_FIELDS:
        out = []
        for value_pieces in cut[fld]:
            kept: list[str] = []
            masked = 0
            for piece in [x for p in value_pieces for x in (unglue(p) if _classify_piece(p) == "entreprise" else [p])]:
                if _BARE_FORM.match(piece):
                    continue  # « SA » alone (a wrapped line): not a company, not a person
                kind = _classify_piece(piece)
                if kind == "entreprise":
                    kept.append(piece)
                    companies.append(piece)
                elif kind in {"public", "association"}:
                    clean, n = _mask_words(piece, ctx, None if kind == "public" else ctx.title_vocab)
                    kept.append(clean)
                    publics.append(clean)
                    masked += n
                else:
                    kept.append(REDACTED)
                    masked += 1
            joined = " ; ".join(x for i, x in enumerate(kept) if not (x == REDACTED and i and kept[i - 1] == REDACTED))
            if masked:
                masks.append({"champ": fld, "motif": "personne physique, adresse ou texte non reconnu (règle prudente)"
                              if joined == REDACTED else "personne ou adresse jointe à une organisation"})
            out.append(joined or REDACTED)
        roles[fld] = out
    title, n_title = _mask_words(pub["titre"], ctx, ctx.title_vocab)
    if n_title:
        masks.append({"champ": "titre", "motif": "mot masqué dans le titre (nom possible, règle prudente)"})
    champs: dict[str, list[str]] = {}
    for fld, values in pub["champs"].items():
        if fld == "coordonnees":
            champs[fld] = [REDACTED for _ in values]
        elif fld == "parcelle":  # « Parzellen-Nr 123, Plan Nr 4 »: every number of a parcel is masked
            champs[fld] = [_mask_words(re.sub(r"\d[\d'.,/-]*", REDACTED, v), ctx, ctx.text_vocab)[0] for v in values]
        elif fld == "numero_econstruction":
            champs[fld] = [redact_text(v)[0] for v in values]
        else:
            strict = fld in {"titre_projet", "point_de_contact"}  # a clerk's name can be frequent there
            champs[fld] = [_mask_words(v, ctx, ctx.title_vocab if strict else ctx.text_vocab)[0] for v in values]
    lines = [f"Demande d'autorisation de construire — {title}"]
    for fld in ("titre_projet", "numero_econstruction"):
        lines += [f"{fld} : {v}" for v in champs.get(fld, [])]
    for fld in ROLE_FIELDS:
        lines += [f"{fld} : {v}" for v in roles[fld]]
    for fld, values in champs.items():
        if fld not in {"titre_projet", "numero_econstruction"}:
            lines += [f"{fld} : {v}" for v in values]
    text = "\n".join(lines)
    for m in masks:
        m["apercu"] = f"{m['champ']} → {REDACTED} · titre : {title[:90]}"
    filtered = {k: v for k, v in pub.items() if k not in {"roles", "champs", "titre", "titre_projet"}}
    project_titles: list[str | None] = [*champs.get("titre_projet", []), None]
    filtered.update({"titre": title, "titre_projet": project_titles[0], "roles": roles,
                     "texte": text, "masquages": len(masks), "entreprises_citees": sorted(set(companies)),
                     "organismes_publics_cites": sorted(set(publics))})
    return filtered, masks


_CARE_OF = re.compile(r"^(?:c/o|p\.\s?a\.|z\.\s?Hd\.|zuhanden)", re.IGNORECASE)


def has_person_marker(text: str) -> bool:
    """« Domicile: X », « c/o X », « z. Hd. X », « Herr X »… left unmasked (shared with the demo export sweep).
    « c/o » or « p.a. » followed by an organisation (« c/o Gérance X SA ») is not a person."""
    for m in _SWEEP_MARKERS.finditer(text or ""):
        if _CARE_OF.match(m.group(0)):
            follow = re.split(r"[,;()]", text[m.end() - 1:])[0].strip()
            if _classify_piece(follow) != "personne":
                continue
        return True
    return False


_AFTER_MASK = re.compile(rf"{re.escape(REDACTED)}\s+([a-zà-öø-ÿ][\w'’\-]{{2,}})")


def _sweep_value(value: str, title: bool, places: set[str] | frozenset[str] = frozenset(),
                 title_words: set[str] | None = None) -> list[str]:
    reasons = []
    if title and title_words is not None and any(
            _fw(w) not in title_words and _fw(w) not in _BASE for w in _AFTER_MASK.findall(value)):
        reasons.append("fragment de mot après un masque (césure ?)")
    if any(_glued_person(p) for p in value.split(" ; ")):
        reasons.append("personne collée à une société")
    if has_person_marker(value):
        reasons.append("marqueur de personne (domicile, c/o, civilité)")
    if title and _SWEEP_ROLE_IN_TITLE.search(value):
        reasons.append("mot de rôle dans un titre")
    for piece in value.split(" ; "):
        if legal_form_at_end(piece):
            continue  # a company may carry its founder's name
        words = [_fold(re.sub(r"^(?:[dlDL]|qu)['’]", "", w)) for w in _WORD.findall(piece) if w[:1].isupper()
                 or re.match(r"^(?:[dlDL]|qu)['’][A-ZÀ-ÖØ-Þ]", w)]
        if any(w not in places and (w in _FIRST or any(x in _FIRST for x in w.split("-"))) for w in words):
            reasons.append("prénom hors forme juridique")
            break
    return reasons


def sweep_rows(rows: list[dict[str, Any]], texts: dict[str, str] | None = None,
               ctx: FilterContext | None = None) -> None:
    """Last check before writing (public rows, report strings, private texts). Raises PersonalDataFound.
    A first name that is a whole locality (« Saint-Maurice ») is not a person."""
    places = ctx.localities if ctx else set()
    findings: list[dict[str, str]] = []

    def check(pid: str, fld: str, value: str | None, title: bool = False, address: bool = False) -> None:
        if not value:
            return
        reasons = _sweep_value(value, title, places, ctx.title_words if ctx and ctx.title_words else None)
        if address and any(_SWEEP_NPA.search(p) for p in value.split(" ; ") if not legal_form_at_end(p)):
            reasons.append("adresse (NPA) dans une valeur gardée")
        findings.extend({"publication": pid, "champ": fld, "motif": r} for r in reasons)

    for r in rows:
        pid = str(r.get("id"))
        check(pid, "titre", r.get("titre"), title=True)
        check(pid, "titre_projet", r.get("titre_projet"), title=True)
        for fld, values in (r.get("roles") or {}).items():
            for v in values:
                check(pid, f"roles.{fld}", v, address=True)
        for v in (r.get("entreprises_citees") or []) + (r.get("organismes_publics_cites") or []):
            check(pid, "organisations", v, address=True)
    for pid, text in (texts or {}).items():
        for line in text.splitlines():
            check(pid, "texte", line.split(" : ", 1)[-1] if " : " in line else line)
    if findings:
        raise PersonalDataFound(findings)
