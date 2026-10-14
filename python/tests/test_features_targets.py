from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from proxsis.features import PanelBuilder
from proxsis.synth.world import WorldConfig, generate_world
from proxsis.targets import build_labels


@pytest.fixture(scope="module")
def world():
    return generate_world(WorldConfig(seed=5, n_companies=250, n_candidates=10))


def test_no_leakage_features_identical_when_future_removed(world):
    """Les caractéristiques à la date T ne changent pas si on supprime tout ce qui
    est publié à partir de T : preuve structurelle d'absence de fuite."""
    cutoff = 120
    T = world.weeks[cutoff]
    full = PanelBuilder(world.companies, world.signals, world.postings, world.weeks).build([cutoff]).frame
    sig_past = world.signals[world.signals["available_at"] < T]
    post_past = world.postings[world.postings["available_at"] < T]
    past = PanelBuilder(world.companies, sig_past, post_past, world.weeks).build([cutoff]).frame
    pd.testing.assert_frame_equal(full, past)


def test_feature_changes_when_past_changes(world):
    """Contre-épreuve : retirer une donnée passée change bien les caractéristiques."""
    cutoff = 120
    T = world.weeks[cutoff]
    full = PanelBuilder(world.companies, world.signals, world.postings, world.weeks).build([cutoff]).frame
    post_cut = world.postings[world.postings["available_at"] < T - timedelta(days=21)]
    other = PanelBuilder(world.companies, world.signals, post_cut, world.weeks).build([cutoff]).frame
    assert not full["post_8w"].equals(other["post_8w"])


def test_window_counts_match_naive_computation(world):
    cutoff = 100
    T = world.weeks[cutoff]
    panel = PanelBuilder(world.companies, world.signals, world.postings, world.weeks).build([cutoff]).frame
    p = world.postings
    naive = p[(p["available_at"] < T) & (p["available_at"] >= T - timedelta(weeks=8))].groupby("company_id").size()
    got = panel.set_index("company_id")["post_8w"]
    for cid, n in naive.items():
        assert got[cid] == n


def test_labels_match_naive_computation(world):
    cutoffs = [60, 100]
    lab = build_labels(world.companies, world.postings, world.weeks, cutoffs)
    N = len(world.companies)
    p = world.postings
    for k, cutoff in enumerate(cutoffs):
        T = world.weeks[cutoff]
        fut = set(p[(p["available_at"] >= T) & (p["available_at"] < T + timedelta(days=56))]["company_id"])
        prior = set(p[(p["available_at"] < T) & (p["available_at"] >= T - timedelta(days=56))]["company_id"])
        y = lab.y["offre_8s"][k * N : (k + 1) * N]
        yb = lab.y["nouveau_besoin_8s"][k * N : (k + 1) * N]
        for i, cid in enumerate(world.companies["company_id"]):
            assert y[i] == int(cid in fut)
            assert yb[i] == int(cid in fut and cid not in prior)


def test_lead_days_within_horizon(world):
    lab = build_labels(world.companies, world.postings, world.weeks, [80, 90])
    ld = lab.lead_days[~np.isnan(lab.lead_days)]
    assert (ld >= 0).all() and (ld < 56).all()
    assert np.isnan(lab.lead_days[lab.y["offre_8s"] == 0]).all()
