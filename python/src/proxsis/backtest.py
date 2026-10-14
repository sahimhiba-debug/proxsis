"""Walk-forward backtest "vu à la date T".

For every weekly cutoff T of the evaluation period:
1. features use only information available before T (``PanelBuilder``);
2. trained models are (re)fitted on rows whose label is fully known before T
   (cutoff ≤ T − horizon: an *embargo* of one horizon);
3. each model ranks the eligible companies; we keep the global top-K list
   and each agency's top-k list;
4. labels (postings in [T, T+H)) are read only for scoring.

Metrics are aggregated per week, and confidence intervals come from a block
bootstrap over weeks.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from proxsis.features import Panel, PanelBuilder, week_index
from proxsis.metrics import (
    block_bootstrap_ci,
    brier,
    expected_calibration_error,
    paired_block_bootstrap_ci,
    reliability_table,
    top_k_mask,
)
from proxsis.models.base import Ranker
from proxsis.models.baselines import BiggestRanker, RandomRanker, RecentActivityRanker
from proxsis.models.m0_rules import RulesRanker
from proxsis.models.m1_gbm import GbmRanker
from proxsis.models.m2_survival import SurvivalRanker, next_posting_weeks
from proxsis.targets import build_labels


@dataclass(frozen=True)
class BacktestConfig:
    target: str = "nouveau_besoin_8s"
    horizon_weeks: int = 8
    warmup_weeks: int = 26
    eval_start: date = date(2024, 7, 1)
    retrain_every: int = 4
    k_global: int = 20
    k_agency: int = 10
    cooldown_weeks: int = 6  # operational simulation: a listed company is not re-listed for 6 weeks
    n_boot: int = 2000
    seed: int = 42
    models: tuple[str, ...] = ("hasard", "plus_grosses", "activite_recente", "M0_regles", "M1_boosting", "M2_survie")


@dataclass
class BacktestResult:
    config: dict[str, Any]
    summary: dict[str, Any]
    per_week: pd.DataFrame
    calibration: dict[str, Any]
    extras: dict[str, Any] = field(default_factory=dict)


def _first_seen(
    companies: pd.DataFrame, signals: pd.DataFrame, postings: pd.DataFrame, weeks: list[date]
) -> np.ndarray:
    """Week index from which a company is known publicly (first signal or posting).

    Companies already existing at the start of the data are known from week 0.
    """
    seen = pd.concat([signals[["company_id", "available_at"]], postings[["company_id", "available_at"]]])
    first = seen.dropna(subset=["company_id"]).groupby("company_id")["available_at"].min()
    fs = companies["company_id"].map(first)
    wi = np.where(fs.notna(), week_index(fs.fillna(weeks[0]), weeks) + 1, 0)
    if "created_week" in companies:
        pre = companies["created_week"].to_numpy() < 0
        wi = np.where(pre, 0, wi)
    return wi


def make_models(names: tuple[str, ...], panel: Panel, cfg: BacktestConfig) -> dict[str, Ranker]:
    available: dict[str, Ranker] = {
        "hasard": RandomRanker(cfg.seed),
        "plus_grosses": BiggestRanker(),
        "activite_recente": RecentActivityRanker(),
        "M0_regles": RulesRanker(),
        "M1_boosting": GbmRanker(panel.feature_cols, seed=cfg.seed),
        "M2_survie": SurvivalRanker(cfg.horizon_weeks, seed=cfg.seed),
    }
    return {n: available[n] for n in names}


def run_backtest(
    companies: pd.DataFrame,
    signals: pd.DataFrame,
    postings: pd.DataFrame,
    weeks: list[date],
    cfg: BacktestConfig | None = None,
    truth_waves: pd.DataFrame | None = None,
    verbose: bool = False,
) -> BacktestResult:
    cfg = cfg or BacktestConfig()
    t0 = time.time()
    H = cfg.horizon_weeks
    W = len(weeks)
    companies = companies.reset_index(drop=True)
    N = len(companies)
    cutoffs = list(range(cfg.warmup_weeks, W - H + 1))
    eval_start_idx = int(week_index(pd.Series([cfg.eval_start]), weeks)[0])
    eval_cutoffs = [c for c in cutoffs if c >= eval_start_idx]

    panel = PanelBuilder(companies, signals, postings, weeks).build(cutoffs)
    labels = build_labels(companies, postings, weeks, cutoffs, H)
    frame = panel.frame
    frame["y"] = labels.y[cfg.target]
    frame["lead_days"] = labels.lead_days
    frame["agency_id"] = np.tile(companies["agency_id"].to_numpy(), len(cutoffs)) if "agency_id" in companies else "all"
    frame["language"] = np.tile(companies["language"].to_numpy(), len(cutoffs))
    frame["canton"] = np.tile(companies["canton"].to_numpy(), len(cutoffs))

    known_from = np.tile(_first_seen(companies, signals, postings, weeks), len(cutoffs))
    eligible = (frame["cutoff_idx"].to_numpy() >= known_from) & (frame["liquidation_520w"].to_numpy() < 1)
    if cfg.target == "nouveau_besoin_8s":
        eligible &= ~labels.prior_posting
    frame["eligible"] = eligible

    if truth_waves is not None:
        frame["y_temp"] = _temp_need_labels(companies, truth_waves, weeks, cutoffs, H)

    nxt = next_posting_weeks(companies, postings, weeks)
    models = make_models(cfg.models, panel, cfg)
    tuning: dict[str, Any] = {}
    if "M1_boosting" in models:
        best_params, tuning = tune_m1(frame, panel.feature_cols, eval_start_idx, H, cfg.seed)
        models["M1_boosting"] = GbmRanker(panel.feature_cols, seed=cfg.seed, params=best_params)
    last_fit: dict[str, int] = {}
    last_listed: dict[str, dict[str, int]] = {n: {} for n in models}
    records = []
    prob_rows: dict[str, list[pd.DataFrame]] = {n: [] for n, m in models.items() if m.outputs_probability}
    fits = 0
    for T in eval_cutoffs:
        cur = frame[(frame["cutoff_idx"] == T) & frame["eligible"]]
        if cur.empty:
            continue
        for name, model in models.items():
            if model.needs_training and (name not in last_fit or T - last_fit[name] >= cfg.retrain_every):
                train = frame[(frame["cutoff_idx"] <= T - H) & frame["eligible"]]
                if name == "M2_survie":
                    # Censoring at T: anything observed before T is usable.
                    tr = frame[(frame["cutoff_idx"] < T) & frame["eligible"]]
                    rows_i = tr.index.to_numpy() % N
                    cut_i = tr["cutoff_idx"].to_numpy()
                    t_ev = nxt[rows_i, cut_i]
                    horizon_obs = (T - cut_i).astype(float)
                    model.fit(
                        tr,
                        tr["y"].to_numpy(),
                        durations=np.minimum(t_ev, horizon_obs),
                        events=(t_ev < horizon_obs).astype(int),
                    )
                else:
                    model.fit(train, train["y"].to_numpy())
                last_fit[name] = T
                fits += 1
            s = model.score(cur)
            keep = ["company_id", "cutoff_idx", "agency_id", "language", "canton", "y", "lead_days"]
            df = cur[keep + (["y_temp"] if "y_temp" in cur else [])].copy()
            df["score"] = s
            df["model"] = name
            df["in_global"] = top_k_mask(df, "cutoff_idx", "score", cfg.k_global).to_numpy()
            df["in_agency"] = top_k_mask(df, "agency_id", "score", cfg.k_agency).to_numpy()
            # Operational list: skip companies already listed in the last `cooldown_weeks` weeks.
            ll = last_listed[name]
            recent = np.array([T - ll.get(c, -10_000) < cfg.cooldown_weeks for c in df["company_id"]], dtype=bool)
            df["in_agency_cd"] = False
            avail = df[~recent]
            if not avail.empty:
                m = top_k_mask(avail, "agency_id", "score", cfg.k_agency)
                df.loc[avail.index[m.to_numpy()], "in_agency_cd"] = True
            for c in df.loc[df["in_agency_cd"], "company_id"]:
                ll[c] = T
            records.append(df)
            if model.outputs_probability:
                prob_rows[name].append(df[["score", "y"]])
        if verbose and T % 10 == 0:
            print(f"  cutoff {T}/{eval_cutoffs[-1]} ({time.time() - t0:.0f}s)")

    res = pd.concat(records, ignore_index=True)
    per_week, summary = _summarise(res, cfg)
    calibration = {}
    for name, parts in prob_rows.items():
        if parts:
            pr = pd.concat(parts)
            calibration[name] = {
                "brier": brier(pr["score"].to_numpy(), pr["y"].to_numpy()),
                "brier_base_rate": brier(np.full(len(pr), pr["y"].mean()), pr["y"].to_numpy()),
                "ece": expected_calibration_error(pr["score"].to_numpy(), pr["y"].to_numpy()),
                "reliability": reliability_table(pr["score"].to_numpy(), pr["y"].to_numpy()).to_dict(orient="records"),
            }
    extras: dict[str, Any] = {
        "n_fits": fits,
        "seconds": round(time.time() - t0, 1),
        "n_eval_weeks": len(eval_cutoffs),
        "n_companies": N,
        "eval_period": [str(weeks[eval_cutoffs[0]]), str(weeks[eval_cutoffs[-1]])],
    }
    if "M0_regles" in models:
        extras["m0_levels"] = _m0_levels(frame, eval_cutoffs, models["M0_regles"])  # type: ignore[arg-type]
    if "M1_boosting" in models and isinstance(models["M1_boosting"], GbmRanker) and models["M1_boosting"].model:
        extras["m1_importance"] = models["M1_boosting"].feature_importance().round(1).to_dict()
    extras["m1_tuning"] = tuning
    if "y_temp" in res:
        extras["temp_need_precision_agency"] = {
            str(n): float(g[g["in_agency"]].groupby("cutoff_idx")["y_temp"].mean().mean())
            for n, g in res.groupby("model")
        }
        extras["temp_need_base_rate"] = float(res.groupby("model")["y_temp"].mean().iloc[0])
    return BacktestResult(asdict(cfg) | {"eval_start": str(cfg.eval_start)}, summary, per_week, calibration, extras)


def _summarise(res: pd.DataFrame, cfg: BacktestConfig) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []
    for (name, T), g in res.groupby(["model", "cutoff_idx"], sort=True):
        pos = g["y"].sum()
        glob = g[g["in_global"]]
        ag = g[g["in_agency"]]
        cd = g[g["in_agency_cd"]]
        rows.append(
            {
                "model": name,
                "cutoff_idx": T,
                "p_at_k_agency_cd": cd.groupby("agency_id")["y"].mean().mean(),
                "recall_agency_cd": cd["y"].sum() / pos if pos else np.nan,
                "p_at_k_global": glob["y"].mean(),
                "p_at_k_agency": ag.groupby("agency_id")["y"].mean().mean(),
                "recall_agency_lists": ag["y"].sum() / pos if pos else np.nan,
                "base_rate": g["y"].mean(),
                "p_at_k_agency_fr": ag[ag["language"] == "fr"]["y"].mean(),
                "p_at_k_agency_de": ag[ag["language"] == "de"]["y"].mean(),
                "recall_fr": ag[(ag["language"] == "fr")]["y"].sum() / max(1, g[g["language"] == "fr"]["y"].sum()),
                "recall_de": ag[(ag["language"] == "de")]["y"].sum() / max(1, g[g["language"] == "de"]["y"].sum()),
                "share_alerts_de": (ag["language"] == "de").mean(),
            }
        )
    per_week = pd.DataFrame(rows)
    summary: dict[str, Any] = {}
    adv = _advance(res)
    for key, g in per_week.groupby("model"):
        name = str(key)
        gi = g.set_index("cutoff_idx")
        entry = {}
        for col in (
            "p_at_k_global",
            "p_at_k_agency",
            "recall_agency_lists",
            "p_at_k_agency_cd",
            "recall_agency_cd",
            "base_rate",
            "p_at_k_agency_fr",
            "p_at_k_agency_de",
            "recall_fr",
            "recall_de",
            "share_alerts_de",
        ):
            lo, hi = block_bootstrap_ci(gi[col], n_boot=cfg.n_boot, seed=cfg.seed)
            entry[col] = {"mean": float(gi[col].mean()), "ci95": [lo, hi]}
        entry.update(adv.get(name, {}))
        summary[name] = entry
    # Paired differences against the best naive baseline (by agency precision).
    baselines = [b for b in ("hasard", "plus_grosses", "activite_recente") if b in summary]
    if baselines:
        best = max(baselines, key=lambda b: summary[b]["p_at_k_agency_cd"]["mean"])
        summary["_best_baseline"] = best
        pw = per_week.pivot(index="cutoff_idx", columns="model")
        for name in summary:
            if name.startswith("_") or name == best:
                continue
            for col in (
                "p_at_k_agency",
                "p_at_k_global",
                "recall_agency_lists",
                "p_at_k_agency_cd",
                "recall_agency_cd",
            ):
                d, lo, hi = paired_block_bootstrap_ci(pw[col][name], pw[col][best], n_boot=cfg.n_boot, seed=cfg.seed)
                summary[name][f"diff_vs_{best}_{col}"] = {"mean": d, "ci95": [lo, hi]}
    return per_week, summary


def _advance(res: pd.DataFrame) -> dict[str, Any]:
    """Lead time ("jours d'avance") per detected need episode.

    An episode = (company, date of the first posting of the new need). It is
    *detected* by a model if the company appeared in its operational agency list
    (with cooldown, i.e. a fixed number of distinct calls) at some
    cutoff in the 8 weeks before the posting; the lead is the number of days
    between the EARLIEST such cutoff and the posting date.
    """
    pos = res[res["y"] == 1].copy()
    pos["event_day"] = pos["cutoff_idx"] * 7 + pos["lead_days"]
    out: dict[str, Any] = {}
    for key, g in pos.groupby("model"):
        name = str(key)
        episodes = g.groupby(["company_id", "event_day"])
        n_ep = episodes.ngroups
        flagged = g[g["in_agency_cd"]]
        lead = flagged.groupby(["company_id", "event_day"])["lead_days"].max()
        out[name] = {
            "episodes": int(n_ep),
            "detection_rate": float(len(lead) / n_ep) if n_ep else None,
            "lead_days_median": float(lead.median()) if len(lead) else None,
            "lead_days_iqr": [float(lead.quantile(0.25)), float(lead.quantile(0.75))] if len(lead) else None,
        }
    return out


def _m0_levels(frame: pd.DataFrame, eval_cutoffs: list[int], m0: RulesRanker) -> dict[str, Any]:
    cur = frame[frame["cutoff_idx"].isin(eval_cutoffs) & frame["eligible"]]
    lv = m0.level(cur)
    out = {}
    for level in ("rouge", "orange", "jaune", "aucun"):
        sel = lv == level
        out[level] = {
            "n": int(sel.sum()),
            "taux_realisation": float(cur["y"].to_numpy()[sel].mean()) if sel.any() else None,
        }
    return out


def _temp_need_labels(
    companies: pd.DataFrame, waves: pd.DataFrame, weeks: list[date], cutoffs: list[int], H: int
) -> np.ndarray:
    """FICTIONAL-ONLY target: the company has a latent temp-worker need in [T, T+H).
    Not measurable with real public data; shows the gap between proxy and true need."""
    idx = {cid: i for i, cid in enumerate(companies["company_id"])}
    N, W = len(companies), len(weeks) + H + 2
    m = np.zeros((N, W))
    tw = waves[waves["temp_need"]]
    wi = week_index(tw["week"], weeks)
    r = tw["company_id"].map(idx).to_numpy().astype(int)
    np.add.at(m, (r, wi), 1)
    return np.concatenate([(m[:, c : c + H].sum(axis=1) > 0).astype(int) for c in cutoffs])


def tune_m1(
    frame: pd.DataFrame, feature_cols: list[str], eval_start_idx: int, H: int, seed: int, val_weeks: int = 26
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Choose M1 hyper-parameters using ONLY data before the evaluation period.

    Train on cutoffs < eval_start - val_weeks - H, validate on the next ``val_weeks``
    cutoffs (labels known before eval_start). Criterion: mean agency P@k proxy =
    average precision of the top decile per week.
    """
    grid = {
        "souple": {"num_leaves": 15, "min_child_samples": 100, "learning_rate": 0.05},
        "regularise": {"num_leaves": 7, "min_child_samples": 300, "learning_rate": 0.03},
        "tres_regularise": {"num_leaves": 4, "min_child_samples": 800, "learning_rate": 0.03},
    }
    v_end = eval_start_idx - H
    v_start = v_end - val_weeks
    tr = frame[(frame["cutoff_idx"] <= v_start - H) & frame["eligible"]]
    va = frame[(frame["cutoff_idx"] > v_start) & (frame["cutoff_idx"] <= v_end) & frame["eligible"]]
    scores = {}
    if tr["y"].sum() < 20 or va.empty:
        return grid["regularise"], {"note": "pas assez de données de validation", "choix": "regularise"}
    for name, params in grid.items():
        m = GbmRanker(feature_cols, seed=seed, params=params)
        m.fit(tr, tr["y"].to_numpy())
        v = va.assign(score=m.score(va))
        top = top_k_mask(v, "cutoff_idx", "score", max(1, int(len(v) / v["cutoff_idx"].nunique() * 0.1)))
        scores[name] = float(v[top].groupby("cutoff_idx")["y"].mean().mean())
    best = max(scores, key=lambda k: scores[k])
    return grid[best], {"validation": [int(v_start), int(v_end)], "scores_top_decile": scores, "choix": best}
