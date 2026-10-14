import json
from datetime import UTC, datetime

import httpx
import pytest

from proxsis.http import HttpCache, OfflineCacheMiss, PoliteClient, RobotsDisallowed


def _transport(calls, robots="User-agent: *\nDisallow: /private\n", status=200):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=robots)
        return httpx.Response(status, json={"ok": True, "path": request.url.path})

    return httpx.MockTransport(handler)


class FakeClock:
    def __init__(self):
        self.t = 0.0
        self.sleeps: list[float] = []

    def now(self) -> float:
        return self.t

    def sleep(self, s: float) -> None:
        self.sleeps.append(s)
        self.t += s


def make_client(tmp_path, calls, offline=False, **kw):
    clock = FakeClock()
    c = PoliteClient(
        cache=HttpCache(tmp_path),
        offline=offline,
        user_agent="Proxsis-test",
        min_interval_s=1.0,
        transport=_transport(calls, **kw),
        monotonic=clock.now,
        sleep=clock.sleep,
        utcnow=lambda: datetime(2026, 10, 4, 12, tzinfo=UTC),
    )
    return c, clock


def test_fetch_then_replay_offline(tmp_path):
    calls: list[str] = []
    c, _ = make_client(tmp_path, calls)
    r1 = c.get("https://api.example.ch/data", params={"q": "1"}, source="example", license="CC-BY", store_raw=True)
    assert r1.status == 200 and not r1.from_cache
    assert r1.json()["ok"] is True
    assert r1.provenance.source == "example"
    assert r1.provenance.license == "CC-BY"
    assert r1.provenance.content_sha256

    calls2: list[str] = []
    off, _ = make_client(tmp_path, calls2, offline=True)
    r2 = off.get("https://api.example.ch/data", params={"q": "1"}, source="example", license="CC-BY", store_raw=True)
    assert r2.from_cache
    assert r2.body == r1.body
    assert calls2 == []  # aucun appel réseau


def test_offline_miss_raises(tmp_path):
    off, _ = make_client(tmp_path, [], offline=True)
    with pytest.raises(OfflineCacheMiss):
        off.get("https://api.example.ch/other", source="example", license="x")


def test_robots_disallow_is_respected(tmp_path):
    calls: list[str] = []
    c, _ = make_client(tmp_path, calls)
    with pytest.raises(RobotsDisallowed):
        c.get("https://api.example.ch/private/x", source="example", license="x")
    assert all("/private" not in u for u in calls)


def test_rate_limit_per_host(tmp_path):
    calls: list[str] = []
    c, clock = make_client(tmp_path, calls)
    c.get("https://api.example.ch/a", source="example", license="x")
    c.get("https://api.example.ch/b", source="example", license="x")
    # Deux requêtes de données sur le même hôte : au moins 1 s d'écart imposé
    assert any(s >= 0.99 for s in clock.sleeps)


def test_user_agent_sent(tmp_path):
    seen = {}

    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        seen["ua"] = request.headers.get("user-agent")
        return httpx.Response(200, text="x")

    c = PoliteClient(
        cache=HttpCache(tmp_path),
        offline=False,
        user_agent="Proxsis-test",
        transport=httpx.MockTransport(handler),
    )
    c.get("https://h.example.ch/x", source="s", license="l")
    assert seen["ua"] == "Proxsis-test"


def test_cache_key_depends_on_params(tmp_path):
    cache = HttpCache(tmp_path)
    assert cache.key("GET", "https://x.ch/a", {"p": "1"}) != cache.key("GET", "https://x.ch/a", {"p": "2"})
    assert cache.key("GET", "https://x.ch/a", {"a": "1", "b": "2"}) == cache.key(
        "GET", "https://x.ch/a", {"b": "2", "a": "1"}
    )


# --- RFC 9309 : la règle la plus précise l'emporte (le module standard applique l'ordre du fichier)
from proxsis.http import RobotsRules  # noqa: E402

ZH_ROBOTS = "User-agent: *\nDisallow: /\nAllow: /ogd/daten/ressourcen\nAllow: /datenkatalog\n"


def test_robots_longest_match_wins_over_file_order():
    r = RobotsRules.parse(ZH_ROBOTS, "Proxsis/0.1")
    assert r.allowed("/ogd/daten/ressourcen/KTZH_00002982_00006183.csv")
    assert not r.allowed("/ogd/data/KANTON_ZUERICH_ZEFIX_Neugruendungen.csv")
    assert not r.allowed("/")


def test_robots_wildcards_and_end_anchor():
    r = RobotsRules.parse("User-agent: *\nDisallow: /dataset/*/history\nDisallow: /*.pdf$\nAllow: /api/v1/", "x")
    assert not r.allowed("/dataset/abc/history")
    assert r.allowed("/dataset/abc")
    assert not r.allowed("/doc/file.pdf")
    assert r.allowed("/doc/file.pdf?x=1")
    assert r.allowed("/api/v1/things")


def test_robots_specific_group_beats_star_and_tie_allows():
    txt = "User-agent: *\nDisallow: /\n\nUser-agent: Proxsis\nAllow: /\nDisallow: /private\n"
    r = RobotsRules.parse(txt, "Proxsis/0.1 (contact)")
    assert r.allowed("/public") and not r.allowed("/private/x")
    tie = RobotsRules.parse("User-agent: *\nDisallow: /a\nAllow: /a\n", "x")
    assert tie.allowed("/a")


def test_robots_unreachable_means_disallow_and_4xx_means_allow(tmp_path):
    def handler(request):
        if request.url.host == "down.example.ch" and request.url.path == "/robots.txt":
            return httpx.Response(503)
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(200, text="ok")

    c = PoliteClient(cache=HttpCache(tmp_path), offline=False, user_agent="u",
                     transport=httpx.MockTransport(handler), sleep=lambda s: None)
    assert c.get("https://up.example.ch/x", source="s", license="l").status == 200
    with pytest.raises(RobotsDisallowed):
        c.get("https://down.example.ch/x", source="s", license="l")


def test_store_raw_false_writes_nothing_to_disk(tmp_path):
    calls: list[str] = []
    c, _ = make_client(tmp_path, calls)
    r = c.get("https://api.example.ch/people", source="s", license="l", store_raw=False)
    assert r.status == 200 and r.json()["ok"] is True
    assert not any(p.is_file() for p in tmp_path.rglob("*"))


def test_robots_refusal_reason_distinguishes_unreachable_from_disallowed(tmp_path):
    def handler(request):
        if request.url.host == "down.example.ch":
            raise httpx.ConnectError("refused")
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /\n")
        return httpx.Response(200, text="ok")

    c = PoliteClient(cache=HttpCache(tmp_path), offline=False, user_agent="u",
                     transport=httpx.MockTransport(handler), sleep=lambda s: None)
    with pytest.raises(RobotsDisallowed, match="injoignable"):
        c.get("https://down.example.ch/x", source="s", license="l")
    with pytest.raises(RobotsDisallowed, match=r"interdit par robots\.txt"):
        c.get("https://up.example.ch/x", source="s", license="l")


# --- Décision de Hiba (2026-10-05) : BO VS et FOSC se consultent à la main, jamais par un script.
from proxsis.http import MANUAL_ONLY_HOSTS, ManualOnlyHost  # noqa: E402


def test_manual_only_hosts_are_never_contacted_not_even_robots(tmp_path):
    calls: list[str] = []

    def handler(request):
        calls.append(str(request.url))
        return httpx.Response(200, text="User-agent: *\nAllow: /\n")

    c = PoliteClient(cache=HttpCache(tmp_path), offline=False, user_agent="u",
                     transport=httpx.MockTransport(handler), sleep=lambda s: None)
    for host in ("amtsblattportal.ch", "www.amtsblattportal.ch", "www.shab.ch", "bulletin-officiel.vs.ch"):
        assert host in MANUAL_ONLY_HOSTS
        with pytest.raises(ManualOnlyHost):
            c.get(f"https://{host}/api/v1/publications", source="s", license="l")
    assert calls == []


def test_manual_only_holds_offline_too(tmp_path):
    c = PoliteClient(cache=HttpCache(tmp_path), offline=True, user_agent="u")
    with pytest.raises(ManualOnlyHost):
        c.get("https://amtsblattportal.ch/x", source="s", license="l")


# --- Audit du 2026-10-05 (M1, m1, m2, m3, m4)
def _client(tmp_path, handler, **kw):
    return PoliteClient(cache=HttpCache(tmp_path), offline=False, user_agent="Proxsis/0.1 (x)",
                        transport=httpx.MockTransport(handler), sleep=lambda s: None, **kw)


def test_robots_check_includes_query_params(tmp_path):
    calls = []

    def handler(r):
        calls.append(str(r.url))
        if r.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /search?q=\n")
        return httpx.Response(200, text="ok")

    with pytest.raises(RobotsDisallowed):
        _client(tmp_path, handler).get("https://h.ch/search", params={"q": "x"}, source="s", license="l")
    assert not any("/search" in c for c in calls)


def test_redirect_target_is_checked_against_robots_and_manual_only(tmp_path):
    def handler(r):
        if r.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /private\n")
        if r.url.host == "a.ch" and r.url.path == "/go":
            return httpx.Response(302, headers={"location": "https://a.ch/private/x"})
        if r.url.host == "a.ch" and r.url.path == "/go2":
            return httpx.Response(302, headers={"location": "https://amtsblattportal.ch/api"})
        return httpx.Response(200, text="ok")

    c = _client(tmp_path, handler)
    with pytest.raises(RobotsDisallowed):
        c.get("https://a.ch/go", source="s", license="l")
    with pytest.raises(ManualOnlyHost):
        c.get("https://a.ch/go2", source="s", license="l")


def test_group_is_selected_by_exact_product_token_not_substring():
    for txt in ("User-agent: a\nAllow: /\n\nUser-agent: *\nDisallow: /\n",
                "User-agent: prox\nAllow: /\n\nUser-agent: *\nDisallow: /\n",
                "User-agent:\nAllow: /\n\nUser-agent: *\nDisallow: /\n"):
        assert not RobotsRules.parse(txt, "Proxsis/0.1").allowed("/x")
    assert RobotsRules.parse("User-agent: proxsis\nAllow: /\n\nUser-agent: *\nDisallow: /\n",
                             "Proxsis/0.1").allowed("/x")


def test_robots_429_means_disallow(tmp_path):
    def handler(r):
        if r.url.path == "/robots.txt":
            return httpx.Response(429)
        return httpx.Response(200, text="ok")

    with pytest.raises(RobotsDisallowed):
        _client(tmp_path, handler).get("https://h.ch/x", source="s", license="l")


def test_percent_encoding_is_normalised():
    r = RobotsRules.parse("User-agent: *\nDisallow: /~user\n", "x")
    assert not r.allowed("/%7Euser/page")


def test_raw_responses_are_not_stored_by_default(tmp_path):
    def handler(r):
        return httpx.Response(404) if r.url.path == "/robots.txt" else httpx.Response(200, text="ok")

    _client(tmp_path, handler).get("https://h.ch/x", source="s", license="l")
    assert not any(p.is_file() for p in tmp_path.rglob("*"))


def test_post_json_obeys_the_same_rules_as_get(tmp_path):
    seen = []

    def handler(r):
        seen.append((r.method, r.url.path))
        if r.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /private\n")
        return httpx.Response(200, json={"ok": True, "echo": json.loads(r.content)})

    c = _client(tmp_path, handler)
    res = c.post_json("https://h.ch/api/table", {"query": []}, source="s", license="l")
    assert res.status == 200 and res.json()["echo"] == {"query": []}
    with pytest.raises(RobotsDisallowed):
        c.post_json("https://h.ch/private/x", {}, source="s", license="l")
    with pytest.raises(ManualOnlyHost):
        c.post_json("https://amtsblattportal.ch/api", {}, source="s", license="l")
    assert ("POST", "/private/x") not in seen
    assert not any(p.is_file() for p in tmp_path.rglob("*"))


# --- Review 1 of the mission (07.10.2026, M3)
def test_a_subdomain_of_a_manual_only_site_is_never_contacted(tmp_path):
    calls: list[str] = []

    def handler(r):
        calls.append(str(r.url))
        return httpx.Response(200, text="User-agent: *\nAllow: /\n")

    with pytest.raises(ManualOnlyHost):
        _client(tmp_path, handler).get("https://api.amtsblattportal.ch/v1/x", source="s", license="l")
    assert calls == []


def test_robots_txt_never_follows_a_redirect_to_a_manual_only_site(tmp_path):
    calls: list[str] = []

    def handler(r):
        calls.append(str(r.url))
        if r.url.host == "a.ch" and r.url.path == "/robots.txt":
            return httpx.Response(301, headers={"location": "https://www.shab.ch/robots.txt"})
        return httpx.Response(200, text="ok")

    with pytest.raises(ManualOnlyHost):
        _client(tmp_path, handler).get("https://a.ch/page", source="s", license="l")
    assert not any("shab.ch" in c for c in calls)


def test_a_server_that_keeps_refusing_raises_instead_of_returning_its_refusal(tmp_path):
    from proxsis.http import RateLimited

    def handler(r):
        if r.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /\n")
        return httpx.Response(429, headers={"retry-after": "1"})

    with pytest.raises(RateLimited, match="429"):
        _client(tmp_path, handler).get("https://a.ch/x", source="s", license="l")
