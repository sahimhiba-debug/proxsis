"""Calendar features computed offline: Swiss public holidays, weeks,
construction winter break.

Holidays: Easter is computed with the anonymous Gregorian algorithm. Only
the holidays used as features are encoded; the cantonal list is partial and
must be checked against the official cantonal lists before production
(see docs/recherche/donnees.md). The construction winter break is an
explicit *assumption* (typical end-of-year closure), not a fact about a
given company.
"""

from __future__ import annotations

from datetime import date, timedelta


def easter_sunday(year: int) -> date:
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month, day = divmod(h + ell - 7 * m + 114, 31)
    return date(year, month, day + 1)


# Holidays beyond the common set, per canton (partial, to verify).
_CANTONAL_FIXED: dict[str, list[tuple[int, int]]] = {
    "VS": [(3, 19), (8, 15), (11, 1), (12, 8)],  # St-Joseph, Assomption, Toussaint, Immaculée Conception
    "GE": [(12, 31)],  # Restauration de la République
    "NE": [(3, 1)],  # Instauration de la République
    "JU": [(6, 23)],  # Commémoration du plébiscite
    "FR": [(8, 15), (11, 1), (12, 8)],
    "LU": [(8, 15), (11, 1), (12, 8)],
    "TI": [(1, 6), (3, 19), (6, 29), (8, 15), (11, 1), (12, 8)],
}
_NO_GOOD_FRIDAY = {"VS", "TI"}
_NO_EASTER_MONDAY = {"VS"}
_NO_WHIT_MONDAY = {"VS"}
_NO_ST_STEPHEN = {"VS", "GE", "JU", "NE"}
_CORPUS_CHRISTI = {"VS", "FR", "JU", "LU", "AI", "NW", "OW", "SZ", "UR", "ZG", "TI"}


def holidays(year: int, canton: str) -> set[date]:
    e = easter_sunday(year)
    days = {date(year, 1, 1), date(year, 8, 1), date(year, 12, 25), e + timedelta(days=39)}  # Ascension
    if canton not in _NO_GOOD_FRIDAY:
        days.add(e - timedelta(days=2))
    if canton not in _NO_EASTER_MONDAY:
        days.add(e + timedelta(days=1))
    if canton not in _NO_WHIT_MONDAY:
        days.add(e + timedelta(days=50))
    if canton not in _NO_ST_STEPHEN:
        days.add(date(year, 12, 26))
    if canton in _CORPUS_CHRISTI:
        days.add(e + timedelta(days=60))
    for m, d in _CANTONAL_FIXED.get(canton, []):
        days.add(date(year, m, d))
    return days


def monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


def weeks_between(start: date, end: date) -> list[date]:
    out = []
    w = monday_of(start)
    while w <= end:
        out.append(w)
        w += timedelta(days=7)
    return out


def is_construction_break(d: date) -> tuple[bool, str]:
    """Typical construction winter closure (hypothesis): from 22 Dec to 6 Jan."""
    flag = (d.month == 12 and d.day >= 22) or (d.month == 1 and d.day <= 6)
    return flag, "Hypothèse : fermeture d'hiver usuelle du bâtiment du 22.12 au 6.1 (à confirmer par entreprise)"
