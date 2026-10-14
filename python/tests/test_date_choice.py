"""Act 4, « Choisissez une date » (Hiba, 07.10.2026): the list of a Monday uses nothing published after it, the file
gives back the measure of CLAIMS.md exactly, and every Monday of the measure is in it, the bad ones as they are."""

import json
from datetime import date, timedelta
from typing import Any

import pandas as pd
import pytest

from proxsis.call_list import LOT_COLUMNS, company_id
from proxsis.cli import ROOT
from proxsis.date_choice import (
    CLAIMS_ID,
    FIRST_WEEK,
    HISTORY_DAYS,
    HORIZON_DAYS,
    LAST_WEEK,
    K,
    monday_list,
    monday_of,
)
from proxsis.demo_export import parse_claims

FILE = ROOT / "apps" / "web" / "src" / "data" / "presentation" / "lundis.json"
REAL = ROOT / "data" / "reel" / "simap"
BEFORE = ("rang", "id", "nom", "ville", "marches_52s", "dernier_marche", "autre_inscription_de")


def _lot(company: str, day: date, canton: str = "VS", n: int = 0) -> dict[str, Any]:
    row: dict[str, Any] = dict.fromkeys(LOT_COLUMNS)
    pid = f"{company}-{day}-{n}"
    row.update(company=company, id=company_id(company), name=f"{company.title()} SA", city="Sion", canton=canton,
               available_at=day, phase="gros_oeuvre", specialty="batiment", title=f"Travaux {pid}",
               project_id=pid, publication_id=pid, url_simap=f"https://www.simap.ch/fr/project-detail/{pid}")
    return row


def _world(extra: list[dict[str, Any]] | None = None) -> pd.DataFrame:
    T0 = date(2025, 1, 6)
    rows = [_lot(f"firme {i:02d}", T0 - timedelta(days=7 * w + i), n=w) for i in range(14) for w in range(i % 5 + 1)]
    rows += [_lot("firme 03", date(2025, 1, 20)), _lot("firme 07", date(2025, 2, 10))]  # after T: the reveal only
    return pd.DataFrame(rows + (extra or []), columns=LOT_COLUMNS)


def _before(m: dict[str, Any]) -> list[tuple[Any, ...]]:
    return [tuple(r[k] for k in BEFORE) for r in m["dix"]]


def test_any_date_is_brought_back_to_its_monday() -> None:
    assert monday_of(date(2025, 11, 9)) == date(2025, 11, 3)  # a Sunday
    assert monday_of(date(2025, 11, 3)) == date(2025, 11, 3)
    assert monday_of(date(2026, 1, 1)) == date(2025, 12, 29)


def test_nothing_published_after_the_monday_changes_the_list() -> None:
    T = date(2025, 1, 6)
    ref = monday_list(_world(), T)
    flood = [_lot("firme 13", T + timedelta(days=d), n=d) for d in range(0, 120, 3)]  # a firm that wins a lot later
    flood += [_lot("firme 00", T + timedelta(days=1), canton="BE")] * 30  # and one whose canton changes later
    flood += [_lot("nouvelle", T + timedelta(days=2), n=d) for d in range(20)]  # and a newcomer
    later = monday_list(_world(flood), T)
    assert _before(later) == _before(ref)
    assert [r["nouveau_marche"] is not None for r in ref["dix"]] == [r["id"] in {company_id("firme 03"),
                                                                               company_id("firme 07")}
                                                                     for r in ref["dix"]]
    truncated = _world()
    assert _before(monday_list(truncated[truncated["available_at"] < T], T)) == _before(ref)


def test_the_reveal_reads_eight_weeks_only() -> None:
    T = date(2025, 1, 6)
    m = monday_list(_world([_lot("firme 05", T + timedelta(days=HORIZON_DAYS))]), T)  # the first day after
    assert {r["id"] for r in m["dix"] if r["nouveau_marche"]} == {company_id("firme 03"), company_id("firme 07")}


def test_a_branch_next_to_its_company_is_said() -> None:
    T = date(2025, 1, 6)
    branch = [_lot("firme 01 filiale visp", T - timedelta(days=d), n=d) for d in range(1, 40, 7)]
    m = monday_list(_world(branch), T)
    by_id = {r["id"]: r for r in m["dix"]}
    assert by_id[company_id("firme 01 filiale visp")]["autre_inscription_de"] == by_id[company_id("firme 01")]["rang"]
    assert by_id[company_id("firme 01")]["autre_inscription_de"] is None


# ---------------------------------------------------------------- the committed file

@pytest.fixture(scope="module")
def data() -> dict[str, Any]:
    d: dict[str, Any] = json.loads(FILE.read_text("utf-8"))
    return d


def test_every_monday_of_the_measure_is_there_good_and_bad(data: dict[str, Any]) -> None:
    mondays = [str(FIRST_WEEK + timedelta(days=7 * i)) for i in range((LAST_WEEK - FIRST_WEEK).days // 7 + 1)]
    assert [m["lundi"] for m in data["lundis"]] == mondays  # none left out for its result
    assert all(len(m["dix"]) == K and m["obtenu"] == sum(bool(r["nouveau_marche"]) for r in m["dix"])
               for m in data["lundis"])
    worst = min(data["lundis"], key=lambda m: m["obtenu"])
    assert worst["choisissable"] and worst["obtenu"] <= 4  # 03.11.2025: 4 out of 10, offered like any other


def test_the_file_gives_back_the_measure_of_claims(data: dict[str, Any]) -> None:
    measure = json.loads((ROOT / "docs/backtest/specialites_v1.json").read_text("utf-8"))["specialites"]["batiment"]
    t0 = measure["cibles"]["t0"]
    weeks = data["lundis"]
    assert sum(m["obtenu"] for m in weeks) / (K * len(weeks)) == pytest.approx(t0["p_at_k"]["frequence_52s"]["moyenne"],
                                                                             abs=1e-12)
    assert sum(m["entreprises_actives"] / m["entreprises_classees"] for m in weeks) / len(weeks) == pytest.approx(
        t0["taux_de_base"], abs=1e-12)
    assert (len(weeks), [weeks[0]["lundi"], weeks[-1]["lundi"]]) == (measure["n_semaines"], measure["semaines"])
    line = parse_claims(ROOT / "CLAIMS.md")[CLAIMS_ID]
    shown = data["mesure"]["affiche"]
    assert f"hasard {shown['hasard']['fr']}" in line["valeur"]
    assert f"fréquence 52 sem. {shown['regle']['fr']}" in line["valeur"]
    assert data["claims"] == CLAIMS_ID


def test_the_range_of_the_mondays_is_the_one_registered(data: dict[str, Any]) -> None:
    line = parse_claims(ROOT / "CLAIMS.md")["PRES-DATE-1"]
    weeks = data["lundis"]
    fmt = lambda iso: f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}"  # noqa: E731
    low, high = min(m["obtenu"] for m in weeks), max(m["obtenu"] for m in weeks)
    lows = " et ".join(fmt(m["lundi"]) for m in weeks if m["obtenu"] == low)
    highs = " et ".join(fmt(m["lundi"]) for m in weeks if m["obtenu"] == high)
    assert f"de {low} sur 10 ({lows}) à {high} sur 10 ({highs})" in line["valeur"]
    assert f"({sum(m['obtenu'] for m in weeks)} sur {K * len(weeks)})" in line["valeur"]
    assert f"{len(weeks)} lundis" in line["affirmation"]
    assert f"dont {data['choix']['nombre']} au choix" in line["affirmation"]


def test_the_mean_on_the_mondays_that_can_be_chosen_is_computed_from_them(data: dict[str, Any]) -> None:
    offered = [m for m in data["lundis"] if m["choisissable"]]
    block = data["au_choix"]
    assert (block["semaines"], block["premiere"], block["derniere"]) == (
        data["choix"]["nombre"], data["choix"]["premier"], data["choix"]["dernier"])
    assert block["obtenu"] == sum(m["obtenu"] for m in offered) and block["sur"] == K * len(offered)
    assert block["regle"] == pytest.approx(block["obtenu"] / block["sur"], abs=1e-12)
    assert block["hasard"] == pytest.approx(
        sum(m["entreprises_actives"] / m["entreprises_classees"] for m in offered) / len(offered), abs=1e-12)
    for key in ("regle", "hasard"):
        shown = f"{100 * block[key] + 1e-9:.1f}".replace(".", ",") + " %"
        assert block["affiche"][key] == {"fr": shown, "de": shown}


def test_only_mondays_with_52_weeks_before_and_8_after_can_be_chosen(data: dict[str, Any]) -> None:
    start = date.fromisoformat(data["source"]["debut_des_donnees"])
    end = date.fromisoformat(data["source"]["fin_des_donnees"])
    for m in data["lundis"]:
        T = date.fromisoformat(m["lundi"])
        assert T.weekday() == 0
        assert m["choisissable"] == ((T - start).days >= HISTORY_DAYS and T + timedelta(days=HORIZON_DAYS) <= end
                                     + timedelta(days=1))
    chosen = [m["lundi"] for m in data["lundis"] if m["choisissable"]]
    assert data["choix"] == {"premier": chosen[0], "dernier": chosen[-1], "nombre": len(chosen),
                             "exemple": "2026-03-02"}


def test_every_shown_figure_predates_the_monday(data: dict[str, Any]) -> None:
    for m in data["lundis"]:
        for r in m["dix"]:
            assert r["dernier_marche"] < m["lundi"]
            if r["nouveau_marche"]:
                won = date.fromisoformat(r["nouveau_marche"]["date"])
                assert date.fromisoformat(m["lundi"]) <= won < date.fromisoformat(m["lundi"]) + timedelta(HORIZON_DAYS)
                assert r["nouveau_marche"]["url"].startswith("https://www.simap.ch/")


@pytest.mark.skipif(not any(REAL.glob("*.jsonl")), reason="données réelles filtrées absentes (data/reel/)")
def test_on_the_real_data_the_list_ignores_what_came_later(data: dict[str, Any]) -> None:
    from proxsis.call_list import lot_table
    from proxsis.cli import SIMAP_FILES
    from proxsis.commands.io import load_simap

    lots = lot_table(load_simap(SIMAP_FILES))
    for m in data["lundis"]:
        T = date.fromisoformat(m["lundi"])
        assert _before(monday_list(lots[lots["available_at"] < T], T)) == _before(m), m["lundi"]
