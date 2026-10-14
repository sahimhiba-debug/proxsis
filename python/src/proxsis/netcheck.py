"""Network check: which data domains actually answer from this machine.

One ``GET https://<domain>/robots.txt`` per domain (robots.txt is meant to be
fetched by automated clients), with the project User-Agent and a short
timeout. Any HTTP status (even 404 or 403 from the target) means the domain is
reachable; a proxy refusal, DNS or connection error means it is not.

Domains come from docs/recherche/donnees.md § 5.1. The domains the project
must never contact (§ 5.1, « À NE PAS autoriser ») are kept apart and are not
requested at all.
"""

from __future__ import annotations

import csv
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import httpx

USER_AGENT = "Proxsis/0.1 (prototype de recherche Hack VS 2026)"

# (domain, priority, usage) — priority 0 = control / AI gateway.
DOMAINS: list[tuple[str, int, str]] = [
    ("api.github.com", 0, "contrôle"),
    ("pypi.org", 0, "contrôle"),
    ("api.publicai.co", 0, "passerelle Public AI (Apertus)"),
    ("publicai.co", 0, "documentation Public AI"),
    ("www.simap.ch", 1, "API simap, conditions"),
    ("www.zefix.admin.ch", 1, "ZefixPublicREST"),
    ("www.zefix.ch", 1, "Zefix"),
    ("www.uid-wse.admin.ch", 1, "webservice IDE"),
    ("www.uid.admin.ch", 1, "registre IDE"),
    ("api3.geo.admin.ch", 1, "RegBL, géocodage"),
    ("api.geo.admin.ch", 1, "geo.admin"),
    ("data.geo.admin.ch", 1, "STAC MétéoSuisse"),
    ("wmts.geo.admin.ch", 1, "geo.admin"),
    ("www.geo.admin.ch", 1, "conditions, fair use"),
    ("docs.geo.admin.ch", 1, "documentation geo.admin"),
    ("public.madd.bfs.admin.ch", 1, "extraits RegBL"),
    ("www.housing-stat.ch", 1, "conditions RegBL"),
    ("www.pxweb.bfs.admin.ch", 1, "STAT-TAB"),
    ("www.bfs.admin.ch", 1, "OFS"),
    ("dam-api.bfs.admin.ch", 1, "fichiers OFS"),
    ("www.agvchapp.bfs.admin.ch", 1, "communes"),
    ("opendata.swiss", 1, "opendata.swiss"),
    ("ckan.opendata.swiss", 1, "API CKAN"),
    ("www.arbeit.swiss", 1, "obligation d'annonce"),
    ("www.amstat.ch", 1, "AMSTAT"),
    ("www.seco.admin.ch", 1, "SECO"),
    ("datenservice.kof.ethz.ch", 1, "KOF"),
    ("tsdb-api.kof.ethz.ch", 1, "KOF TSDB"),
    ("kof.ethz.ch", 1, "KOF"),
    ("openholidaysapi.org", 1, "jours fériés"),
    ("www.openholidaysapi.org", 1, "jours fériés"),
    ("date.nager.at", 1, "jours fériés"),
    ("edudoc.ch", 1, "vacances scolaires"),
    ("www.edk.ch", 1, "vacances scolaires"),
    ("opendatadocs.meteoswiss.ch", 1, "doc MétéoSuisse"),
    ("www.meteoschweiz.admin.ch", 1, "MétéoSuisse"),
    ("daten.statistik.zh.ch", 2, "OGD ZH"),
    ("www.web.statistik.zh.ch", 2, "OGD ZH"),
    ("data.stadt-zuerich.ch", 2, "OGD ville de Zurich"),
    ("data.bl.ch", 2, "OGD BL"),
    ("opendata.fr.ch", 2, "OGD FR"),
    ("www.vd.ch", 2, "canton VD"),
    ("www.vs.ch", 2, "canton VS"),
    ("www.fr.ch", 2, "canton FR"),
    ("sitg.ge.ch", 2, "SITG GE"),
    ("ge.ch", 2, "canton GE"),
    ("www.uvek-gis.admin.ch", 2, "Programme Bâtiments"),
    ("www.dasgebaeudeprogramm.ch", 2, "Programme Bâtiments"),
    ("www.swissstaffing.ch", 2, "indice swissstaffing"),
    ("baumeister.swiss", 2, "SSE"),
    ("www.ave-wbv.ch", 2, "congés bâtiment"),
    ("api.i14y.admin.ch", 2, "catalogue I14Y"),
    ("openplzapi.org", 2, "NPA"),
    ("transport.opendata.ch", 2, "trajets"),
    ("api.opentransportdata.swiss", 2, "OJP"),
    ("api-manager.opentransportdata.swiss", 2, "OJP clés"),
    ("opentransportdata.swiss", 2, "OJP conditions"),
    ("api.openrouteservice.org", 2, "trajets"),
    ("api.adzuna.com", 2, "Adzuna"),
    ("developer.adzuna.com", 2, "Adzuna conditions"),
    ("api.open-meteo.com", 2, "météo"),
    ("open-meteo.com", 2, "météo conditions"),
    ("schema.org", 2, "vocabulaire"),
    ("www.faovd.ch", 2, "FAO VD (après accord de l'éditeur)"),
    ("api.job-room.ch", 2, "Job-Room (après accord écrit du SECO)"),
    ("www.job-room.ch", 2, "Job-Room (après accord écrit du SECO)"),
    ("data.statistiques.developpement-durable.gouv.fr", 3, "Sitadel"),
    ("www.data.gouv.fr", 3, "data.gouv.fr"),
    ("www-genesis.destatis.de", 3, "Destatis"),
    ("genesis.destatis.de", 3, "Destatis"),
    ("www.regionalstatistik.de", 3, "Regionalstatistik"),
    ("www.planning.data.gov.uk", 3, "UK planning"),
    ("api.ted.europa.eu", 3, "TED"),
    ("docs.ted.europa.eu", 3, "TED doc"),
]

# FOSC / BO VS (proxsis.http.MANUAL_ONLY_HOSTS) are consulted by people only since 2026-10-05: not listed.
# docs/recherche/donnees.md § 5.1 « À NE PAS autoriser » : never requested.
NEVER_CONTACT: frozenset[str] = frozenset(
    {"app2.ge.ch", "www.jobs.ch", "www.jobup.ch", "www.indeed.ch", "ch.indeed.com", "www.linkedin.com",
     "router.project-osrm.org"}
)


@dataclass
class DomainCheck:
    domain: str
    url: str
    reachable: bool
    status: int | None
    error: str
    elapsed_s: float
    checked_at: str


def check_domain(domain: str, client: httpx.Client, timeout_s: float = 10.0) -> DomainCheck:
    if domain in NEVER_CONTACT:
        raise ValueError(f"{domain} ne doit jamais être contacté")
    url = f"https://{domain}/robots.txt"
    t0 = time.perf_counter()
    status: int | None = None
    error = ""
    try:
        resp = client.get(url, timeout=timeout_s)
        status = resp.status_code
    except httpx.HTTPError as exc:
        error = f"{type(exc).__name__}: {str(exc)[:160]}"
    return DomainCheck(domain, url, status is not None, status, error, round(time.perf_counter() - t0, 3),
                       datetime.now(UTC).isoformat(timespec="seconds"))


def run(out_csv: Path) -> list[DomainCheck]:
    results: list[DomainCheck] = []
    with httpx.Client(headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
        for domain, _prio, _use in DOMAINS:
            results.append(check_domain(domain, client))
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["priority", "usage", *asdict(results[0]).keys()])
        w.writeheader()
        for (_domain, prio, use), r in zip(DOMAINS, results, strict=True):
            w.writerow({"priority": prio, "usage": use, **asdict(r)})
    return results
