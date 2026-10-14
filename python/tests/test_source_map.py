"""La carte des sources (suite 10, § 3): the real numbers of the catalogue (data/catalogue.csv), counted by the code,
never by hand, and the same as the CLAIMS line SOURCES-1."""

import csv
import json
from pathlib import Path

import pytest

from proxsis.cli import ROOT, main
from proxsis.demo_export import parse_claims
from proxsis.source_map import EXCLUDED, IN_SERVICE, REQUESTS, source_map

CATALOGUE = ROOT / "data" / "catalogue.csv"


def _rows() -> list[dict[str, str]]:
    with CATALOGUE.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_the_catalogue_is_counted_line_by_line():
    m = source_map(_rows())
    assert m["etudiees"] == 68
    assert m["en_service"]["nombre"] == 2
    assert m["demandes"]["nombre"] == 4
    assert m["ecartees"]["nombre"] == 9
    others = m["autres"]
    assert (others["nombre"], others["conditions_a_verifier"], others["sans_usage_pour_la_liste"]) == (53, 43, 10)
    assert 2 + 4 + 9 + 53 == 68


def test_every_named_line_exists_and_the_groups_do_not_overlap():
    rows = {r["id"]: r for r in _rows()}
    requested = [x for req in REQUESTS for x in req["lignes"]]
    excluded = [x for ids in EXCLUDED.values() for x in ids]
    named = [*IN_SERVICE, *requested, *excluded]
    assert len(named) == len(set(named))
    assert set(named) <= set(rows)
    # what is « écarté » is exactly what the catalogue says « non », each with the reason of its family
    assert set(excluded) == {i for i, r in rows.items() if r["verdict"] == "non"}
    assert not any(rows[i]["verdict"] == "non" for i in [*IN_SERVICE, *requested])


def test_the_four_requests_are_the_texts_of_docs_demandes():
    assert [r["cle"] for r in REQUESTS] == ["portail", "zefix", "jobroom", "regbl"]
    for r in REQUESTS:
        assert (ROOT / r["fichier"]).exists(), r["fichier"]
        assert r["statut"] == "envoyee" and r["mois"] == "2026-10"


def test_an_unknown_line_or_a_new_verdict_non_is_refused():
    rows = _rows()
    with pytest.raises(ValueError, match="écartée sans famille"):
        source_map([*rows, {"id": "nouvelle_source", "verdict": "non"}])
    with pytest.raises(ValueError, match="absente du catalogue"):
        source_map([r for r in rows if r["id"] != "zefix_publicrest"])


def test_the_command_writes_the_file_of_the_page_and_it_matches_claims(tmp_path: Path):
    out = tmp_path / "carte.json"
    assert main(["carte-sources", "--out", str(out)]) == 0
    produced = out.read_bytes()
    assert produced == (ROOT / "apps/web/src/data/sources/carte.json").read_bytes()  # committed = reproduced
    data = json.loads(produced)
    claim = parse_claims(ROOT / "CLAIMS.md")[data["claims"]]
    for figure in ("68 sources", "2 en service", "4 couvertes", "9 écartées", "53 autres"):
        assert figure in claim["valeur"], figure


def test_a_claims_line_that_differs_is_refused(tmp_path: Path):
    claims = tmp_path / "CLAIMS.md"
    text = (ROOT / "CLAIMS.md").read_text("utf-8").replace("9 écartées", "6 écartées")
    claims.write_text(text, "utf-8")
    with pytest.raises(SystemExit):
        main(["carte-sources", "--claims", str(claims), "--out", str(tmp_path / "carte.json")])
    assert not (tmp_path / "carte.json").exists()
