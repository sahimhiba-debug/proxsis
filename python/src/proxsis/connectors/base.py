"""Connector contract.

A connector knows (1) how to build polite requests for one public source and
(2) how to parse the responses into *raw records* (plain dicts). The
ingestion pipeline then applies the personal-data filter and maps records to
the normalised schema, keeping provenance (source, url, retrieved_at,
licence) on every row.

Endpoints and parameters come from public documentation (see
docs/recherche/donnees.md). Because the development environment cannot
reach the sources, the contract tests use SYNTHETIC samples shaped after the
documentation (``tests/fixtures/<source>/``, each marked ``_fixture_note``).
They must be replaced by recorded real responses as soon as the network is
open (``proxsis record --source <name>``).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from proxsis.http import FetchResult, PoliteClient
from proxsis.pii import PiiFilter


@dataclass
class RawRecord:
    source: str
    record_id: str
    category: str  # e.g. "adjudication", "registre_commerce", "permis_construire"
    event_date: date | None
    available_at: date
    url: str
    license: str
    retrieved_at: str
    fields: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        d = dict(self.fields)
        d.update(
            source=self.source,
            record_id=self.record_id,
            category=self.category,
            event_date=self.event_date,
            available_at=self.available_at,
            url=self.url,
            license=self.license,
            retrieved_at=self.retrieved_at,
        )
        return d


class Connector(ABC):
    name: str = "base"
    license: str = "inconnu"
    base_url: str = ""
    min_interval_s: float = 1.0

    @abstractmethod
    def requests(self, since: date, until: date, **kw: Any) -> list[tuple[str, dict[str, Any]]]:
        """List of (url, params) to fetch for the period."""

    @abstractmethod
    def parse(self, result: FetchResult) -> list[RawRecord]:
        """Parse one response into raw records."""

    def fetch(self, client: PoliteClient, since: date, until: date, **kw: Any) -> list[RawRecord]:
        out: list[RawRecord] = []
        for url, params in self.requests(since, until, **kw):
            # Raw responses may name persons: they stay in memory, the PII filter runs before anything is written.
            res = client.get(url, params=params, source=self.name, license=self.license, store_raw=False)
            if res.status == 200:
                out.extend(self.parse(res))
        return out


def apply_pii(records: list[RawRecord], f: PiiFilter | None = None) -> tuple[list[RawRecord], list[str]]:
    """Run the personal-data filter on raw records. Returns kept records and drop reasons."""
    f = f or PiiFilter()
    kept, dropped = [], []
    for r in records:
        res = f.apply({"category": r.category, **r.fields})
        if res.record is None:
            dropped.append(f"{r.source}:{r.record_id}: {res.dropped_reason}")
            continue
        res.record.pop("category", None)
        r.fields = res.record
        kept.append(r)
    return kept, dropped


def first_text(v: Any, lang: str = "fr") -> str:
    """simap-style multilingual values: str or {de, fr, it, en}."""
    if isinstance(v, dict):
        for k in (lang, "fr", "de", "it", "en"):
            if v.get(k):
                return str(v[k])
        return ""
    return "" if v is None else str(v)
