"""Persist a FICTIONAL world snapshot (CSV + manifest with hashes)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from proxsis.synth.world import World


def save_world(w: World, root: Path) -> Path:
    d = root / f"seed{w.config.seed}_{w.config.fingerprint()}"
    d.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in ("companies", "signals", "postings", "waves", "agencies", "consultants", "candidates"):
        df = getattr(w, name)
        p = d / f"{name}.csv"
        df.to_csv(p, index=False)
        files[name] = {"rows": len(df), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    manifest = {
        "FICTIF": True,
        "avertissement": "Données inventées — jamais présentées comme réelles",
        "config": asdict(w.config),
        "fingerprint": w.config.fingerprint(),
        "files": files,
    }
    (d / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1, default=str), "utf-8")
    return d
