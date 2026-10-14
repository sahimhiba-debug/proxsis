"""Annotation workflow of a real test set whose texts must stay out of git.

1. :func:`prepare` — assignment (20 items in blind double annotation) written
   publicly (ids only); one page per annotator written privately (texts).
2. :func:`agreement_step` — splits each annotator export into primary and
   second annotations (from the assignment), computes the field-by-field
   agreement and reliability (public, no text) and an arbitration page for the
   disagreements (private).
3. :func:`freeze_step` — reference = primary annotations, with arbitration on
   the disagreements; frozen privately (texts) and publicly (hashes), both
   registered in FROZEN.md, **before any measurement**.

The annotation profile (fields asked and compared, see
``annotation_agreement.PROFILES``) is chosen at step 1, recorded in
``repartition.json`` and reused by steps 2 and 3: French and German lots are
assigned, measured and frozen separately.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from proxsis.annotation_agreement import (
    DEFAULT_PROFILE,
    agreement,
    assign,
    compared_fields,
    freeze_private,
    merge_gold_partial,
    reliability,
)
from proxsis.annotation_page import build_page

TITLES = {DEFAULT_PROFILE: "Annotation — jeu réel", "bo_fr": "Annotation — Bulletin officiel, français",
          "bo_de_structure": "Annotation — Bulletin officiel, lot allemand (champs structurés)"}


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in path.read_text("utf-8").splitlines() if x.strip()]


def profile_of(repartition: Path) -> str:
    """Profile recorded at assignment time (an assignment written before profiles existed is the default one)."""
    profile = str(json.loads(repartition.read_text("utf-8")).get("profil", DEFAULT_PROFILE))
    compared_fields(profile)  # unknown profile → error
    return profile


def prepare(items: list[dict[str, Any]], annotators: list[str], public_dir: Path, private_dir: Path,
            n_double: int = 20, seed: int = 20261005,
            profile: str = DEFAULT_PROFILE) -> dict[str, dict[str, str | None]]:
    compared_fields(profile)  # unknown profile → error, before anything is written
    rep = assign(items, annotators, n_double=n_double, seed=seed)  # who annotates what: independent of the profile
    public_dir.mkdir(parents=True, exist_ok=True)
    (public_dir / "repartition.json").write_text(json.dumps(
        {"graine": seed, "double_annotation": n_double, "annotateurs": annotators, "profil": profile, "items": rep},
        ensure_ascii=False, indent=1) + "\n", "utf-8")
    pages = private_dir / "pages"
    pages.mkdir(parents=True, exist_ok=True)
    by_id = {it["id"]: it for it in items}
    for who in annotators:
        mine = [by_id[i] for i, a in rep.items() if who in (a["primaire"], a["second"])]
        page_items = [{k: v for k, v in it.items() if k not in ("collecteur", "strate")} for it in mine]
        (pages / f"annotation_{who}.html").write_text(
            build_page(page_items, title=f"{TITLES[profile]} ({who}, {len(mine)} publications)", profile=profile),
            "utf-8")
    return rep


def _split(exports: list[Path], repartition: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rep = json.loads(repartition.read_text("utf-8"))["items"]
    primary, second = [], []
    for f in exports:
        for r in _read(f):
            a = rep.get(r["id"])
            if a is None:
                continue
            if r.get("annotateur") == a["primaire"]:
                primary.append(r)
            elif r.get("annotateur") == a["second"]:
                second.append(r)
    return primary, second


def agreement_step(exports: list[Path], repartition: Path, items: list[dict[str, Any]], public_dir: Path,
                   private_dir: Path) -> dict[str, Any]:
    profile = profile_of(repartition)
    primary, second = _split(exports, repartition)
    doubles = {r["id"] for r in second}
    rep, dis = agreement([r for r in primary if r["id"] in doubles], second, profile=profile)
    rel = reliability(rep)
    (public_dir / "accord.json").write_text(json.dumps(rep | {"fiabilite": rel}, ensure_ascii=False, indent=1)
                                            + "\n", "utf-8")
    with (public_dir / "desaccords.jsonl").open("w", encoding="utf-8") as fh:
        for d in dis:
            fh.write(json.dumps({"id": d["id"], "champs": d["champs"]}, ensure_ascii=False) + "\n")
    by_id = {it["id"]: it for it in items}
    arb = [{k: v for k, v in by_id[d["id"]].items() if k not in ("collecteur", "strate")} for d in dis]
    (private_dir / "pages").mkdir(parents=True, exist_ok=True)
    (private_dir / "pages" / "arbitrage.html").write_text(
        build_page(arb, title=f"Arbitrage — {len(arb)} désaccords", profile=profile), "utf-8")
    return rep


def freeze_step(exports: list[Path], repartition: Path, items: list[dict[str, Any]], arbitration: Path | None,
                public_dir: Path, private_dir: Path, frozen_md: Path, name: str) -> dict[str, Any]:
    profile = profile_of(repartition)
    primary, second = _split(exports, repartition)
    gold = merge_gold_partial(primary, second, _read(arbitration) if arbitration else [], profile=profile)
    missing = {it["id"] for it in items} - {g["id"] for g in gold}
    if missing:
        raise ValueError(f"{len(missing)} publications sans annotation principale : {sorted(missing)[:5]}…")
    priv, pub, sha_priv, sha_pub = freeze_private(
        items, gold, private_dir / f"{name}.jsonl", public_dir / f"{name}_reference.jsonl", frozen_md,
        note=f"{len(gold)} publications RÉELLES ; {sum(g['double_annotation'] for g in gold)} en double "
             f"annotation + arbitrage ; profil {profile} ; textes hors git")
    return {"prive": priv, "public": pub, "sha_prive": sha_priv, "sha_public": sha_pub, "n": len(gold),
            "profil": profile}
