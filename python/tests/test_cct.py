"""CCT Location de services 2026: wage category of a worker (art. 20 al. 4 and 5) and minimum wages."""

import pytest

from proxsis.cct import CATEGORIES, MIN_WAGE_2026, cct_category


def test_cfc_of_the_branch_is_qualified():
    c = cct_category(training="cfc", practice_years=0, hours_by_year=[], training_exists=True)
    assert c.code == "qualifie" and "al. 4" in c.rule


def test_afp_needs_three_years_of_practice_to_be_qualified():
    assert cct_category("afp", 3, [1500, 1500, 1500], True).code == "qualifie"
    assert cct_category("afp", 2, [1500, 1500], True).code == "non_qualifie"


def test_four_years_and_1000_hours_each_year_make_a_specialised_worker_not_a_qualified_one():
    c = cct_category("aucune", 4, [1200, 1100, 1000, 1500], True)
    assert c.code == "specialise" and "al. 5" in c.rule
    # one calendar year under 1 000 hours: prudent reading (each year) → not specialised, flagged as open point
    c2 = cct_category("aucune", 4, [1200, 900, 1100, 1500], True)
    assert c2.code == "non_qualifie" and c2.open_point
    # no vocational training exists for the activity → al. 5 does not apply
    assert cct_category("aucune", 6, [2000] * 6, False).code == "non_qualifie"


def test_minimum_wages_2026_standard_region_and_ratio():
    assert MIN_WAGE_2026["non_qualifie"]["heure"] == 21.22
    assert MIN_WAGE_2026["specialise"]["heure"] == 22.76
    assert MIN_WAGE_2026["qualifie"]["heure"] == 25.86
    assert MIN_WAGE_2026["specialise"]["annee"] == pytest.approx(0.88 * MIN_WAGE_2026["qualifie"]["annee"], rel=1e-3)
    for code in CATEGORIES:
        assert CATEGORIES[code]["fr"] and CATEGORIES[code]["de"]


def test_missing_hours_are_said_to_be_missing():
    c = cct_category("aucune", 5, [], True)
    assert c.code == "non_qualifie" and "heures non renseignées" in c.rule


def test_applicable_cct_depends_on_the_trade():
    from proxsis.cct import applicable_cct

    assert applicable_cct("macon")["cct"].startswith("CN") and applicable_cct("macon")["minimum_cct_ls"] is False
    assert "électricité" in applicable_cct("electricien")["cct"]
    assert applicable_cct("polymecanicien")["minimum_cct_ls"] is True
