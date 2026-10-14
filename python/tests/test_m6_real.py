"""M6 on real public series — tests on SYNTHETIC series."""

from datetime import date, timedelta

import numpy as np
import pandas as pd

from proxsis.m6_real import evaluate_series, forecast_at


def _weekly(n=400, seed=0, lead=True):
    rng = np.random.default_rng(seed)
    idx = [date(2018, 1, 1) + timedelta(weeks=i) for i in range(n)]
    x = rng.normal(0, 1, n).cumsum() * 0.3
    season = 10 * np.sin(2 * np.pi * np.arange(n) / 52)
    y = 100 + season + rng.normal(0, 1, n)
    if lead:
        y[3:] += 6 * x[:-3]  # x leads y by 3 weeks
    return pd.Series(y, index=idx), pd.DataFrame({"x": x}, index=idx)


def test_no_leakage_future_values_do_not_change_a_forecast():
    y, ex = _weekly()
    o = y.index[300]
    a = forecast_at(y, ex, origin=o, horizons=range(1, 5), period=52)
    y2 = y.copy()
    y2[y2.index >= o] = np.nan
    ex2 = ex.copy()
    ex2[ex2.index >= o] = np.nan
    b = forecast_at(y2, ex2, origin=o, horizons=range(1, 5), period=52)
    for h in range(1, 5):
        assert a["boosting"][h] == b["boosting"][h]
        assert a["saisonnier_naif"][h] == b["saisonnier_naif"][h]


def test_boosting_beats_naive_when_a_real_leading_signal_exists():
    y, ex = _weekly(lead=True)
    rep = evaluate_series(y, ex, first_origin=y.index[250], step=6, horizons=range(1, 4), period=52, n_boot=200)
    assert set(rep["wape"]) >= {"saisonnier_naif", "derniere_valeur", "moyenne_4", "boosting"}
    best_naive = min(rep["wape"][m] for m in ("saisonnier_naif", "derniere_valeur", "moyenne_4"))
    assert rep["wape"]["boosting"] < best_naive
    d = rep["boosting_moins_meilleure_naive"]
    assert d["ic95"][0] <= d["moyenne"] <= d["ic95"][1]


def test_report_states_the_period_and_number_of_origins():
    y, _ = _weekly(lead=False)
    rep = evaluate_series(y, None, first_origin=y.index[300], step=8, horizons=range(1, 3), period=52, n_boot=50)
    assert rep["n_origines"] > 5 and rep["periode"][0] == str(y.index[300])


def test_missing_periods_do_not_make_the_whole_score_nan():
    y, _ = _weekly(lead=False)
    y = y.drop(y.index[[310, 311, 330]])  # gaps in the real series
    rep = evaluate_series(y, None, first_origin=y.index[280], step=8, horizons=range(1, 4), period=52, n_boot=50)
    assert all(np.isfinite(v) for v in rep["wape"].values())
