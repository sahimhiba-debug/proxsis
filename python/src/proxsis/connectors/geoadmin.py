"""geo.admin.ch — swisstopo geocoding (SearchServer) and RegBL/GWR building
status via the public REST API.

Documentation used (docs/recherche/donnees.md § 4.5 and § 4.14): base
``https://api3.geo.admin.ch/rest/services``; geocoding ``GET /api/SearchServer``
(``type=locations``, ``searchText``, ``sr=4326``); RegBL ``GET /api/MapServer/find``
on layer ``ch.bfs.gebaeude_wohnungs_register`` (building status codes GSTAT:
projected / authorised / under construction — code list to verify). Fair-use
limits apply (FAQ of api.geo.admin.ch).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from proxsis.connectors.base import Connector, RawRecord
from proxsis.http import FetchResult, PoliteClient

# GSTAT codes (catalogue RegBL, to verify against the official code list).
GSTAT = {"1001": "projete", "1002": "autorise", "1003": "en_construction", "1004": "existant"}


class GeoAdminGeocoder:
    name = "geo.admin.ch (swisstopo)"
    license = "Données géographiques de la Confédération, conditions d'utilisation geo.admin.ch (OGD) — fair use"
    url = "https://api3.geo.admin.ch/rest/services/api/SearchServer"

    def __init__(self, client: PoliteClient) -> None:
        self.client = client

    def geocode(self, text: str) -> tuple[float, float, str] | None:
        res = self.client.get(
            self.url,
            params={"type": "locations", "searchText": text, "sr": "4326", "limit": 1},
            source=self.name,
            license=self.license,
        )
        if res.status != 200:
            return None
        results = res.json().get("results") or []
        if not results:
            return None
        a = results[0].get("attrs", {})
        return float(a["lat"]), float(a["lon"]), str(a.get("label", ""))


class RegblConnector(Connector):
    name = "RegBL/GWR (geo.admin.ch)"
    license = (
        "OFS RegBL via geo.admin.ch — conditions d'utilisation des données publiques à vérifier "
        "(extraits contradictoires)"
    )
    base_url = "https://api3.geo.admin.ch/rest/services/api/MapServer/find"

    def requests(self, since: date, until: date, **kw: Any) -> list[tuple[str, dict[str, Any]]]:
        out = []
        for commune_code in kw.get("bfs_numbers", []):
            for gstat in ("1001", "1002", "1003"):
                out.append(
                    (
                        self.base_url,
                        {
                            "layer": "ch.bfs.gebaeude_wohnungs_register",
                            "searchField": "ggdenr",
                            "searchText": str(commune_code),
                            "returnGeometry": "false",
                            "contains": "false",
                            "gstat": gstat,
                        },
                    )
                )
        return out

    def parse(self, result: FetchResult) -> list[RawRecord]:
        out = []
        for r in result.json().get("results", []):
            a = r.get("attributes", {})
            status = GSTAT.get(str(a.get("gstat")), "autre")
            if status not in ("projete", "autorise", "en_construction"):
                continue
            # Minimisation: no owner, no address beyond the commune.
            out.append(
                RawRecord(
                    source=self.name,
                    record_id=str(a.get("egid") or r.get("id")),
                    category="batiment_projet",
                    event_date=None,
                    available_at=result.provenance.retrieved_at.date(),
                    url=result.url,
                    license=self.license,
                    retrieved_at=result.provenance.retrieved_at.isoformat(),
                    fields={
                        "status": status,
                        "commune": a.get("ggdename"),
                        "bfs": a.get("ggdenr"),
                        "canton": a.get("gdekt"),
                        "category_code": a.get("gkat"),
                        "construction_year": a.get("gbauj"),
                    },
                )
            )
        return out
