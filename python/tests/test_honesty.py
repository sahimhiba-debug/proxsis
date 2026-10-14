"""Every number measured on invented data says so, in the result file itself."""

import json
from pathlib import Path

import pytest

from proxsis.honesty import AGENT_SET_WARNING, FICTIF_WARNING, mark

DOCS = Path(__file__).resolve().parents[2] / "docs"


def test_mark_fictional_adds_exact_warning():
    out = mark({"wape": 0.3}, fictif=True)
    assert out["avertissement"] == FICTIF_WARNING
    assert out["wape"] == 0.3
    assert FICTIF_WARNING == "monde fictif : prouve que le code fonctionne, pas sa performance réelle"


def test_mark_agent_written_set_adds_second_warning():
    out = mark({}, fictif=True, agent_written_set=True)
    assert out["avertissement_jeu_de_test"] == AGENT_SET_WARNING
    assert "optimistes" in AGENT_SET_WARNING


def test_mark_real_data_without_fictif_flag_has_no_fictional_warning():
    out = mark({"n": 3}, fictif=False)
    assert "avertissement" not in out


@pytest.mark.parametrize("path", sorted((DOCS / "modeles").glob("*.json")), ids=lambda p: p.name)
def test_every_published_fictional_result_carries_the_warning(path):
    data = json.loads(path.read_text("utf-8"))
    blob = json.dumps(data, ensure_ascii=False)
    if "FICTI" in blob.upper():
        assert data.get("avertissement") == FICTIF_WARNING, path.name
    if path.name.startswith("m3_"):
        assert data.get("avertissement_jeu_de_test") == AGENT_SET_WARNING, path.name
