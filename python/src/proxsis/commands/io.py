"""Readers shared by the commands (JSON lines, simap records, building permits, places, annotation workflow)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: str) -> list[dict[str, Any]]:

    return [json.loads(x) for x in Path(path).read_text("utf-8").splitlines() if x.strip()]


def workflow_items(args: argparse.Namespace) -> list[dict[str, Any]]:
    from proxsis.manual_collection import load_items

    return read_jsonl(args.items) if args.items else load_items(Path(args.dossier))


def load_simap(files: list[str]) -> list[dict[str, Any]]:
    seen, out = set(), []
    for f in files:
        for r in read_jsonl(f):
            if r["publication_id"] not in seen:
                seen.add(r["publication_id"])
                out.append(r)
    return out


def permits(path: str | None) -> list[dict[str, Any]] | None:
    """Building permits imported from the Bulletin officiel (accepted, persons already masked), if present."""
    if not path or not Path(path).exists():
        return None
    return [r for r in read_jsonl(path) if r.get("statut") == "acceptée"]


def read_places(path: str) -> list[dict[str, Any]]:
    import csv

    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["lat"], r["lon"] = float(r["lat"]), float(r["lon"])
    return rows
