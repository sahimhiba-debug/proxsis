"""Data of the « Votre prochain lundi » presentation (apps/web/src/data/presentation/).

Only counts and public references leave this module: the territory scene receives, per commune and ISO week, the
number of accepted building-permit publications of the Bulletin officiel (one publication = one id, counted once),
placed at the centre of the commune's swisstopo localities. No title, no party, no parcel: the scene shows that
information exists, the dossiers show what it says.
"""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from datetime import date
from typing import Any

from proxsis.connectors import simap
from proxsis.gazette_pdf import iso_week

MENTION_BO = {"fr": "Bulletin officiel du Valais — seule la publication officielle fait foi.",
              "de": "Amtsblatt des Kantons Wallis — massgebend ist allein die amtliche Publikation."}


def _key(name: str) -> str:
    """« Commune Noble-Contrée », « St. Niklaus VS », « Unterbäch (VS) » → the commune's name in the directory."""
    n = re.sub(r"^(?:Commune|Gemeinde)\s+(?:de\s+|d['’])?", "", name.strip())
    n = re.sub(r"\s*\(VS\)$|\s+VS$", "", n)
    n = unicodedata.normalize("NFKD", n)
    return "".join(c for c in n if not unicodedata.combining(c)).lower()


def _centres(places: list[dict[str, Any]]) -> dict[str, tuple[str, float, float]]:
    """Commune key → (official name, lat, lon): its own locality when one bears its name, otherwise the centre of
    its localities (a postal locality can be listed under several communes)."""
    acc: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for p in places:
        acc[str(p["commune"])].append(p)
    out = {}
    for commune, locs in acc.items():
        own = [p for p in locs if _key(str(p["localite"])) == _key(commune)]
        pts = own or locs
        out[_key(commune)] = (commune, round(sum(float(p["lat"]) for p in pts) / len(pts), 4),
                              round(sum(float(p["lon"]) for p in pts) / len(pts), 4))
    return out


def territory(rows: list[dict[str, Any]], places: list[dict[str, Any]]) -> dict[str, Any]:
    """Accepted publications per commune and week; those without a commune (cantonal commission) or whose commune
    has no swisstopo locality are counted off the map, with their reason."""
    centres = _centres(places)
    seen: set[str] = set()
    per: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    off = {"sans_commune": 0, "commune_non_localisee": 0}
    dates: list[str] = []
    for r in rows:
        if r.get("statut") != "acceptée" or r["id"] in seen or not r.get("date_publication"):
            continue
        seen.add(r["id"])
        d = str(r["date_publication"])[:10]
        dates.append(d)
        commune = r.get("commune")
        if not commune:
            off["sans_commune"] += 1
        elif _key(commune) not in centres:
            off["commune_non_localisee"] += 1
        else:
            per[_key(commune)][str(iso_week(d))] += 1
    communes = [{"commune": centres[k][0], "lat": centres[k][1], "lon": centres[k][2], "total": sum(w.values()),
                 "semaines": dict(sorted(w.items()))} for k, w in sorted(per.items())]
    weeks = sorted({str(iso_week(d)) for d in dates})
    return {"source": MENTION_BO, "total_publications": len(seen), "n_communes": len(communes),
            "periode": {"debut": min(dates), "fin": max(dates)} if dates else None, "semaines": weeks,
            "communes": communes, "hors_carte": off}


MENTION_SIMAP = simap.MANDATORY_NOTICE


def awards_layer(records: list[dict[str, Any]], places: list[dict[str, Any]],
                 period: tuple[str, str]) -> dict[str, Any]:
    """Public construction contracts awarded (simap) over the same period, placed at the commune of their postal
    code (same points as the permits). Counts only: no title, no authority, no company."""
    centres = _centres(places)
    by_npa: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for p in places:
        if p.get("npa"):
            by_npa[str(p["npa"])][_key(str(p["commune"]))] += 1
    seen: set[str] = set()
    per: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    off = {"sans_lieu": 0}
    for r in records:
        d = str(r.get("publication_date") or "")[:10]
        if not d or not period[0] <= d <= period[1] or r["id"] in seen:
            continue
        seen.add(r["id"])
        npa = str(r.get("order_postal_code") or "")
        candidates = by_npa.get(npa)
        if not candidates:
            off["sans_lieu"] += 1
            continue
        key = sorted(candidates.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        per[key][str(iso_week(d))] += 1
    communes = [{"commune": centres[k][0], "lat": centres[k][1], "lon": centres[k][2], "total": sum(w.values()),
                 "semaines": dict(sorted(w.items()))} for k, w in sorted(per.items()) if k in centres]
    return {"source": MENTION_SIMAP, "total": len(seen), "communes": communes, "hors_carte": off}


def example_points(urls: list[str], records: list[dict[str, Any]],
                   places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Place of each guided announcement (simap project page) at its commune, from the award's postal code."""
    centres = _centres(places)
    commune_of_npa = {str(p["npa"]): _key(str(p["commune"])) for p in places if p.get("npa")}
    out = []
    for url in urls:
        pid = url.rstrip("/").rsplit("/", 1)[-1]
        rec = next((r for r in records if r.get("project_id") == pid), None)
        key = commune_of_npa.get(str((rec or {}).get("order_postal_code") or ""))
        if rec and key in centres:
            name, lat, lon = centres[key]
            out.append({"url": url, "commune": name, "lat": lat, "lon": lon,
                        "date": str(rec["publication_date"])[:10]})
    return out


def presentation_data(rows: list[dict[str, Any]], places: list[dict[str, Any]], prepared: date,
                      awards: list[dict[str, Any]] | None = None,
                      examples: list[str] | None = None) -> dict[str, Any]:
    t = territory(rows, places)
    period = (t["periode"]["debut"], t["periode"]["fin"]) if t["periode"] else ("", "")
    return {"schema": 1, "prepare_le": str(prepared), "territoire": t,
            "marches": awards_layer(awards or [], places, period),
            "exemples": example_points(examples or [], awards or [], places)}
