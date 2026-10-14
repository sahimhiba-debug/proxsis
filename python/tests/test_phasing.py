"""Phasing learnt from real simap lots (tests on SYNTHETIC chantiers)."""

from datetime import date, timedelta

import numpy as np
import pytest

from proxsis import phasing as ph


def _lot(pid, auth, city, title, code, day, price=None):
    return {"project_id": pid, "publication_id": pid + "-p", "contracting_authority": auth, "order_city": city,
            "title": {"fr": title}, "bkp_codes": [code] if code else [], "decision_date": day, "publication_date": day,
            "vendors": [{"name": "Exemple SA", "price_chf": price}], "pub_type": "award", "cpv_code": "45214200"}


def test_phase_of_codes():
    assert ph.phase_of(["211.0"]) == "gros_oeuvre"
    assert ph.phase_of(["23"]) == "electricite"
    assert ph.phase_of(["285"]) == "finitions"
    assert ph.phase_of(["112", "211"]) == "preparatoire"  # earliest phase wins
    assert ph.phase_of([]) is None and ph.phase_of(["291"]) is None  # fees are not work
    assert "macon" in ph.PHASE_TRADES["gros_oeuvre"] and "electricien" in ph.PHASE_TRADES["electricite"]


def test_lots_of_the_same_building_are_grouped():
    lots = [_lot("a", "Ville X", "Sion", "CFC 211 Maçonnerie - Ecole du Lac", "211", "2025-01-10"),
            _lot("b", "Ville X", "Sion", "CFC 23 Electricité - Ecole du Lac", "23", "2025-04-10"),
            _lot("c", "Ville X", "Sion", "CFC 211 Maçonnerie - Piscine des Iles", "211", "2025-02-01"),
            _lot("d", "Ville Y", "Sion", "CFC 23 Electricité - Ecole du Lac", "23", "2025-04-10")]
    groups = ph.group_chantiers(lots)
    sizes = sorted(len(g["lots"]) for g in groups)
    assert sizes == [1, 1, 2]
    lac = next(g for g in groups if len(g["lots"]) == 2)
    assert {lot["phase"] for lot in lac["lots"]} == {"gros_oeuvre", "electricite"}


def _synthetic(n=80, seed=0):
    rng = np.random.default_rng(seed)
    lots, start = [], date(2024, 10, 1)
    for i in range(n):
        d0 = start + timedelta(days=int(rng.integers(0, 600)))
        word = "".join(chr(97 + (i * 7 + j * 3 + j * j) % 26) for j in range(6))
        name = f"Bâtiment {word.capitalize()} {chr(97 + i % 26)}{chr(97 + (i // 26) % 26)}ville"
        lots.append(_lot(f"g{i}", f"Commune {i % 9}", f"Ville{i % 9}", f"CFC 211 Maçonnerie - {name}", "211",
                         d0.isoformat(), 1e6))
        for code, mu in (("23", 90), ("25", 100), ("285", 200)):
            if rng.random() < 0.8:
                lag = max(0, int(rng.normal(mu, 20)))
                lots.append(_lot(f"g{i}-{code}", f"Commune {i % 9}", f"Ville{i % 9}", f"CFC {code} - {name}", code,
                                 (d0 + timedelta(days=lag)).isoformat(), 2e5))
    return lots


def test_lags_are_measured_with_uncertainty():
    stats = ph.measure_lags(ph.group_chantiers(_synthetic()))
    el = stats["electricite"]
    assert el["n"] > 30 and 70 <= el["mediane_jours"] <= 110
    assert el["ic95_mediane"][0] <= el["mediane_jours"] <= el["ic95_mediane"][1]
    assert stats["finitions"]["mediane_jours"] > stats["electricite"]["mediane_jours"]


def test_model_validated_on_more_recent_chantiers():
    rep = ph.validate(ph.group_chantiers(_synthetic(n=160)), cutoff=date(2025, 10, 1))
    assert rep["n_chantiers_apprentissage"] > 0 and rep["n_chantiers_test"] > 0
    assert 0.6 <= rep["couverture_p10_p90"] <= 1.0  # 80 % intervals should cover ~80 %
    assert rep["mae_mediane_jours"] < rep["mae_reference_jours"]  # beats a single global lag


def test_needs_per_trade_and_week_from_one_award():
    model = ph.PhasingModel.fit(ph.group_chantiers(_synthetic()))
    needs = model.needs(anchor=date(2026, 3, 2), amount_chf=2e6)
    assert {"semaine", "metier", "personnes_bas", "personnes_milieu", "personnes_haut"} <= set(needs.columns)
    assert (needs["personnes_bas"] <= needs["personnes_milieu"]).all()
    assert (needs["personnes_milieu"] <= needs["personnes_haut"]).all()
    assert set(needs["metier"]) >= {"macon", "electricien"}
    assert needs["semaine"].min() >= date(2026, 3, 2)
    assert model.assumptions and all("hypothèse" in a or "mesuré" in a for a in model.assumptions)


def test_unknown_amount_gives_wider_needs_not_a_crash():
    model = ph.PhasingModel.fit(ph.group_chantiers(_synthetic()))
    needs = model.needs(anchor=date(2026, 3, 2), amount_chf=None)
    assert len(needs) > 0 and np.isfinite(needs["personnes_haut"]).all()


@pytest.mark.parametrize("title, stem", [("CFC 211 Maçonnerie - Ecole du Lac", "ecole lac"),
                                         ("BKP 281.0 Estriche - Schulhaus Dorf", "schulhaus dorf")])
def test_title_stem_removes_codes_and_trade_words(title, stem):
    assert ph.title_stem(title) == stem
