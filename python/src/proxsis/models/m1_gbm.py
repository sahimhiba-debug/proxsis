"""M1 — gradient-boosted trees (LightGBM) on the point-in-time panel.

Binary objective (probability that the target happens within the horizon);
companies are ranked by that probability. Hyper-parameters are fixed
(docs/adr/0005-m1-boosting.md) and never tuned on the evaluation period.
Explanations use LightGBM's native SHAP contributions (``pred_contrib``),
aggregated by feature family so the consultant reads business reasons.
"""

from __future__ import annotations

from collections.abc import Mapping

import lightgbm as lgb
import numpy as np
import pandas as pd

from proxsis.features import FEATURE_GROUPS
from proxsis.models.base import Ranker, Reason

DEFAULT_PARAMS: dict[str, object] = {
    "objective": "binary",
    "learning_rate": 0.05,
    "num_leaves": 15,
    "min_child_samples": 100,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "lambda_l2": 1.0,
    "verbose": -1,
    "num_threads": 4,
}
N_ROUNDS = 250

_GROUP_DE: dict[str, str] = {
    "award": "Projekt — öffentlicher Auftrag",
    "cpermit": "Projekt — Baugesuch des Unternehmens",
    "branch": "Unternehmen — neue Zweigniederlassung",
    "capital": "Unternehmen — Kapitalerhöhung",
    "newreg": "Unternehmen — Neueintragung",
    "noise_mut": "Unternehmen — Zweckänderung",
    "move": "Unternehmen — Sitzverlegung",
    "liquidation": "Unternehmen — Liquidation",
    "post": "Rekrutierung — veröffentlichte Inserate",
    "region": "Region — Baugesuche im Umkreis von 25 km",
    "size": "Unternehmensgrösse",
    "season": "Saison",
    "sector": "Branche",
    "is": "Branche",
}


def _group(col: str) -> str:
    return col.split("_")[0]


class GbmRanker(Ranker):
    name = "M1_boosting"
    needs_training = True
    outputs_probability = True

    def __init__(
        self,
        feature_cols: list[str],
        seed: int = 0,
        params: Mapping[str, object] | None = None,
        n_rounds: int = N_ROUNDS,
    ) -> None:
        self.feature_cols = feature_cols
        self.params = {**DEFAULT_PARAMS, **(params or {}), "seed": seed}
        self.n_rounds = n_rounds
        self.model: lgb.Booster | None = None

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: object) -> None:
        ds = lgb.Dataset(X[self.feature_cols], label=y, categorical_feature=["sector"], free_raw_data=True)
        self.model = lgb.train(self.params, ds, num_boost_round=self.n_rounds)

    def score(self, X: pd.DataFrame) -> np.ndarray:
        assert self.model is not None, "fit() first"
        return np.asarray(self.model.predict(X[self.feature_cols]), dtype=float)

    def contributions(self, X: pd.DataFrame) -> pd.DataFrame:
        assert self.model is not None
        contrib = np.asarray(self.model.predict(X[self.feature_cols], pred_contrib=True))
        df = pd.DataFrame(contrib[:, :-1], columns=self.feature_cols, index=X.index)
        return df.T.groupby(_group).sum().T  # family-level SHAP (log-odds)

    def explain(self, X: pd.DataFrame, top_n: int = 3) -> list[list[Reason]]:
        g = self.contributions(X)
        out = []
        for _, row in g.iterrows():
            top = row[row > 0].sort_values(ascending=False).head(top_n)
            out.append([Reason(str(k), FEATURE_GROUPS.get(str(k), str(k)), _GROUP_DE.get(str(k), str(k)), float(v))
                        for k, v in top.items()])
        return out

    def feature_importance(self) -> pd.Series:
        assert self.model is not None
        imp = pd.Series(self.model.feature_importance("gain"), index=self.feature_cols)
        return imp.groupby(_group).sum().sort_values(ascending=False)
