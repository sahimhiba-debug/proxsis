"""Real test of every catalogue line (data/catalogue.csv), politely.

For each line, the URLs tested on 2026-10-04 (column ``test_reel_2026_10_04``,
all blocked by the cloud proxy at the time) are requested again, unless:
* the verdict is ``non`` (project rule), or
* the source needs an account, a key or a written agreement (:data:`NO_CALL`):
  it is reported, never worked around, or
* robots.txt (RFC 9309) disallows the path.

Bodies are never stored (``store_raw=False``): only status, content type and
size are recorded.
"""

from __future__ import annotations

import csv
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from proxsis.http import HttpCache, PoliteClient, RobotsDisallowed, manual_only
from proxsis.netcheck import NEVER_CONTACT, USER_AGENT

NO_CALL: dict[str, str] = {
    "jobroom_api": "non appelé : accord écrit du SECO requis (règle du projet)",
    "vd_fao_camac": "non appelé : accord de l'éditeur de la FAO requis",
    "zefix_publicrest": "non appelé : compte obligatoire (zefix@bj.admin.ch) et robots.txt « Disallow: / »",
    "adzuna_api": "non appelé : clé d'API (inscription) et accord écrit d'usage commercial requis",
    "careerjet_api": "non appelé : identifiant partenaire requis (inscription)",
    "ojp_opentransportdata": "non appelé : clé d'API requise (inscription gratuite)",
    "openrouteservice": "non appelé : clé d'API requise (inscription)",
    "osrm_routage": "non appelé : serveur public réservé à un usage non commercial",
    "de_destatis_genesis": "non appelé : compte GENESIS requis (inscription)",
    "x28_donnees_emploi": "non appelé : contrat commercial requis",
    "baublatt_docu": "non appelé : contrat commercial requis",
    # Audit m6: the full cantonal extract (≈ 59 MB) was downloaded on 2026-10-05 although commercial use needs a
    # written confirmation from the FSO (housing-stat.ch); not requested again until then.
    "regbl_madd_dump": "non appelé : confirmation écrite de l'OFS requise avant tout usage commercial",
}

_GET = re.compile(r"GET (\S+) ->")


def plan_row(row: dict[str, str]) -> tuple[str, Any]:
    """("skip", reason) or ("call", [urls])."""
    if row.get("verdict") == "non":
        return "skip", "non appelé : verdict « non » (règle du projet)"
    if row["id"] in NO_CALL:
        return "skip", NO_CALL[row["id"]]
    found = _GET.findall(row.get("test_reel_2026_10_04", ""))
    if any(manual_only(u) for u in found):
        return "skip", "non appelé : consultation manuelle uniquement (décision de Hiba du 2026-10-05)"
    urls = [u for u in found if httpx.URL(u).host not in NEVER_CONTACT]
    if not urls:
        return "skip", "non appelé : aucune URL testable"
    return "call", urls


def probe_url(client: PoliteClient, url: str) -> dict[str, Any]:
    out: dict[str, Any] = {"url": url, "http": None, "type": "", "octets": 0, "resultat": ""}
    try:
        res = client.get(url, source="test-catalogue", license="test", store_raw=False)
    except RobotsDisallowed as exc:
        msg = str(exc)
        out["resultat"] = "robots.txt interdit" if "interdit par robots.txt" in msg else msg.split(" : http")[0]
        return out
    except httpx.HTTPError as exc:
        out["resultat"] = f"erreur réseau : {type(exc).__name__}"
        return out
    out.update(http=res.status, type=res.headers.get("content-type", ""), octets=len(res.body))
    out["resultat"] = "répond" if res.status < 400 else f"HTTP {res.status}"
    return out


def run(catalogue: Path, details_csv: Path, column: str = "test_reel_2026_10_05") -> list[dict[str, Any]]:
    rows = list(csv.DictReader(catalogue.open(encoding="utf-8")))
    client = PoliteClient(HttpCache(details_csv.parent / ".nocache"), offline=False, user_agent=USER_AGENT,
                          min_interval_s=2.0, timeout_s=20.0)
    details: list[dict[str, Any]] = []
    stamp = datetime.now(UTC).date().isoformat()
    for row in rows:
        action, payload = plan_row(row)
        if action == "skip":
            row[column] = f"{payload} ({stamp})"
            details.append({"id": row["id"], "url": "", "http": "", "type": "", "octets": "", "resultat": payload})
            continue
        parts = []
        for url in payload:
            r = probe_url(client, url)
            details.append({"id": row["id"], **r})
            code = r["http"] if r["http"] is not None else "—"
            parts.append(f"GET {url} -> {r['resultat']} (HTTP {code}, {r['type'] or 'type ?'}, {r['octets']} o)")
        row[column] = f"{' | '.join(parts)} ; testé le {stamp} depuis le Mac (réseau ouvert)"
    client.close()
    fields = list(rows[0].keys())
    if column not in fields:
        fields.insert(fields.index("test_reel_2026_10_04") + 1, column)
    with catalogue.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    details_csv.parent.mkdir(parents=True, exist_ok=True)
    with details_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "url", "http", "type", "octets", "resultat"])
        w.writeheader()
        w.writerows(details)
    return details
