"""M0 — explainable rules written by the team.

Principle: *count signal families, not signals*. The rules, windows and
thresholds below are chosen from domain reasoning (see
docs/adr/0004-m0-regles.md), not tuned on the backtest.

Families:
* Projet      — public contract awarded recently, or the company filed a
                building permit within the year;
* Entreprise  — new branch, new registration, capital increase;
* Recrutement — the company hires regularly (≥ 2 postings in 52 weeks);
* Région      — (construction firms) unusually many building permits nearby.
A known liquidation excludes the company.

Alert level: ROUGE ≥ 3 families, ORANGE = 2, JAUNE = 1.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from proxsis.models.base import Ranker, Reason


@dataclass(frozen=True)
class Rule:
    code: str
    family: str
    label_fr: str
    label_de: str
    test: Callable[[pd.DataFrame], np.ndarray]


def _region_high(X: pd.DataFrame) -> np.ndarray:
    v = X["region_permits_13w"].to_numpy(float)
    thr = np.quantile(v, 0.75) if len(v) else np.inf
    return np.asarray((X["is_construction"].to_numpy() == 1) & (v > thr))


RULES: list[Rule] = [
    Rule(
        "marche_recent",
        "projet",
        "Marché public attribué ces 6 dernières semaines",
        "Öffentlicher Auftrag in den letzten 6 Wochen erhalten",
        lambda X: X["award_6w"].to_numpy() >= 1,
    ),
    Rule(
        "gros_marche",
        "projet",
        "Marchés attribués > CHF 500 000 sur 13 semaines",
        "Zuschläge > CHF 500 000 in 13 Wochen",
        lambda X: X["award_logvalue_13w"].to_numpy() >= np.log1p(500_000),
    ),
    Rule(
        "permis_entreprise",
        "projet",
        "Permis de construire déposé par l'entreprise dans l'année",
        "Baugesuch des Unternehmens im letzten Jahr",
        lambda X: X["cpermit_52w"].to_numpy() >= 1,
    ),
    Rule(
        "succursale",
        "entreprise",
        "Nouvelle succursale inscrite (13 semaines)",
        "Neue Zweigniederlassung eingetragen (13 Wochen)",
        lambda X: X["branch_13w"].to_numpy() >= 1,
    ),
    Rule(
        "nouvelle_inscription",
        "entreprise",
        "Entreprise nouvellement inscrite au RC",
        "Neu im Handelsregister eingetragen",
        lambda X: X["newreg_17w"].to_numpy() >= 1,
    ),
    Rule(
        "capital",
        "entreprise",
        "Augmentation de capital (26 semaines)",
        "Kapitalerhöhung (26 Wochen)",
        lambda X: X["capital_26w"].to_numpy() >= 1,
    ),
    Rule(
        "recrute_regulierement",
        "recrutement",
        "Recrute régulièrement (≥ 2 offres sur 12 mois)",
        "Rekrutiert regelmässig (≥ 2 Inserate in 12 Monaten)",
        lambda X: X["post_52w"].to_numpy() >= 2,
    ),
    Rule(
        "region_active",
        "region",
        "Forte activité de permis à moins de 25 km",
        "Viele Baugesuche im Umkreis von 25 km",
        _region_high,
    ),
]

LEVELS = {3: "rouge", 2: "orange", 1: "jaune", 0: "aucun"}


class RulesRanker(Ranker):
    name = "M0_regles"

    def _fired(self, X: pd.DataFrame) -> dict[str, np.ndarray]:
        return {r.code: np.asarray(r.test(X), dtype=bool) for r in RULES}

    def families(self, X: pd.DataFrame) -> np.ndarray:
        fired = self._fired(X)
        fams = sorted({r.family for r in RULES})
        per_fam = np.stack([np.any([fired[r.code] for r in RULES if r.family == f], axis=0) for f in fams])
        return per_fam.sum(axis=0)

    def level(self, X: pd.DataFrame) -> np.ndarray:
        n = np.minimum(self.families(X), 3)
        return np.array([LEVELS[int(k)] for k in n])

    def score(self, X: pd.DataFrame) -> np.ndarray:
        n = self.families(X).astype(float)
        tie = X["award_logvalue_13w"].to_numpy(float) / 20 + X["size_log_employees"].to_numpy(float) / 100
        s = n * 10 + tie
        excluded = X["liquidation_520w"].to_numpy() >= 1
        return np.where(excluded, -1e9, s)

    def explain(self, X: pd.DataFrame, top_n: int = 3) -> list[list[Reason]]:
        fired = self._fired(X)
        out: list[list[Reason]] = []
        for i in range(len(X)):
            reasons = [Reason(r.code, r.label_fr, r.label_de, 1.0) for r in RULES if fired[r.code][i]]
            out.append(reasons[: max(top_n, len(reasons))])
        return out
