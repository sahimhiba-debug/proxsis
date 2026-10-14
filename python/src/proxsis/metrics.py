"""Evaluation metrics: precision@k per list, recall, lead time, calibration,
and block-bootstrap confidence intervals (blocks = weeks).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def top_k_mask(df: pd.DataFrame, group_col: str, score_col: str, k: int) -> pd.Series:
    """True for the k best rows of each group. Ties broken by row order (stable)."""
    order = df.reset_index(drop=True)
    ranks = (
        order.assign(_pos=np.arange(len(order)))
        .sort_values([group_col, score_col, "_pos"], ascending=[True, False, True], kind="mergesort")
        .groupby(group_col, sort=False)
        .cumcount()
    )
    mask = pd.Series(False, index=order.index)
    mask.loc[ranks.index] = ranks.to_numpy() < k
    mask.index = df.index
    return mask


def precision_at_k_by_group(df: pd.DataFrame, group_col: str, score_col: str, y_col: str, k: int) -> pd.Series:
    m = top_k_mask(df, group_col, score_col, k)
    return df[m].groupby(group_col)[y_col].mean()


def brier(p: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((np.asarray(p, float) - np.asarray(y, float)) ** 2))


def reliability_table(p: np.ndarray, y: np.ndarray, n_bins: int = 10) -> pd.DataFrame:
    p = np.asarray(p, float)
    y = np.asarray(y, float)
    bins = np.clip((p * n_bins).astype(int), 0, n_bins - 1)
    rows = []
    for b in range(n_bins):
        sel = bins == b
        n = int(sel.sum())
        rows.append(
            {
                "bin": b,
                "lo": b / n_bins,
                "hi": (b + 1) / n_bins,
                "mean_pred": float(p[sel].mean()) if n else float("nan"),
                "obs_rate": float(y[sel].mean()) if n else float("nan"),
                "n": n,
            }
        )
    return pd.DataFrame(rows)


def expected_calibration_error(p: np.ndarray, y: np.ndarray, n_bins: int = 10) -> float:
    t = reliability_table(p, y, n_bins)
    t = t[t["n"] > 0]
    if t.empty:
        return float("nan")
    return float((t["n"] * (t["mean_pred"] - t["obs_rate"]).abs()).sum() / t["n"].sum())


def block_bootstrap_ci(
    values_by_block: pd.Series, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float]:
    """Percentile CI of the mean, resampling whole blocks (weeks) with replacement."""
    v = values_by_block.dropna().to_numpy(dtype=float)
    if len(v) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(v), size=(n_boot, len(v)))
    means = v[idx].mean(axis=1)
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def paired_block_bootstrap_ci(
    a: pd.Series, b: pd.Series, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float, float]:
    """Mean difference a-b over common blocks with its bootstrap CI."""
    joined = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    d = joined["a"] - joined["b"]
    lo, hi = block_bootstrap_ci(d, n_boot=n_boot, alpha=alpha, seed=seed)
    return float(d.mean()), lo, hi
