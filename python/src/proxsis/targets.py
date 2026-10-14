"""Ground-truth targets measurable with public data.

Cible A ``offre_8s``         : the company publishes ≥1 job posting within the
                               8 weeks starting at cutoff T: [T, T+56d).
Cible B ``nouveau_besoin_8s``: A, and the company had NO posting in the 8 weeks
                               before T. This is where anticipation adds value:
                               a consultant cannot learn the need from an
                               existing posting.
Cible C ``offre_batiment_8s``: A restricted to construction trades.

Limits (documented in docs/backtest/cibles.md): postings are a proxy of the
need (some needs are never posted; some postings are evergreen), and agency
postings must be excluded upstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from proxsis.features import week_index
from proxsis.taxonomy import TRADES

TARGETS = ("offre_8s", "nouveau_besoin_8s", "offre_batiment_8s")


@dataclass
class Labels:
    y: dict[str, np.ndarray]  # target -> flat array aligned with the panel rows
    lead_days: np.ndarray  # days from cutoff to first posting in window (nan if none)
    prior_posting: np.ndarray  # bool: posting in the 8 weeks before T


def build_labels(
    companies: pd.DataFrame, postings: pd.DataFrame, weeks: list[date], cutoffs: list[int], horizon_weeks: int = 8
) -> Labels:
    c = companies.reset_index(drop=True)
    idx = {cid: i for i, cid in enumerate(c["company_id"])}
    N, W = len(c), len(weeks)
    big = W + horizon_weeks + 2
    p = postings[postings["company_id"].isin(idx)].copy()
    rows = p["company_id"].map(idx).to_numpy().astype(int)
    wi = week_index(p["available_at"], weeks)
    day_in_week = (pd.to_datetime(p["available_at"]) - pd.to_datetime([weeks[0]] * len(p))).dt.days.to_numpy() - 7 * wi
    is_constr = p["trade"].map(lambda t: TRADES[t].construction).to_numpy()
    ok = (wi >= 0) & (wi < big)
    any_m = np.zeros((N, big))
    con_m = np.zeros((N, big))
    first_day = np.full((N, big), np.inf)
    np.add.at(any_m, (rows[ok], wi[ok]), 1)
    np.add.at(con_m, (rows[ok & is_constr], wi[ok & is_constr]), 1)
    np.minimum.at(first_day, (rows[ok], wi[ok]), day_in_week[ok].astype(float))

    w = np.asarray(cutoffs)
    y_any, y_con, prior, lead = [], [], [], []
    for wc in w:
        fut = any_m[:, wc : wc + horizon_weeks]
        y_any.append(fut.sum(axis=1) > 0)
        y_con.append(con_m[:, wc : wc + horizon_weeks].sum(axis=1) > 0)
        prior.append(any_m[:, max(0, wc - horizon_weeks) : wc].sum(axis=1) > 0)
        # first posting day offset from cutoff (cutoff = Monday of week wc)
        offs = np.arange(fut.shape[1]) * 7.0
        cand = np.where(fut > 0, offs[None, :] + first_day[:, wc : wc + horizon_weeks], np.inf)
        ld = cand.min(axis=1)
        lead.append(np.where(np.isfinite(ld), ld, np.nan))
    y_any_a = np.concatenate(y_any)
    prior_a = np.concatenate(prior)
    return Labels(
        y={
            "offre_8s": y_any_a.astype(int),
            "nouveau_besoin_8s": (y_any_a & ~prior_a).astype(int),
            "offre_batiment_8s": np.concatenate(y_con).astype(int),
        },
        lead_days=np.concatenate(lead),
        prior_posting=prior_a,
    )


def label_complete_until(cutoff_idx: int, horizon_weeks: int = 8) -> int:
    """Last week index whose information is needed to know the label of ``cutoff_idx``."""
    return cutoff_idx + horizon_weeks - 1
