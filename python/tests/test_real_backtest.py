"""Real backtest on public data (target T0: a new public award within 8 weeks)."""

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from proxsis.real_backtest import evaluate_t0, events_from_records, snapshot


def _rec(pid, day, vendor, canton="VS", price=None):
    return {"publication_id": pid, "publication_date": day, "pub_type": "award", "order_canton": canton,
            "vendors": [{"name": vendor, "price_chf": price}], "provenance": {"url": f"u/{pid}"}}


def test_events_use_normalised_names_and_skip_private_persons():
    ev = events_from_records([_rec("a", "2025-01-06", "Exemple Bau AG"), _rec("b", "2025-01-07", "EXEMPLE BAU A.G."),
                              _rec("c", "2025-01-08", "[particulier]")])
    assert ev["company"].nunique() == 1 and len(ev) == 2


def test_snapshot_uses_only_past_information():
    ev = events_from_records([_rec("a", "2025-01-06", "A SA"), _rec("b", "2025-03-03", "A SA"),
                              _rec("c", "2025-02-03", "B SA")])
    T = date(2025, 2, 3)
    s = snapshot(ev, T, horizon_days=56)
    assert set(s.index) == {"a"}  # B SA is first seen ON T: unknown before T (legal form dropped)
    assert s.loc["a", "n_52s"] == 1 and s.loc["a", "target"]  # award on 2025-03-03 within 8 weeks


def test_a_missing_adjudicator_is_not_counted_whatever_the_pandas_version():
    # pandas 2 made "None" / "nan" texts of missing adjudicators with astype(str) and counted them; pandas 3 did not.
    # The published measures (REEL-SPEC-*) are those of pandas 3: missing adjudicators are not counted.
    recs = [_rec("a", "2025-01-06", "A SA") | {"contracting_authority": "Commune de Sion"},
            _rec("b", "2025-01-13", "A SA") | {"contracting_authority": None},
            _rec("c", "2025-01-20", "A SA") | {"contracting_authority": float("nan")},
            _rec("d", "2025-01-27", "A SA") | {"contracting_authority": "Commune de Sion"},
            _rec("e", "2023-01-02", "A SA") | {"contracting_authority": "Canton du Valais"}]  # older than 52 weeks
    s = snapshot(events_from_records(recs), date(2025, 2, 3), horizon_days=56)
    assert s.loc["a", "n_auth_52s"] == 1 and s.loc["a", "n_52s"] == 4


def test_evaluation_reports_rankers_base_rate_and_ci():
    rng = np.random.default_rng(0)
    recs, k = [], 0
    start = date(2024, 7, 1)
    for c in range(60):
        rate = 0.02 + 0.2 * (c < 10)  # 10 frequent winners
        for w in range(110):
            if rng.random() < rate:
                recs.append(_rec(f"p{k}", (start + timedelta(weeks=w)).isoformat(), f"Firma {c} AG"))
                k += 1
    ev = events_from_records(recs)
    rep = evaluate_t0(ev, first_week=date(2025, 7, 7), last_week=date(2026, 6, 1), k=10, n_boot=200, seed=1)
    assert set(rep["p_at_k"]) == {"hasard", "recence", "frequence_52s", "m0_marches"}
    assert rep["p_at_k"]["frequence_52s"]["moyenne"] > rep["taux_de_base"]
    lo, hi = rep["p_at_k"]["frequence_52s"]["ic95"]
    assert lo <= rep["p_at_k"]["frequence_52s"]["moyenne"] <= hi
    assert rep["n_semaines"] > 40


def test_evaluation_refuses_a_horizon_past_the_data():
    ev = events_from_records([_rec("a", "2025-01-06", "A SA")])
    with pytest.raises(ValueError):
        evaluate_t0(ev, first_week=date(2025, 1, 6), last_week=date(2025, 1, 6), k=5)


def test_events_frame_columns():
    ev = events_from_records([_rec("a", "2025-01-06", "A SA", price=1000.0)])
    assert isinstance(ev, pd.DataFrame)
    assert {"company", "available_at", "canton", "value_chf", "url"} <= set(ev.columns)


def test_block_length_is_at_least_the_horizon_and_sensitivity_is_reported():
    rng = np.random.default_rng(0)
    recs, k = [], 0
    start = date(2024, 7, 1)
    for c in range(40):
        for w in range(110):
            if rng.random() < (0.25 if c < 8 else 0.03):
                recs.append(_rec(f"p{k}", (start + timedelta(weeks=w)).isoformat(), f"Firma {c} AG"))
                k += 1
    rep = evaluate_t0(events_from_records(recs), first_week=date(2025, 7, 7), last_week=date(2026, 6, 1), k=10,
                      n_boot=100, seed=1)
    assert rep["bloc_semaines"] >= 8
    assert set(rep["sensibilite_bloc_12"]) >= {"frequence_52s"}


def test_data_end_beyond_the_collected_data_is_refused():
    ev = events_from_records([_rec("a", "2025-01-06", "A SA"), _rec("b", "2025-06-02", "B SA")])
    with pytest.raises(ValueError, match="fin des données"):
        evaluate_t0(ev, first_week=date(2025, 1, 6), last_week=date(2025, 3, 3), k=1, data_end=date(2025, 12, 31))


# --- Cible « surprise » et modèle combiné (demande de Hiba, 2026-10-05)
def _world(seed=0, n=60, weeks=120):
    rng = np.random.default_rng(seed)
    recs, k = [], 0
    start = date(2024, 9, 2)
    for c in range(n):
        base = 0.2 if c < 10 else 0.03
        for w in range(weeks):
            rate = base * (4 if (c % 7 == 0 and 70 <= w < 80) else 1)  # some companies surge
            if rng.random() < rate:
                day = (start + timedelta(weeks=w)).isoformat()
                recs.append(_rec(f"p{k}", day, f"Firma {c} AG", price=1e5 * (1 + c % 5)))
                k += 1
    return events_from_records(recs)


def test_surge_target_definition():
    from proxsis.real_backtest import snapshot

    ev = events_from_records([_rec("a", "2025-01-06", "A SA"), _rec("b", "2025-03-03", "A SA"),
                              _rec("c", "2025-03-10", "A SA"), _rec("d", "2025-03-17", "B SA"),
                              _rec("e", "2024-06-03", "B SA")] + [_rec(f"x{i}", f"2024-{m:02d}-02", "B SA") for i, m in
                                                                 enumerate(range(7, 13))])
    s = snapshot(ev, date(2025, 2, 24), horizon_days=56)
    assert bool(s.loc["a", "surge"])  # 1 win in the past year, 2 in the next 8 weeks
    assert not bool(s.loc["b", "surge"])  # 7 wins in the past year (≈1 per 8 weeks): 1 more is not a surge


def test_extended_evaluation_reports_surprise_and_combined_model_without_leakage():
    from proxsis.real_backtest import evaluate_extended

    ev = _world()
    rep = evaluate_extended(ev, first_week=date(2025, 9, 1), last_week=date(2026, 9, 7), k=10, n_boot=100, seed=1,
                            train_from=date(2025, 3, 3))
    assert {"t0", "pic"} <= set(rep["cibles"])
    assert {"frequence_52s", "combine"} <= set(rep["cibles"]["t0"]["p_at_k"])
    assert 0 <= rep["part_premiers_gagnants"] <= 1
    assert rep["entrainement"]["dernier_label_avant_T_jours"] >= 56  # labels fully known at T
    d = rep["cibles"]["t0"]["combine_moins_frequence"]
    assert d["ic95"][0] <= d["moyenne"] <= d["ic95"][1]


def test_extended_evaluation_ranks_a_region_only_and_scores_the_surprise_flags():
    from proxsis.real_backtest import evaluate_extended

    ev = _world()
    region = set(sorted(ev["company"].unique())[::2])
    rep = evaluate_extended(ev, first_week=date(2025, 9, 1), last_week=date(2026, 9, 7), k=5, n_boot=50, seed=1,
                            train_from=date(2025, 3, 3), eval_companies=region)
    assert rep["region"]["entreprises"] == len(region)
    flags = rep["drapeaux_surprise"]
    assert set(flags) == {"rythme_double", "nouveau_venu"}
    for v in flags.values():
        assert {"signalements", "taux_t0", "taux_pic", "taux_de_base_t0"} <= set(v)
        assert {"signalements", "taux_t0", "taux_de_base_t0"} <= set(v["hors_top_k"])
    assert {"signalements", "taux_t0", "taux_pic"} <= set(rep["surprises_retenues"])


def test_region_can_be_defined_at_each_date():
    from proxsis.real_backtest import evaluate_extended

    ev = _world()
    seen = []

    def region_at(T, past):
        seen.append(past["available_at"].max() < T)
        return set(past["company"].unique()[::2])

    evaluate_extended(ev, first_week=date(2025, 9, 1), last_week=date(2026, 9, 7), k=5, n_boot=20, seed=1,
                      train_from=date(2025, 3, 3), eval_companies=region_at)
    assert seen and all(seen)


def test_surprise_flags_definition():
    import pandas as pd

    from proxsis.real_backtest import surprise_flags

    snap = pd.DataFrame({"n_52s": [3, 10, 1], "n_8s": [3, 2, 1], "first_days": [300.0, 400.0, 20.0]},
                        index=["bond", "regulier", "nouveau"])
    f = surprise_flags(snap, horizon_days=56)
    assert f.loc["bond", "rythme_double"] and not f.loc["regulier", "rythme_double"]
    assert f.loc["nouveau", "nouveau_venu"] and not f.loc["bond", "nouveau_venu"]
