"""M2 — survival model for the time until the next public need.

Cox proportional hazards (lifelines) on point-in-time features. Each panel
row (company i, cutoff t) is a subject; the event is the first job posting at
or after t; observation is censored at the training date T (administrative
censoring), so recent rows are usable without waiting for the full horizon —
the main advantage of survival models over a fixed-horizon classifier.

Outputs: P(need within H weeks) for ranking, and the most likely window
("quand ?") from the predicted survival curve.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter

from proxsis.models.base import Ranker

SURV_FEATURES: tuple[str, ...] = (
    "award_6w",
    "award_13w",
    "award_26w",
    "award_logvalue_13w",
    "award_weeks_since",
    "cpermit_26w",
    "cpermit_52w",
    "cpermit_78w",
    "cpermit_logvalue_52w",
    "branch_13w",
    "capital_26w",
    "newreg_17w",
    "post_26w",
    "post_52w",
    "post_weeks_since",
    "region_permits_13w",
    "size_log_employees",
    "season_sin",
    "season_cos",
    "is_construction",
)


class SurvivalRanker(Ranker):
    name = "M2_survie"
    needs_training = True
    outputs_probability = True

    def __init__(self, horizon_weeks: int = 8, penalizer: float = 0.1, max_rows: int = 40_000, seed: int = 0) -> None:
        self.h = horizon_weeks
        self.penalizer = penalizer
        self.max_rows = max_rows
        self.seed = seed
        self.cols: list[str] = []
        self.mu: pd.Series | None = None
        self.sd: pd.Series | None = None
        self.cph: CoxPHFitter | None = None

    def _prep(self, X: pd.DataFrame) -> pd.DataFrame:
        assert self.mu is not None and self.sd is not None
        Z = (X[self.cols].astype(float) - self.mu) / self.sd
        return Z.clip(-8, 8)

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: object) -> None:
        durations = np.asarray(kwargs["durations"], dtype=float)
        events = np.asarray(kwargs["events"], dtype=int)
        rng = np.random.default_rng(self.seed)
        n = len(X)
        sel = rng.choice(n, size=min(n, self.max_rows), replace=False) if n > self.max_rows else np.arange(n)
        Xs = X.iloc[sel]
        cols = [c for c in SURV_FEATURES if c in Xs and Xs[c].astype(float).std() > 0]
        self.cols = cols
        self.mu = Xs[cols].astype(float).mean()
        self.sd = Xs[cols].astype(float).std().replace(0, 1)
        df = self._prep(Xs)
        df["duration"] = np.maximum(durations[sel], 1e-3)
        df["event"] = events[sel]
        self.cph = CoxPHFitter(penalizer=self.penalizer)
        self.cph.fit(df, duration_col="duration", event_col="event", show_progress=False)

    def survival_at(self, X: pd.DataFrame, times: list[float]) -> np.ndarray:
        assert self.cph is not None
        sf = self.cph.predict_survival_function(self._prep(X), times=times)
        return np.asarray(sf.to_numpy().T)  # rows x times

    def score(self, X: pd.DataFrame) -> np.ndarray:
        return 1.0 - self.survival_at(X, [float(self.h)])[:, 0]

    def likely_window(self, X: pd.DataFrame) -> np.ndarray:
        """Week offset (1..H) with the highest predicted probability of the first need."""
        s = self.survival_at(X, [float(t) for t in range(0, self.h + 1)])
        f = s[:, :-1] - s[:, 1:]
        return np.asarray(f.argmax(axis=1) + 1)

    def hazard_ratios(self) -> pd.Series:
        assert self.cph is not None
        ratios: pd.Series = np.exp(self.cph.params_).sort_values(ascending=False)
        return ratios


def next_posting_weeks(companies: pd.DataFrame, postings: pd.DataFrame, weeks: list[Any],
                       extra: int = 60) -> np.ndarray:
    """nxt[i, j] = fractional weeks from Monday of week j to company i's first posting at/after it."""
    from proxsis.features import week_index

    c = companies.reset_index(drop=True)
    idx = {cid: i for i, cid in enumerate(c["company_id"])}
    N, W = len(c), len(weeks) + extra
    first = np.full((N, W), np.inf)
    p = postings[postings["company_id"].isin(idx)]
    rows = p["company_id"].map(idx).to_numpy().astype(int)
    wi = week_index(p["available_at"], weeks)
    days = (pd.to_datetime(p["available_at"]) - pd.Timestamp(weeks[0])).dt.days.to_numpy()
    ok = (wi >= 0) & (wi < W)
    np.minimum.at(first, (rows[ok], wi[ok]), days[ok].astype(float))
    nxt = np.full((N, W + 1), np.inf)
    for j in range(W - 1, -1, -1):
        nxt[:, j] = np.minimum(first[:, j], nxt[:, j + 1])
    starts = (np.arange(W + 1) * 7.0)[None, :]
    return np.asarray((nxt - starts) / 7.0)
