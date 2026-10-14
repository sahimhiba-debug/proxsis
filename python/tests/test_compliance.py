"""Job-reporting obligation 2026 (art. 21a LEI, art. 53a-53f OSE, DEFR ordinance RS 823.111.3)."""

from datetime import date

import pytest

from proxsis.compliance import (
    TRADE_CH_ISCO,
    announcement_text,
    check,
    free_publication_date,
    is_subject_2026,
    valais_holidays,
)


def test_subject_codes_follow_the_ordinance_prefixes_and_exclusion():
    assert is_subject_2026("71140") and is_subject_2026("71310") and is_subject_2026("72120")
    assert is_subject_2026("93131") and is_subject_2026("93100")  # « 93 sans 93120 »: prefix, not the XLSX rows
    assert not is_subject_2026("93120")  # civil-engineering labourers are excluded
    assert is_subject_2026("42260") and is_subject_2026("94110") and is_subject_2026("12212")
    assert not is_subject_2026("71121") and not is_subject_2026("74110")


def test_every_trade_has_a_genre_and_labourer_depends_on_the_site():
    for trade, m in TRADE_CH_ISCO.items():
        assert len(m["genre"]) == 5 and m["fr"] and m["de"], trade
    assert check("manoeuvre_construction", site="batiment")["soumis"] is True
    assert check("manoeuvre_construction", site="genie_civil")["soumis"] is False
    assert check("macon")["soumis"] is False
    assert check("platrier")["soumis"] is True


def test_exceptions_short_missions_and_orp_registered_and_no_splitting_advice():
    c = check("peintre", duration_days=10)
    assert c["soumis"] is True and c["annonce_requise"] is False and "14 jours" in c["exception"]
    c = check("peintre", duration_days=30, orp_registered=True)
    assert c["annonce_requise"] is False and "ORP" in c["exception"]
    c = check("peintre", duration_days=30)
    assert c["annonce_requise"] is True and c["exception"] is None
    assert "découper" in c["avertissement"]


def test_five_working_days_official_example_of_the_seco_directive():
    # online Monday 5.7.2021 → restriction 6-12.7 → free publication from Tuesday 13.7 (directive B16-B17)
    assert free_publication_date(date(2021, 7, 5), holidays=set()) == date(2021, 7, 13)


def test_valais_holidays_are_skipped():
    h = valais_holidays(2026)
    assert date(2026, 11, 1) in h and date(2026, 12, 8) in h and date(2026, 5, 14) in h  # Ascension 2026
    # online Friday 30.10.2026: restriction Mon 2.11 to Fri 6.11 → free from the next day, Saturday 7.11
    assert free_publication_date(date(2026, 10, 30), holidays=h) == date(2026, 11, 7)
    # online Monday 7.12.2026: 8.12 holiday → 9,10,11,14,15 → free from 16.12
    assert free_publication_date(date(2026, 12, 7), holidays=h) == date(2026, 12, 16)


def test_announcement_text_has_the_mandatory_content_of_art_53b_and_both_languages():
    fr = announcement_text("platrier", client="Exemple SA", place="Sion", start=date(2026, 10, 19),
                           duration="durée déterminée (8 semaines)", rate=100, agency="Flexsis Martigny", lang="fr",
                           address="Avenue de la Gare 38, 1920 Martigny")
    for word in ("Plâtrier", "Sion", "100 %", "19.10.2026", "Exemple SA", "Flexsis Martigny", "durée",
                 "Avenue de la Gare 38"):
        assert word in fr
    de = announcement_text("platrier", client="Exemple SA", place="Sion", start=date(2026, 10, 19),
                           duration="befristet (8 Wochen)", rate=100, agency="Flexsis Martigny", lang="de",
                           address="Avenue de la Gare 38, 1920 Martigny")
    assert "Gipser" in de and "Exemple SA" in de and "Adresse" in de


def test_an_estimated_need_gives_a_draft_whose_date_and_rate_are_left_to_the_company():
    for lang, draft, slot in (("fr", "Brouillon : besoin estimé", "[à confirmer avec l'entreprise]"),
                              ("de", "Entwurf: geschätzter Bedarf", "[mit dem Unternehmen zu bestätigen]")):
        text = announcement_text("platrier", client="Exemple SA", place="Sion", start=None, duration="—", rate=None,
                                 agency="Flexsis Martigny", lang=lang, draft=True)
        assert text.startswith(draft) and text.count(slot) == 2
        assert "100 %" not in text and "2026" not in text


def test_the_2026_list_is_refused_outside_2026():
    # review 1 (I9): the list of the ordinance is valid from 1.1 to 31.12.2026 only; after that the engine must stop
    # and ask for the new list instead of answering with the old one
    from proxsis.compliance import ListOutOfDate

    assert check("macon", on=date(2026, 10, 5))["soumis"] is False
    assert check("macon", on=date(2026, 12, 31))["soumis"] is False
    for day in (date(2027, 1, 4), date(2025, 12, 31)):
        with pytest.raises(ListOutOfDate, match="2026"):
            check("macon", on=day)


def test_the_shared_cases_hold_for_the_python_calculation():
    # the same file is checked by the TypeScript calculation (apps/web/src/lib/compliance.test.ts): the two agree
    import json
    from pathlib import Path

    shared = Path(__file__).resolve().parents[2] / "apps/web/src/lib/compliance-cases.json"
    cases = json.loads(shared.read_text("utf-8"))
    hol = {date.fromisoformat(d) for d in cases["jours_feries"]}
    assert len(cases["cas"]) == 365
    for c in cases["cas"]:
        assert free_publication_date(date.fromisoformat(c["en_ligne"]), hol).isoformat() == c["publication_libre"], c
