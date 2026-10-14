from datetime import timedelta

import numpy as np
import pytest

from proxsis.entities import uid_is_valid
from proxsis.schema import Company, Signal, validate_frame
from proxsis.synth.world import WorldConfig, generate_world


@pytest.fixture(scope="module")
def world():
    return generate_world(WorldConfig(seed=7, n_companies=300, n_candidates=100))


def test_deterministic_with_seed():
    cfg = WorldConfig(seed=3, n_companies=80, n_candidates=10)
    a, b = generate_world(cfg), generate_world(cfg)
    assert a.companies.equals(b.companies)
    assert a.signals.equals(b.signals)
    assert a.postings.equals(b.postings)


def test_everything_is_marked_fictional(world):
    for df in (
        world.companies,
        world.signals,
        world.postings,
        world.waves,
        world.agencies,
        world.consultants,
        world.candidates,
    ):
        assert df["fictif"].all()
    assert world.agencies["name"].str.contains("FICTIF").all()
    assert world.consultants["display_name"].str.contains("FICTIF").all()


def test_uids_valid_and_unique(world):
    assert world.companies["uid"].map(uid_is_valid).all()
    assert world.companies["uid"].is_unique


def test_signals_respect_publication_order(world):
    s = world.signals
    assert (s["available_at"] >= s["event_date"]).all()
    assert s["family"].isin(["marche_attribue", "permis_construire", "mutation_rc"]).all()


def test_private_permits_have_no_company(world):
    s = world.signals
    priv = s[s.get("applicant_private").fillna(False).astype(bool)]
    assert len(priv) > 0
    assert priv["company_id"].isna().all()


def test_schema_contracts(world):
    comp = world.companies.drop(columns=["created_week", "liquidated_week", "agency_id", "employees_true"])
    comp = comp.assign(retrieved_at="2026-10-04T00:00:00+00:00")
    assert validate_frame(comp, Company, max_rows=200) == []
    sig = world.signals.drop(columns=[c for c in ("expected_start", "applicant_private") if c in world.signals])
    sig = sig.assign(
        retrieved_at="2026-10-04T00:00:00+00:00",
        trades=sig["trades"].fillna("").map(lambda t: [x for x in t.split(";") if x]),
    )
    assert validate_frame(sig, Signal, max_rows=300) == []


def test_postings_within_horizon(world):
    end = world.config.end + timedelta(days=6)
    assert (world.postings["available_at"] <= end).all()
    assert (world.signals["available_at"] <= end).all()


def test_no_hiring_before_creation(world):
    c = world.companies
    new = c[c["created_week"] >= 0].set_index("company_id")
    w = world.waves.merge(new[["created_week"]], left_on="company_id", right_index=True)
    weeks = {d: i for i, d in enumerate(world.weeks)}
    assert all(weeks[row.week] > row.created_week for row in w.itertuples())


def test_every_company_has_an_agency(world):
    assert world.companies["agency_id"].isin(world.agencies["agency_id"]).all()


def _signal_driven_share(cfg):
    w = generate_world(cfg)
    return w.waves["signal_driven"].mean(), len(w.waves)


def test_null_world_keeps_signals_but_removes_effect():
    base = WorldConfig(seed=11, n_companies=200, n_candidates=10)
    null = WorldConfig(seed=11, n_companies=200, n_candidates=10, signal_effect=0.0)
    w1, w0 = generate_world(base), generate_world(null)
    # Mêmes signaux publics (même graine, mêmes tirages de signaux)
    assert len(w1.signals) == len(w0.signals)
    # Moins de vagues d'embauche dans le monde nul (pas de surcroît causé par les projets)
    assert len(w0.waves) < len(w1.waves)
    assert np.isfinite(len(w0.postings))
