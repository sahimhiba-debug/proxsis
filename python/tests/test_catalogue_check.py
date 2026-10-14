import httpx

from proxsis.catalogue_check import NO_CALL, plan_row, probe_url
from proxsis.http import HttpCache, PoliteClient


def test_rows_with_verdict_non_are_never_called():
    action, reason = plan_row({"id": "ge_sad_consult", "verdict": "non", "test_reel_2026_10_04": "non teste"})
    assert action == "skip" and "non" in reason


def test_rows_requiring_agreement_or_account_are_not_called():
    for rid in ("jobroom_api", "zefix_publicrest", "adzuna_api", "osrm_routage"):
        assert rid in NO_CALL
        action, reason = plan_row({"id": rid, "verdict": "sous_conditions",
                                   "test_reel_2026_10_04": "GET https://x.ch/ -> 000"})
        assert action == "skip" and reason == NO_CALL[rid]


def test_row_urls_are_extracted_from_previous_test_column():
    action, urls = plan_row({"id": "openplz_api", "verdict": "sous_conditions",
                             "test_reel_2026_10_04":
                                 "GET https://openplzapi.org/ch/Localities?name=Sion -> curl: (56)"})
    assert action == "call" and urls == ["https://openplzapi.org/ch/Localities?name=Sion"]


def test_url_disallowed_by_robots_is_reported_not_called(tmp_path):
    calls = []

    def handler(req):
        calls.append(req.url.path)
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /api/\n")
        return httpx.Response(200, json={})

    c = PoliteClient(HttpCache(tmp_path), offline=False, user_agent="u", transport=httpx.MockTransport(handler),
                     sleep=lambda s: None)
    res = probe_url(c, "https://h.ch/api/x?q=1")
    assert res["resultat"] == "robots.txt interdit"
    assert calls == ["/robots.txt"]


def test_url_answer_is_recorded_without_storing_body(tmp_path):
    def handler(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(200, json={"a": 1}, headers={"content-type": "application/json"})

    c = PoliteClient(HttpCache(tmp_path), offline=False, user_agent="u", transport=httpx.MockTransport(handler),
                     sleep=lambda s: None)
    res = probe_url(c, "https://h.ch/data")
    assert res["http"] == 200 and res["type"].startswith("application/json") and res["octets"] > 0
    assert not any(p.is_file() for p in tmp_path.rglob("*"))


def test_manual_only_sources_are_not_called():
    action, reason = plan_row({"id": "amtsblatt_fosc_hr", "verdict": "sous_conditions",
                               "test_reel_2026_10_04": "GET https://amtsblattportal.ch/api/v1/publications -> 000"})
    assert action == "skip" and "manuelle" in reason
