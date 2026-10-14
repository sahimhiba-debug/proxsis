"""Real backtest on public data only — target T0.

T0 = « the company wins at least one new public award (simap.ch) published in
the 8 weeks after the Monday T ». It is the only company-level target that the
public sources we may use today can measure. It is an **activity proxy**, not a
staffing need: a staffing need (T2, an order to Flexsis) needs Flexsis' order
history (docs/affaires/demande-donnees-pilote.md).

Point in time: at week T, only awards published before T are used, and only
companies already seen before T can be ranked (a public radar cannot know the
others). Rankers: random (exact expectation = base rate), recency, frequency
over 52 weeks, and « M0 marchés » (recency-weighted award count, half-life 8
weeks — what the rule-based radar reduces to when the only signal is awards).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

from proxsis.entities import is_legal_entity_name, normalize_name
from proxsis.pii import PRIVATE_PLACEHOLDER

RANKERS = ("hasard", "recence", "frequence_52s", "m0_marches")


def events_from_records(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for r in records:
        if not str(r.get("pub_type", "")).startswith(("award", "direct")) or not r.get("publication_date"):
            continue
        for v in r.get("vendors") or []:
            name = (v.get("name") or "").strip()
            if not name or name == PRIVATE_PLACEHOLDER or not is_legal_entity_name(name):
                continue
            rows.append({"company": normalize_name(name), "name": name,
                         "available_at": date.fromisoformat(str(r["publication_date"])[:10]),
                         "canton": r.get("order_canton"), "value_chf": v.get("price_chf"),
                         "authority": r.get("contracting_authority"),
                         "publication_id": r.get("publication_id"), "url": (r.get("provenance") or {}).get("url")})
    ev = pd.DataFrame(rows, columns=["company", "name", "available_at", "canton", "value_chf", "authority",
                                     "publication_id", "url"])
    return ev.drop_duplicates(["company", "publication_id"]).reset_index(drop=True)


def snapshot(ev: pd.DataFrame, T: date, horizon_days: int = 56, half_life_days: float = 56.0) -> pd.DataFrame:
    """Features « seen at date T » and the targets, one row per company known before T.

    Targets: ``target`` (T0: at least one award in [T, T + horizon[) and ``surge`` (« pic » : at least 2 awards in
    the horizon and at least twice the company's usual pace over the past 52 weeks)."""
    cols = ["n_52s", "n_26s", "n_8s", "last_days", "m0", "value_52s", "n_auth_52s", "first_days", "k_next",
            "target", "surge"]
    past = ev[ev["available_at"] < T]
    if past.empty:
        return pd.DataFrame(columns=cols)
    age = past["available_at"].map(lambda d: (T - d).days).astype(float)
    val = pd.to_numeric(past["value_chf"], errors="coerce").fillna(0.0)
    # A missing adjudicator, or one older than 52 weeks, is not counted by nunique. Not `astype(str)`: pandas 2 turns
    # a missing value into the text "None" or "nan" (counted), pandas 3 keeps it missing; the published measures
    # (REEL-SPEC-*, computed with pandas 3.0.6) are those of this rule, whatever the pandas version (07.10.2026).
    authority_52 = past["authority"].where(past["authority"].notna() & (age <= 364))
    p = past.assign(age=age, in52=age <= 364, in26=age <= 182, in8=age <= 56, w=np.power(0.5, age / half_life_days),
                    v52=np.where(age <= 364, val, 0.0), a52=authority_52)
    g = p.groupby("company")
    snap = pd.DataFrame({"n_52s": g["in52"].sum().astype(int), "n_26s": g["in26"].sum().astype(int),
                         "n_8s": g["in8"].sum().astype(int), "last_days": g["age"].min(), "m0": g["w"].sum(),
                         "value_52s": g["v52"].sum(), "n_auth_52s": g["a52"].nunique(), "first_days": g["age"].max()})
    fut = ev[(ev["available_at"] >= T) & (ev["available_at"] < T + timedelta(days=horizon_days))]
    k_next = fut.groupby("company").size()
    snap["k_next"] = k_next.reindex(snap.index).fillna(0).astype(int)
    snap["target"] = snap["k_next"] > 0
    usual = snap["n_52s"] * (horizon_days / 7) / 52
    snap["surge"] = (snap["k_next"] >= 2) & (snap["k_next"] >= 2 * usual)
    return snap.sort_index()


def region_at(lots: pd.DataFrame, cantons: set[str], T: date, past: pd.DataFrame) -> set[str]:
    """Audit m1: firms whose most frequent laureate canton, among lots (every specialty) published before T, is in
    ``cantons``, among the companies of ``past`` (the events published before T): the region of a ranking at T is
    defined with past information only. Shared by the specialty backtest (CLAIMS REEL-SPEC-BAT) and the dated
    Monday of the presentation (``date_choice``)."""
    prior = lots[lots["available_at"] < T]
    mode = prior.groupby("company")["canton"].agg(_first_mode)
    return set(mode[mode.isin(cantons)].index) & set(past["company"])


def _first_mode(x: pd.Series) -> Any:
    """The most frequent value (ties: the smallest, pandas' ``mode`` order); None when there is none."""
    m = x.mode()
    return m.iloc[0] if len(m) else None


def first_time_winners(ev: pd.DataFrame, T: date, horizon_days: int = 56) -> tuple[int, int]:
    """(winners in the horizon never seen before T, all winners in the horizon)."""
    known = set(ev.loc[ev["available_at"] < T, "company"])
    fut = set(ev.loc[(ev["available_at"] >= T) & (ev["available_at"] < T + timedelta(days=horizon_days)), "company"])
    return len(fut - known), len(fut)


def _rank(snap: pd.DataFrame, ranker: str) -> pd.Index:
    s = snap.reset_index().rename(columns={"index": "company"})
    if ranker == "recence":
        s = s.sort_values(["last_days", "company"], ascending=[True, True])
    elif ranker == "frequence_52s":
        s = s.sort_values(["n_52s", "last_days", "company"], ascending=[False, True, True])
    elif ranker == "m0_marches":
        s = s.sort_values(["m0", "company"], ascending=[False, True])
    else:
        raise ValueError(ranker)
    companies: pd.Index = pd.Index(s["company"])
    return companies


def _block_boot_ci(x: np.ndarray, n_boot: int, block: int, rng: np.random.Generator) -> tuple[float, float]:
    n = len(x)
    if n == 0:
        return (float("nan"), float("nan"))
    nb = int(np.ceil(n / block))
    means = []
    for _ in range(n_boot):
        starts = rng.integers(0, max(n - block + 1, 1), nb)
        idx = np.concatenate([np.arange(s, min(s + block, n)) for s in starts])[:n]
        means.append(float(np.mean(x[idx])))
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def evaluate_t0(ev: pd.DataFrame, first_week: date, last_week: date, k: int = 20, horizon_days: int = 56,
                data_end: date | None = None, n_boot: int = 2000, seed: int = 0,
                block: int | None = None) -> dict[str, Any]:
    # Audit M6: neighbouring weeks share 7 of their 8 horizon weeks → blocks at least as long as the horizon.
    block = max(block or 0, -(-horizon_days // 7))
    last_event = ev["available_at"].max() if not ev.empty else first_week
    if data_end is not None and data_end > last_event + timedelta(days=7):
        # Audit m14: a data end later than the collected data would silently truncate the last targets.
        raise ValueError(f"fin des données ({data_end}) postérieure à la dernière adjudication collectée "
                         f"({last_event}) de plus d'une semaine")
    end = data_end or last_event
    if last_week + timedelta(days=horizon_days) > end + timedelta(days=1):
        raise ValueError(f"l'horizon de la dernière semaine ({last_week} + {horizon_days} j) "
                         f"dépasse les données ({end})")
    weeks = []
    d = first_week - timedelta(days=first_week.weekday())
    while d <= last_week:
        weeks.append(d)
        d += timedelta(days=7)
    per: dict[str, list[float]] = {r: [] for r in RANKERS}
    base, sizes = [], []
    for T in weeks:
        snap = snapshot(ev, T, horizon_days)
        if len(snap) < k:
            continue
        rate = float(snap["target"].mean())
        base.append(rate)
        sizes.append(len(snap))
        per["hasard"].append(rate)  # exact expectation of a random top-k
        for r in RANKERS[1:]:
            top = _rank(snap, r)[:k]
            per[r].append(float(snap.loc[top, "target"].mean()))
    rng = np.random.default_rng(seed)
    out: dict[str, Any] = {"cible": "T0 : nouveau marché public (simap) dans les 8 semaines", "k": k,
                           "n_semaines": len(base), "semaines": [str(weeks[0]), str(weeks[-1])],
                           "taux_de_base": float(np.mean(base)) if base else None,
                           "entreprises_classees_moyenne": float(np.mean(sizes)) if sizes else None,
                           "p_at_k": {}}
    for r in RANKERS:
        x = np.array(per[r])
        out["p_at_k"][r] = {"moyenne": float(x.mean()) if len(x) else None,
                            "ic95": list(_block_boot_ci(x, n_boot, block, rng))}
    out["bloc_semaines"] = block
    out["sensibilite_bloc_12"] = {r: list(_block_boot_ci(np.array(per[r]), n_boot, max(12, block), rng))
                                  for r in RANKERS}
    best = max(("recence", "frequence_52s"), key=lambda r: out["p_at_k"][r]["moyenne"] or 0)
    diff = np.array(per["m0_marches"]) - np.array(per[best])
    out["m0_moins_meilleure_naive"] = {"naive": best, "moyenne": float(diff.mean()) if len(diff) else None,
                                       "ic95": list(_block_boot_ci(diff, n_boot, block, rng))}
    return out


def surprise_flags(snap: pd.DataFrame, horizon_days: int = 56) -> pd.DataFrame:
    """Surprise detector, rule part: « rythme_double » (at least 2 awards in the last 8 weeks and at least twice
    the usual pace of the 44 weeks before) and « nouveau_venu » (first award less than ``horizon_days`` ago)."""
    prior = (snap["n_52s"] - snap["n_8s"]).astype(float) * 8 / 44
    return pd.DataFrame({"rythme_double": (snap["n_8s"] >= 2) & (snap["n_8s"] >= 2 * prior),
                         "nouveau_venu": snap["first_days"].astype(float) <= horizon_days}, index=snap.index)


FEATURES = ("n_52s", "n_26s", "n_8s", "last_days", "m0", "value_52s", "n_auth_52s", "first_days")


def _x(snap: pd.DataFrame) -> np.ndarray:
    x = snap[list(FEATURES)].astype(float).to_numpy()
    x = np.log1p(np.clip(x, 0, None))
    trend = (snap["n_8s"] * 6.5 - snap["n_52s"]).astype(float).to_numpy()[:, None] / 10.0
    return np.hstack([x, trend])


def evaluate_extended(ev: pd.DataFrame, first_week: date, last_week: date, train_from: date, k: int = 20,
                      horizon_days: int = 56, n_boot: int = 2000, seed: int = 0, retrain_every: int = 4,
                      data_end: date | None = None,
                      eval_companies: set[str] | Callable[[date, pd.DataFrame], set[str]] | None = None
                      ) -> dict[str, Any]:
    """T0 and « pic » targets; rankers: random, recency, frequency, M0, and a combined logistic model trained
    on past weeks whose labels were fully observed at T (week W with W + horizon <= T).

    ``eval_companies``: rank and score only these companies (e.g. firms based in Valais), as a fixed set or as a
    function of the date and of the events published before it (audit m1: the population is then defined with
    past information only); the model is still trained on every company. Surprise flags are also scored outside
    the top k, where the call list shows them, and on the 3 retained surprises (outside the top k, by the « pic »
    model score). The rule flags of the surprise detector are scored too (hit rate of the flagged
    companies on both targets, against the base rate)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    end = data_end or (ev["available_at"].max() if not ev.empty else last_week)
    if last_week + timedelta(days=horizon_days) > end + timedelta(days=1):
        raise ValueError("l'horizon de la dernière semaine dépasse les données")
    block = -(-horizon_days // 7)
    all_weeks = []
    d = train_from - timedelta(days=train_from.weekday())
    while d <= last_week:
        all_weeks.append(d)
        d += timedelta(days=7)
    snaps = {W: snapshot(ev, W, horizon_days) for W in all_weeks}
    region_sizes: list[int] = []

    def _region(sn: pd.DataFrame, W: date) -> pd.DataFrame:
        if eval_companies is None:
            return sn
        allowed = eval_companies(W, ev[ev["available_at"] < W]) if callable(eval_companies) else eval_companies
        return sn.loc[sn.index.isin(allowed)]

    eval_weeks = [W for W in all_weeks if first_week <= W and len(_region(snaps[W], W)) >= k]
    flag_hits: dict[str, dict[str, list[float]]] = {f: {"t0": [], "pic": [], "base": [], "t0_hors": [],
                                                        "base_hors": []}
                                                    for f in ("rythme_double", "nouveau_venu")}
    retained: dict[str, list[float]] = {"t0": [], "pic": []}
    targets = {"t0": "target", "pic": "surge"}
    per: dict[str, dict[str, list[float]]] = {t: {r: [] for r in (*RANKERS, "combine")} for t in targets}
    base: dict[str, list[float]] = {t: [] for t in targets}
    models: dict[str, Any] = {}
    min_gap = 10**9
    new_w, all_w = 0, 0
    for i, T in enumerate(eval_weeks):
        snap = _region(snaps[T], T)
        region_sizes.append(len(snap))
        flags = surprise_flags(snap, horizon_days)
        top_freq = set(_rank(snap, "frequence_52s")[:k])
        outside = ~snap.index.isin(top_freq)
        for f in flag_hits:
            sel = snap[flags[f]]
            flag_hits[f]["t0"] += list(sel["target"].astype(float))
            flag_hits[f]["pic"] += list(sel["surge"].astype(float))
            flag_hits[f]["base"].append(float(snap["target"].mean()))
            flag_hits[f]["t0_hors"] += list(snap[flags[f] & outside]["target"].astype(float))
            if outside.any():
                flag_hits[f]["base_hors"].append(float(snap[outside]["target"].mean()))
        nw, aw = first_time_winners(ev, T, horizon_days)
        new_w += nw
        all_w += aw
        train_weeks = [W for W in all_weeks if W + timedelta(days=horizon_days) <= T and len(snaps[W])]
        if train_weeks:
            min_gap = min(min_gap, (T - max(train_weeks)).days)
        for t, col in targets.items():
            y = snap[col].astype(bool)
            base[t].append(float(y.mean()))
            per[t]["hasard"].append(float(y.mean()))
            for r in RANKERS[1:]:
                per[t][r].append(float(y.loc[_rank(snap, r)[:k]].mean()))
            if i % retrain_every == 0 or t not in models:
                tr = pd.concat([snaps[W] for W in train_weeks]) if train_weeks else pd.DataFrame()
                if len(tr) and tr[col].astype(bool).nunique() == 2:
                    sc = StandardScaler().fit(_x(tr))
                    m = LogisticRegression(max_iter=2000).fit(sc.transform(_x(tr)), tr[col].astype(bool))
                    models[t] = (sc, m)
            if t in models:
                sc, m = models[t]
                score = pd.Series(m.predict_proba(sc.transform(_x(snap)))[:, 1], index=snap.index)
                top = score.sort_values(ascending=False, kind="mergesort").index[:k]
                per[t]["combine"].append(float(y.loc[top].mean()))
                if t == "pic":  # the 3 surprises the call list shows: flagged, outside the top k, best « pic » score
                    flagged = snap.index[(flags["rythme_double"] | flags["nouveau_venu"]) & outside]
                    kept = score.loc[flagged].sort_values(ascending=False, kind="mergesort").index[:3]
                    retained["t0"] += list(snap.loc[kept, "target"].astype(float))
                    retained["pic"] += list(snap.loc[kept, "surge"].astype(float))
            else:
                per[t]["combine"].append(per[t]["frequence_52s"][-1])
    rng = np.random.default_rng(seed)
    out: dict[str, Any] = {"k": k, "n_semaines": len(eval_weeks), "semaines": [str(eval_weeks[0]), str(eval_weeks[-1])],
                           "bloc_semaines": block, "cibles": {},
                           "part_premiers_gagnants": new_w / all_w if all_w else None,
                           "premiers_gagnants": {"nouveaux": new_w, "tous": all_w},
                           "region": {"entreprises": (len(eval_companies) if isinstance(eval_companies, set)
                                                      else None),
                                      "entreprises_classees_moyenne": float(np.mean(region_sizes)) if region_sizes
                                      else None,
                                      "note": "classement restreint à ces entreprises ; apprentissage sur toutes"},
                           "drapeaux_surprise": {
                               f: {"signalements": len(h["t0"]),
                                   "taux_t0": float(np.mean(h["t0"])) if h["t0"] else None,
                                   "taux_pic": float(np.mean(h["pic"])) if h["pic"] else None,
                                   "taux_de_base_t0": float(np.mean(h["base"])) if h["base"] else None,
                                   "hors_top_k": {"signalements": len(h["t0_hors"]),
                                                  "taux_t0": float(np.mean(h["t0_hors"])) if h["t0_hors"] else None,
                                                  "taux_de_base_t0": float(np.mean(h["base_hors"]))
                                                  if h["base_hors"] else None}}
                               for f, h in flag_hits.items()},
                           "surprises_retenues": {"signalements": len(retained["t0"]),
                                                  "taux_t0": float(np.mean(retained["t0"])) if retained["t0"] else None,
                                                  "taux_pic": float(np.mean(retained["pic"])) if retained["pic"]
                                                  else None},
                           "entrainement": {"depuis": str(train_from), "reentrainement_semaines": retrain_every,
                                            "modele": "régression logistique (variables standardisées, log)",
                                            "variables": [*FEATURES, "tendance"],
                                            "dernier_label_avant_T_jours": min_gap}}
    for t in targets:
        res: dict[str, Any] = {"taux_de_base": float(np.mean(base[t])), "p_at_k": {}}
        for r, xs in per[t].items():
            x = np.array(xs)
            res["p_at_k"][r] = {"moyenne": float(x.mean()), "ic95": list(_block_boot_ci(x, n_boot, block, rng))}
        diff = np.array(per[t]["combine"]) - np.array(per[t]["frequence_52s"])
        res["combine_moins_frequence"] = {"moyenne": float(diff.mean()),
                                          "ic95": list(_block_boot_ci(diff, n_boot, block, rng))}
        out["cibles"][t] = res
    return out
