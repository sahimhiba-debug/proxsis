"""Act 4 of « Votre prochain lundi »: three dated stories replayed « at date T » and the measurement screen.

Synthetic simap samples (format observed on 2026-10-06, invented names) — never a recorded real response, which
would contain contact persons. The last tests read the committed files."""

import json
import re
from datetime import date
from pathlib import Path

import httpx
import pytest

from proxsis.demo_export import parse_claims, pii_sweep
from proxsis.http import HttpCache, PoliteClient
from proxsis.presentation_stories import (
    LIMIT_SENTENCE,
    MEASURE_SENTENCE,
    StorySpec,
    bo_citations,
    build_story,
    company_awards,
    fetch_tenders,
    hindsight_leaks,
    measure_block,
    tender_facts,
    tender_from_past,
)

ROOT = Path(__file__).resolve().parents[2]


def _award(num, day, vendor="Exemple Travaux SA", title="Réfection de la route du Moulin", price=500000.0,
           authority="Commune d'Exemple", decision=None, process="open"):
    return {"id": f"simap:{num}", "project_id": f"proj-{num.split('-')[0]}", "publication_id": f"pub-{num}",
            "publication_number": num, "pub_type": "award" if process == "open" else "direct_award",
            "process_type": process, "publication_date": day, "decision_date": decision, "creation_language": "fr",
            "title": {"fr": title}, "contracting_authority": authority, "number_of_submissions": 3,
            "vendors": [{"name": vendor, "price_chf": price}]}


RECORDS = [
    _award("100-02", "2026-03-02"),
    _award("110-02", "2026-05-13", decision="2026-05-05"),
    _award("120-01", "2026-06-30", process="direct"),
    _award("130-02", "2026-08-12"),
    _award("140-02", "2026-05-14", vendor="Autre Entreprise SA"),
]
TENDERS = {"110-02": {"publication_id": "pub-110-01", "numero": "110-01", "date": "2026-02-10",
                      "titre": {"fr": "Réfection de la route du Moulin"}, "langue": "fr",
                      "delai_offres": "2026-03-20", "execution": None,
                      "url_api": "https://www.simap.ch/api/publications/v1/project/proj-110/publication-details/pub-110-01",
                      "url": "https://www.simap.ch/fr/project-detail/proj-110"}}
SPEC = StorySpec(id="exemple", company_id="ent-x", company="Exemple Travaux SA", ville="Exemple",
                 T=date(2026, 5, 18), pivot="110-02", region={"fr": "Région d'exemple", "de": "Beispielregion"},
                 objets={"110-02": {"fr": "la réfection d'une route", "de": "die Sanierung einer Strasse"}},
                 kind="reussite")


def test_the_initial_tender_is_the_earliest_tender_publication_of_the_project():
    past = {"pastPublications": [
        {"id": "c", "pubType": "correction", "publicationDate": "2026-01-05", "publicationNumber": "9-02"},
        {"id": "t2", "pubType": "tender", "publicationDate": "2026-01-20", "publicationNumber": "9-03",
         "corrected": True},
        {"id": "t1", "pubType": "tender", "publicationDate": "2025-12-02", "publicationNumber": "9-01"}]}
    assert tender_from_past(past) == {"publication_id": "t1", "numero": "9-01", "date": "2025-12-02"}
    only_awards = {"pastPublications": [{"id": "a", "pubType": "award", "publicationDate": "2026-01-01"}]}
    assert tender_from_past(only_awards) is None


def test_tender_facts_keep_dates_and_a_filtered_title_never_contacts():
    detail = {
        "project-info": {"title": {"fr": "Route du Moulin, renseignements : M. Jean Exemple", "de": None},
                         "procOfficeAddress": {"contactPerson": {"fr": "Jean Exemple"}, "email": "j@exemple.ch",
                                               "phone": "+41271234567"}},
        "procurement": {"executionDeadlineType": "period",
                        "executionPeriod": {"dateFrom": "2026-04-01", "dateTo": "2026-11-30"},
                        "executionNote": {"fr": "Contact : Jean Exemple, 079 123 45 67"}},
        "dates": {"publicationDate": "2026-02-10", "offerDeadline": "2026-03-20T12:00:00+01:00"},
        "base": {"creationLanguage": "fr", "publicationDate": "2026-02-10"},
    }
    f = tender_facts(detail)
    blob = json.dumps(f, ensure_ascii=False)
    assert "Jean" not in blob and "@" not in blob and "+41" not in blob and "079" not in blob
    assert f["date"] == "2026-02-10" and f["delai_offres"] == "2026-03-20" and f["langue"] == "fr"
    assert f["execution"] == {"type": "period", "debut": "2026-04-01", "fin": "2026-11-30", "jours": None}
    assert f["titre"]["fr"].startswith("Route du Moulin")
    detail["procurement"]["executionPeriod"] = {"dateRange": ["2026-05-01", "2026-11-30T00:00:00+01:00"]}
    assert tender_facts(detail)["execution"]["debut"] == "2026-05-01"
    assert tender_facts(detail)["execution"]["fin"] == "2026-11-30"


def test_fetch_tenders_goes_through_the_polite_api_client_and_stores_nothing_raw(tmp_path):
    calls: list[str] = []

    def handler(req):
        calls.append(req.url.path)
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /fr/\n")
        if req.url.path.endswith("past-publications"):
            return httpx.Response(200, json={"pastPublications": [
                {"id": "pub-110-01", "pubType": "tender", "publicationDate": "2026-02-10",
                 "publicationNumber": "110-01"}]})
        return httpx.Response(200, json={"project-info": {"title": {"fr": "Route du Moulin"}},
                                         "procurement": {"executionDeadlineType": "none"},
                                         "dates": {"publicationDate": "2026-02-10", "offerDeadline": None},
                                         "base": {"creationLanguage": "fr"}})

    cache = tmp_path / "c"
    c = PoliteClient(HttpCache(cache), offline=False, user_agent="t", transport=httpx.MockTransport(handler),
                     sleep=lambda s: None)
    out = fetch_tenders(c, [r for r in RECORDS if r["publication_number"] == "110-02"])
    assert out["110-02"]["date"] == "2026-02-10" and out["110-02"]["numero"] == "110-01"
    assert out["110-02"]["url"] == "https://www.simap.ch/fr/project-detail/proj-110"
    assert out["110-02"]["provenance"]["source"] == "simap.ch"
    assert all(p == "/robots.txt" or p.startswith("/api/") for p in calls)
    assert not any(cache.rglob("*.json")) if cache.exists() else True


def test_company_awards_are_the_vendor_s_awards_once_each():
    aw = company_awards([*RECORDS, RECORDS[0]], "Exemple Travaux SA")
    assert [a["numero"] for a in aw] == ["100-02", "110-02", "120-01", "130-02"]


def test_a_story_shows_at_T_only_what_was_published_before_T():
    s = build_story(SPEC, company_awards(RECORDS, SPEC.company), TENDERS, data_end=date(2026, 9, 30))
    known = s["arrets"]["connu"]
    assert {p["date"] for p in known["pieces"]} == {"2026-02-10", "2026-05-13"}
    assert known["contexte"]["n_52s"] == 2 and known["contexte"]["dernier"] == "2026-05-13"
    assert hindsight_leaks(s) == []
    later = s["arrets"]["ensuite"]["evenements"]
    assert [e["date"] for e in later] == ["2026-06-30", "2026-08-12"]
    iv = {i["code"]: i for i in s["intervalles"]}
    assert iv["appel_offres_adjudication"]["jours"] == (date(2026, 5, 13) - date(2026, 2, 10)).days
    assert iv["appel_offres_adjudication"]["arret"] == "connu"
    assert iv["signalement_adjudication_suivante"]["jours"] == 43
    assert iv["signalement_adjudication_suivante"]["nom"]["fr"] == (
        "entre le lundi de la liste et la publication de l'adjudication suivante")
    assert s["type"] == "reussite" and s["besoin_personnel"]["fr"] == LIMIT_SENTENCE["fr"]


def test_a_later_fact_slipped_into_the_first_two_stops_is_caught():
    s = build_story(SPEC, company_awards(RECORDS, SPEC.company), TENDERS, data_end=date(2026, 9, 30))
    s["arrets"]["signalement"]["texte"]["fr"] += " Nouveau marché le 30.06.2026."
    assert hindsight_leaks(s)


def test_planned_dates_published_in_the_tender_are_known_at_T():
    planned = {**TENDERS["110-02"], "execution": {"type": "date_time", "debut": "2026-05-01", "fin": "2026-11-30",
                                                  "jours": None}}
    s = build_story(SPEC, company_awards(RECORDS, SPEC.company), {"110-02": planned}, data_end=date(2026, 9, 30))
    assert "du 01.05.2026 au 30.11.2026" in s["arrets"]["connu"]["texte"]["fr"]
    assert "30.11.2026" in s["arrets"]["connu"]["texte"]["de"]
    assert hindsight_leaks(s) == []
    iv = {i["code"]: i for i in s["intervalles"]}
    assert iv["travaux_prevus"]["jours"] == 213 and iv["travaux_prevus"]["arret"] == "connu"
    with pytest.raises(ValueError):
        bad = dict(TENDERS)
        bad["110-02"] = {**TENDERS["110-02"], "date": "2026-05-20"}
        build_story(SPEC, company_awards(RECORDS, SPEC.company), bad, data_end=date(2026, 9, 30))


def test_a_signal_without_a_new_award_in_eight_weeks_is_a_limit_told_as_clearly():
    spec = StorySpec(**{**SPEC.__dict__, "T": date(2026, 8, 17), "pivot": "130-02", "kind": "limite",
                        "objets": {"130-02": {"fr": "une route", "de": "eine Strasse"}}})
    s = build_story(spec, company_awards(RECORDS, spec.company), {}, data_end=date(2026, 9, 30))
    assert s["type"] == "limite" and s["arrets"]["ensuite"]["evenements"] == []
    assert LIMIT_SENTENCE["fr"] in s["arrets"]["ensuite"]["texte"]["fr"]
    assert LIMIT_SENTENCE["de"] in s["arrets"]["ensuite"]["texte"]["de"]
    iv = {i["code"]: i for i in s["intervalles"]}
    assert iv["signalement_sans_adjudication"]["jours"] == (date(2026, 9, 30) - date(2026, 8, 17)).days
    with pytest.raises(ValueError):  # the declared kind must be what the data say
        build_story(StorySpec(**{**spec.__dict__, "kind": "reussite"}), company_awards(RECORDS, spec.company), {},
                    data_end=date(2026, 9, 30))


def test_bo_citations_need_an_established_role():
    rows = [{"id": "a", "date_publication": "2026-08-21", "commune": "Ardon", "statut": "acceptée",
             "url": "https://bulletin-officiel.vs.ch/x", "entreprises_citees": ["Exemple Travaux SA"],
             "roles": {"auteur_plans_entreprise": ["Exemple Travaux SA"], "requerant": ["[masqué]"]}},
            {"id": "b", "date_publication": "2026-08-28", "commune": "Sion", "statut": "acceptée", "url": "u",
             "entreprises_citees": ["Exemple Travaux SA"], "roles": {}}]
    assert bo_citations(rows, "Exemple Travaux SA") == [
        {"id": "a", "date": "2026-08-21", "commune": "Ardon", "role": "auteur_plans_entreprise",
         "url": "https://bulletin-officiel.vs.ch/x"}]


REEL_T0 = {"n_semaines": 44, "semaines": ["2025-10-06", "2026-08-03"], "taux_de_base": 0.1598,
           "p_at_k": {"hasard": {"moyenne": 0.1598, "ic95": [0.145, 0.181]},
                      "recence": {"moyenne": 0.3102, "ic95": [0.287, 0.370]},
                      "frequence_52s": {"moyenne": 0.55, "ic95": [0.48403, 0.68525]},
                      "m0_marches": {"moyenne": 0.52727, "ic95": [0.47, 0.63]}},
           "m0_moins_meilleure_naive": {"naive": "frequence_52s", "moyenne": -0.02273, "ic95": [-0.0886, 0.0136]},
           "donnees": {"adjudications": 1892, "entreprises": 731, "fin_des_donnees": "2026-09-30"}}


def test_the_measure_block_repeats_the_claims_line_and_never_calls_the_gap_established():
    claim = parse_claims(ROOT / "CLAIMS.md")["REEL-T0"]
    m = measure_block(REEL_T0, claim)
    v = {x["code"]: x for x in m["valeurs"]}
    assert (v["hasard"]["pct"], v["recence"]["pct"], v["frequence_52s"]["pct"], v["m0_marches"]["pct"]) == (
        16.0, 31.0, 55.0, 52.7)
    assert v["frequence_52s"]["ic95"] == [48.4, 68.5] and "ic95" not in v["m0_marches"]
    assert m["ecart"]["points"] == -2.3 and m["ecart"]["ic95"] == [-8.9, 1.4]
    p = m["perimetre"]
    assert (p["adjudications"], p["entreprises"], p["semaines"]) == (1892, 731, 44)
    assert m["phrase"]["fr"] == MEASURE_SENTENCE["fr"]
    assert "8 semaines" in m["definition"]["fr"] and "20 entreprises" in m["definition"]["fr"]
    assert "embauche" in m["portee"]["fr"] and "Einstellungen" in m["portee"]["de"]
    assert "pas établie" in m["ecart"]["lecture"]["fr"] and "nicht belegt" in m["ecart"]["lecture"]["de"]
    for x in m["valeurs"]:  # every figure shown is written as such in the CLAIMS line
        assert x["affiche"]["fr"] in claim["valeur"]
    with pytest.raises(ValueError):  # a CLAIMS line that says something else stops the export
        measure_block({**REEL_T0, "p_at_k": {**REEL_T0["p_at_k"], "recence": {"moyenne": 0.33, "ic95": [0, 1]}}},
                      claim)


# ---------------------------------------------------------------- committed files

HISTOIRES = ROOT / "apps/web/src/data/presentation/histoires.json"


def test_committed_stories_three_dated_one_limit_one_near_martigny_no_hindsight_no_private_data():
    h = json.loads(HISTOIRES.read_text("utf-8"))
    stories = h["histoires"]
    assert len(stories) == 3
    assert any(s["type"] == "limite" for s in stories)
    assert any("Martigny" in s["region"]["fr"] for s in stories)
    for s in stories:
        assert hindsight_leaks(s) == [], s["id"]
        assert s["besoin_personnel"] == LIMIT_SENTENCE
        for i in s["intervalles"]:
            assert i["jours"] == (date.fromisoformat(i["fin"]) - date.fromisoformat(i["debut"])).days
            assert i["nom"]["fr"].startswith("entre ") and i["nom"]["de"].startswith("zwischen ")
    assert h["source"]["mention"] == ("Ceci n'est pas une publication officielle. Les données publiées sur la "
                                      "plateforme www.simap.ch font foi.")
    assert pii_sweep(h) == []


def test_committed_stories_and_measure_are_in_the_claims_registry():
    h = json.loads(HISTOIRES.read_text("utf-8"))
    claims = parse_claims(ROOT / "CLAIMS.md")
    reel = json.loads((ROOT / "docs/backtest/reel_t0.json").read_text("utf-8"))
    assert h["mesure"] == measure_block(reel, claims["REEL-T0"])
    for s in h["histoires"]:
        row = claims[s["claims"]]
        assert s["claims"].startswith("PRES-HIST-")
        for i in s["intervalles"]:
            assert f"{i['jours']} j" in row["valeur"], (s["id"], i["code"])
        for p in s["arrets"]["connu"]["pieces"] + s["arrets"]["ensuite"]["evenements"]:
            d = p["date"]
            assert f"{d[8:10]}.{d[5:7]}.{d[:4]}" in row["valeur"], (s["id"], d)


def _texts(o):
    if isinstance(o, dict):
        return [t for k, v in o.items() for t in ([*v.values()] if k == "texte" else _texts(v))]
    return [t for v in o for t in _texts(v)] if isinstance(o, list) else []


def test_texts_write_dates_the_swiss_way():
    h = json.loads(HISTOIRES.read_text("utf-8"))
    texts = _texts(h["histoires"])
    assert texts and not [t for t in texts if re.search(r"\d{4}-\d{2}-\d{2}", t)]


def test_story_texts_say_publication_dates_and_never_more_than_the_data():
    """Review of 06.10.2026: an award date shown is its publication on simap (the decision is earlier); a procedure is
    named as simap names it; the data show no PUBLISHED public contract, not that there was no contract; a forecast is
    not written as a fact."""
    import json
    from pathlib import Path

    data = json.loads(Path("../apps/web/src/data/presentation/histoires.json").read_text("utf-8"))
    text = json.dumps(data, ensure_ascii=False)
    for wrong in ("attribution directe", "Direktvergabe", "à venir", "steht noch aus", "obtient un nouveau marché",
                  "erhält", "suivi d'aucun nouveau marché.", "kein neuer Auftrag"):
        assert wrong not in text, wrong
    assert "procédure sur invitation" in text and "Einladungsverfahren" in text
    assert "aucune adjudication n'est publiée à cette date" in text
    assert data["validation"] == "a_valider"  # until the review sheets are ticked (working notes)

