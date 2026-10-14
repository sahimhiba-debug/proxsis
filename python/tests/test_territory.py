"""Visit, time 1 (brief « à distance », 4.1): on the map, only companies whose dossier passes every check, the seat and
the place of a contract kept apart, nothing published after the Monday of the list."""

import json
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from proxsis.call_list import LOT_COLUMNS
from proxsis.cli import LOCALITES_CSV, ROOT
from proxsis.territory import CHECKS, Localities, build

WEB = ROOT / "apps" / "web" / "src" / "data"
COMMUNES = {int(c["bfs"]): c["nom"] for c in json.loads((WEB / "presentation" / "communes_vs.json").read_text("utf-8"))[
    "communes"]}
PLACES = Localities.read(Path(LOCALITES_CSV), COMMUNES)
BFS = {name: b for b, name in COMMUNES.items()}


def test_a_published_place_goes_to_its_commune() -> None:
    assert PLACES.commune_of("1907", "Saxon") == BFS["Saxon"]  # the locality spreads over Saxon and Martigny
    assert PLACES.commune_of("1934", "Le Châble VS") == BFS["Val de Bagnes"]
    assert PLACES.commune_of("1890", "St-Maurice") == BFS["Saint-Maurice"]
    assert PLACES.commune_of(None, "Saint-Maurice") == BFS["Saint-Maurice"]
    assert PLACES.commune_of("8000", "Zürich") is None  # outside the map: never placed by guessing


def _call(cid: str, reason: bool = True) -> dict[str, Any]:
    guide = [{"code": "questions", "phrases": [{"texte": "Quand ?", "sources": []}]}]
    if reason:
        guide.append({"code": "pourquoi", "phrases": [{"texte": "Marché publié.", "sources": [1]}]})
    return {"entreprise": cid, "faits": [{"id": 1, "type": "reel", "url": "https://www.simap.ch/fr/project-detail/a"}],
            "fr": {"guide": guide}}


def _lot(cid: str, day: date, seat: tuple[str, str], at: tuple[str, str], url: str) -> dict[str, Any]:
    row: dict[str, Any] = dict.fromkeys(LOT_COLUMNS)
    row.update(id=cid, available_at=day, postal_code=seat[0], city=seat[1], order_postal_code=at[0], order_city=at[1],
               url_simap=url)
    return row


def test_seat_and_contract_apart_checks_and_the_monday() -> None:
    T = date(2026, 10, 5)
    sion, saxon = ("1950", "Sion"), ("1907", "Saxon")
    url = "https://www.simap.ch/fr/project-detail/"
    companies = {
        "ent-a": {"nom": "Alpha Construction SA", "ville": "Saxon",
                  "chronologie": [{"date": "2026-09-01", "titre": "Route", "url_simap": url + "1"},
                                  {"date": "2026-10-06", "titre": "Plus tard", "url_simap": url + "2"}]},
        "ent-b": {"nom": "Beta SA", "ville": "Sion", "chronologie": [{"date": "2026-09-02", "titre": "Pont",
                                                                       "url_simap": url + "3"}]},
        "ent-c": {"nom": "Jean Exemple", "ville": "Sion", "chronologie": [{"date": "2026-09-03", "titre": "Mur",
                                                                            "url_simap": url + "4"}]},
    }
    lots = pd.DataFrame([_lot("ent-a", date(2026, 9, 1), saxon, sion, url + "1"),
                         _lot("ent-a", date(2026, 10, 6), saxon, saxon, url + "2"),
                         _lot("ent-b", date(2026, 9, 2), sion, sion, url + "3"),
                         _lot("ent-c", date(2026, 9, 3), sion, sion, url + "4")], columns=LOT_COLUMNS)
    calls = {"ent-a": _call("ent-a"), "ent-b": _call("ent-b", reason=False), "ent-c": _call("ent-c")}
    d = build(companies, calls, lots, PLACES, T, guided=["ent-a"], example=("Saxon", "ent-a"), mention="m")
    assert set(d["entreprises"]) == {"ent-a"}
    assert {e["id"]: e["controles_echoues"] for e in d["exclues"]} == {
        "ent-b": ["appel_prepare"], "ent-c": ["forme_juridique", "donnees_personnelles"]}  # a person: both checks
    assert d["communes"][str(BFS["Saxon"])] == {"siege": ["ent-a"], "marches": []}  # its contract after T is not shown
    assert d["communes"][str(BFS["Sion"])]["marches"] == [{"id": "ent-a", "date": "2026-09-01", "titre": "Route",
                                                          "url": url + "1"}]
    assert d["communes"][str(BFS["Sion"])]["siege"] == []
    with pytest.raises(ValueError):
        build(companies, calls, lots, PLACES, T, guided=[], example=("Saxon", "ent-b"), mention="m")


def test_the_committed_file() -> None:
    d = json.loads((WEB / "presentation" / "territoire.json").read_text("utf-8"))
    kept = d["entreprises"]
    assert d["exemple"] == {"commune": str(BFS["Saxon"]), "entreprise": "ent-1ef761b229"}
    assert set(d["controles"]) == set(CHECKS)
    for bfs, place in d["communes"].items():
        assert int(bfs) in COMMUNES
        assert all(i in kept for i in place["siege"]) and all(m["id"] in kept for m in place["marches"])
        assert all(m["date"] < d["lundi"] for m in place["marches"])
    for cid, c in kept.items():
        assert cid in d["communes"][str(c["commune_siege"])]["siege"]
    assert all(set(e["controles_echoues"]) <= set(CHECKS) and e["id"] not in kept for e in d["exclues"])
    companies = json.loads((WEB / "demo" / "entreprises.json").read_text("utf-8"))
    assert set(kept) | {e["id"] for e in d["exclues"]} == set(companies)  # every company of the app is accounted for
