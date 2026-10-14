import numpy as np
import pandas as pd
import pytest

from proxsis.metrics import (
    block_bootstrap_ci,
    brier,
    expected_calibration_error,
    precision_at_k_by_group,
    reliability_table,
    top_k_mask,
)


def test_top_k_mask_per_group_breaks_ties_deterministically():
    df = pd.DataFrame({"g": ["a"] * 4 + ["b"] * 3, "score": [0.9, 0.1, 0.5, 0.5, 0.2, 0.8, 0.3]})
    m = top_k_mask(df, "g", "score", k=2)
    assert list(m) == [True, False, True, False, False, True, True]


def test_precision_at_k_by_group():
    df = pd.DataFrame(
        {
            "g": ["w1"] * 4 + ["w2"] * 4,
            "score": [4, 3, 2, 1, 4, 3, 2, 1],
            "y": [1, 0, 1, 0, 0, 0, 1, 1],
        }
    )
    per = precision_at_k_by_group(df, "g", "score", "y", k=2)
    assert per.loc["w1"] == pytest.approx(0.5)
    assert per.loc["w2"] == pytest.approx(0.0)


def test_brier_and_ece_perfect():
    y = np.array([0, 1, 0, 1])
    p = np.array([0.0, 1.0, 0.0, 1.0])
    assert brier(p, y) == 0.0
    assert expected_calibration_error(p, y) == 0.0


def test_ece_detects_miscalibration():
    rng = np.random.default_rng(0)
    p = rng.uniform(0, 1, 5000)
    y = (rng.uniform(0, 1, 5000) < p).astype(int)
    assert expected_calibration_error(p, y) < 0.03
    assert expected_calibration_error(np.clip(p * 0.3, 0, 1), y) > 0.15


def test_reliability_table_shape():
    p = np.linspace(0, 1, 100)
    y = (p > 0.5).astype(int)
    t = reliability_table(p, y, n_bins=10)
    assert len(t) == 10
    assert set(t.columns) >= {"bin", "mean_pred", "obs_rate", "n"}


def test_block_bootstrap_ci_contains_mean_and_is_reproducible():
    rng = np.random.default_rng(1)
    vals = pd.Series(rng.normal(0.4, 0.1, 100), index=range(100))
    lo, hi = block_bootstrap_ci(vals, n_boot=500, seed=3)
    lo2, hi2 = block_bootstrap_ci(vals, n_boot=500, seed=3)
    assert (lo, hi) == (lo2, hi2)
    assert lo < vals.mean() < hi
    assert hi - lo < 0.1
