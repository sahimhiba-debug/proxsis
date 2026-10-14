"""Reproducible generation of the model result files in ``docs/modeles``.

``proxsis rapports-modeles`` rewrites every file from the code and the
fixed seeds below; each file carries the mandatory warnings
(:mod:`proxsis.honesty`).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from proxsis.fairness import availability_by_group, run_audit_samples, sample_needs
from proxsis.honesty import mark
from proxsis.models.m5_matching import CandidateMatcher, Need
from proxsis.synth.world import World, WorldConfig, generate_world

FROZEN_V1 = Path(__file__).resolve().parents[3] / "data" / "annotations" / "extraction_v1.jsonl"


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", "utf-8")


def m3_report() -> dict[str, Any]:
    from proxsis.models.m3_extraction import RulesExtractor, evaluate

    r = asdict(evaluate(RulesExtractor(), FROZEN_V1))
    r.pop("latency_s_mean")  # machine-dependent, not reproducible
    r["protocole"] = ("jeu gelé extraction_v1.jsonl : 36 publications FICTIVES rédigées et annotées par l'agent de "
                      "développement ; règles écrites sur un jeu de développement généré par le même agent")
    return mark(r, fictif=True, agent_written_set=True)


def m4_report(w: World) -> dict[str, Any]:
    from proxsis.models.m4_entity_resolution import EntityResolver, ExactNameResolver, benchmark, make_mentions

    mentions = make_mentions(w.companies, 3000, seed=8)
    return mark({
        "protocole": "monde FICTIF seed=42 (4000 entreprises), 3000 mentions bruitées seed=8 (tenues à l'écart ; "
                     "seuils choisis sur seed=7), 20 % d'entreprises inconnues, 35 % avec IDE",
        "M4_flou_auto": benchmark(EntityResolver(w.companies), mentions),
        "M4_flou_auto_plus_revue_acceptee": benchmark(EntityResolver(w.companies), mentions, count_review_as_link=True),
        "base_nom_exact_normalise": benchmark(ExactNameResolver(w.companies), mentions),
    }, fictif=True)


def m6_report(w: World) -> dict[str, Any]:
    from proxsis.models.m6_forecast import evaluate, weekly_series

    s = weekly_series(w.postings, w.companies, w.weeks)
    ev = evaluate(s, w.weeks, first_origin=w.weeks.index(date(2024, 7, 1)), step=4, H=8)
    return mark(asdict(ev) | {
        "protocole": "monde FICTIF seed=42 ; séries hebdomadaires d'offres par famille de métiers x région "
                     "linguistique (8 séries) ; origines glissantes toutes les 4 semaines dès 2024-07-01 ; "
                     "horizons 1-8 semaines"}, fictif=True)


def _quality(candidates: pd.DataFrame, needs: list[Need], factory: Any, ref: dict[str, list[str]] | None,
             k: int) -> tuple[dict[str, float], dict[str, list[str]]]:
    """What the consultant would see: skill, distance, experience of the top-k, and overlap with ``ref``."""
    m = factory(candidates)
    exp = candidates.set_index("candidate_id")["experience_years"]
    picks: dict[str, list[str]] = {}
    skill: list[float] = []
    dist: list[float] = []
    years: list[float] = []
    overlap: list[float] = []
    for i, need in enumerate(needs):
        e = m.eligible(need).set_index("candidate_id")
        sug = m.suggest(need, k)
        ids = [s.candidate_id for s in sug]
        picks[str(i)] = ids
        if not ids:
            continue
        skill.extend(e.loc[ids, "m_skill"])
        dist.extend(s.distance_km for s in sug)
        years.extend(exp.loc[ids])
        if ref is not None and ref[str(i)]:
            overlap.append(len(set(ids) & set(ref[str(i)])) / len(ref[str(i)]))
    q = {"proximite_metier_moyenne": float(np.mean(skill)), "distance_km_moyenne": float(np.mean(dist)),
         "experience_ans_moyenne": float(np.mean(years)),
         "part_metier_exact": float(np.mean(np.array(skill) == 1.0))}
    if ref is not None:
        q["recouvrement_top5_avec_v1"] = float(np.mean(overlap))
    return q, picks


def m5_report(w: World, n_samples: int = 20, n_needs: int = 300, k: int = 5,
              n_confirm: int = 100) -> dict[str, Any]:
    start = w.weeks[-1]
    variants: dict[str, dict[str, Any]] = {
        "plafond 15 ans (v1)": {"exp_cap_years": 15.0}, "plafond 10 ans": {"exp_cap_years": 10.0},
        "plafond 5 ans": {"exp_cap_years": 5.0}, "plafond 3 ans": {"exp_cap_years": 3.0},
        "plafond 1 an (expérience quasi binaire)": {"exp_cap_years": 1.0},
        "sans expérience (poids 0)": {"exp_weight": 0.0},
    }
    q_needs = sample_needs(w.companies, start, n_needs, seed=1000)  # quality sample, apart from audit draws
    # Audit M4: the reference is v1 explicitly (15 years), not whatever the code default is.
    _, ref = _quality(w.candidates, q_needs, partial(CandidateMatcher, exp_cap_years=15.0), None, k)
    out: dict[str, Any] = {}
    for name, params in variants.items():
        factory = partial(CandidateMatcher, **params)
        audit = run_audit_samples(w.candidates, w.companies, start, n_needs, n_samples, k, matcher_factory=factory)
        quality, _ = _quality(w.candidates, q_needs, factory, ref, k)
        out[name] = {"parametres": params, "audit": audit, "qualite_visible": quality}
    # Audit M5: choose on seeds 0..n-1, confirm on other seeds (100..199) — never report on the selection seeds only.
    confirmation = {}
    for name in ("plafond 15 ans (v1)", "plafond 10 ans", "plafond 5 ans"):
        factory = partial(CandidateMatcher, **variants[name])
        a = run_audit_samples(w.candidates, w.companies, start, n_needs, n_confirm, k, matcher_factory=factory,
                              seed_offset=100)
        confirmation[name] = {"parametres": variants[name], "di_ratio_age": a["di_ratio"]["audit_age_band"],
                              "part_tirages_sous_0_8_age": a["part_tirages_sous_0_8"]["audit_age_band"],
                              "part_tirages_sous_0_8_age_ic95": a["part_tirages_sous_0_8_ic95"]["audit_age_band"],
                              "taux_selection_moyen_age": a["taux_selection_moyen"]["audit_age_band"]}
    return mark({
        "confirmation_hors_echantillon": {"graines": [100, 100 + n_confirm - 1], "variantes": confirmation},
        "disponibilite_par_age": availability_by_group(w.candidates, start, "audit_age_band"),
        "protocole": (f"monde FICTIF seed=42, {len(w.candidates)} candidats fictifs ; audit répété sur {n_samples} "
                      f"tirages indépendants de {n_needs} besoins (graines 0..{n_samples - 1}), top-{k} ; qualité "
                      f"visible mesurée sur un tirage séparé de {n_needs} besoins (graine 1000) ; confirmation "
                      f"hors échantillon sur {n_confirm} autres tirages (graines 100..{99 + n_confirm})"),
        "limite": ("aucune vérité terrain : on ne sait pas si un candidat plus expérimenté réussit mieux sa mission. "
                   "Le coût réel du plafond ne se mesure qu'avec l'historique des missions (pilote)."),
        "variantes": out,
    }, fictif=True)


def write_all(out_dir: Path, seed: int = 42) -> list[Path]:
    w = generate_world(WorldConfig(seed=seed))
    files = {
        "m3_resultats_regles_v1.json": m3_report(),
        "m4_resultats_v1.json": m4_report(w),
        "m6_resultats_v1.json": m6_report(w),
        "m5_audit_equite_v3.json": m5_report(w),
    }
    for name, data in files.items():
        _write(out_dir / name, data)
    return [out_dir / n for n in files]
