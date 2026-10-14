"""No personal data in what the repository publishes: EVERY data file tracked by git (JSON, JSON lines, and the JSON
embedded in an HTML page), whatever command wrote it, passes the same sweep as the exports (``demo_export.pii_sweep``).
The files are enumerated from git, not listed by hand (review 1, I3); the few exceptions below say why."""

import json
import re
import subprocess
from pathlib import Path

import pytest

from proxsis.demo_export import pii_sweep

ROOT = Path(__file__).resolve().parents[2]
EXCEPTIONS = {
    "apps/web/src/data/presentation/communes_vs.json": "contours des communes : noms officiels et géométrie",
    "data/annotations/extraction_v1.jsonl": "jeu de test FICTIF (noms inventés exprès pour tester la détection)",
}
TOOLING = (".claude/", ".mcp.json", "python/tests/fixtures/", "apps/web/package", "apps/web/tsconfig", "apps/web/knip",
           "scripts/production/domaines.json", "apps/web/perf-budget.json")


def _tracked_data_files() -> list[str]:
    listing = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True)
    if listing.returncode != 0:  # an archive or a copy: what the repository publishes is a question for a clone
        pytest.skip("pas un dépôt git : le balayage porte sur les fichiers suivis par git", allow_module_level=True)
    files = listing.stdout.split()
    return sorted(f for f in files if f.endswith((".json", ".jsonl", ".html")) and not f.startswith(TOOLING)
                  and not f.startswith("apps/web/e2e/"))


def _read(path: Path) -> object:
    text = path.read_text("utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if path.suffix == ".html":  # the data a page carries (annotation pages)
        return [json.loads(block) for block in re.findall(r'<script id="items"[^>]*>(.*?)</script>', text, re.S)]
    return json.loads(text)


PUBLIC_FILES = [f for f in _tracked_data_files() if f not in EXCEPTIONS]


@pytest.mark.parametrize("rel", PUBLIC_FILES)
def test_public_file_has_no_personal_data(rel: str) -> None:
    assert pii_sweep(_read(ROOT / rel)) == []


def test_every_published_kind_of_file_is_swept() -> None:
    swept = set(PUBLIC_FILES)
    assert sum(f.startswith("apps/web/src/data/") for f in swept) >= 15  # demo (11), presentation (3), live week (1)
    assert {"apps/annotation/index.html", "data/annotations/reel_v2/a_annoter.jsonl",
            "data/terrain/liste_2026-10-05_batiment.json", "data/manuel/import_pdf/publications.jsonl"} <= swept
    assert set(EXCEPTIONS) <= set(_tracked_data_files())  # an exception that no longer exists is removed here


def test_the_fictional_test_set_is_entirely_fictional() -> None:
    rows = _read(ROOT / "data/annotations/extraction_v1.jsonl")
    assert isinstance(rows, list) and rows and all(r.get("fictif") is True for r in rows)


def test_the_sweep_is_not_a_sieve() -> None:
    record = {"adjudicateur": "Exemple Jean", "titre": "Chalet, Monsieur Jean Exemple, domicilié à Sion"}
    assert {h["chemin"] for h in pii_sweep(record)} >= {".adjudicateur", ".titre"}
