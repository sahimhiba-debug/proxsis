"""Flexsis agency specialties and the classification of a simap lot into a work phase and a specialty.

Several Flexsis agencies carry a trade label (« Bâtiment », « Électricité », « Technique », « Industrie »; 16 of 48,
docs/recherche/flexsis_offre.md); the three Valais agencies only carry a town name. The specialty here is the
trade family of a lot. A lot is classified, in order of reliability:

1. CFC / BKP code (``phasing.phase_of``; CFC structure SN 506 500:2017, CRB);
2. NPK chapter (CRB Normpositionen-Katalog: chapters 1xx general items and civil works, 2xx civil works,
   3xx structural building work);
3. CPV code (Common Procurement Vocabulary 2008, division 45 « construction work » and, for industry, the
   supply divisions of manufactured goods). A generic CPV (45000000, 45200000) is flagged
   ``cpv_generique``: it says « construction » but not which work.

Architecture and engineering services (CPV 71) are not labour for a staffing agency: no specialty.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from proxsis.phasing import PHASE_TRADES, phase_of


@dataclass(frozen=True)
class Specialty:
    code: str
    label_fr: str
    label_de: str
    phases: tuple[str, ...]
    trades: tuple[str, ...]


SPECIALTIES: dict[str, Specialty] = {
    s.code: s
    for s in [
        Specialty("batiment", "Bâtiment", "Bau",
                  ("preparatoire", "terrassement", "genie_civil", "gros_oeuvre", "enveloppe", "amenagement_int",
                   "metallerie", "menuiserie", "finitions", "exterieur"),
                  ("macon", "manoeuvre_construction", "coffreur", "grutier", "machiniste", "charpentier", "platrier",
                   "peintre")),
        Specialty("electricite", "Électricité", "Elektro", ("electricite",), ("electricien",)),
        Specialty("technique", "Technique du bâtiment", "Gebäudetechnik", ("cvc", "sanitaire", "transport",
                                                                            "equipement"),
                  ("installateur_sanitaire",)),
        Specialty("industrie", "Industrie", "Industrie", ("industrie",),
                  ("operateur_production", "polymecanicien", "soudeur")),
    ]
}
PHASE_SPECIALTY: dict[str, str] = {p: s.code for s in SPECIALTIES.values() for p in s.phases}

# Phases outside ``phasing.PHASES`` (no CFC code): trades and durations used by the needs estimate.
EXTRA_PHASE_TRADES: dict[str, tuple[str, ...]] = {
    "genie_civil": ("machiniste", "manoeuvre_construction", "macon"),
    "menuiserie": ("charpentier",),  # closest trade of the taxonomy for joinery (no « menuisier » yet)
    "metallerie": ("soudeur",),  # CFC 272 « ouvrages métalliques » (metalwork, locksmithing)
    "industrie": ("operateur_production", "polymecanicien", "soudeur"),
}

# CPV 2008 prefixes → phase (longest prefix wins). Division 45 = construction work.
_CPV_PHASE: dict[str, str] = {
    "4511": "terrassement", "4512": "terrassement",
    "4521": "gros_oeuvre", "4522": "genie_civil", "4523": "genie_civil", "4524": "genie_civil",
    "4525": "genie_civil", "4526": "enveloppe",
    "4531": "electricite", "4532": "enveloppe", "4533": "sanitaire", "4534": "exterieur", "4535": "cvc",
    "4541": "amenagement_int", "4542": "menuiserie", "4543": "finitions",
    "4544": "finitions", "4545": "finitions", "4550": "terrassement",
    # supply of manufactured goods made by industrial firms (machines, metal structures, electrical equipment)
    "31": "industrie", "34": "industrie", "38": "industrie", "42": "industrie", "43": "industrie",
    "4421": "industrie", "4431": "industrie", "4451": "industrie", "4461": "industrie",
}
_CPV_GENERIC = ("45000000", "45100000", "45200000", "45300000", "45400000")


def _phase_from_npk(codes: list[str]) -> str | None:
    chapters = {str(c).strip()[:1] for c in codes or [] if str(c).strip()}
    if "3" in chapters:
        return "gros_oeuvre"
    if chapters & {"1", "2"}:
        return "genie_civil"
    return None


def lot_phase(record: dict[str, Any]) -> tuple[str | None, str | None]:
    """(phase, source of the classification) — source in {cfc, npk, cpv, cpv_generique} or (None, None)."""
    codes = [str(c).strip() for c in record.get("bkp_codes") or []]
    ph = phase_of(codes)
    if ph == "amenagement_int":  # CFC 27 mixes plastering (271), metalwork (272) and joinery (273)
        sub = {c[:3] for c in codes if c.startswith("27")}
        if sub and "271" not in sub:
            ph = "metallerie" if "272" in sub else ("menuiserie" if "273" in sub else ph)
    if ph:
        return ph, "cfc"
    ph = _phase_from_npk(record.get("npk_codes") or [])
    if ph:
        return ph, "npk"
    cpv = str(record.get("cpv_code") or "").strip()
    if not cpv:
        return None, None
    for n in (4, 2):
        ph = _CPV_PHASE.get(cpv[:n])
        if ph:
            return ph, "cpv"
    if cpv.startswith("453"):
        return "equipement", "cpv_generique"  # building installation, kind unknown
    if cpv.startswith("454"):
        return "finitions", "cpv_generique"
    if cpv.startswith("451"):
        return "terrassement", "cpv_generique"
    if cpv in _CPV_GENERIC or cpv.startswith("45"):
        return "gros_oeuvre", "cpv_generique"
    return None, None


def lot_specialty(record: dict[str, Any]) -> str | None:
    ph, _ = lot_phase(record)
    return PHASE_SPECIALTY.get(ph) if ph else None


def phase_trades(phase: str) -> tuple[str, ...]:
    return PHASE_TRADES.get(phase) or EXTRA_PHASE_TRADES.get(phase, ())


def specialty_trades(code: str) -> tuple[str, ...]:
    return SPECIALTIES[code].trades
