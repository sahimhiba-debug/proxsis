"""Company identifiers and names: UID (IDE) handling, name normalisation,
legal-entity detection.

The UID check digit follows the eCH-0097 rule: weights 5,4,3,2,7,6,5,4 on
the first eight digits, ``11 - (sum mod 11)``; 11 -> 0; 10 -> invalid.
"""

from __future__ import annotations

import re
import unicodedata

_UID_WEIGHTS = (5, 4, 3, 2, 7, 6, 5, 4)
_UID_RE = re.compile(r"(?:CHE)?[\s\-.]*(\d{3})[\s.]*(\d{3})[\s.]*(\d{3})", re.IGNORECASE)


def uid_check_digit(first8: str) -> int | None:
    if len(first8) != 8 or not first8.isdigit():
        raise ValueError("expected 8 digits")
    s = sum(int(d) * w for d, w in zip(first8, _UID_WEIGHTS, strict=True))
    check = 11 - (s % 11)
    if check == 11:
        return 0
    if check == 10:
        return None
    return check


def uid_is_valid(raw: object) -> bool:
    return normalize_uid(raw) is not None


def normalize_uid(raw: object) -> str | None:
    """Return ``CHE#########`` or ``None`` if absent (incl. NaN) or checksum invalid."""
    if not isinstance(raw, str) or not raw:
        return None
    m = _UID_RE.search(raw)
    if not m:
        return None
    digits = "".join(m.groups())
    expected = uid_check_digit(digits[:8])
    if expected is None or expected != int(digits[8]):
        return None
    return f"CHE{digits}"


def format_uid(uid: str) -> str:
    d = uid.replace("CHE", "")
    return f"CHE-{d[0:3]}.{d[3:6]}.{d[6:9]}"


# --- names ---------------------------------------------------------------

# Ordered longest first so that "s.a r.l." wins over "s.a."
_LEGAL_FORMS: list[tuple[str, str]] = [
    (r"s\.?\s?a\.?\s?r\.?\s?l\.?", "SARL"),
    (r"s\.?\s?à\s?r\.?\s?l\.?", "SARL"),
    (r"sàrl", "SARL"),
    (r"sarl", "SARL"),
    (r"g\.?\s?m\.?\s?b\.?\s?h\.?", "GMBH"),
    (r"sagl", "SAGL"),
    (r"genossenschaft", "GENOSSENSCHAFT"),
    (r"société coopérative|societe cooperative|coopérative|cooperative", "COOPERATIVE"),
    (r"a\.?\s?g\.?", "AG"),
    (r"s\.?\s?a\.?", "SA"),
    (r"ltd\.?|limited", "LTD"),
    (r"inc\.?|incorporated", "INC"),
    (r"corp\.?|corporation", "CORP"),
    (r"s\.?\s?p\.?\s?a\.?", "SPA"),
    (r"llc", "LLC"),
    (r"b\.?\s?v\.?|n\.?\s?v\.?", "BV_NV"),
    (r"snc", "SNC"),
    (r"kg", "KG"),
    (r"stiftung|fondation", "FONDATION"),
    (r"verein|association", "ASSOCIATION"),
]
_LEGAL_FORM_RES = [
    (re.compile(rf"(?:^|[\s,(])(?:{pat})(?=$|[\s,)])", re.IGNORECASE), code) for pat, code in _LEGAL_FORMS
]

# Words that mark public bodies or organisations (FR/DE/IT)
_ORG_WORDS = re.compile(
    r"\b("
    r"commune|municipalit[ée]|ville de|canton|[ée]tat d[eu]|etat d[eu]|conf[ée]d[ée]ration|"
    r"bourgeoisie|paroisse|hôpital|hopital|[ée]cole|universit[ée]|service|office|d[ée]partement|"
    r"soci[ée]t[ée]|entreprise|holding|groupe|consortium|"
    r"gemeinde|einwohnergemeinde|burgergemeinde|kirchgemeinde|stadt|kanton|bund|amt|"
    r"spital|schule|universit[äa]t|gesellschaft|konsortium|"
    r"comune|cantone"
    r")\b",
    re.IGNORECASE,
)

_UMLAUTS = {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "ae", "Ö": "oe", "Ü": "ue", "ß": "ss"}


def _strip_accents(s: str) -> str:
    for k, v in _UMLAUTS.items():
        s = s.replace(k, v)
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def legal_form(name: str) -> str | None:
    for rx, code in _LEGAL_FORM_RES:
        if rx.search(name):
            return code
    return None


# Company forms only (foundations and associations are handled by the callers), at the END of a name, optionally
# followed by « en formation » / « in Gründung » / « en liquidation ».
_COMPANY_CODES = {"SARL", "GMBH", "SAGL", "GENOSSENSCHAFT", "COOPERATIVE", "AG", "SA", "LTD", "INC", "CORP", "SPA",
                  "LLC", "BV_NV", "SNC", "KG"}
_LEGAL_FORM_END_RES = [
    (re.compile(rf"(?:^|[\s,(])(?:{pat})\s*(?:en (?:formation|liquidation)|in (?:gründung|liquidation))?\s*$",
                re.IGNORECASE), code)
    for pat, code in _LEGAL_FORMS if code in _COMPANY_CODES
]


def legal_form_at_end(name: str) -> str | None:
    """Company legal form ending the name (« Exemple Immobilier SA », « Beispiel Planung GmbH in Gründung »)."""
    for rx, code in _LEGAL_FORM_END_RES:
        if rx.search(name or ""):
            return code
    return None


def is_legal_entity_name(name: str) -> bool:
    """Heuristic: True if the name designates a company or a public body.

    Used by the personal-data filter: anything that is *not* a legal entity
    is treated as a private person and must not be stored.
    """
    if not name or not name.strip():
        return False
    return legal_form(name) is not None or bool(_ORG_WORDS.search(name))


def normalize_name(name: str) -> str:
    """Canonical form for matching: lowercase, no accents, no legal form,
    no punctuation, '&'/'und' -> 'et', single spaces."""
    s = name
    for rx, _ in _LEGAL_FORM_RES:
        s = rx.sub(" ", s)
    s = _strip_accents(s).lower()
    s = s.replace("&", " et ").replace("+", " et ")
    s = re.sub(r"\bund\b", " et ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\b(en|in) liquidation\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()
