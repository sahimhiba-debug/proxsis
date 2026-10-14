import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FROZEN = {"data/annotations/extraction_v1.jsonl": "c40a6c45ab58a2db87b334974dfca3e2d8be2d4d23c51b775408732e9b542cd6"}


def test_frozen_files_unchanged():
    for rel, sha in FROZEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == sha, f"{rel} a été modifié après gel"


def test_extraction_set_is_fictional_and_balanced():
    rows = [
        json.loads(line) for line in (ROOT / "data/annotations/extraction_v1.jsonl").read_text("utf-8").splitlines()
    ]
    assert len(rows) == 36
    assert all(r["fictif"] for r in rows)
    assert sum(r["lang"] == "fr" for r in rows) == 18
    assert {r["doc_type"] for r in rows} == {"permis_construire", "adjudication", "registre_commerce"}


def test_every_set_registered_in_frozen_md_is_unchanged_when_present():
    """Audit M8: every file registered in FROZEN.md (simap, manual set, private or public) keeps its hash. A private
    file (texts out of git) is checked on the machines that have it."""
    import re

    md = (ROOT / "data/annotations/FROZEN.md").read_text("utf-8")
    rows = re.findall(r"^\| `([^`]+)`[^|]*\| `([0-9a-f]{64})` \|", md, re.M)
    assert rows
    search = [ROOT / "data/annotations", ROOT / "data/manuel/annotation", ROOT / "data/manuel/textes"]
    for name, sha in rows:
        for d in search:
            f = d / name
            if f.exists():
                assert hashlib.sha256(f.read_bytes()).hexdigest() == sha, f"{f} a été modifié après gel"
