"""Official directory of localities with postcodes (Amtliches Ortschaftenverzeichnis, swisstopo), WGS84 CSV.

Open government data: free use, the source must be cited (« Source : Office fédéral de topographie swisstopo »).
One ZIP (about 190 kB) fetched with the polite client (robots.txt, throttle); nothing else is called. Used to
place companies (simap gives the laureate's locality) and fictional candidates on the map and to compute
distances. Coordinates are those of the locality, not of an address.
"""

from __future__ import annotations

import csv
import io
import re
import unicodedata
import zipfile
from typing import Any

from proxsis.http import PoliteClient

URL = ("https://data.geo.admin.ch/ch.swisstopo-vd.ortschaftenverzeichnis_plz/ortschaftenverzeichnis_plz/"
       "ortschaftenverzeichnis_plz_4326.csv.zip")
SOURCE = "Office fédéral de topographie swisstopo, répertoire officiel des localités (OGD)"
LICENSE = "données ouvertes swisstopo : utilisation libre, indication de la source obligatoire"


def _key(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"\s+\d{1,2}$", "", s.strip())  # postal office number: « Sion 4 »
    s = re.sub(r"\s*\(?\b(vs|vd|ge|fr|ne|ju|be)\b\)?\s*$", "", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def parse(zip_bytes: bytes, cantons: tuple[str, ...] = ("VS",)) -> list[dict[str, Any]]:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        text = z.read(name).decode("utf-8-sig")
    out = []
    for r in csv.DictReader(io.StringIO(text), delimiter=";"):
        if cantons and r["Kantonskürzel"] not in cantons:
            continue
        out.append({"localite": r["Ortschaftsname"], "npa": r["PLZ4"], "commune": r["Gemeindename"],
                    "bfs": r["BFS-Nr"], "canton": r["Kantonskürzel"], "lat": float(r["N"]), "lon": float(r["E"]),
                    "langue": r["Sprache"], "source": SOURCE})
    return out


def fetch(client: PoliteClient, cantons: tuple[str, ...] = ("VS",)) -> list[dict[str, Any]]:
    res = client.get(URL, source=SOURCE, license=LICENSE, store_raw=False)
    if res.status != 200:
        raise RuntimeError(f"swisstopo : HTTP {res.status}")
    rows = parse(res.body, cantons)
    for r in rows:
        r["retrieved_at"] = res.provenance.retrieved_at.isoformat(timespec="seconds")
    return rows


def geocode(name: str, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Locality first (exact key), then commune; None when the name is not in the directory."""
    k = _key(name)
    if not k:
        return None
    for field in ("localite", "commune"):
        hits = [r for r in rows if _key(r[field]) == k]
        if hits:
            return hits[0]
    return None
