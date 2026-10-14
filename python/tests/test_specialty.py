"""Lot → phase → Flexsis agency specialty (tests on SYNTHETIC records)."""

from proxsis.specialty import SPECIALTIES, lot_phase, lot_specialty, specialty_trades


def _r(bkp=(), npk=(), cpv="45000000"):
    return {"bkp_codes": list(bkp), "npk_codes": list(npk), "cpv_code": cpv}


def test_cfc_code_wins_over_cpv():
    assert lot_phase(_r(bkp=("230",), cpv="45210000")) == ("electricite", "cfc")
    assert lot_specialty(_r(bkp=("230",))) == "electricite"
    assert lot_specialty(_r(bkp=("211",))) == "batiment"
    assert lot_specialty(_r(bkp=("244",))) == "technique"


def test_npk_chapters_map_to_civil_or_structural_work():
    assert lot_phase(_r(npk=("111", "211", "237"), cpv="45000000")) == ("genie_civil", "npk")
    assert lot_phase(_r(npk=("113", "314"), cpv="45000000")) == ("gros_oeuvre", "npk")


def test_specific_cpv_is_used_when_no_code():
    assert lot_phase(_r(cpv="45310000")) == ("electricite", "cpv")
    assert lot_phase(_r(cpv="45442100")) == ("finitions", "cpv")
    assert lot_phase(_r(cpv="45330000")) == ("sanitaire", "cpv")
    assert lot_specialty(_r(cpv="45233120")) == "batiment"


def test_generic_cpv_is_flagged_and_services_are_not_labour():
    assert lot_phase(_r(cpv="45000000")) == ("gros_oeuvre", "cpv_generique")
    assert lot_phase(_r(cpv="71500000")) == (None, None)  # architecture / engineering services
    assert lot_specialty(_r(cpv="71500000")) is None


def test_supply_of_industrial_goods_is_industry():
    assert lot_specialty(_r(cpv="42900000")) == "industrie"
    assert lot_specialty(_r(cpv="44210000")) == "industrie"


def test_every_specialty_has_bilingual_label_and_trades():
    for s, spec in SPECIALTIES.items():
        assert spec.label_fr and spec.label_de
        assert specialty_trades(s), s


def test_cpv_refinements_from_the_week1_audit():
    assert lot_phase(_r(cpv="45421000")) == ("menuiserie", "cpv")  # joinery / locksmith: no plasterer need
    assert specialty_trades("batiment") and "charpentier" in specialty_trades("batiment")
    assert lot_phase(_r(cpv="45261000"))[0] == "enveloppe"  # roofing is not structural work
    assert lot_phase(_r(cpv="45300000")) == ("equipement", "cpv_generique")
    assert lot_specialty(_r(cpv="45300000")) == "technique"
    assert lot_phase(_r(cpv="45400000")) == ("finitions", "cpv_generique")


def test_cfc_27_is_split_into_plastering_metalwork_and_joinery():
    assert lot_phase(_r(bkp=("271",))) == ("amenagement_int", "cfc")
    assert lot_phase(_r(bkp=("272",))) == ("metallerie", "cfc")
    assert lot_phase(_r(bkp=("273.0",))) == ("menuiserie", "cfc")
    assert lot_specialty(_r(bkp=("272",))) == "batiment"
