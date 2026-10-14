"""Visit, time 2 (brief « à distance », 4.2): the following Monday is computed by the same rule as the frozen list of
the first Monday, which it must give back, and invents no publication after the end of the data."""

import json
from datetime import date

import pytest

from proxsis.cli import ROOT
from proxsis.next_monday import RANKED, next_monday

FILE = ROOT / "apps" / "web" / "src" / "data" / "presentation" / "lundi_suivant.json"
REAL = ROOT / "data" / "reel" / "simap"


def test_the_committed_file() -> None:
    d = json.loads(FILE.read_text("utf-8"))
    curated = json.loads((ROOT / "apps/web/src/data/presentation/dossiers.json").read_text("utf-8"))
    assert d["premier"] == curated["rejeu"]
    assert (date.fromisoformat(d["lundi"]) - date.fromisoformat(d["premier"])).days == 7
    assert [c["rang"] for c in d["classement"]] == list(range(1, RANKED + 1))
    assert d["fin_des_donnees"] < d["premier"] and d["nouvelles_publications"] == []


def test_a_monday_is_required() -> None:
    with pytest.raises(ValueError):
        next_monday([], date(2026, 10, 6), [], date(2026, 9, 30))


@pytest.mark.skipif(not any(REAL.glob("*.jsonl")), reason="données réelles filtrées absentes (data/reel/)")
def test_the_rule_gives_back_the_frozen_list() -> None:
    from proxsis.cli import SIMAP_FILES
    from proxsis.commands.io import load_simap

    curated = json.loads((ROOT / "apps/web/src/data/presentation/dossiers.json").read_text("utf-8"))
    records = load_simap(SIMAP_FILES)
    with pytest.raises(ValueError):  # another list is refused
        next_monday(records, date(2026, 10, 5), list(reversed(curated["dix"])), date(2026, 9, 30))
    d = next_monday(records, date(2026, 10, 5), curated["dix"], date(2026, 9, 30))
    assert d == json.loads(FILE.read_text("utf-8"))
