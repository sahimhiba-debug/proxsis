"""Rules vs Apertus on the frozen REAL test set (step 5 of the 2026-10-05 brief).

The comparison refuses to run on a file whose SHA-256 is not registered in
``data/annotations/FROZEN.md``: the set must be frozen before any measurement.
Personal-data leaks on real texts are detected by patterns (masked
placeholders copied into an output, civility + name, e-mail, phone), since the
real private names were removed before storage and are unknown to us.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from proxsis.honesty import mark
from proxsis.models.m3_extraction import evaluate

_LEAK = re.compile(r"\[masqué\]|\[particulier\]|\b(?:M\.|Mme|Herr|Frau)\s+[A-ZÀ-Ý][a-zà-ÿ]+|[\w.+-]+@[\w-]+\.\w+|"
                   r"(?:\+41|\b0)\d{2}\s?\d{3}\s?\d{2}\s?\d{2}\b")


class NotFrozenError(RuntimeError):
    """The test set is not registered in FROZEN.md: no measurement allowed."""


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class _Cached:
    """Each text is sent once to the extractor (an LLM call costs time and quota)."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.name = getattr(inner, "name", type(inner).__name__)
        self._memo: dict[str, dict[str, Any]] = {}

    def extract(self, text: str) -> dict[str, Any]:
        if text not in self._memo:
            self._memo[text] = self.inner.extract(text)
        return self._memo[text]


def _leaks(extractor: Any, rows: list[dict[str, Any]]) -> int:
    n = 0
    for r in rows:
        out = extractor.extract(r["text"])
        n += bool(_LEAK.search(json.dumps({k: v for k, v in out.items() if k != "private_person"},
                                          ensure_ascii=False)))
    return n


def compare(frozen: Path, frozen_md: Path, extractors: list[Any], pause_s: float = 0.0,
            donnees: str = "RÉEL", reliability: dict[str, Any] | None = None) -> dict[str, Any]:
    """``reliability`` (from :func:`proxsis.annotation_agreement.reliability`): fields on which the two human
    annotators did not agree are listed per extractor in ``champs_a_prendre_avec_precaution``."""
    sha = _sha(frozen)
    md = frozen_md.read_text("utf-8")
    if sha not in md:
        raise NotFrozenError(f"{frozen.name} (sha256 {sha[:12]}…) n'est pas inscrit dans {frozen_md.name}")
    line = next(x for x in md.splitlines() if sha in x)
    if "FICTI" in line.upper():  # audit m17: the data type is read from the register, not guessed from the name
        donnees = "FICTIF-AGENT"
    rows = [json.loads(x) for x in frozen.read_text("utf-8").splitlines() if x.strip()]
    out: dict[str, Any] = {"donnees": donnees, "jeu": {"fichier": frozen.name, "sha256": sha, "n": len(rows),
                                                       "langues": sorted({r.get("lang") for r in rows})},
                           "extracteurs": {}}
    for raw in extractors:
        ex = _Cached(raw)
        t0 = time.perf_counter()
        rep = asdict(evaluate(ex, frozen, private_names=["[masqué]", "[particulier]"]))
        rep["pii_leaks"] = _leaks(ex, rows)
        rep["duree_totale_s"] = round(time.perf_counter() - t0, 1)
        if reliability is not None:
            scored = set(rep["field_accuracy"]) | {"trades"}
            rep["champs_a_prendre_avec_precaution"] = sorted(
                f for f, v in reliability.items() if f in scored and not v.get("fiable", False))
        out["extracteurs"][ex.name] = rep
        if pause_s:
            time.sleep(pause_s)
    if reliability is not None:
        out["fiabilite_humaine"] = reliability
    if donnees != "RÉEL":
        out = mark(out, fictif=True, agent_written_set=donnees == "FICTIF-AGENT")
    return out
