"""simap.ch connector. The fixtures are SYNTHETIC samples in the format observed on
2026-10-05 (field names and nesting), with invented names — never a recorded
real response, which would contain contact persons."""

import json
import re
from datetime import UTC, datetime

import httpx
import pytest

from proxsis.connectors import simap
from proxsis.http import HttpCache, PoliteClient

SUMMARY = {
    "id": "proj-1", "title": {"de": "BKP 211 Baumeisterarbeiten Schulhaus", "fr": None, "en": None, "it": None},
    "projectNumber": "1", "projectType": "tender", "projectSubType": "construction", "processType": "open",
    "publicationId": "pub-2", "publicationDate": "2026-10-05", "publicationNumber": "1-02", "pubType": "award",
    "procOfficeName": {"de": "Exempel Architekten AG"},
    "orderAddress": {"countryId": "CH", "cantonId": "LU", "postalCode": "6000", "city": {"de": "Musterdorf"}},
}


def _detail(vendor="Beispiel Bau AG", price=1234567.5, note=None):
    return {
        "id": "pub-2", "type": "award", "projectType": "tender",
        "procurement": {
            "orderType": "construction", "pubType": "award",
            "orderDescription": {"de": "<p>Baumeisterarbeiten. Auskunft: Herr Hans Muster, hans.muster@exemple.ch, "
                                       "Tel. 041 123 45 67</p>", "fr": None},
            "cpvCode": {"code": "45214200", "label": {"de": "Bauarbeiten für Schulgebäude", "fr": "Travaux"}},
            "bkpCodes": [{"code": "211", "label": {"de": "Baumeisterarbeiten",
                                                   "fr": "Travaux de l'entreprise de maçonnerie"}}],
            "npkCodes": [], "additionalCpvCodes": [],
        },
        "project-info": {
            "title": {"de": "BKP 211 Baumeisterarbeiten Schulhaus", "fr": None},
            "procOfficeAddress": {"name": {"de": "Exempel Architekten AG"},
                                  "contactPerson": {"de": "Hans Muster"},
                                  "phone": "+41411234567", "email": "hans.muster@exemple.ch",
                                  "cantonId": "LU", "city": {"de": "Musterstadt"}, "street": {"de": "Weg 1"}},
            "procurementRecipientAddress": {"name": {"de": "Gemeinde Musterdorf"},
                                            "contactPerson": {"de": "Anna Beispiel"},
                                            "phone": "+41761234567", "email": "anna@musterdorf.ch", "cantonId": "LU",
                                            "city": {"de": "Musterdorf"}},
        },
        "decision": {
            "vendors": [{"vendorName": vendor,
                         "vendorAddress": {"street": "Rue 3", "city": "Bern", "postalCode": "3018",
                                           "cantonId": "BE", "countryId": "CH"},
                         "price": {"currency": "CHF", "price": price, "vatType": "incl"}, "note": {"de": note}}],
            "numberOfSubmissions": 4, "awardDecisionDate": "2026-09-30",
        },
    }


EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"\+41\d{9}|0\d{2} \d{3} \d{2} \d{2}")


def test_normalize_keeps_only_allowlisted_fields_and_no_personal_data():
    rec, report = simap.normalize(SUMMARY, _detail(), retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    blob = json.dumps(rec, ensure_ascii=False)
    assert "Hans Muster" not in blob and "Anna Beispiel" not in blob
    assert not EMAIL.search(blob) and not PHONE.search(blob)
    assert "Weg 1" not in blob and "Rue 3" not in blob  # street addresses are not needed
    assert rec["vendors"][0]["name"] == "Beispiel Bau AG"
    assert rec["vendors"][0]["canton"] == "BE"
    assert rec["vendors"][0]["price_chf"] == 1234567.5
    assert rec["contracting_authority"] == "Gemeinde Musterdorf"
    assert rec["order_canton"] == "LU" and rec["order_city"] == "Musterdorf"
    assert rec["publication_date"] == "2026-10-05" and rec["decision_date"] == "2026-09-30"
    assert rec["bkp_codes"] == ["211"] and rec["cpv_code"] == "45214200"
    assert report.redactions >= 1


def test_normalize_carries_provenance_with_mandatory_notice():
    rec, _ = simap.normalize(SUMMARY, _detail(), retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    prov = rec["provenance"]
    assert prov["source"] == "simap.ch" and prov["content_sha256"] == "ab"
    assert prov["url"].startswith("https://www.simap.ch/api/publications/v1/project/proj-1/publication-details/pub-2")
    assert prov["fictif"] is False
    assert rec["mention_obligatoire"] == simap.MANDATORY_NOTICE
    assert "font foi" in simap.MANDATORY_NOTICE


def test_vendor_that_is_a_private_person_is_masked():
    rec, _ = simap.normalize(SUMMARY, _detail(vendor="Hans Muster"), retrieved_at=datetime(2026, 10, 5, tzinfo=UTC),
                             raw_sha256="ab")
    assert rec["vendors"][0]["name"] == "[particulier]"
    assert rec["private_person"] is True


def test_text_fields_are_redacted_before_return():
    rec, _ = simap.normalize(SUMMARY, _detail(), retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    assert "Baumeisterarbeiten" in rec["description"]["de"]
    assert "Muster" not in rec["description"]["de"]
    assert "<p>" not in rec["description"]["de"]


def _transport(pages, details, calls):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /fr/project-detail\n")
        if request.url.path.endswith("project-search"):
            last = request.url.params.get("lastItem")
            page = pages[0] if last is None else pages[1]
            return httpx.Response(200, json=page)
        return httpx.Response(200, json=details)

    return httpx.MockTransport(handler)


def test_fetch_writes_only_filtered_records(tmp_path):
    pages = [{"projects": [SUMMARY], "pagination": {"lastItem": "x|1", "itemsPerPage": 1}},
             {"projects": [], "pagination": {"lastItem": None, "itemsPerPage": 1}}]
    calls: list[str] = []
    cache_dir = tmp_path / "cache"
    client = PoliteClient(HttpCache(cache_dir), offline=False, user_agent="t",
                          transport=_transport(pages, _detail(), calls), sleep=lambda s: None)
    out = tmp_path / "simap.jsonl"
    n = simap.fetch_to_jsonl(client, out, lang="de", pub_types=("award_tender",), sub_types=("construction",),
                             date_from="2026-10-01", date_to="2026-10-05", max_pages=5)
    assert n == 1
    assert not cache_dir.exists() or not any(p.is_file() for p in cache_dir.rglob("*"))  # raw never stored
    line = out.read_text("utf-8")
    assert "hans.muster" not in line and "Hans Muster" not in line
    assert any("project-search" in c for c in calls) and any("publication-details" in c for c in calls)


@pytest.mark.parametrize("bad", ["award", "Award"])
def test_invalid_pub_type_rejected_before_any_call(bad):
    with pytest.raises(ValueError):
        simap.search_params(lang="fr", pub_types=(bad,), sub_types=("construction",), date_from="2026-10-01",
                            date_to="2026-10-05")


def test_fetch_is_resumable_and_does_not_refetch_known_publications(tmp_path):
    pages = [{"projects": [SUMMARY], "pagination": {"lastItem": None, "itemsPerPage": 1}}]
    out = tmp_path / "simap.jsonl"
    calls1: list[str] = []
    c1 = PoliteClient(HttpCache(tmp_path / "c"), offline=False, user_agent="t",
                      transport=_transport(pages, _detail(), calls1), sleep=lambda s: None)
    assert simap.fetch_to_jsonl(c1, out, lang="de", pub_types=("award_tender",), sub_types=("construction",),
                                date_from="2026-10-01", date_to="2026-10-05") == 1
    calls2: list[str] = []
    c2 = PoliteClient(HttpCache(tmp_path / "c"), offline=False, user_agent="t",
                      transport=_transport(pages, _detail(), calls2), sleep=lambda s: None)
    assert simap.fetch_to_jsonl(c2, out, lang="de", pub_types=("award_tender",), sub_types=("construction",),
                                date_from="2026-10-01", date_to="2026-10-05") == 0
    assert not any("publication-details" in c for c in calls2)
    assert len(out.read_text("utf-8").splitlines()) == 1


def test_price_kept_when_currency_is_lowercase_as_in_real_responses():
    d = _detail()
    d["decision"]["vendors"][0]["price"] = {"currency": "chf", "price": 484245.0, "vatType": "full"}
    rec, _ = simap.normalize(SUMMARY, d, retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    assert rec["vendors"][0]["price_chf"] == 484245.0
    d["decision"]["vendors"][0]["price"] = {"currency": "eur", "price": 10.0}
    rec, _ = simap.normalize(SUMMARY, d, retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    assert rec["vendors"][0]["price_chf"] is None


# --- Audit du 2026-10-05 (B1, M2, M7, m16)
@pytest.mark.parametrize("authority", ["HUG", "tpg", "Hôpitaux Universitaires de Genève", "Gymnase de La Cité",
                                       "Bundesamt für Bauten und Logistik BBL"])
def test_contracting_authority_is_a_public_body_and_keeps_its_name(authority):
    d = _detail()
    d["project-info"]["procurementRecipientAddress"]["name"] = {"de": authority}
    rec, _ = simap.normalize(SUMMARY, d, retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    assert rec["contracting_authority"] == authority


@pytest.mark.parametrize("vendor, masked", [
    ("Hans Muster", True), ("Anna Beispiel-Exempel", True),
    ("Thermo Fisher Scientific Inc.", False), ("Marti Bauunternehmung", False), ("Implenia Schweiz", False),
    ("Exemple Peinture", False), ("Stadler Rail", False),
])
def test_vendor_masked_only_when_it_looks_like_a_person(vendor, masked):
    rec, _ = simap.normalize(SUMMARY, _detail(vendor=vendor), retrieved_at=datetime(2026, 10, 5, tzinfo=UTC),
                             raw_sha256="ab")
    assert (rec["vendors"][0]["name"] == "[particulier]") is masked


def test_license_carries_the_mandatory_notice():
    assert simap.MANDATORY_NOTICE in simap.LICENSE


def test_past_award_publications_are_completed(tmp_path):
    out = tmp_path / "simap.jsonl"
    rec, _ = simap.normalize(SUMMARY | {"publicationNumber": "1-03"}, _detail(),
                             retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    out.write_text(json.dumps(rec, ensure_ascii=False) + "\n")
    past = {"pastPublications": [
        {"id": "pub-1", "publicationDate": "2026-05-04", "pubType": "tender"},
        {"id": "pub-0b", "publicationDate": "2026-06-01", "pubType": "award", "lotNumber": 1},
        {"id": "pub-2", "publicationDate": "2026-10-05", "pubType": "award"}]}
    calls: list[str] = []

    def handler(req):
        calls.append(req.url.path)
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        if req.url.path.endswith("past-publications"):
            return httpx.Response(200, json=past)
        return httpx.Response(200, json=_detail(vendor="Autre Lot SA"))

    c = PoliteClient(HttpCache(tmp_path / "c"), offline=False, user_agent="t", transport=httpx.MockTransport(handler),
                     sleep=lambda s: None)
    n = simap.complete_past_awards(c, out)
    lines = [json.loads(x) for x in out.read_text("utf-8").splitlines()]
    assert n == 1 and len(lines) == 2
    assert lines[1]["publication_id"] == "pub-0b" and lines[1]["publication_date"] == "2026-06-01"
    assert lines[1]["vendors"][0]["name"] == "Autre Lot SA"
    assert sum("publication-details" in c for c in calls) == 1  # pub-2 already known, tender skipped
    assert simap.complete_past_awards(c, out) == 0  # idempotent


def test_search_params_can_filter_by_issuing_organisation():
    p = simap.search_params("fr", ("award_tender",), ("construction",), "2024-07-01", "2026-09-30",
                            issued_by=(simap.VALAIS_ROOT,))
    assert p["issuedByOrganizations"] == [simap.VALAIS_ROOT]
    assert "orderAddressCantons" not in p


def test_refresh_rewrites_only_selected_records_with_the_current_filter(tmp_path):
    out = tmp_path / "simap.jsonl"
    old_style = {"id": "simap:pub-2", "project_id": "proj-1", "publication_id": "pub-2",
                 "publication_date": "2026-10-05",
                 "contracting_authority": "[particulier]", "vendors": [{"name": "[particulier]"}], "title": {},
                 "order_canton": "LU", "order_city": "Musterdorf", "order_postal_code": "6000"}
    keep = {"id": "simap:other", "project_id": "p9", "publication_id": "other", "contracting_authority": "Ville X",
            "vendors": [{"name": "Y SA"}]}
    out.write_text(json.dumps(keep) + "\n" + json.dumps(old_style) + "\n")
    calls: list[str] = []

    def handler(req):
        calls.append(req.url.path)
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(200, json=_detail(vendor="Marti Bauunternehmung"))

    c = PoliteClient(HttpCache(tmp_path / "c"), offline=False, user_agent="t", transport=httpx.MockTransport(handler),
                     sleep=lambda s: None)
    n = simap.refresh_records(c, out, lambda r: r["contracting_authority"] == "[particulier]")
    lines = [json.loads(x) for x in out.read_text("utf-8").splitlines()]
    assert n == 1 and len(lines) == 2 and lines[0] == keep
    assert lines[1]["contracting_authority"] == "Gemeinde Musterdorf"
    assert lines[1]["vendors"][0]["name"] == "Marti Bauunternehmung"
    assert lines[1]["publication_date"] == "2026-10-05" and lines[1]["order_city"] == "Musterdorf"
    assert sum("publication-details" in x for x in calls) == 1


def test_vendor_with_an_ide_is_a_registered_company_even_with_a_person_name():
    d = _detail(vendor="Hans Muster")
    d["decision"]["vendors"][0]["vendorUid"] = "CHE-116.281.710"  # valid check digit
    rec, _ = simap.normalize(SUMMARY, d, retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    v = rec["vendors"][0]
    assert v["name"] == "Hans Muster" and v["uid"] == "CHE116281710" and rec["private_person"] is False
    assert "street" not in json.dumps(v)  # company data only, no street address


def test_ide_found_anywhere_in_the_vendor_record_or_note():
    d = _detail(vendor="Hans Muster", note="Raison individuelle inscrite, CHE-116.281.710")
    rec, _ = simap.normalize(SUMMARY, d, retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    assert rec["vendors"][0]["uid"] == "CHE116281710" and rec["vendors"][0]["name"] == "Hans Muster"


@pytest.mark.parametrize("authority", ["Gaston exemplaire", "Exemple Rodolphe (PPE Les Prés)"])
def test_contracting_authority_that_looks_like_a_person_is_masked(authority):
    d = _detail()
    d["project-info"]["procurementRecipientAddress"]["name"] = {"fr": authority}
    rec, _ = simap.normalize(SUMMARY, d, retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    assert rec["contracting_authority"] == "[particulier]"


def test_parenthesised_details_of_an_authority_are_dropped():
    d = _detail()
    d["project-info"]["procurementRecipientAddress"]["name"] = {"fr": "Commune de Val de Bagnes (Exemple)"}
    rec, _ = simap.normalize(SUMMARY, d, retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    assert rec["contracting_authority"] == "Commune de Val de Bagnes"


def test_a_detail_that_does_not_answer_makes_the_fetch_fail_after_keeping_what_was_read(tmp_path):
    second = {**SUMMARY, "id": "p-9", "publicationId": "pub-9"}
    pages = [{"projects": [SUMMARY, second], "pagination": {"lastItem": None, "itemsPerPage": 2}}]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /fr/project-detail\n")
        if request.url.path.endswith("project-search"):
            return httpx.Response(200, json=pages[0])
        if "pub-9" in str(request.url):
            return httpx.Response(404)  # a detail that cannot be read: the week would be incomplete
        return httpx.Response(200, json=_detail())

    client = PoliteClient(HttpCache(tmp_path / "c"), offline=False, user_agent="t",
                          transport=httpx.MockTransport(handler), sleep=lambda s: None)
    out = tmp_path / "simap.jsonl"
    with pytest.raises(simap.SimapIncomplete, match="1 fiche"):
        simap.fetch_to_jsonl(client, out, lang="de", pub_types=("award_tender",), sub_types=("construction",),
                             date_from="2026-10-01", date_to="2026-10-05")
    assert len(out.read_text("utf-8").splitlines()) == 1  # what was read is kept: a new run completes it


def test_a_project_page_needs_a_project_id_and_is_never_none_in_the_address():
    assert simap.project_page(None) is None and simap.project_page("") is None
    assert simap.project_page("abc") == "https://www.simap.ch/fr/project-detail/abc"
    assert simap.project_page("abc", "de") == "https://www.simap.ch/de/project-detail/abc"
    assert simap.project_page("abc", "it") == "https://www.simap.ch/fr/project-detail/abc"


def test_correction_is_not_a_search_filter_of_simap():
    # verified on 13.10.2026 against the API (« newestPubTypes=correction » → HTTP 400, E0025 « Invalid parameter ») and
    # its specification (ProjectSearchPubTypeFilter: revocation and abandonment, no correction): refused before any call
    with pytest.raises(ValueError):
        simap.search_params(lang="fr", pub_types=("correction",), sub_types=("construction",), date_from="2026-10-12",
                            date_to="2026-10-12")
    assert simap.search_params(lang="fr", pub_types=simap.WITHDRAWAL_TYPES, sub_types=("construction",),
                               date_from="2026-10-12", date_to="2026-10-12")["newestPubTypes"] == ["revocation",
                                                                                                  "abandonment"]


def test_a_corrected_publication_is_marked_as_such():
    # a correction on simap is a new version of a publication, marked « corrected » in the search (simap.yaml,
    # ProjectsSearchEntryLatestPub.corrected)
    rec, _ = simap.normalize(SUMMARY | {"corrected": True}, _detail(), retrieved_at=datetime(2026, 10, 5, tzinfo=UTC),
                             raw_sha256="ab")
    assert rec["corrected"] is True
    rec, _ = simap.normalize(SUMMARY, _detail(), retrieved_at=datetime(2026, 10, 5, tzinfo=UTC), raw_sha256="ab")
    assert rec["corrected"] is False
