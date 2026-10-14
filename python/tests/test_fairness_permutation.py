"""Permutation test of the disparate-impact ratio (FICTIONAL candidates)."""

from datetime import date

import numpy as np

from proxsis.fairness import permutation_test
from proxsis.models.m5_matching import CandidateMatcher, Need
from proxsis.synth.candidates import generate_candidates

PLACES = [{"localite": "Sion", "commune": "Sion", "lat": 46.23, "lon": 7.36, "langue": "fr", "poids": 1}]
TODAY = date(2026, 10, 5)


def _needs():
    return [Need(f"e{i}", t, 46.23, 7.36, TODAY) for i, t in enumerate(["macon", "coffreur", "manoeuvre_construction",
                                                                      "peintre", "platrier", "electricien"] * 3)]


class Biased(CandidateMatcher):
    """Deliberately biased: prefers one nationality group (reads a forbidden column through the full frame)."""

    def __init__(self, candidates, **kw):
        super().__init__(candidates, **kw)
        self.group = candidates.set_index("candidate_id")["audit_nationality_group"]

    def score_frame(self, need, e):
        return np.where(self.group.loc[e["candidate_id"]].to_numpy() == "CH", 1.0, 0.0) + 0.001 * np.arange(len(e))


def test_the_permutation_test_detects_a_biased_matcher_and_not_a_neutral_one():
    pool = generate_candidates(PLACES, today=TODAY, n=300, seed=11)
    neutral = permutation_test(pool, _needs(), "audit_nationality_group", n_perm=200, seed=0)
    biased = permutation_test(pool, _needs(), "audit_nationality_group", n_perm=200, seed=0, matcher_factory=Biased)
    assert biased["p_valeur"] < 0.05
    assert neutral["p_valeur"] > biased["p_valeur"]
    assert set(neutral["taux_selection"]) >= {"CH"}
