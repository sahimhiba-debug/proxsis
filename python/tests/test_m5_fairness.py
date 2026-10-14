from datetime import date

import numpy as np
import pandas as pd
import pytest

from proxsis.fairness import run_audit
from proxsis.models.m5_matching import CandidateMatcher, Need
from proxsis.synth.world import WorldConfig, generate_world


@pytest.fixture(scope="module")
def world():
    return generate_world(WorldConfig(seed=8, n_companies=200, n_candidates=600))


def _needs(world, n=60, seed=0):
    rng = np.random.default_rng(seed)
    comp = world.companies.sample(n, random_state=seed)
    from proxsis.taxonomy import SECTOR_TRADES

    return [
        Need(r.company_id, str(rng.choice(SECTOR_TRADES[r.sector])), r.lat, r.lon, world.weeks[-1])
        for r in comp.itertuples()
    ]


def test_strict_criteria_hold(world):
    m = CandidateMatcher(world.candidates)
    need = Need("c", "grutier", 46.233, 7.360, date(2026, 10, 5))
    for s in m.suggest(need, k=10):
        row = world.candidates.set_index("candidate_id").loc[s.candidate_id]
        assert "permis_grue" in row["certifications"]
        assert s.distance_km <= row["max_travel_km"] + 1e-6


def test_each_suggestion_has_reasons_in_both_languages(world):
    m = CandidateMatcher(world.candidates)
    for need in _needs(world, 10):
        for s in m.suggest(need):
            assert s.reasons_fr and s.reasons_de and len(s.reasons_fr) == len(s.reasons_de)


def test_matcher_never_sees_protected_attributes(world):
    m = CandidateMatcher(world.candidates)
    assert not any(c.startswith("audit_") for c in m.c.columns)


def test_audit_counterfactual_invariance(world):
    rep = run_audit(world.candidates, _needs(world), k=5)
    assert rep.counterfactual_invariant
    assert set(rep.di_ratio) <= {"audit_gender", "audit_age_band", "audit_nationality_group"}


def test_audit_detects_injected_bias(world):
    """Contrôle de la procédure : un appariement volontairement biaisé doit être signalé."""

    class Biased(CandidateMatcher):
        def __init__(self, candidates: pd.DataFrame) -> None:
            super().__init__(candidates)
            self._penalised = set(candidates.loc[candidates["audit_gender"] == "F", "candidate_id"])

        def score_frame(self, need, e):
            base = super().score_frame(need, e)
            return base - 0.5 * e["candidate_id"].isin(self._penalised).to_numpy()

    rep = run_audit(world.candidates, _needs(world), k=3, matcher_factory=Biased)
    assert any(f.startswith("audit_gender") for f in rep.flags)
    assert not rep.counterfactual_invariant


def test_audit_reports_experience_age_proxy(world):
    rep = run_audit(world.candidates, _needs(world), k=5)
    assert rep.proxies["experience_years"]["audit_age_band"] > 0.3


def test_experience_cap_saturates_the_experience_effect():
    from proxsis.models.m5_matching import experience_component

    capped = experience_component(np.array([0, 2, 5, 12, 30]), cap_years=5)
    assert capped[2] == pytest.approx(1.0) and capped[3] == pytest.approx(1.0) and capped[4] == pytest.approx(1.0)
    assert capped[0] == 0.0 and 0 < capped[1] < 1
    default = experience_component(np.array([5, 12]), cap_years=15)
    assert default[0] < default[1] < 1.0


def test_matcher_cap_parameter_changes_scores_only_through_experience(world):
    need = _needs(world, 1)[0]
    base, capped = CandidateMatcher(world.candidates), CandidateMatcher(world.candidates, exp_cap_years=3)
    e = base.eligible(need)
    diff = base.score_frame(need, e) - capped.score_frame(need, e)
    assert np.all(diff <= 1e-12)  # a lower cap can only raise the experience component
    assert np.allclose(diff[e["experience_years"].to_numpy() == 0], 0)


def test_multi_sample_audit_reports_spread(world):
    from proxsis.fairness import run_audit_samples

    rep = run_audit_samples(world.candidates, world.companies, world.weeks[-1], n_needs=40, n_samples=3, k=5)
    age = rep["di_ratio"]["audit_age_band"]
    assert set(age) == {"moyenne", "min", "max", "valeurs"} and len(age["valeurs"]) == 3
    assert age["min"] <= age["moyenne"] <= age["max"]
    assert rep["counterfactual_invariant"] is True


def test_zero_experience_weight_ignores_experience(world):
    need = _needs(world, 1)[0]
    m = CandidateMatcher(world.candidates, exp_weight=0.0)
    e = m.eligible(need)
    e2 = e.assign(experience_years=e["experience_years"] + 10)
    assert np.allclose(m.score_frame(need, e), m.score_frame(need, e2))


def test_multi_sample_audit_reports_mean_selection_per_group(world):
    from proxsis.fairness import run_audit_samples

    rep = run_audit_samples(world.candidates, world.companies, world.weeks[-1], n_needs=40, n_samples=2, k=5)
    rates = rep["taux_selection_moyen"]["audit_age_band"]
    assert set(rates) <= {"18-29", "30-44", "45-54", "55+"} and all(0 <= v <= 1 for v in rates.values())
    assert 0 <= rep["part_tirages_sous_0_8"]["audit_age_band"] <= 1


def test_default_experience_cap_stays_v1_until_adr_0012_is_accepted():
    """Audit M5: ADR-0012 is « proposé » → the code keeps the v1 behaviour (15 years) until Hiba validates."""
    from proxsis.models.m5_matching import DEFAULT_EXP_CAP_YEARS

    assert DEFAULT_EXP_CAP_YEARS == 15.0


def test_audit_samples_can_use_other_seeds_and_report_share_below_threshold_ci(world):
    from proxsis.fairness import run_audit_samples

    a = run_audit_samples(world.candidates, world.companies, world.weeks[-1], n_needs=30, n_samples=3, k=5,
                          seed_offset=100)
    assert a["graines"] == [100, 101, 102]
    lo, hi = a["part_tirages_sous_0_8_ic95"]["audit_age_band"]
    assert 0 <= lo <= a["part_tirages_sous_0_8"]["audit_age_band"] <= hi <= 1


def test_availability_by_age_is_measured(world):
    from proxsis.fairness import availability_by_group

    t = availability_by_group(world.candidates, world.weeks[-1], "audit_age_band")
    assert set(t) <= {"18-29", "30-44", "45-54", "55+"}
    assert all({"n", "jours_moyens", "part_dispo_14j"} <= set(v) for v in t.values())
