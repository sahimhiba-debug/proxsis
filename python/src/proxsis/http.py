"""Polite HTTP client with an on-disk cache and offline replay.

* Every response is stored on disk (body + metadata) under a deterministic
  key; ``offline=True`` replays the cache and never touches the network
  (this is how the demo runs without connectivity).
* robots.txt is fetched once per host and respected, with RFC 9309 semantics
  (the most specific rule wins, unlike ``urllib.robotparser`` which applies
  rules in file order); 4xx = no restriction, 5xx or unreachable = disallow.
* ``store_raw=False`` keeps the raw body in memory only: sources that may
  contain personal data are filtered by the connector *before* anything is
  written (the raw response never touches the disk).
* A minimum interval between two requests to the same host is enforced;
  ``429``/``503`` responses are retried with ``Retry-After`` (max 3 times).
* Each result carries a :class:`~proxsis.provenance.Provenance`.
"""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlencode, urlsplit

import httpx

from proxsis.provenance import Provenance, content_hash


class OfflineCacheMiss(LookupError):
    """Offline mode and the request is not in the cache."""


class RobotsDisallowed(PermissionError):
    """robots.txt forbids this path for our user agent."""


class ManualOnlyHost(PermissionError):
    """This host is consulted by people only, never by a script (decision of 2026-10-05)."""


# Bulletin officiel du Valais and FOSC/SHAB (amtsblattportal): manual consultation only.
# No request at all, not even robots.txt (docs/annotation/consigne_collecte_manuelle.md).
MANUAL_ONLY_HOSTS: frozenset[str] = frozenset({
    "amtsblattportal.ch", "www.amtsblattportal.ch", "shab.ch", "www.shab.ch", "bulletin-officiel.vs.ch",
})


def manual_only(url: str) -> bool:
    """The host of ``url`` is one of MANUAL_ONLY_HOSTS or one of their subdomains (« api.amtsblattportal.ch »)."""
    host = (urlsplit(url).hostname or "").lower()
    return any(host == h or host.endswith("." + h) for h in MANUAL_ONLY_HOSTS)


class RateLimited(RuntimeError):
    """The server kept answering 429 or 503 after every retry: an error, never a response passed on as data."""


@dataclass
class FetchResult:
    url: str
    status: int
    body: bytes
    headers: dict[str, str]
    provenance: Provenance
    from_cache: bool

    def json(self) -> Any:
        return json.loads(self.body)

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


@dataclass
class RobotsRules:
    """robots.txt rules for one user agent, matched per RFC 9309."""

    rules: list[tuple[bool, str]]  # (allow, pattern)

    @classmethod
    def allow_all(cls) -> RobotsRules:
        return cls([])

    @classmethod
    def disallow_all(cls) -> RobotsRules:
        return cls([(False, "/")])

    @classmethod
    def parse(cls, text: str, user_agent: str) -> RobotsRules:
        token = user_agent.split("/")[0].strip().lower()
        groups: list[tuple[list[str], list[tuple[bool, str]]]] = []
        agents: list[str] = []
        rules: list[tuple[bool, str]] = []
        last_was_agent = False
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            key, value = (x.strip() for x in line.split(":", 1))
            key = key.lower()
            if key == "user-agent":
                if not last_was_agent and (agents or rules):
                    groups.append((agents, rules))
                    agents, rules = [], []
                agents.append(value.lower())
                last_was_agent = True
            elif key in ("allow", "disallow"):
                last_was_agent = False
                if value:
                    rules.append((key == "allow", value))
        if agents or rules:
            groups.append((agents, rules))
        # RFC 9309: the group whose user-agent equals our product token (case-insensitive); never a substring.
        specific = [r for a, r in groups if any(x and x != "*" and x == token for x in a)]
        chosen = specific or [r for a, r in groups if "*" in a]
        return cls([rule for g in chosen for rule in g])

    @staticmethod
    def _match(pattern: str, path: str) -> bool:
        pattern, path = unquote(pattern), unquote(path)  # %7E and ~ are the same path
        anchored = pattern.endswith("$")
        body = pattern[:-1] if anchored else pattern
        rx = "".join(".*" if ch == "*" else re.escape(ch) for ch in body)
        return re.match(rx + ("$" if anchored else ""), path) is not None

    def allowed(self, path: str) -> bool:
        best_len, best_allow = -1, True
        for allow, pattern in self.rules:
            if self._match(pattern, path):
                n = len(pattern)
                if n > best_len or (n == best_len and allow):
                    best_len, best_allow = n, allow
        return best_allow


class HttpCache:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    @staticmethod
    def key(method: str, url: str, params: Mapping[str, Any] | None = None) -> str:
        q = urlencode(sorted((params or {}).items()), doseq=True)
        return content_hash(f"{method.upper()} {url}?{q}".encode())

    def _paths(self, key: str) -> tuple[Path, Path]:
        d = self.root / key[:2]
        return d / f"{key}.json", d / f"{key}.body"

    def get(self, key: str) -> tuple[dict[str, Any], bytes] | None:
        meta_p, body_p = self._paths(key)
        if not meta_p.exists() or not body_p.exists():
            return None
        return json.loads(meta_p.read_text("utf-8")), body_p.read_bytes()

    def put(self, key: str, meta: dict[str, Any], body: bytes) -> None:
        meta_p, body_p = self._paths(key)
        meta_p.parent.mkdir(parents=True, exist_ok=True)
        body_p.write_bytes(body)
        meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), "utf-8")


class PoliteClient:
    def __init__(
        self,
        cache: HttpCache,
        offline: bool,
        user_agent: str,
        min_interval_s: float = 1.0,
        transport: httpx.BaseTransport | None = None,
        respect_robots: bool = True,
        timeout_s: float = 30.0,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        utcnow: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.cache = cache
        self.offline = offline
        self.user_agent = user_agent
        self.min_interval_s = min_interval_s
        self.respect_robots = respect_robots
        self._monotonic = monotonic
        self._sleep = sleep
        self._utcnow = utcnow
        self._last_call: dict[str, float] = {}
        self._robots: dict[str, RobotsRules] = {}
        self._robots_note: dict[str, str] = {}
        self._http = httpx.Client(
            transport=transport,
            timeout=timeout_s,
            headers={"User-Agent": user_agent},
            follow_redirects=False,  # each redirect target is checked (manual-only hosts, robots.txt)
        )

    # -- politeness -------------------------------------------------------
    def _throttle(self, host: str) -> None:
        last = self._last_call.get(host)
        if last is not None:
            wait = self.min_interval_s - (self._monotonic() - last)
            if wait > 0:
                self._sleep(wait)
        self._last_call[host] = self._monotonic()

    def _robots_for(self, scheme: str, host: str) -> RobotsRules:
        if host in self._robots:
            return self._robots[host]
        try:
            url = f"{scheme}://{host}/robots.txt"
            for _hop in range(6):  # robots.txt itself + at most 5 redirects, each checked like any request
                if manual_only(url):
                    raise ManualOnlyHost(f"robots.txt redirigé vers un site en consultation manuelle : {url}")
                self._throttle(urlsplit(url).netloc)
                resp = self._http.get(url)
                if not resp.is_redirect:
                    break
                url = str(resp.url.join(resp.headers.get("location", "")))
            if resp.status_code == 200:
                rules, note = RobotsRules.parse(resp.text, self.user_agent), "interdit par robots.txt"
            elif 400 <= resp.status_code < 500 and resp.status_code != 429:
                rules, note = RobotsRules.allow_all(), ""
            else:
                rules = RobotsRules.disallow_all()
                note = f"robots.txt injoignable (HTTP {resp.status_code}) : accès refusé par prudence (RFC 9309)"
        except httpx.HTTPError as exc:
            rules = RobotsRules.disallow_all()
            note = f"serveur injoignable ({type(exc).__name__}) : accès refusé par prudence (RFC 9309)"
        self._robots[host] = rules
        self._robots_note[host] = note
        return rules

    def _check_robots(self, url: str) -> None:
        if not self.respect_robots:
            return
        parts = urlsplit(url)
        path = parts.path or "/"
        if parts.query:
            path += "?" + parts.query
        if not self._robots_for(parts.scheme, parts.netloc).allowed(path):
            raise RobotsDisallowed(f"{self._robots_note.get(parts.netloc, 'interdit par robots.txt')} : {url}")

    # -- API --------------------------------------------------------------
    def get(
        self,
        url: str,
        *,
        source: str,
        license: str,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        refresh: bool = False,
        store_raw: bool = False,
    ) -> FetchResult:
        if manual_only(url):
            raise ManualOnlyHost(f"consultation manuelle uniquement : {url}")
        key = self.cache.key("GET", url, params)
        cached = self.cache.get(key) if store_raw else None
        if cached is not None and (self.offline or not refresh):
            meta, body = cached
            prov = Provenance(
                source=meta["source"],
                url=meta["url"],
                retrieved_at=datetime.fromisoformat(meta["retrieved_at"]),
                license=meta["license"],
                content_sha256=meta.get("sha256"),
            )
            return FetchResult(meta["url"], meta["status"], body, meta.get("headers", {}), prov, True)
        if self.offline:
            raise OfflineCacheMiss(f"{url} {dict(params or {})}")

        target = str(httpx.URL(url, params=params)) if params else url
        resp: httpx.Response | None = None
        for _hop in range(6):  # the request itself + at most 5 redirects, each one checked
            if manual_only(target):
                raise ManualOnlyHost(f"redirection vers un site en consultation manuelle : {target}")
            self._check_robots(target)
            host = urlsplit(target).netloc
            for _attempt in range(4):
                self._throttle(host)
                resp = self._http.get(target, headers=headers)
                if resp.status_code not in (429, 503):
                    break
                retry_after = resp.headers.get("retry-after", "")
                delay = float(retry_after) if retry_after.isdigit() else 2.0 * (2**_attempt)
                self._sleep(min(delay, 60.0))
            else:
                raise RateLimited(f"HTTP 429 ou 503 après 4 essais : {target}")
            if not resp.is_redirect:
                break
            target = str(resp.url.join(resp.headers.get("location", "")))
        if resp is None:  # unreachable: the loops above always send at least one request
            raise RuntimeError(f"aucune réponse pour {url}")
        body = resp.content
        full_url = str(resp.request.url)
        retrieved = self._utcnow()
        sha = content_hash(body)
        meta = {
            "source": source,
            "url": full_url,
            "status": resp.status_code,
            "retrieved_at": retrieved.isoformat(),
            "license": license,
            "sha256": sha,
            "headers": {
                k: v for k, v in resp.headers.items() if k.lower() in ("content-type", "etag", "last-modified")
            },
        }
        if resp.status_code == 200 and store_raw:
            self.cache.put(key, meta, body)
        prov = Provenance(source=source, url=full_url, retrieved_at=retrieved, license=license, content_sha256=sha)
        return FetchResult(full_url, resp.status_code, body, meta["headers"], prov, False)

    def post_json(self, url: str, payload: Any, *, source: str, license: str) -> FetchResult:
        """POST a JSON query (e.g. PxWeb tables) with the same rules as :meth:`get` (manual-only hosts,
        robots.txt, pace). Never cached: the answer depends on the body."""
        if self.offline:
            raise OfflineCacheMiss(f"POST {url}")
        if manual_only(url):
            raise ManualOnlyHost(f"consultation manuelle uniquement : {url}")
        self._check_robots(url)
        self._throttle(urlsplit(url).netloc)
        resp = self._http.post(url, json=payload)
        body = resp.content
        retrieved = self._utcnow()
        sha = content_hash(body)
        prov = Provenance(source=source, url=url, retrieved_at=retrieved, license=license, content_sha256=sha)
        headers = {k: v for k, v in resp.headers.items() if k.lower() in ("content-type", "etag", "last-modified")}
        return FetchResult(url, resp.status_code, body, headers, prov, False)

    def close(self) -> None:
        self._http.close()
