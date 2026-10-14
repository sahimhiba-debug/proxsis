"""Contract tests of the connectors on SYNTHETIC samples shaped after the
public documentation (the sources are unreachable from the dev environment)."""

import json
from datetime import UTC, date, datetime
from pathlib import Path

import httpx
import pytest

from proxsis.connectors.amtsblatt import ALLOWED, AmtsblattConnector, is_blocked
from proxsis.connectors.geoadmin import GeoAdminGeocoder
from proxsis.connectors.simap import AWARD_TYPES, SimapConnector
from proxsis.connectors.zefix import ZefixConnector
from proxsis.http import FetchResult, HttpCache, ManualOnlyHost, PoliteClient
from proxsis.ingest import ingest
from proxsis.provenance import Provenance

FIX = Path(__file__).parent / "fixtures"


def _result(path: Path, url: str = "https://example/x") -> FetchResult:
    body = path.read_bytes()
    prov = Provenance("test", url, datetime(2026, 10, 5, tzinfo=UTC), "test")
    return FetchResult(url, 200, body, {}, prov, False)


def test_all_fixtures_are_marked_synthetic():
    for p in FIX.rglob("*"):
        if p.is_file():
            assert "SYNTHÉTIQUE" in p.read_text("utf-8") or "FICTIF" in p.read_text("utf-8"), p


class TestSimap:
    def test_request_has_mandatory_params(self):
        url, params = SimapConnector().requests(date(2026, 9, 1), date(2026, 9, 30))[0]
        assert url.endswith("/publications/v2/project/project-search")
        assert params["lang"] in ("fr", "de", "it", "en")
        assert params["projectSubTypes"]  # quick-filter obligatoire sans recherche textuelle
        assert set(params["newestPubTypes"].split(",")) == set(AWARD_TYPES)
        assert "award" not in params["newestPubTypes"].split(",")

    def test_parse_award_detail_real_format(self):
        summary = json.loads((FIX / "simap/search_page.json").read_text("utf-8"))["projects"][0]
        recs = SimapConnector().parse(_result(FIX / "simap/detail_award.json"), summary=summary)
        assert len(recs) == 1
        r = recs[0]
        assert r.category == "adjudication"
        assert r.fields["company_name"] == "Brevin Génie Civil SA"
        assert r.fields["uid"] is None  # simap ne publie pas l'IDE des lauréats
        assert r.fields["value_chf"] == pytest.approx(1184500.30)
        assert r.available_at == date(2026, 9, 14) and r.event_date == date(2026, 9, 8)
        assert r.fields["canton"] == "VS" and r.fields["commune"] == "Sembrancher"
        assert "Exemple" not in json.dumps(r.fields, ensure_ascii=False)

    def test_search_page_yields_no_records(self):
        assert SimapConnector().parse(_result(FIX / "simap/search_page.json")) == []

    def test_fetch_never_stores_raw_responses(self, tmp_path):
        search = json.loads((FIX / "simap/search_page.json").read_text("utf-8"))
        detail = (FIX / "simap/detail_award.json").read_bytes()

        def handler(req: httpx.Request) -> httpx.Response:
            if req.url.path == "/robots.txt":
                return httpx.Response(404)
            if "project-search" in req.url.path:
                return httpx.Response(200, json=search)
            return httpx.Response(200, content=detail)

        online = PoliteClient(
            HttpCache(tmp_path),
            offline=False,
            user_agent="t",
            min_interval_s=0,
            transport=httpx.MockTransport(handler),
            sleep=lambda s: None,
        )
        recs = SimapConnector().fetch(online, date(2026, 9, 1), date(2026, 9, 30))
        assert len(recs) == 1 and recs[0].fields["commune"] == "Sembrancher"
        assert not any(p.is_file() for p in tmp_path.rglob("*"))  # filtre avant tout enregistrement


class TestAmtsblatt:
    def test_blocked_rubrics_cannot_be_requested(self):
        for code in ("KK", "SB", "NA", "GB-VS01"):
            assert is_blocked(code)
            with pytest.raises(ValueError):
                AmtsblattConnector(codes=(code,))

    def test_requests_use_whitelisted_params_and_published_state(self):
        reqs = AmtsblattConnector(codes=("HR", "BA-VS05")).requests(date(2026, 9, 1), date(2026, 9, 30))
        assert reqs[0][1]["publicationStates"] == "PUBLISHED"
        assert reqs[0][1]["rubrics"] == "HR" and reqs[1][1]["subRubrics"] == "BA-VS05"

    def test_parse_hr_new_registration(self):
        recs = AmtsblattConnector().parse(_result(FIX / "amtsblatt/hr_new.xml"))
        assert len(recs) == 1 and recs[0].category == "registre_commerce"
        assert recs[0].fields["subtype"] == "nouvelle_inscription"
        assert recs[0].fields["uid"] == "CHE346292984"

    def test_excluded_rubric_is_rejected_at_parse(self):
        assert AmtsblattConnector().parse(_result(FIX / "amtsblatt/kk_bankruptcy.xml")) == []

    def test_allowlist_contains_no_person_rubric(self):
        assert not any(is_blocked(c) for c in ALLOWED)


class TestIngestion:
    def test_end_to_end_pii_and_schema(self):
        recs = (
            SimapConnector().parse(_result(FIX / "simap/detail_award.json"))
            + AmtsblattConnector().parse(_result(FIX / "amtsblatt/hr_new.xml"))
            + AmtsblattConnector().parse(_result(FIX / "amtsblatt/ba_private.xml"))
        )
        signals, companies, _log = ingest(recs)
        assert set(signals["family"]) == {"marche_attribue", "mutation_rc", "permis_construire"}
        blob = signals.to_json() + companies.to_json()
        assert "Dupont" not in blob  # aucun nom de particulier conservé
        private = signals[signals["family"] == "permis_construire"]
        assert private["company_id"].isna().all()
        assert set(companies["name"]) == {"Brevin Génie Civil SA", "Abrel Construction Sàrl"}
        assert {"source", "url", "retrieved_at", "license"} <= set(signals.columns)


def test_zefix_drops_person_fields():
    recs = ZefixConnector().parse(_result(FIX / "zefix/company.json"))
    assert len(recs) == 1
    assert "persons" not in recs[0].fields and "Dupont" not in json.dumps(recs[0].fields, ensure_ascii=False)


def test_geocoder_parses_search(tmp_path):
    body = (FIX / "geoadmin/search.json").read_bytes()
    client = PoliteClient(
        HttpCache(tmp_path),
        offline=False,
        user_agent="t",
        min_interval_s=0,
        transport=httpx.MockTransport(
            lambda r: httpx.Response(404) if r.url.path == "/robots.txt" else httpx.Response(200, content=body)
        ),
    )
    assert GeoAdminGeocoder(client).geocode("Sion") == (46.233, 7.36, "Sion (VS)")


def test_amtsblatt_and_base_fetch_never_store_raw_responses(tmp_path):
    """Consigne du 2026-10-05 : filtre des données personnelles AVANT tout enregistrement."""
    xml = (FIX / "amtsblatt/hr_new.xml").read_bytes()

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        if req.url.path.endswith("/xml"):
            return httpx.Response(200, content=xml)
        return httpx.Response(200, json={"content": [{"id": "FICTIF-HR01-0001"}]})

    calls: list[str] = []

    def counting(req: httpx.Request) -> httpx.Response:
        calls.append(str(req.url))
        return handler(req)

    client = PoliteClient(HttpCache(tmp_path), offline=False, user_agent="t", min_interval_s=0,
                          transport=httpx.MockTransport(counting), sleep=lambda s: None)
    # Décision du 2026-10-05 : FOSC / BO VS se consultent à la main ; le connecteur ne fait aucun appel.
    with pytest.raises(ManualOnlyHost):
        AmtsblattConnector(codes=("HR",)).fetch(client, date(2026, 9, 1), date(2026, 9, 30), max_pages=1)
    assert not any("amtsblattportal" in c for c in calls)
    ZefixConnector().fetch(client, date(2026, 9, 1), date(2026, 9, 30))
    assert not any(p.is_file() for p in tmp_path.rglob("*"))
