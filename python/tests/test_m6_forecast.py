import numpy as np

from proxsis.models.m6_forecast import evaluate, weekly_series
from proxsis.synth.world import WorldConfig, generate_world


def test_series_complete_grid_and_counts():
    w = generate_world(WorldConfig(seed=3, n_companies=300, n_candidates=5))
    s = weekly_series(w.postings, w.companies, w.weeks)
    assert s["y"].sum() == len(
        w.postings[w.postings["available_at"] < w.weeks[-1] + __import__("datetime").timedelta(days=7)]
    )
    assert s.groupby(["family", "language"]).size().nunique() == 1


def test_evaluation_runs_and_reports_all_methods():
    w = generate_world(WorldConfig(seed=3, n_companies=400, n_candidates=5))
    s = weekly_series(w.postings, w.companies, w.weeks)
    ev = evaluate(s, w.weeks, first_origin=150, step=8)
    assert set(ev.wape) == {"saisonnier_naif", "moyenne_4s", "lightgbm_global"}
    assert all(np.isfinite(v) for v in ev.wape.values())
