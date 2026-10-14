"""Reproducible backtest suite: main run, alternative targets, null world,
sensitivity analyses and seed variability. Writes JSON + Markdown."""

from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import lightgbm
import numpy as np
import pandas as pd
import sklearn

from proxsis import __version__
from proxsis.backtest import BacktestConfig, BacktestResult, run_backtest
from proxsis.honesty import FICTIF_WARNING
from proxsis.report import calibration_table, language_table, main_table, ranking_table, variants_table
from proxsis.synth.world import World, WorldConfig, generate_world


def _git_rev() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "inconnu"


def snapshot_hash(w: World) -> str:
    import hashlib

    h = hashlib.sha256()
    for df in (w.companies, w.signals, w.postings):
        h.update(pd.util.hash_pandas_object(df.astype(str), index=False).to_numpy().tobytes())
    return h.hexdigest()[:16]


def _pack(r: BacktestResult, w: World) -> dict[str, Any]:
    return {
        "config": r.config,
        "world": asdict(w.config) | {"fingerprint": w.config.fingerprint(), "snapshot_sha256_16": snapshot_hash(w)},
        "summary": r.summary,
        "calibration": r.calibration,
        "extras": r.extras,
    }


_CODE_FILES = ("backtest.py", "features.py", "targets.py", "metrics.py", "models", "synth")
CACHE_DIR = Path(__file__).resolve().parents[2] / ".cache" / "backtest"


def _code_hash() -> str:
    import hashlib

    h = hashlib.sha256()
    root = Path(__file__).resolve().parent
    for name in _CODE_FILES:
        p = root / name
        files = sorted(p.rglob("*.py")) if p.is_dir() else [p]
        for f in files:
            h.update(f.read_bytes())
    return h.hexdigest()[:12]


def _checkpointed(
    wc: WorldConfig, bc: BacktestConfig, with_truth: bool, log: Any
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Run (or reload) one backtest. Checkpoints survive interruptions; the key covers the
    world config, the backtest config and the source code of the engine."""
    import hashlib

    key = hashlib.sha256(
        json.dumps([asdict(wc), asdict(bc), with_truth, _code_hash()], default=str, sort_keys=True).encode()
    ).hexdigest()[:20]
    jp, cp = CACHE_DIR / f"{key}.json", CACHE_DIR / f"{key}.csv"
    if jp.exists() and cp.exists():
        log("     (reprise depuis le point de contrôle)")
        return json.loads(jp.read_text("utf-8")), pd.read_csv(cp)
    w = generate_world(wc)
    r = run_backtest(w.companies, w.signals, w.postings, w.weeks, bc, truth_waves=w.waves if with_truth else None)
    packed = json.loads(json.dumps(_pack(r, w), default=str))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    jp.write_text(json.dumps(packed, ensure_ascii=False), "utf-8")
    r.per_week.to_csv(cp, index=False)
    return packed, r.per_week


def run_suite(seed: int = 42, quick: bool = False, verbose: bool = True) -> dict[str, Any]:
    n = 1500 if quick else 4000
    n_boot = 300 if quick else 2000
    base_w = WorldConfig(seed=seed, n_companies=n, n_candidates=10)
    base_b = BacktestConfig(seed=seed, n_boot=n_boot)
    out: dict[str, Any] = {
        "meta": {
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "proxsis_version": __version__,
            "git": _git_rev(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "lightgbm": lightgbm.__version__,
            "sklearn": sklearn.__version__,
            "quick": quick,
            "avertissement": FICTIF_WARNING,
            "precision_avertissement": "Monde FICTIF simulé : ces chiffres valident la mécanique (absence de fuite, "
            "capacité à retrouver un signal), pas la valeur commerciale réelle.",
        },
        "variants": {},
    }

    def log(msg: str) -> None:
        if verbose:
            print(msg, flush=True)

    log("[1/4] run principal")
    out["main"], out["_per_week_main"] = _checkpointed(base_w, base_b, True, log)

    log("[2/4] cibles alternatives")
    for tgt in ("offre_8s", "offre_batiment_8s"):
        log(f"   - {tgt}")
        out["variants"][f"cible={tgt}"], _ = _checkpointed(base_w, replace(base_b, target=tgt), False, log)

    log("[3/4] monde nul et sensibilité")
    variants = {
        "monde nul (signal_effect=0)": replace(base_w, signal_effect=0.0),
        "signal_effect=0.5": replace(base_w, signal_effect=0.5),
        "signal_effect=2": replace(base_w, signal_effect=2.0),
        "p_post=0.4 (moins d'offres publiées)": replace(base_w, p_post=0.4),
        "taille observée sans bruit": replace(base_w, size_noise_sigma=0.0),
    }
    for name, wc in variants.items():
        log(f"   - {name}")
        out["variants"][name], _ = _checkpointed(wc, base_b, False, log)

    log("[4/4] variabilité entre mondes (graines)")
    for sd in (seed + 1, seed + 2):
        log(f"   - graine {sd}")
        out["variants"][f"graine={sd}"], _ = _checkpointed(
            replace(base_w, seed=sd), replace(base_b, seed=sd), False, log
        )
    return out


def render_markdown(res: dict[str, Any]) -> str:
    m = res["main"]
    s = m["summary"]
    best = s["_best_baseline"]
    ex = m["extras"]
    d1 = s["M1_boosting"][f"diff_vs_{best}_p_at_k_agency_cd"]
    d0 = s["M0_regles"][f"diff_vs_{best}_p_at_k_agency_cd"]
    null = res["variants"].get("monde nul (signal_effect=0)", {}).get("summary", {})
    null_best = null.get("_best_baseline")
    null_d1 = null.get("M1_boosting", {}).get(f"diff_vs_{null_best}_p_at_k_agency_cd") if null else None
    lv = ex.get("m0_levels", {})
    tn = ex.get("temp_need_precision_agency", {})
    verdict_m1 = "bat" if d1["ci95"][0] > 0 else "ne bat pas de façon significative"
    verdict_m0 = "bat" if d0["ci95"][0] > 0 else "ne bat pas"
    return (
        f"""# Rapport de backtest — Proxsis (monde FICTIF)

> **{FICTIF_WARNING[0].upper() + FICTIF_WARNING[1:]}.**

> **À lire d'abord.** Les données internes de Flexsis et les sources publiques ne sont pas
> accessibles depuis l'environnement de développement (voir les notes de travail). Ce backtest
> tourne sur un **monde FICTIF simulé** (`proxsis.synth.world`), avec des paramètres écrits
> à l'avance. Il prouve que la **mécanique** est saine (pas de fuite d'information du futur,
> capacité à retrouver un signal quand il existe, comparaison honnête aux méthodes naïves).
> Il ne prouve **pas** que la méthode marche sur le marché réel : c'est le rôle du pilote
> (`docs/affaires/pilote.md`). Le même code tournera sur les données réelles dès que les
> sources seront branchées.

Généré le {res["meta"]["generated_at"]} — commit `{res["meta"]["git"]}` — graine {m["world"]["seed"]} —
empreinte du monde `{m["world"]["fingerprint"]}` — instantané `{m["world"]["snapshot_sha256_16"]}`.
Reproduire : `make backtest` (ou `proxsis backtest --seed {m["world"]["seed"]}`).

## 1. Protocole

- **Monde** : {m["world"]["n_companies"]} entreprises FICTIVES (FR et DE), {ex["n_eval_weeks"]} semaines
  d'évaluation ({ex["eval_period"][0]} → {ex["eval_period"][1]}), 16 agences fictives.
- **Cible principale** `{m["config"]["target"]}` : l'entreprise publie une offre d'emploi dans les
  {m["config"]["horizon_weeks"]} semaines **alors qu'elle n'en avait publié aucune** dans les
  {m["config"]["horizon_weeks"]} semaines précédentes (un nouveau besoin, que le consultant ne peut pas
  voir dans une annonce existante). Définitions et limites : `docs/backtest/cibles.md`.
- **Vu à la date T** : chaque semaine T, seules les informations publiées avant T sont utilisées
  (test structurel `tests/test_features_targets.py::test_no_leakage...`). Les modèles appris sont
  réentraînés toutes les {m["config"]["retrain_every"]} semaines sur des exemples dont la cible est
  connue avant T (embargo d'un horizon). Les hyperparamètres de M1 sont choisis sur une période de
  validation **antérieure** à l'évaluation (choix : `{ex.get("m1_tuning", {}).get("choix")}`).
- **Listes** : chaque agence reçoit chaque semaine une liste de {m["config"]["k_agency"]} entreprises.
  Liste **opérationnelle** : une entreprise déjà proposée n'est pas reproposée pendant
  {m["config"]["cooldown_weeks"]} semaines (même nombre d'appels distincts pour toutes les méthodes).
- **Méthodes naïves** : hasard, plus grosses entreprises (taille estimée, bruitée), activité récente.
- **Intervalles** : bootstrap par blocs de semaines ({m["config"]["n_boot"]} tirages), IC à 95 %.

## 2. Résultats principaux

{main_table(s)}

Taux de base (part des entreprises éligibles qui réalisent la cible) : {_p(s["hasard"]["base_rate"]["mean"])}.
Meilleure méthode naïve : **{best}**.

- **M1 {verdict_m1}** la meilleure méthode naïve : écart de P@10 opérationnelle
  {_pts(d1)}.
- **M0 {verdict_m0}** la meilleure méthode naïve : écart {_pts(d0)}.
- Les jours d'avance mesurent le délai entre la **première** apparition de l'entreprise dans la liste
  de son agence et la publication de l'offre (épisodes détectés seulement).

### Classement pur (sans délai de relance)

{ranking_table(s)}

### Niveaux d'alerte de M0 (calibration des niveaux)

| Niveau | Nombre d'entreprises-semaines | Taux de réalisation |
|---|---|---|
"""
        + "\n".join(f"| {k} | {v['n']} | {_p(v['taux_realisation'])} |" for k, v in lv.items())
        + f"""

### Calibration des probabilités

{calibration_table(m["calibration"])}

### Couverture par langue

{language_table(s)}

### Besoin réel de personnel temporaire (mesurable seulement dans le monde FICTIF)

Précision des listes d'agence sur le **besoin latent** (vague d'embauche avec besoin de temporaires),
taux de base {_p(ex.get("temp_need_base_rate"))} :
"""
        + "\n".join(f"- {k} : {_p(v)}" for k, v in tn.items())
        + f"""

## 3. Monde nul, sensibilité et variabilité

{variants_table(res["variants"])}

- **Monde nul** : les signaux sont générés à l'identique mais n'ont aucun effet causal. Écart M1 vs
  meilleure naïve : {_pts(null_d1) if null_d1 else "—"}. Un écart nettement positif trahirait une fuite ;
  ce contrôle est aussi un test automatique (`test_null_world_no_model_beats_best_baseline_significantly`).
- Les variantes `signal_effect` montrent comment le gain dépend de la force réelle — inconnue — du lien
  entre signaux publics et embauches. **C'est précisément ce que le pilote doit mesurer.**

## 4. Ce qui ne marche pas ou reste fragile (échecs compris)

"""
        + _fragilities(s, best, d1, d0, lv, ex)
        + """
- La cible « offre publiée » n'est qu'un indicateur du besoin : toutes les vagues d'embauche ne donnent
  pas d'offre publique, et la précision sur le besoin latent est plus basse.
- L'auteur du générateur a aussi écrit les modèles : le monde fictif reflète nos hypothèses. Seules les
  données réelles et le pilote trancheront.

## 5. Importance des familles de signaux (M1, gain)

"""
        + "\n".join(f"- {k} : {v}" for k, v in ex.get("m1_importance", {}).items())
        + "\n"
    )


def _fragilities(
    s: dict[str, Any], best: str, d1: dict[str, Any], d0: dict[str, Any], lv: dict[str, Any], ex: dict[str, Any]
) -> str:
    out = []
    gain = 100 * d1["mean"]
    if d1["ci95"][0] <= 0:
        out.append("- M1 **ne bat pas** significativement la meilleure méthode naïve sur ce monde.")
    elif gain < 5:
        out.append(f"- Le gain de M1 sur la meilleure méthode naïve est **modeste** ({gain:+.1f} pts de P@10).")
    imp = ex.get("m1_importance", {})
    if imp:
        top = max(imp, key=lambda k: imp[k])
        out.append(
            f"- La famille la plus utilisée par M1 est `{top}` "
            f"({100 * imp[top] / max(1e-9, sum(imp.values())):.0f} % du gain total)."
        )
    if d0["ci95"][1] < 0:
        out.append(
            "- Les règles M0, écrites sans réglage, font **moins bien** que la meilleure méthode naïve en "
            "précision ; leur intérêt est l'explication."
        )
    rates = [lv.get(k, {}).get("taux_realisation") for k in ("rouge", "orange", "jaune", "aucun")]
    if all(r is not None for r in rates):
        ordered = all(rates[i] >= rates[i + 1] for i in range(3))
        out.append(
            "- Les niveaux d'alerte de M0 sont "
            + (
                "**ordonnés** (rouge ≥ orange ≥ jaune ≥ aucun)."
                if ordered
                else "**mal ordonnés** : ne pas les afficher tels quels."
            )
        )
    return "\n".join(out) + "\n"


def _p(x: float | None) -> str:
    return "—" if x is None else f"{100 * x:.1f} %"


def _pts(e: dict[str, Any]) -> str:
    lo, hi = e["ci95"]
    return f"{100 * e['mean']:+.1f} pts [IC95 {100 * lo:+.1f} ; {100 * hi:+.1f}]"


def write_outputs(res: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    pw = res.pop("_per_week_main", None)
    if pw is not None:
        pw.to_csv(json_path.with_name("par_semaine.csv"), index=False, float_format="%.4f")
    json_path.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), "utf-8")
    md_path.write_text(render_markdown(res), "utf-8")
