"""Common interface of all rankers (baselines and models M0–M2).

A ranker scores rows of the point-in-time panel (one row = one company at
one cutoff). Higher score = call first. ``explain`` returns, for each row,
the reasons displayed in the app (the consultant decides, the tool shows its
logic — nLPD art. 21).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Reason:
    code: str
    label_fr: str
    label_de: str
    weight: float  # contribution (rules: points; trees: SHAP value on log-odds)

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "label_fr": self.label_fr,
            "label_de": self.label_de,
            "weight": round(float(self.weight), 4),
        }


class Ranker(ABC):
    name: str = "ranker"
    needs_training: bool = False
    outputs_probability: bool = False

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: object) -> None:  # noqa: B027
        """Optional: trained models override."""

    @abstractmethod
    def score(self, X: pd.DataFrame) -> np.ndarray: ...

    def explain(self, X: pd.DataFrame, top_n: int = 3) -> list[list[Reason]]:
        return [[] for _ in range(len(X))]
