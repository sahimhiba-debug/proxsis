import httpx

from proxsis.netcheck import DOMAINS, NEVER_CONTACT, check_domain


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler), headers={"User-Agent": "test"})


def test_http_answer_is_reachable_even_if_404():
    c = _client(lambda r: httpx.Response(404))
    res = check_domain("exemple.ch", client=c)
    assert res.reachable is True
    assert res.status == 404
    assert res.url == "https://exemple.ch/robots.txt"


def test_proxy_refusal_is_blocked_not_reachable():
    def handler(request):
        raise httpx.ProxyError("CONNECT tunnel failed, response 403")

    res = check_domain("exemple.ch", client=_client(handler))
    assert res.reachable is False
    assert res.status is None
    assert "ProxyError" in res.error


def test_connect_error_is_recorded():
    def handler(request):
        raise httpx.ConnectError("nodename nor servname provided")

    res = check_domain("exemple.ch", client=_client(handler))
    assert res.reachable is False
    assert "ConnectError" in res.error


def test_forbidden_domains_are_never_in_the_check_list():
    listed = {d for d, _prio, _use in DOMAINS}
    assert listed.isdisjoint(NEVER_CONTACT)
    assert "router.project-osrm.org" in NEVER_CONTACT
    assert "www.simap.ch" in listed


def test_manual_only_hosts_are_not_in_the_automatic_check():
    from proxsis.http import MANUAL_ONLY_HOSTS

    assert {d for d, _p, _u in DOMAINS}.isdisjoint(MANUAL_ONLY_HOSTS)
