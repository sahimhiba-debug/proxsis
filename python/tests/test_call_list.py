"""Weekly call list per agency specialty (tests on SYNTHETIC simap-like records)."""

from datetime import date, timedelta

import numpy as np
import pytest

from proxsis.call_list import CallListConfig, build_call_list, lot_table, own_lot_needs, reason_text

MENTION = "Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi."


def _rec(i, day, vendor, canton="VS", city="Sion", bkp=("211",), cpv="45000000", price=500_000.0, auth="Commune A"):
    return {"publication_id": f"pub{i}", "project_id": f"proj{i}", "pub_type": "award", "publication_date": str(day),
            "decision_date": str(day - timedelta(days=10)), "title": {"fr": f"Ecole {i} - CFC 211"},
            "bkp_codes": list(bkp), "npk_codes": [], "cpv_code": cpv, "order_canton": canton, "order_city": city,
            "contracting_authority": auth,
            "vendors": [{"name": vendor, "canton": canton, "city": city, "price_chf": price}],
            "provenance": {"source": "simap.ch", "url": f"https://www.simap.ch/api/x/{i}"},
            "mention_obligatoire": MENTION}


def _world(seed=0, n_weeks=120, end=date(2026, 9, 28)):
    """Regular firms win steadily; « Bondit SA » doubles its pace in the last weeks; « Nouvelle Sàrl » appears."""
    rng = np.random.default_rng(seed)
    start = end - timedelta(weeks=n_weeks)
    recs, i = [], 0
    firms = [(f"Entreprise {c} SA", "VS" if k % 2 == 0 else "VD", 0.05 + 0.04 * (k % 5))
             for k, c in enumerate("ABCDEFGHIJKLMNOPQRST")]
    for w in range(n_weeks):
        day = start + timedelta(weeks=w, days=2)
        for name, canton, rate in firms:
            if rng.random() < rate:
                recs.append(_rec(i, day, name, canton=canton, city="Sion" if canton == "VS" else "Lausanne"))
                i += 1
        if w >= n_weeks - 6 and w % 2 == 0:
            recs.append(_rec(i, day, "Bondit SA", price=900_000.0))
            i += 1
        if w in (5, 60):
            recs.append(_rec(i, day, "Bondit SA"))
            i += 1
    recs.append(_rec(i, end - timedelta(days=5), "Nouvelle Sàrl", city="Martigny", price=None))
    recs.append(_rec(i + 1, end - timedelta(days=4), "Etude Archi SA", cpv="71200000", bkp=()))
    return recs


AS_OF = date(2026, 9, 28)


def test_lot_table_keeps_legal_entities_with_phase_specialty_and_links():
    lots = lot_table([_rec(1, AS_OF, "Maçonnerie Exemple SA"), _rec(2, AS_OF, "[particulier]"),
                      _rec(3, AS_OF, "Elec SA", bkp=("232",))])
    assert set(lots["name"]) == {"Maçonnerie Exemple SA", "Elec SA"}
    row = lots.set_index("name").loc["Elec SA"]
    assert row["phase"] == "electricite" and row["specialty"] == "electricite" and row["phase_source"] == "cfc"
    assert row["url_simap"] == "https://www.simap.ch/fr/project-detail/proj3"


def test_call_list_is_point_in_time_regional_and_explained():
    recs = _world()
    out = build_call_list(recs, CallListConfig(as_of=AS_OF, specialty="batiment", region_cantons=("VS",), k=5))
    ents = out["entreprises"]
    assert len(ents) == 5
    assert all(e["canton"] == "VS" for e in ents)
    for e in ents:
        assert e["raisons"] and e["sources"] and e["confiance"] in {"elevee", "moyenne", "faible"}
        assert all(s["date"] < str(AS_OF) for s in e["sources"])  # nothing published after the week's Monday
        assert e["sources"][0]["url_simap"].startswith("https://www.simap.ch/")
        assert 0.0 <= e["score"] <= 1.0
    assert out["mention_obligatoire"] == MENTION
    assert out["modele"]["semaines_apprentissage"] > 10
    assert out["modele"]["dernier_label_avant_as_of_jours"] >= 56  # labels fully observed before the list date
    # a future award must not change today's list
    later = [*recs, _rec(99999, AS_OF + timedelta(days=3), "Entreprise A SA")]
    out2 = build_call_list(later, CallListConfig(as_of=AS_OF, specialty="batiment", region_cantons=("VS",), k=5))
    assert [e["id"] for e in out2["entreprises"]] == [e["id"] for e in ents]


def test_surprises_detect_a_jump_and_a_newcomer():
    out = build_call_list(_world(), CallListConfig(as_of=AS_OF, specialty="batiment", region_cantons=("VS",), k=3))
    flagged = {e["nom"]: e["surprise"] for e in out["entreprises"] + out["surprises"] if e["surprise"]}
    assert "nouveau_venu" in flagged.get("Nouvelle Sàrl", [])
    assert "rythme_double" in flagged.get("Bondit SA", [])
    assert all(e["nom"] != "Etude Archi SA" for e in out["entreprises"] + out["surprises"])  # services: no labour


def test_needs_per_trade_and_week_with_ranges_and_declared_assumptions():
    out = build_call_list(_world(), CallListConfig(as_of=AS_OF, specialty="batiment", region_cantons=("VS",), k=5))
    e = next(x for x in out["entreprises"] + out["surprises"] if x["nom"] == "Bondit SA")
    assert e["besoin"], "a recent structural-work lot must produce a weekly need"
    for row in e["besoin"]:
        assert row["metier"] in {"macon", "manoeuvre_construction", "coffreur", "grutier"}
        assert row["personnes_bas"] <= row["personnes_milieu"] <= row["personnes_haut"]
        assert AS_OF <= date.fromisoformat(row["semaine"]) < AS_OF + timedelta(weeks=8)
    assert any("hypothèse" in h for h in out["hypotheses"])


def test_missing_amount_lowers_confidence():
    out = build_call_list(_world(), CallListConfig(as_of=AS_OF, specialty="batiment", region_cantons=("VS",), k=3))
    e = next(x for x in out["entreprises"] + out["surprises"] if x["nom"] == "Nouvelle Sàrl")
    assert e["confiance"] != "elevee"
    assert any(r["code"] in {"montant_estime", "montant_non_publie"} for r in e["raisons"])
    assert not e["besoin"], "no published amount and no structural-work lot to scale from: no number is shown"


def test_own_lot_needs_starts_after_award_and_spreads_over_phase_duration():
    df = own_lot_needs("gros_oeuvre", AS_OF, 1_000_000.0)
    assert df["semaine"].min() >= AS_OF + timedelta(weeks=4)
    assert set(df["metier"]) == {"macon", "manoeuvre_construction", "coffreur", "grutier"}
    total_mid = df["personnes_milieu"].sum()
    assert total_mid == pytest.approx(1_000_000 * 0.35 / 2300, rel=1e-6)  # person-weeks = labour / weekly cost


def test_reasons_render_in_french_and_german():
    r = {"code": "marches_52s", "n": 4}
    assert "4" in reason_text(r, "fr") and "4" in reason_text(r, "de")
    assert reason_text(r, "fr") != reason_text(r, "de")


def test_default_order_is_frequency_then_recency_and_combined_is_an_option():
    recs = _world()
    out = build_call_list(recs, CallListConfig(as_of=AS_OF, specialty="batiment", region_cantons=("VS",), k=8))
    n = [e["n_52s"] for e in out["entreprises"]]
    assert n == sorted(n, reverse=True)
    comb = build_call_list(recs, CallListConfig(as_of=AS_OF, region_cantons=("VS",), k=8, ranker="combine"))
    s = [e["score"] for e in comb["entreprises"]]
    assert s == sorted(s, reverse=True)
    with pytest.raises(ValueError):
        build_call_list(recs, CallListConfig(as_of=AS_OF, ranker="magie"))


def test_reasons_use_proper_plural_and_french_decimal_comma():
    one = reason_text({"code": "marches_52s", "n": 1}, "fr")
    assert one == "1 marché public gagné dans la spécialité en 52 semaines"
    assert reason_text({"code": "marches_52s", "n": 3}, "fr").startswith("3 marchés publics gagnés")
    assert reason_text({"code": "marches_52s", "n": 1}, "de").startswith("1 öffentlicher Auftrag")
    t = reason_text({"code": "rythme_double", "n8": 2, "habituel": 0.7}, "fr")
    assert "0,7" in t and "0.7" not in t
    assert "0.7" in reason_text({"code": "rythme_double", "n8": 2, "habituel": 0.7}, "de")


def test_missing_authority_gives_no_nan_in_reasons():
    t = reason_text({"code": "dernier_marche", "jours": 3, "titre": "Ecole", "adjudicateur": None}, "fr")
    assert "nan" not in t.lower() and "None" not in t and "()" not in t


def test_imported_permits_add_context_reasons_without_changing_the_order():
    recs = _world()
    base = build_call_list(recs, CallListConfig(as_of=AS_OF, k=5))
    permits = [{"date_publication": "2026-09-10", "commune": "Sion", "entreprises_citees": ["Entreprise A SA"],
                "url": "https://bulletin-officiel.vs.ch/api/v1/publications/x/pdf", "statut": "acceptée"},
               {"date_publication": "2026-05-01", "commune": "Sion", "entreprises_citees": [], "url": "u",
                "statut": "acceptée"}]
    out = build_call_list(recs, CallListConfig(as_of=AS_OF, k=5), permits=permits)
    assert [e["id"] for e in out["entreprises"]] == [e["id"] for e in base["entreprises"]]
    sion = [e for e in out["entreprises"] if e["ville"] == "Sion"]
    assert sion and all(any(r["code"] == "permis_commune" and r["n"] == 1 for r in e["raisons"]) for e in sion)


def test_a_large_lot_lasts_longer_instead_of_inflating_the_weekly_team():
    df = own_lot_needs("genie_civil", AS_OF, 4_000_000.0)
    weekly_mid = df.groupby("semaine")["personnes_milieu"].sum()
    assert weekly_mid.max() <= 10.0 + 1e-9  # declared team cap for civil works
    assert df["personnes_milieu"].sum() == pytest.approx(4_000_000 * 0.35 / 2300, rel=1e-6)  # person-weeks kept


def test_need_rows_keep_their_source_phases():
    out = build_call_list(_world(), CallListConfig(as_of=AS_OF, k=5))
    rows = [r for e in out["entreprises"] + out["surprises"] for r in e["besoin"]]
    assert rows and all(r["phases"] for r in rows)


def test_expected_lots_are_listed_once_per_phase():
    out = build_call_list(_world(), CallListConfig(as_of=AS_OF, k=5))
    for e in out["entreprises"] + out["surprises"]:
        phases = [x["phase"] for x in e["lots_attendus"]]
        assert len(phases) == len(set(phases))


def test_reason_rendering_singular_day_and_newcomer_caveat():
    assert "1 jour :" in reason_text({"code": "dernier_marche", "jours": 1, "titre": "X", "adjudicateur": "C"}, "fr")
    assert "ne prédit pas" in reason_text({"code": "nouveau_venu"}, "fr")
    assert "keinen neuen Zuschlag" in reason_text({"code": "nouveau_venu"}, "de")


def test_a_lot_already_running_is_said_to_be_in_progress():
    t = reason_text({"code": "besoin", "bas": "2", "haut": "5", "debut": "2026-09-28", "metiers": ["macon"],
                     "en_cours": True}, "fr")
    assert "en cours" in t and "dès le" not in t


def test_audit_m3_reasons_never_show_a_headcount_and_no_internal_word():
    for en_cours in (False, True):
        r = {"code": "besoin", "bas": "14", "haut": "34", "debut": "2026-09-28", "metiers": ["macon"],
             "en_cours": en_cours}
        fr, de = reason_text(r, "fr"), reason_text(r, "de")
        assert "14" not in fr and "34" not in fr and "14" not in de and "34" not in de
        assert "à confirmer" in fr and "zu bestätigen" in de and "nombre de personnes non estimé" in fr
    assert "indice" not in reason_text({"code": "nouveau_venu"}, "fr")


def test_the_last_contract_reason_has_a_short_form_for_cards():
    # exported as such so that no screen cuts the sentence (review 1, I8)
    from proxsis.call_list import reason_short, reason_text

    r = {"code": "dernier_marche", "jours": 13, "titre": "Route", "adjudicateur": "Commune de Sion"}
    assert reason_short(r, "fr") == "Dernier marché il y a 13 jours"
    assert reason_text(r, "fr").startswith("Dernier marché il y a 13 jours : ")
    assert reason_short(r | {"jours": 1}, "de") == "Letzter Zuschlag vor 1 Tag"
    assert reason_short({"code": "marches_52s", "n": 3}) is None
