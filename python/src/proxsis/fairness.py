"""Fairness audit of candidate suggestions (procedure, run on FICTIONAL data).

For a sample of needs, compare who is *eligible* (passes the strict criteria)
with who is *suggested* (top-k):
* selection rate per group = suggested / eligible, aggregated over needs;
* disparate-impact ratio = min rate / max rate per attribute; < 0.8 flags a
  potential adverse impact (four-fifths rule, used as a screening signal,
  not as a legal test);
* counterfactual invariance: permuting the protected attributes must not
  change any suggestion (no direct use);
* proxies: association between each score input and each protected
  attribute (indicates *indirect* effects to discuss).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from proxsis.models.m5_matching import CandidateMatcher, Need

PROTECTED = ("audit_gender", "audit_age_band", "audit_nationality_group")


@dataclass
class AuditReport:
    n_needs: int
    k: int
    selection: dict[str, dict[str, float]]
    di_ratio: dict[str, float]
    flags: list[str]
    counterfactual_invariant: bool
    proxies: dict[str, dict[str, float]]

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__


def run_audit(
    candidates: pd.DataFrame,
    needs: list[Need],
    k: int = 5,
    seed: int = 0,
    matcher_factory: Callable[[pd.DataFrame], CandidateMatcher] = CandidateMatcher,
) -> AuditReport:
    matcher = matcher_factory(candidates)
    elig_counts: dict[str, dict[str, int]] = {a: {} for a in PROTECTED}
    sel_counts: dict[str, dict[str, int]] = {a: {} for a in PROTECTED}
    groups = candidates.set_index("candidate_id")
    picks: list[list[str]] = []
    for need in needs:
        e = matcher.eligible(need)
        s = [x.candidate_id for x in matcher.suggest(need, k)]
        picks.append(s)
        for a in PROTECTED:
            for g, n in groups.loc[e["candidate_id"], a].value_counts().items():
                elig_counts[a][str(g)] = elig_counts[a].get(str(g), 0) + int(n)
            for g, n in groups.loc[s, a].value_counts().items() if s else []:
                sel_counts[a][str(g)] = sel_counts[a].get(str(g), 0) + int(n)
    selection, di, flags = {}, {}, []
    for a in PROTECTED:
        rates = {g: sel_counts[a].get(g, 0) / n for g, n in elig_counts[a].items() if n >= 20}
        selection[a] = rates
        if len(rates) >= 2 and max(rates.values()) > 0:
            di[a] = min(rates.values()) / max(rates.values())
            if di[a] < 0.8:
                low = min(rates, key=lambda g: rates[g])
                flags.append(f"{a}: ratio {di[a]:.2f} < 0,8 (groupe le moins sélectionné : {low})")
    # Counterfactual: permute protected attributes, suggestions must be identical.
    rng = np.random.default_rng(seed)
    shuffled = candidates.copy()
    for a in PROTECTED:
        shuffled[a] = rng.permutation(shuffled[a].to_numpy())
    m2 = matcher_factory(shuffled)
    invariant = all([x.candidate_id for x in m2.suggest(n, k)] == p for n, p in zip(needs, picks, strict=True))
    # Proxies: correlation ratio (eta) between numeric inputs and groups.
    proxies: dict[str, dict[str, float]] = {}
    for col in ("experience_years", "max_travel_km"):
        proxies[col] = {a: _eta(candidates[col].astype(float), candidates[a]) for a in PROTECTED}
    proxies["driving_licence"] = {
        a: _eta(candidates["driving_licence"].astype(float), candidates[a]) for a in PROTECTED
    }
    return AuditReport(len(needs), k, selection, di, flags, invariant, proxies)


def _eta(x: pd.Series, g: pd.Series) -> float:
    """Correlation ratio η ∈ [0, 1]: share of the variance of x explained by the groups."""
    mu = x.mean()
    ss_tot = float(((x - mu) ** 2).sum())
    if ss_tot == 0:
        return 0.0
    ss_b = float(sum(len(v) * (v.mean() - mu) ** 2 for _, v in x.groupby(g)))
    return float(np.sqrt(ss_b / ss_tot))


def sample_needs(companies: pd.DataFrame, start: date, n: int, seed: int) -> list[Need]:
    """Needs drawn at random among companies: one trade of the company's sector, starting at ``start``."""
    from proxsis.taxonomy import SECTOR_TRADES

    rng = np.random.default_rng(seed)
    comp = companies.sample(n, random_state=seed)
    return [Need(str(r["company_id"]), str(rng.choice(np.array(SECTOR_TRADES[str(r["sector"])]))), float(r["lat"]),
                 float(r["lon"]), start) for r in comp.to_dict("records")]


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, float(c - h)), min(1.0, float(c + h)))


def availability_by_group(candidates: pd.DataFrame, start: date, attribute: str) -> dict[str, dict[str, float]]:
    """Days until available and share available within 14 days, per group (to explain gaps, not to score)."""
    days = (pd.to_datetime(candidates["available_from"]).dt.date.map(lambda d: (d - start).days)).clip(lower=0)
    out = {}
    for g, idx in candidates.groupby(attribute).groups.items():
        d = days.loc[idx]
        out[str(g)] = {"n": len(d), "jours_moyens": float(d.mean()), "part_dispo_14j": float((d <= 14).mean())}
    return out


def run_audit_samples(candidates: pd.DataFrame, companies: pd.DataFrame, start: date, n_needs: int = 300,
                      n_samples: int = 20, k: int = 5,
                      matcher_factory: Callable[[pd.DataFrame], CandidateMatcher] = CandidateMatcher,
                      seed_offset: int = 0) -> dict[str, Any]:
    """Repeat the audit on ``n_samples`` independent draws of needs (seeds 0..n-1).

    A single draw is not enough: the disparate-impact ratio moves by several
    hundredths from one draw to the next, which matters near the 0.8 threshold.
    """
    seeds = list(range(seed_offset, seed_offset + n_samples))
    reports = [run_audit(candidates, sample_needs(companies, start, n_needs, s), k=k, seed=s,
                         matcher_factory=matcher_factory) for s in seeds]
    di: dict[str, dict[str, Any]] = {}
    for a in PROTECTED:
        vals = [r.di_ratio[a] for r in reports if a in r.di_ratio]
        di[a] = {"moyenne": float(np.mean(vals)), "min": float(np.min(vals)), "max": float(np.max(vals)),
                 "valeurs": [round(v, 4) for v in vals]}
    flagged = sum(bool(r.flags) for r in reports)
    rates: dict[str, dict[str, float]] = {}
    below: dict[str, float] = {}
    below_ci: dict[str, list[float]] = {}
    for a in PROTECTED:
        groups = sorted({g for r in reports for g in r.selection[a]})
        rates[a] = {g: float(np.mean([r.selection[a][g] for r in reports if g in r.selection[a]])) for g in groups}
        n_below = sum(r.di_ratio.get(a, 1.0) < 0.8 for r in reports)
        below[a] = n_below / len(reports)
        below_ci[a] = list(_wilson(n_below, len(reports)))
    return {"n_samples": n_samples, "graines": seeds, "n_needs": n_needs, "k": k, "di_ratio": di,
            "taux_selection_moyen": rates, "part_tirages_sous_0_8": below, "part_tirages_sous_0_8_ic95": below_ci,
            "tirages_avec_alerte": flagged,
            "counterfactual_invariant": all(r.counterfactual_invariant for r in reports),
            "proxies": reports[0].proxies}


def permutation_test(candidates: pd.DataFrame, needs: list[Need], attribute: str, n_perm: int = 500, seed: int = 0,
                     k: int = 5, matcher_factory: Callable[..., CandidateMatcher] = CandidateMatcher,
                     min_group: int = 20) -> dict[str, Any]:
    """Is selection independent of the protected attribute, given who was eligible? The matcher's eligible sets and
    choices are kept; only the attribute is permuted among the candidates. Statistic: chi-square of selections per
    group against « same rate for everybody » (the min/max ratio is too noisy with small groups to be tested; it is
    reported for information). p-value = share of permutations with a statistic at least the observed one."""
    matcher = matcher_factory(candidates)
    elig: list[list[str]] = []
    picks: list[list[str]] = []
    for need in needs:
        elig.append(list(matcher.eligible(need)["candidate_id"]))
        picks.append([s.candidate_id for s in matcher.suggest(need, k)])
    pos = {c: i for i, c in enumerate(candidates["candidate_id"])}
    e_idx = np.array([pos[c] for x in elig for c in x], dtype=int)
    p_idx = np.array([pos[c] for x in picks for c in x], dtype=int)
    overall = len(p_idx) / len(e_idx) if len(e_idx) else 0.0

    def stats(groups: np.ndarray) -> tuple[float, float | None, dict[str, float]]:
        e = pd.Series(groups[e_idx]).value_counts()
        p = pd.Series(groups[p_idx]).value_counts()
        chi2 = 0.0
        for g, n in e.items():
            expected = n * overall
            if expected > 0:
                chi2 += (float(p.get(g, 0)) - expected) ** 2 / expected
        rates = {str(g): float(p.get(g, 0)) / float(n) for g, n in e.items() if n >= min_group}
        di = min(rates.values()) / max(rates.values()) if len(rates) >= 2 and max(rates.values()) > 0 else None
        return chi2, di, rates

    groups = candidates[attribute].astype(str).to_numpy()
    chi2, di, rates = stats(groups)
    rng = np.random.default_rng(seed)
    perm = [stats(rng.permutation(groups))[0] for _ in range(n_perm)]
    return {"attribut": attribute, "statistique": "khi-deux des sélections par groupe", "khi2_observe": chi2,
            "p_valeur": float(np.mean([x >= chi2 for x in perm])) if perm else None, "permutations": len(perm),
            "ratio_observe": di, "taux_selection": rates, "taux_global": overall}
