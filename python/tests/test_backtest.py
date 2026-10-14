import pytest

from proxsis.backtest import BacktestConfig, run_backtest
from proxsis.synth.world import WorldConfig, generate_world

FAST = BacktestConfig(
    n_boot=200, models=("hasard", "plus_grosses", "activite_recente", "M0_regles", "M1_boosting"), retrain_every=8
)


@pytest.fixture(scope="module")
def result():
    w = generate_world(WorldConfig(seed=21, n_companies=900, n_candidates=10))
    return run_backtest(w.companies, w.signals, w.postings, w.weeks, FAST, truth_waves=w.waves)


def test_summary_has_all_models_and_cis(result):
    for m in FAST.models:
        e = result.summary[m]
        lo, hi = e["p_at_k_agency_cd"]["ci95"]
        assert lo <= e["p_at_k_agency_cd"]["mean"] <= hi


def test_random_matches_base_rate(result):
    r = result.summary["hasard"]
    lo, hi = r["p_at_k_agency"]["ci95"]
    base = r["base_rate"]["mean"]
    assert lo - 0.02 <= base <= hi + 0.02


def test_operational_lists_respect_cooldown(result):
    pw = result.per_week
    assert {"p_at_k_agency_cd", "recall_agency_cd"} <= set(pw.columns)


def test_m1_tuning_uses_only_pre_evaluation_data(result):
    t = result.extras["m1_tuning"]
    eval_start_idx = 78  # 2024-07-01 relative to 2023-01-02
    assert t["validation"][1] <= eval_start_idx - FAST.horizon_weeks


@pytest.mark.slow
def test_null_world_no_model_beats_best_baseline_significantly():
    """Monde nul : les signaux n'ont aucun effet causal. Un modèle qui battrait
    nettement la meilleure méthode naïve trahirait une fuite d'information."""
    w = generate_world(WorldConfig(seed=22, n_companies=1500, n_candidates=10, signal_effect=0.0))
    r = run_backtest(w.companies, w.signals, w.postings, w.weeks, FAST)
    best = r.summary["_best_baseline"]
    for m in ("M0_regles", "M1_boosting"):
        d = r.summary[m][f"diff_vs_{best}_p_at_k_agency_cd"]
        # La borne basse de l'IC à 95 % de l'écart ne doit pas être nettement positive.
        assert d["ci95"][0] < 0.01, (m, d)
