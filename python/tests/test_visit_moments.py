"""New moments of the visit (brief of 07.10.2026, § 3.2 to 3.4): the data the screens will read, every figure from a
line of CLAIMS.md and recomputed by ``proxsis moments-presentation``.

* « Cette semaine » (PRES-SEMAINE-1): the publications of the week before the first Monday, those the list retained,
  its ten calls; nothing added after the end of the data.
* « Celles qui accélèrent » (REEL-SURPRISE): the measure file, refused when it differs from CLAIMS.
* « Plusieurs faits vont dans le même sens » (PRES-CARRON-1, PRES-BITZ-1, PRES-THELER-1): the facts of the three guided
  dossiers exactly as CLAIMS states them, each with its date and its source; never a private applicant.
"""

import copy
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest

from proxsis.cli import ROOT, main
from proxsis.demo_export import parse_claims, pii_sweep
from proxsis.visit_moments import (
    FACTS_CLAIMS,
    SURGE_CLAIMS,
    WEEK_CLAIMS,
    accelerating,
    guided_facts,
    week_counts,
)

WEB = ROOT / "apps" / "web" / "src" / "data" / "presentation"
WEEK_FILE, SURGE_FILE, FACTS_FILE = WEB / "cette_semaine.json", WEB / "accelerent.json", WEB / "faits.json"
FROZEN = ROOT / "data" / "terrain" / "liste_2026-10-05_batiment.json"
BO = ROOT / "data" / "manuel" / "import_pdf" / "publications.jsonl"
MEASURE = ROOT / "docs" / "backtest" / "specialites_v1.json"
REAL = ROOT / "data" / "reel" / "simap"
needs_real = pytest.mark.skipif(not any(REAL.glob("*.jsonl")), reason="données réelles filtrées absentes (data/reel/)")
MONDAY = date(2026, 10, 5)


def fmt(iso: str) -> str:
    return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}"


def _claims() -> dict[str, dict[str, str]]:
    return parse_claims(ROOT / "CLAIMS.md")


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text("utf-8"))
    return data


def _bo_rows() -> list[dict[str, Any]]:
    return [json.loads(x) for x in BO.read_text("utf-8").splitlines() if x.strip()]


# ---------------------------------------------------------------- « Cette semaine » on a small synthetic world

def _rec(i: int, day: date, vendor: str, canton: str = "VS", bkp: tuple[str, ...] = ("211",)) -> dict[str, Any]:
    return {"publication_id": f"pub{i}", "project_id": f"proj{i}", "pub_type": "award", "publication_date": str(day),
            "decision_date": str(day - timedelta(days=10)), "title": {"fr": f"Ecole {i} - CFC 211"},
            "bkp_codes": list(bkp), "npk_codes": [], "cpv_code": "45000000", "order_canton": canton,
            "order_city": "Sion", "contracting_authority": "Commune A",
            "vendors": [{"name": vendor, "canton": canton, "city": "Sion", "price_chf": 100_000.0}],
            "provenance": {"source": "simap.ch", "url": f"https://www.simap.ch/api/x/{i}"}}


def _permit(i: int, day: date | None, accepted: bool = True) -> dict[str, Any]:
    return {"id": f"bo{i}", "statut": "acceptée" if accepted else "rejetée",
            "date_publication": str(day) if day else None, "commune": "Sion", "entreprises_citees": [], "roles": {}}


def _world() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    long_ago = MONDAY - timedelta(days=200)
    recs = [_rec(1, long_ago, "Valais Bâtiment SA"), _rec(2, long_ago, "Vaud Bâtiment SA", canton="VD"),
            _rec(3, long_ago, "Valais Elec SA", bkp=("232",)),
            # the week: Monday 28.09 to Sunday 04.10
            _rec(10, MONDAY - timedelta(days=7), "Valais Bâtiment SA"),  # retained: building, Valais, a company
            _rec(11, MONDAY - timedelta(days=1), "Vaud Bâtiment SA", canton="VD"),  # read: another canton
            _rec(12, MONDAY - timedelta(days=3), "Valais Elec SA", bkp=("232",)),  # read: another specialty
            _rec(13, MONDAY - timedelta(days=2), "[particulier]"),  # read: no identified company
            _rec(14, MONDAY - timedelta(days=4), "Nouvelle Construction SA"),  # retained: first award, Valais
            # outside the week
            _rec(20, MONDAY - timedelta(days=8), "Valais Bâtiment SA"), _rec(21, MONDAY, "Valais Bâtiment SA")]
    permits = [_permit(1, MONDAY - timedelta(days=3)), _permit(2, MONDAY - timedelta(days=9)),
               _permit(3, MONDAY)]
    frozen = {"as_of": str(MONDAY), "specialite": "batiment", "region": ["VS"], "k": 10, "entreprises_classees": 2,
              "liste_id": "test", "entreprises": [{"id": "ent-x"}] * 10}
    return recs, permits, frozen


def _week(recs: list[dict[str, Any]], permits: list[dict[str, Any]], frozen: dict[str, Any]) -> dict[str, Any]:
    return week_counts(recs, permits, frozen, data_end=MONDAY - timedelta(days=1), check_ten=False)


def test_the_week_is_the_seven_days_before_the_monday_of_the_list() -> None:
    d = _week(*_world())
    assert d["lundi"] == "2026-10-05" and d["semaine"] == {"du": "2026-09-28", "au": "2026-10-04"}
    assert d["lues"] == {"total": 6, "simap": 5, "bulletin_officiel": 1}  # nothing of the Monday, nothing before


def test_retained_are_the_building_awards_of_the_valais_companies_of_the_list() -> None:
    d = _week(*_world())
    # neither another canton, nor another specialty, nor a masked laureate; the Bulletin officiel is read, never ordered
    assert d["retenues"] == {"total": 2, "simap": 2, "bulletin_officiel": 0}
    assert d["appels"] == 10


def test_the_population_must_be_the_one_of_the_frozen_list() -> None:
    recs, permits, frozen = _world()
    with pytest.raises(ValueError):
        _week(recs, permits, {**frozen, "entreprises_classees": 3})
    with pytest.raises(ValueError):  # a Tuesday is not the Monday of a list
        _week(recs, permits, {**frozen, "as_of": "2026-10-06"})
    with pytest.raises(ValueError):  # the ten of the list must be in its population
        week_counts(recs, permits, frozen, data_end=MONDAY - timedelta(days=1))


def test_a_week_cut_by_the_end_of_the_data_is_never_shown() -> None:
    # questionnaire of Hiba, 07.10.2026, A3: simap stops on Friday 02.10 here, so the week shown is the one before,
    # whole (21 to 27.09), and nothing after the end of the data is read
    recs, permits, frozen = _world()
    d = week_counts(recs, permits, frozen, data_end=MONDAY - timedelta(days=3), check_ten=False)
    assert d["semaine"] == {"du": "2026-09-21", "au": "2026-09-27"}
    assert d["lues"] == {"total": 2, "simap": 1, "bulletin_officiel": 1}
    assert d["retenues"] == {"total": 1, "simap": 1, "bulletin_officiel": 0}
    # the Bulletin officiel ending first cuts the week too (its import stops on Tuesday 29.09 here)
    d = week_counts(recs, [_permit(4, MONDAY - timedelta(days=6)), _permit(2, MONDAY - timedelta(days=9))], frozen,
                    data_end=MONDAY - timedelta(days=1), check_ten=False)
    assert d["semaine"] == {"du": "2026-09-21", "au": "2026-09-27"}
    assert d["fin_des_donnees"]["bulletin_officiel"] == "2026-09-29"


# ---------------------------------------------------------------- the committed files and CLAIMS

def test_the_week_file_says_what_claims_says() -> None:
    d = _load(WEEK_FILE)
    line = _claims()[WEEK_CLAIMS]
    assert d["claims"] == WEEK_CLAIMS and line["donnees"] == "RÉEL"
    assert line["commande"] == "proxsis moments-presentation"
    assert "apps/web/src/data/presentation/cette_semaine.json" in line["fichier"]
    lues, ret = d["lues"], d["retenues"]
    assert lues["total"] == lues["simap"] + lues["bulletin_officiel"]
    assert ret["total"] == ret["simap"] + ret["bulletin_officiel"] and ret["total"] <= lues["total"]
    assert (f"{lues['total']} publications lues ({lues['simap']} adjudications simap, {lues['bulletin_officiel']} "
            f"demandes d'autorisation du Bulletin officiel)") in line["valeur"]
    assert (f"{ret['total']} retenues ({ret['simap']} adjudications simap, {ret['bulletin_officiel']} du Bulletin "
            f"officiel)") in line["valeur"]
    assert f"{d['appels']} appels" in line["valeur"]
    assert f"du {fmt(d['semaine']['du'])} au {fmt(d['semaine']['au'])}" in line["affirmation"]
    assert fmt(d["fin_des_donnees"]["simap"]) in line["limite"]
    assert fmt(d["fin_des_donnees"]["bulletin_officiel"]) in line["limite"]


def test_the_week_is_the_first_monday_of_the_visit_and_its_ten_calls() -> None:
    d = _load(WEEK_FILE)
    frozen, curated = _load(FROZEN), _load(WEB / "dossiers.json")
    assert d["lundi"] == curated["rejeu"] == frozen["as_of"]
    assert d["appels"] == len(frozen["entreprises"]) == len(curated["dix"]) == 10
    assert d["liste"]["liste_id"] == frozen["liste_id"]
    assert d["fin_des_donnees"]["simap"] < d["lundi"] and d["fin_des_donnees"]["bulletin_officiel"] < d["lundi"]
    bo_dates = [str(r["date_publication"])[:10] for r in _bo_rows() if r.get("statut") == "acceptée"]
    assert max(bo_dates) == d["fin_des_donnees"]["bulletin_officiel"]
    assert sum(d["semaine"]["du"] <= x <= d["semaine"]["au"] for x in bo_dates) == d["lues"]["bulletin_officiel"]


@needs_real
def test_the_week_is_recomputed_from_the_frozen_data() -> None:
    from proxsis.cli import PERMITS_JSONL, SIMAP_FILES
    from proxsis.commands.io import load_simap, permits

    d = _load(WEEK_FILE)
    again = week_counts(load_simap(SIMAP_FILES), permits(PERMITS_JSONL) or [], _load(FROZEN),
                        data_end=date.fromisoformat(d["fin_des_donnees"]["simap"]))
    assert {k: v for k, v in again.items() if k != "provenance"} == {k: v for k, v in d.items() if k != "provenance"}


# ---------------------------------------------------------------- « Celles qui accélèrent »

def test_accelerating_repeats_the_measure_and_its_claims_line() -> None:
    measure = _load(MEASURE)
    line = _claims()[SURGE_CLAIMS]
    d = accelerating(measure, _claims())
    rd = measure["specialites"]["batiment"]["drapeaux_surprise"]["rythme_double"]["hors_top_k"]
    assert d["accelerent"]["cas"] == rd["signalements"] == 298
    assert d["accelerent"]["taux"] == rd["taux_t0"] and d["hors_des_dix"]["taux"] == rd["taux_de_base_t0"]
    assert d["accelerent"]["affiche"] == {"fr": "38,3 %", "de": "38,3 %"}
    assert d["hors_des_dix"]["affiche"] == {"fr": "17,3 %", "de": "17,3 %"}
    assert (d["perimetre"]["semaines"], d["perimetre"]["premiere"], d["perimetre"]["derniere"]) == (
        57, "2025-07-07", "2026-08-03")
    assert "taux descriptifs" in line["limite"] and d["nuance"]["fr"]
    assert d == _load(SURGE_FILE)


def test_a_measure_that_differs_from_claims_is_refused() -> None:
    measure, claims = _load(MEASURE), _claims()
    line = claims[SURGE_CLAIMS]
    with pytest.raises(ValueError):
        accelerating(measure, {**claims, SURGE_CLAIMS: {**line, "valeur": line["valeur"].replace("38,3 %", "40,0 %")}})
    other = copy.deepcopy(measure)
    other["specialites"]["batiment"]["drapeaux_surprise"]["rythme_double"]["hors_top_k"]["signalements"] = 297
    with pytest.raises(ValueError):
        accelerating(other, claims)
    shorter = copy.deepcopy(measure)
    shorter["specialites"]["batiment"]["n_semaines"] = 56
    with pytest.raises(ValueError):  # not the Mondays of the measure REEL-SPEC-BAT
        accelerating(shorter, claims)
    with pytest.raises(ValueError):  # the nuance of CLAIMS must stay
        accelerating(measure, {**claims, SURGE_CLAIMS: {**line, "limite": "—"}})


# ---------------------------------------------------------------- « Plusieurs faits vont dans le même sens »

def test_the_guided_facts_are_exactly_those_of_claims() -> None:
    d = guided_facts(_load(FROZEN), _bo_rows(), _claims())
    assert d == _load(FACTS_FILE)
    claims = _claims()
    assert set(d["dossiers"]) == set(_load(WEB / "dossiers.json")["guides"])
    assert sorted(x["claims"] for x in d["dossiers"].values()) == sorted(FACTS_CLAIMS)
    for cid, dossier in d["dossiers"].items():
        line = claims[dossier["claims"]]
        assert line["valeur"].startswith(f"{dossier['marches_52s']['nombre']} ; dernier publié le ")
        assert line["donnees"] == "RÉEL"
        for f in dossier["faits"]:
            assert fmt(f["date"]) in line["valeur"], (cid, f["date"])
            if f["type"] == "marche":
                assert f["source"] == "simap" and f["url"].startswith("https://www.simap.ch/")
            else:
                assert f["type"] == "demande_autorisation" and f["source"] == "bulletin_officiel"
                assert f["role"] == "auteur_plans_entreprise"
                assert "url" not in f and "id" not in f  # the request names the applicant: never linked
                assert f["commune"] in line["valeur"]
        dates = [f["date"] for f in dossier["faits"]]
        assert dates == sorted(dates, reverse=True)
    assert d["sources"]["bulletin_officiel"]["nom"]["fr"] == "Bulletin officiel du Valais"
    assert d["sources"]["bulletin_officiel"]["mention"]["fr"] == "relevé manuel pendant le prototype"
    assert d["sources"]["simap"]["mention"] == _load(WEB / "lundis.json")["source"]["mention"]


def test_each_fact_comes_from_the_files_named_by_claims() -> None:
    from proxsis.presentation_stories import bo_citations

    d, frozen = _load(FACTS_FILE), _load(FROZEN)
    entries = {e["id"]: e for e in frozen["entreprises"]}
    rows = _bo_rows()
    demo = _load(ROOT / "apps" / "web" / "src" / "data" / "demo" / "entreprises.json")
    for cid, dossier in d["dossiers"].items():
        e = entries[cid]
        assert dossier["nom"] == e["nom"] and dossier["marches_52s"]["nombre"] == e["n_52s"]
        published = {(s["date"], s["url_simap"]) for s in e["sources"]}
        chronology = {(s["date"], s["url_simap"]) for s in demo[cid]["chronologie"]}
        for f in dossier["faits"]:
            if f["type"] == "marche":
                assert (f["date"], f["url"]) in published and (f["date"], f["url"]) in chronology
        latest = [f for f in dossier["faits"] if f["type"] == "marche" and f["dernier"]]
        assert [f["date"] for f in latest] == [e["sources"][0]["date"]]
        bo = [f for f in dossier["faits"] if f["type"] == "demande_autorisation"]
        cited = bo_citations(rows, e["nom"])
        assert sorted((f["date"], f["commune"]) for f in bo) == sorted((c["date"], c["commune"]) for c in cited)
        assert all(c["role"] == "auteur_plans_entreprise" for c in cited)


def test_the_three_guided_dossiers_say_what_their_line_says() -> None:
    d = _load(FACTS_FILE)["dossiers"]
    claims = _claims()
    carron, bitz, theler = (next(x for x in d.values() if x["claims"] == c) for c in FACTS_CLAIMS)
    # its latest award and the three other recent ones its line dates (questionnaire of Hiba, 07.10.2026, A4)
    assert [f["date"] for f in carron["faits"]] == ["2026-08-12", "2026-08-12", "2026-06-30", "2026-05-13"]
    assert [f["dernier"] for f in carron["faits"]].count(True) == 1
    assert ("3 autres marchés récents publiés les 13.05.2026, 30.06.2026 et 12.08.2026"
            in claims["PRES-CARRON-1"]["valeur"])
    assert [(f["type"], f["date"]) for f in bitz["faits"]] == [
        ("demande_autorisation", "2026-08-28"), ("demande_autorisation", "2026-08-28"),
        ("demande_autorisation", "2026-08-21"), ("marche", "2026-05-02")]
    assert "3 demandes d'autorisation où elle est **auteure des plans**" in claims["PRES-BITZ-1"]["valeur"]
    ng24 = [f["date"] for f in theler["faits"] if f["serie"] == "NG24"]
    assert ng24 == ["2026-09-21", "2026-07-03", "2026-06-26"] == [f["date"] for f in theler["faits"]]
    assert ("3 tronçons NG24 attribués, publiés les 26.06.2026, 03.07.2026 et 21.09.2026"
            in claims["PRES-THELER-1"]["valeur"])
    last = theler["faits"][0]
    assert last["dernier"] and f"« {last['titre_original']} »" in claims["PRES-THELER-1"]["valeur"]


def test_a_fact_that_claims_does_not_state_is_refused() -> None:
    claims = _claims()
    frozen, rows = _load(FROZEN), _bo_rows()
    for cid, old in (("PRES-CARRON-1", "12.08.2026"), ("PRES-BITZ-1", "21.08.2026"), ("PRES-THELER-1", "03.07.2026")):
        changed = {**claims, cid: {**claims[cid], "valeur": claims[cid]["valeur"].replace(old, "01.01.2026")}}
        with pytest.raises(ValueError):
            guided_facts(frozen, rows, changed)
    def as_owner(r: dict[str, Any]) -> dict[str, Any]:  # the same company, in another role
        roles = r.get("roles") or {}
        mine = roles.get("auteur_plans_entreprise") or []
        if "Bitz travaux publics SA" not in mine:
            return r
        return {**r, "roles": {**roles, "auteur_plans_entreprise": [], "maitre_ouvrage": mine}}

    with pytest.raises(ValueError):  # a role other than author of the plans is not in the line
        guided_facts(frozen, [as_owner(r) for r in rows], claims)


def test_the_moment_files_carry_no_personal_data_and_their_provenance() -> None:
    for path in (WEEK_FILE, SURGE_FILE, FACTS_FILE):
        d = _load(path)
        assert pii_sweep(d) == [], path.name
        text = path.read_text("utf-8")
        assert "[particulier]" not in text and "requérant" not in text and "requerant" not in text
        assert d["provenance"]["commande"] == "proxsis moments-presentation"
        assert d["provenance"]["calcule_le"] == "2026-10-07"


@needs_real
def test_the_command_writes_the_three_files_byte_for_byte(tmp_path: Path) -> None:
    assert main(["moments-presentation", "--out-dir", str(tmp_path)]) == 0
    for name in ("cette_semaine.json", "accelerent.json", "faits.json"):
        assert (tmp_path / name).read_bytes() == (WEB / name).read_bytes(), name
