"""Naive baselines every model must beat.

* ``hasard``            — random order (seeded per cutoff).
* ``plus_grosses``      — largest companies first.
* ``activite_recente``  — companies that posted recently first (8, 26, 52 weeks).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from proxsis.models.base import Ranker, Reason


class RandomRanker(Ranker):
    name = "hasard"

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed

    def score(self, X: pd.DataFrame) -> np.ndarray:
        cut = int(X["cutoff_idx"].iloc[0]) if "cutoff_idx" in X and len(X) else 0
        return np.random.default_rng(self.seed * 100_003 + cut).random(len(X))


class BiggestRanker(Ranker):
    name = "plus_grosses"

    def score(self, X: pd.DataFrame) -> np.ndarray:
        return X["size_log_employees"].to_numpy(dtype=float)

    def explain(self, X: pd.DataFrame, top_n: int = 3) -> list[list[Reason]]:
        return [
            [Reason("taille", "Grande entreprise", "Grosses Unternehmen", float(v))] for v in X["size_log_employees"]
        ]


class RecentActivityRanker(Ranker):
    name = "activite_recente"

    def score(self, X: pd.DataFrame) -> np.ndarray:
        return np.asarray(
            X["post_8w"].to_numpy(float) * 10_000
            + X["post_26w"].to_numpy(float) * 100
            + X["post_52w"].to_numpy(float)
            - X["post_weeks_since"].to_numpy(float) / 1_000
        )
