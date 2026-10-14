"""Week-1 reports are generated from the committed JSON (every figure from a command)."""

import re
from pathlib import Path

from proxsis.docs_week1 import write_all

ROOT = Path(__file__).resolve().parents[2]


def test_reports_regenerate_from_the_committed_json(tmp_path):
    import shutil

    for rel in ("docs/backtest/specialites_v1.json", "docs/modeles/semaine1_v1.json",
                "docs/modeles/phasage_reel_v1.json", "docs/recherche/apercu_simap.json",
                "docs/recherche/apercu_simap.md", "data/fictif/candidats_300.csv", "CLAIMS.md"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, tmp_path / rel)
    for p in write_all(tmp_path):
        text = p.read_text("utf-8")
        assert not re.search(r"\bNone\b|\bnan\b", text, flags=re.IGNORECASE), p
        assert "47 % des projets" not in text
    claims = (tmp_path / "CLAIMS.md").read_text("utf-8")
    for cid in ("REEL-SPEC-BAT", "REEL-SURPRISE", "REDEP-1", "EQ-1", "CONF-1", "PHAS-2", "SIMAP-3"):
        assert f"| {cid} |" in claims
