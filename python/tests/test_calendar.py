from datetime import date

from proxsis.calendar import easter_sunday, holidays, is_construction_break, monday_of, weeks_between


def test_easter_known_dates():
    assert easter_sunday(2024) == date(2024, 3, 31)
    assert easter_sunday(2025) == date(2025, 4, 20)
    assert easter_sunday(2026) == date(2026, 4, 5)


def test_national_day_everywhere():
    for canton in ("VS", "ZH", "GE"):
        assert date(2026, 8, 1) in holidays(2026, canton)


def test_cantonal_specifics():
    vs = holidays(2026, "VS")
    ge = holidays(2026, "GE")
    zh = holidays(2026, "ZH")
    # Saint-Joseph (19 mars) en Valais
    assert date(2026, 3, 19) in vs
    # Restauration de la République (31 décembre) à Genève
    assert date(2026, 12, 31) in ge
    # Lundi de Pâques et Ascension à Zurich
    assert date(2026, 4, 6) in zh
    assert date(2026, 5, 14) in zh


def test_monday_of_and_weeks():
    assert monday_of(date(2026, 10, 4)) == date(2026, 9, 28)
    assert monday_of(date(2026, 10, 5)) == date(2026, 10, 5)
    w = weeks_between(date(2026, 1, 1), date(2026, 1, 31))
    assert w[0] == date(2025, 12, 29) and all(d.weekday() == 0 for d in w)


def test_construction_break_is_flagged_as_assumption():
    flag, note = is_construction_break(date(2026, 12, 28))
    assert flag is True
    assert "hypothèse" in note.lower()
    flag2, _ = is_construction_break(date(2026, 6, 15))
    assert flag2 is False
