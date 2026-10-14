"""CLAIMS.md is a well-formed register: every line says its data type and how to reproduce it."""

import re
from pathlib import Path

CLAIMS = Path(__file__).resolve().parents[2] / "CLAIMS.md"


def _rows():
    lines = [x for x in CLAIMS.read_text("utf-8").splitlines() if x.startswith("| ") and not x.startswith("| ID")]
    return [[c.strip() for c in x.strip("|").split(" | ")] for x in lines]


def test_every_claim_has_seven_columns_and_a_known_data_type():
    rows = _rows()
    assert rows
    for r in rows:
        assert len(r) == 7, r
        assert r[3] in {"RÉEL", "FICTIF", "FICTIF-AGENT", "SOURCE PUBLIQUE"}, r


def test_ids_are_unique():
    ids = [r[0] for r in _rows()]
    assert len(ids) == len(set(ids))


def test_fictional_warning_is_stated():
    assert "monde fictif : prouve que le code fonctionne, pas sa performance réelle" in CLAIMS.read_text("utf-8")


def test_public_sources_say_where_and_when_they_were_read():
    """A fact read elsewhere (brief of 07.10.2026, suite 2), not a measure of Proxsis: its address and reading date."""
    rows = [r for r in _rows() if r[3] == "SOURCE PUBLIQUE"]
    assert rows
    # Q09 (suite 9) : pour une seule source, l'adresse complète est gardée hors de Git (data/reel, jamais commité) ;
    # la fiche dit le journal, la date et où se trouve l'adresse. L'exception est nommée : elle ne peut pas s'étendre.
    hors_git = {"EXT-GROUPE-DELAI"}
    for r in rows:
        assert r[0].startswith("EXT-"), r
        assert re.search(r"\blus? le \d{2}\.\d{2}\.\d{4}", r[4]), r
        if r[0] in hors_git:
            assert "hors de Git" in r[4] and "data/reel/" in r[4], r
        else:
            assert "https://" in r[4], r
    assert hors_git <= {r[0] for r in rows}
