"""Zefix PublicREST — commercial register (identity, UID, seat, status).

Documentation used (docs/recherche/donnees.md § 4.3): base
``https://www.zefix.admin.ch/ZefixPublicREST/api/v1``; Basic Auth mandatory
(free account requested from zefix@bj.admin.ch); ``GET /company/uid/{uid}``,
``POST /company/search``, ``GET /sogc/bydate/{date}``.

Minimisation: person fields (signatories, board members, owners of sole
proprietorships) are never imported — only legal name, UID, legal form,
seat, status and purpose. The undocumented website API (ZefixREST) is NOT
used (verdict "non" in the catalogue).
"""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import httpx

from proxsis.connectors.base import Connector, RawRecord
from proxsis.entities import normalize_uid
from proxsis.http import FetchResult

KEPT_FIELDS = ("name", "uid", "legalForm", "legalSeat", "status", "purpose", "canton", "sogcDate", "chid")


class ZefixConnector(Connector):
    name = "zefix"
    license = "opendata.swiss « zefix-zentraler-firmenindex » : terms_by (citation de la source) — texte à vérifier"
    base_url = "https://www.zefix.admin.ch/ZefixPublicREST/api/v1"

    def auth(self) -> httpx.BasicAuth | None:
        user, pwd = os.environ.get("ZEFIX_API_USER"), os.environ.get("ZEFIX_API_PASSWORD")
        return httpx.BasicAuth(user, pwd) if user and pwd else None

    def requests(self, since: date, until: date, **kw: Any) -> list[tuple[str, dict[str, Any]]]:
        uids = kw.get("uids") or []
        return [(f"{self.base_url}/company/uid/{normalize_uid(u)}", {}) for u in uids if normalize_uid(u)]

    def parse(self, result: FetchResult) -> list[RawRecord]:
        body = result.json()
        items = body if isinstance(body, list) else [body]
        out = []
        for it in items:
            kept = {k: it.get(k) for k in KEPT_FIELDS if k in it}
            uid = normalize_uid(str(kept.get("uid") or ""))
            if not uid or not kept.get("name"):
                continue
            seat = kept.get("legalSeat")
            out.append(
                RawRecord(
                    source=self.name,
                    record_id=uid,
                    category="identite_entreprise",
                    event_date=None,
                    available_at=result.provenance.retrieved_at.date(),
                    url=result.url,
                    license=self.license,
                    retrieved_at=result.provenance.retrieved_at.isoformat(),
                    fields={
                        "company_name": kept["name"],
                        "uid": uid,
                        "legal_form": (kept.get("legalForm") or {}).get("shortName", {}).get("fr")
                        if isinstance(kept.get("legalForm"), dict)
                        else kept.get("legalForm"),
                        "commune": seat if isinstance(seat, str) else None,
                        "canton": kept.get("canton"),
                        "status": kept.get("status"),
                        "purpose": kept.get("purpose"),
                    },
                )
            )
        return out
