"""amtsblattportal.ch — FOSC/SHAB (commercial register) and cantonal official
gazettes (incl. Bulletin officiel du Valais).

Documentation used (docs/recherche/donnees.md § 4.2): base
``https://amtsblattportal.ch/api/v1``; ``GET /publications`` (metadata only,
``publicationStates=PUBLISHED`` mandatory, filters ``rubrics``,
``subRubrics``, ``cantons``, ``publicationDate.start/end``,
``pageRequest.page/size``); full text in ``GET /publications/{id}/xml``.
Pitfall: unknown parameter names are silently ignored and return the whole
corpus → requests are built from a whitelist of parameters.

Personal data: ALLOWLIST of rubrics. Rubrics about natural persons
(bankruptcies, debt enforcement, successions, civil status, land register…)
can never be requested: ``requests`` raises ``ValueError``.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date
from typing import Any

from proxsis.connectors.base import Connector, RawRecord
from proxsis.entities import normalize_uid
from proxsis.http import FetchResult, PoliteClient

# rubric/sub-rubric -> Proxsis category
ALLOWED: dict[str, str] = {
    "HR": "registre_commerce",
    "HR01": "registre_commerce",
    "HR02": "registre_commerce",
    "HR03": "registre_commerce",
    "BA-VS05": "permis_construire",
    "BA-VS10": "grand_projet",
    "BA-VS15": "grand_projet",
    "BA-VS20": "grand_projet",
    "AR-VS40": "adjudication",
    "AL-VS20": "offre_emploi_publique",
}
BLOCKED_PREFIXES = (
    "KK",
    "SB",
    "LS",
    "SR",
    "NA",
    "ES",
    "TE",
    "VA",
    "FZ",
    "BV",
    "BU",
    "UV",
    "GB",
    "GE",
    "SJ",
    "GR",
    "AA-GR",
)
_PARAMS_WHITELIST = {
    "publicationStates",
    "rubrics",
    "subRubrics",
    "cantons",
    "publicationDate.start",
    "publicationDate.end",
    "pageRequest.page",
    "pageRequest.size",
}
_HR_SUBTYPE = [
    ("radiation", r"radi(é|e)e|gelöscht|Löschung"),
    ("liquidation", r"liquidation|aufgelöst"),
    ("succursale", r"succursale|Zweigniederlassung"),
    ("augmentation_capital", r"augmentation du capital|Kapitalerhöhung|capital-actions.*?à CHF|Aktienkapital neu"),
    ("transfert_siege", r"Sitz neu|siège transféré|nouveau siège"),
    ("changement_but", r"nouveau but|Zweck neu"),
    ("nouvelle_inscription", r"nouvelle inscription|Neueintragung"),
]


def is_blocked(code: str) -> bool:
    """True for rubrics about natural persons. Anything not allowlisted is refused anyway."""
    if code in ALLOWED:
        return False
    return any(code == p or code.startswith(p) for p in BLOCKED_PREFIXES)


class AmtsblattConnector(Connector):
    name = "amtsblattportal.ch"
    license = "Accès libre selon la documentation de l'API ; CGU du portail à vérifier ; seul le PDF signé fait foi"
    base_url = "https://amtsblattportal.ch/api/v1"
    min_interval_s = 1.5

    def __init__(self, cantons: tuple[str, ...] = ("VS",), codes: tuple[str, ...] = ("HR", "BA-VS05")) -> None:
        for c in codes:
            if c not in ALLOWED or is_blocked(c):
                raise ValueError(f"rubrique non autorisée (liste blanche) : {c}")
        self.cantons = cantons
        self.codes = codes

    def requests(self, since: date, until: date, **kw: Any) -> list[tuple[str, dict[str, Any]]]:
        out = []
        for code in self.codes:
            key = "rubrics" if "-" not in code and len(code) <= 2 else "subRubrics"
            params = {
                "publicationStates": "PUBLISHED",
                key: code,
                "cantons": ",".join(self.cantons),
                "publicationDate.start": since.isoformat(),
                "publicationDate.end": until.isoformat(),
                "pageRequest.size": 100,
                "pageRequest.page": int(kw.get("page", 0)),
            }
            assert set(params) <= _PARAMS_WHITELIST
            out.append((f"{self.base_url}/publications", params))
        return out

    def fetch(self, client: PoliteClient, since: date, until: date, **kw: Any) -> list[RawRecord]:
        out: list[RawRecord] = []
        for url, params in self.requests(since, until):
            for page in range(int(kw.get("max_pages", 20))):
                params = {**params, "pageRequest.page": page}
                res = client.get(url, params=params, source=self.name, license=self.license, store_raw=False)
                if res.status != 200:
                    break
                items = _items(res.json())
                for it in items:
                    pid = it.get("id") or (it.get("meta") or {}).get("id")
                    xml = client.get(f"{self.base_url}/publications/{pid}/xml", source=self.name,
                                     license=self.license, store_raw=False)  # texts name persons: never stored raw
                    if xml.status == 200:
                        out.extend(self.parse(xml))
                if len(items) < int(params["pageRequest.size"]):
                    break
        return out

    def parse(self, result: FetchResult) -> list[RawRecord]:
        root = ET.fromstring(result.body)
        texts = {_local(e.tag): (e.text or "").strip() for e in root.iter() if (e.text or "").strip()}
        code = texts.get("subRubric") or texts.get("rubric") or ""
        if is_blocked(code) or code not in ALLOWED:
            return []  # defence in depth: never keep a non-allowlisted rubric
        pub = _date(texts.get("publicationDate"))
        if pub is None:
            return []
        body = " ".join(
            v
            for k, v in texts.items()
            if k in ("title", "publicationText", "text", "content", "purpose", "description", "projectDescription")
        )
        category = ALLOWED[code]
        fields: dict[str, Any] = {
            "rubric": code,
            "title": texts.get("title", ""),
            "text": body,
            "uid": normalize_uid(texts.get("uid")),
            "company_name": texts.get("name") or texts.get("companyName"),
            "commune": texts.get("town") or texts.get("municipality") or texts.get("seat"),
            "canton": texts.get("canton") or texts.get("cantons"),
            "applicant": texts.get("applicant") or texts.get("builder"),
            "owner": texts.get("landowner") or texts.get("owner"),
        }
        if category == "registre_commerce":
            fields["subtype"] = next((s for s, rx in _HR_SUBTYPE if re.search(rx, body, re.IGNORECASE)), "autre")
        return [
            RawRecord(
                self.name,
                texts.get("id") or texts.get("publicationNumber") or result.url,
                category,
                pub,
                pub,
                result.url,
                self.license,
                result.provenance.retrieved_at.isoformat(),
                fields,
            )
        ]


def _items(body: Any) -> list[dict[str, Any]]:
    if isinstance(body, list):
        return body
    for key in ("content", "publications", "items", "data"):
        if isinstance(body.get(key), list):
            return list(body[key])
    return []


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _date(v: str | None) -> date | None:
    if not v:
        return None
    try:
        return date.fromisoformat(v[:10])
    except ValueError:
        return None
