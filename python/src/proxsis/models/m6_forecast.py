"""M6 — weekly forecast of job postings per trade family × region.

Simple first: seasonal-naive (same week last year), recent mean (last 4
weeks). Then a global LightGBM model on lags and calendar. Deep temporal
models are NOT implemented: with a few dozen short series (≈ 4 years of
weekly data) the literature (M4/M5 lessons, docs/recherche/etat-de-l-art.md)
does not support them, and they would have to beat the trees on this same
rolling-origin evaluation to be kept (docs/adr/0009-m6-prevision.md).

Evaluation: rolling origin, horizons 1–8 weeks, WAPE and MASE (scale =
in-sample seasonal-naive error).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import lightgbm as lgb
import numpy as np
import pandas as pd

from proxsis.features import week_index
from proxsis.taxonomy import TRADES

TRADE_FAMILY = {
    t: (
        "construction"
        if v.construction
        else "logistique"
        if t in ("cariste", "agent_logistique", "chauffeur_pl")
        else "pharma"
        if t in ("operateur_pharma", "laborantin")
        else "industrie_horlogerie"
    )
    for t, v in TRADES.items()
}


def weekly_series(postings: pd.DataFrame, companies: pd.DataFrame, weeks: list[date]) -> pd.DataFrame:
    """Counts per (family, region, week). Region = language region of the company (fr / de)."""
    p = postings.merge(companies[["company_id", "language"]], on="company_id", how="left")
    p["family"] = p["trade"].map(TRADE_FAMILY)
    p["wi"] = week_index(p["available_at"], weeks)
    p = p[(p["wi"] >= 0) & (p["wi"] < len(weeks))]
    g = p.groupby(["family", "language", "wi"]).size().rename("y").reset_index()
    full = pd.MultiIndex.from_product(
        [sorted(p["family"].unique()), sorted(p["language"].unique()), range(len(weeks))],
        names=["family", "language", "wi"],
    )
    return g.set_index(["family", "language", "wi"]).reindex(full, fill_value=0).reset_index()


def _lags(df: pd.DataFrame, weeks: list[date]) -> pd.DataFrame:
    df = df.sort_values(["family", "language", "wi"]).copy()
    grp = df.groupby(["family", "language"])["y"]
    for lag in (1, 2, 3, 4, 8, 52):
        df[f"lag{lag}"] = grp.shift(lag)
    df["mean4"] = grp.transform(lambda s: s.shift(1).rolling(4).mean())
    woy = np.array([weeks[i].isocalendar()[1] for i in df["wi"]])
    df["woy_sin"] = np.sin(2 * np.pi * woy / 52)
    df["woy_cos"] = np.cos(2 * np.pi * woy / 52)
    df["fam"] = df["family"].astype("category")
    df["lang"] = df["language"].astype("category")
    return df


@dataclass
class ForecastEval:
    wape: dict[str, float]
    mase: dict[str, float]
    n_origins: int
    horizons: int


def evaluate(series: pd.DataFrame, weeks: list[date], first_origin: int, step: int = 4, H: int = 8) -> ForecastEval:
    """Rolling-origin evaluation. At origin o, models see weeks < o and forecast o..o+H-1.

    For LightGBM, horizon-h forecasts use direct models on features lagged by ≥ h
    (lags < h are masked), so no future value is ever used.
    """
    df = _lags(series, weeks)
    W = len(weeks)
    errs: dict[str, list[float]] = {"saisonnier_naif": [], "moyenne_4s": [], "lightgbm_global": []}
    ys: list[float] = []
    scale_err = []
    origins = list(range(first_origin, W - H + 1, step))
    feat_all = ["lag1", "lag2", "lag3", "lag4", "lag8", "lag52", "mean4", "woy_sin", "woy_cos", "fam", "lang"]
    for o in origins:
        train = df[(df["wi"] < o) & df["lag52"].notna()]
        test = df[(df["wi"] >= o) & (df["wi"] < o + H)]
        # in-sample scale: seasonal naive error before o
        hist = df[(df["wi"] < o) & df["lag52"].notna()]
        scale_err.append(float(np.mean(np.abs(hist["y"] - hist["lag52"]))))
        preds_lgb = np.zeros(len(test))
        for h in range(1, H + 1):
            allowed = [
                f for f in feat_all if not (f.startswith("lag") and int(f[3:]) < h) and not (f == "mean4" and h > 1)
            ]
            # Direct model for horizon h: target y(t), features observed at t-h → shift features by (h-1).
            tr = train.copy()
            m = lgb.train(
                {
                    "objective": "poisson",
                    "learning_rate": 0.05,
                    "num_leaves": 7,
                    "min_data_in_leaf": 20,
                    "verbose": -1,
                    "seed": 0,
                },
                lgb.Dataset(tr[allowed], label=tr["y"]),
                num_boost_round=200,
            )
            sel = (test["wi"] == o + h - 1).to_numpy()
            if sel.any():
                preds_lgb[sel] = m.predict(test.loc[sel, allowed])
        y = test["y"].to_numpy(float)
        ys.extend(y)
        errs["saisonnier_naif"].extend(np.abs(y - test["lag52"].fillna(0).to_numpy()))
        last4 = df[(df["wi"] >= o - 4) & (df["wi"] < o)].groupby(["family", "language"])["y"].mean()
        m4 = test.apply(lambda r, last4=last4: last4.get((r["family"], r["language"]), 0.0), axis=1).to_numpy()
        errs["moyenne_4s"].extend(np.abs(y - m4))
        errs["lightgbm_global"].extend(np.abs(y - preds_lgb))
    total = float(np.sum(ys)) or 1.0
    scale = float(np.mean(scale_err)) or 1.0
    return ForecastEval(
        wape={k: float(np.sum(v) / total) for k, v in errs.items()},
        mase={k: float(np.mean(v) / scale) for k, v in errs.items()},
        n_origins=len(origins),
        horizons=H,
    )
