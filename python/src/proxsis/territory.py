"""Visit, time 1 « Le premier lundi » (brief « à distance », 4.1): the communes of Valais the director can touch and, in
each, the companies active in our data — those whose seat is there and those that won a published contract located
there, kept apart — only when the company's dossier passes every check. The others are listed with their reasons.

Inputs: the application's companies and prepared calls (``proxsis export-demo``), the filtered simap awards (seat
and contract location: postal code and locality), the official localities of Valais (swisstopo: locality and postal
code → commune number) and the commune boundaries of the map (same official numbers). Only awards published before
the Monday of the list count.
"""

from __future__ import annotations

import csv
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from proxsis.demo_export import pii_sweep
from proxsis.entities import is_legal_entity_name, normalize_name

# Every check a dossier passes to appear on the map (« seulement celles dont le dossier passe tous les contrôles »).
CHECKS = {
    "forme_juridique": "le nom porte une forme juridique (une entreprise, pas une personne)",
    "siege_commune": "le siège publié se rattache à une commune du Valais de la carte",
    "marche_source": "au moins un marché publié avant le lundi de la liste, daté, avec sa page simap.ch",
    "appel_prepare": "l'appel préparé donne une raison fondée sur un fait publié et des questions à poser",
    "donnees_personnelles": "le dossier passe le balayage des données personnelles",
    "nom_unique": "aucune autre entreprise de l'application ne porte le même nom",
}
_CONSORTIUM = ("consortium", "arge ", "arbeitsgemeinschaft", "groupement", "ingénieurs associés")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = s.replace("saint-", "st-").replace("saint ", "st-").replace("st. ", "st-")
    s = " ".join(s.replace("-", " ").split())
    return s.removesuffix(" vs")


class Localities:
    """Official localities of Valais (swisstopo): (postal code, locality) → commune number."""

    def __init__(self, rows: list[dict[str, str]], communes: dict[int, str]):
        self.communes = communes
        self.by_both: dict[tuple[str, str], set[int]] = defaultdict(set)
        self.by_name: dict[str, set[int]] = defaultdict(set)
        self.by_npa: dict[str, set[int]] = defaultdict(set)
        for r in rows:
            bfs = int(r["bfs"])
            if bfs not in communes:
                continue
            self.by_both[(r["npa"], _norm(r["localite"]))].add(bfs)
            self.by_name[_norm(r["localite"])].add(bfs)
            self.by_npa[r["npa"]].add(bfs)

    @classmethod
    def read(cls, path: Path, communes: dict[int, str]) -> Localities:
        with path.open(encoding="utf-8") as fh:
            return cls(list(csv.DictReader(fh)), communes)

    def commune_of(self, npa: Any, locality: Any) -> int | None:
        """The commune of a published place; a locality spread over two communes goes to the one of the same name;
        None when the place cannot be placed without guessing."""
        name = _norm(str(locality or ""))
        code = str(npa or "").strip()
        for found in (self.by_both.get((code, name)), self.by_name.get(name), self.by_npa.get(code)):
            if not found:
                continue
            if len(found) == 1:
                return next(iter(found))
            same = [b for b in found if _norm(self.communes[b]) == name]
            if len(same) == 1:
                return same[0]
        return None


def _place(rows: pd.DataFrame, postal: str, city: str) -> tuple[Any, Any] | None:
    """The most frequent published place of a set of awards (ties: alphabetical order, stable)."""
    c = Counter((str(p or ""), str(v or "")) for p, v in zip(rows[postal], rows[city], strict=True) if p or v)
    return min(c.items(), key=lambda kv: (-kv[1], kv[0]))[0] if c else None


def _prepared(call: dict[str, Any] | None) -> bool:
    if not call:
        return False
    real = {f["id"] for f in call.get("faits") or [] if f.get("type") == "reel" and str(f.get("url", "")).startswith(
        "https://www.simap.ch/")}
    guide = {g["code"]: g for g in call.get("fr", {}).get("guide") or []}
    reason = any(set(p.get("sources") or []) & real for p in guide.get("pourquoi", {}).get("phrases") or [])
    return reason and bool(guide.get("questions", {}).get("phrases"))


def build(companies: dict[str, dict[str, Any]], calls: dict[str, dict[str, Any]], lots: pd.DataFrame,
          localities: Localities, as_of: date, guided: list[str], example: tuple[str, str],
          mention: str) -> dict[str, Any]:
    """``example``: the prepared commune (its name) and company of the visit; both must pass."""
    lots = lots[lots["available_at"] < as_of]
    names = Counter(normalize_name(c["nom"]) for c in companies.values())
    places: dict[int, dict[str, Any]] = defaultdict(lambda: {"siege": [], "marches": []})
    kept: dict[str, dict[str, Any]] = {}
    left_out: list[dict[str, Any]] = []
    for cid in sorted(companies):
        c = companies[cid]
        mine = lots[lots["id"] == cid]
        seat = _place(mine, "postal_code", "city")
        seat_bfs = localities.commune_of(*seat) if seat else localities.commune_of(None, c.get("ville"))
        dated = [e for e in c.get("chronologie") or [] if e.get("date", "9999") < str(as_of)
                 and str(e.get("url_simap", "")).startswith("https://www.simap.ch/")]
        failed = [k for k, ok in (
            ("forme_juridique", is_legal_entity_name(c["nom"])),
            ("siege_commune", seat_bfs is not None),
            ("marche_source", bool(dated)),
            ("appel_prepare", _prepared(calls.get(cid))),
            ("donnees_personnelles", not pii_sweep({"nom": c["nom"], "ville": c.get("ville"), "chronologie": dated})),
            ("nom_unique", names[normalize_name(c["nom"])] == 1),
        ) if not ok]
        if failed or seat_bfs is None:  # (a seat without a commune is the failed check « siege_commune »)
            left_out.append({"id": cid, "nom": c["nom"], "controles_echoues": failed})
            continue
        consortium = any(w in c["nom"].lower() for w in _CONSORTIUM)
        kept[cid] = {"nom": c["nom"], "ville": c.get("ville"), "commune_siege": seat_bfs, "guide": cid in guided,
                     "consortium": consortium}
        places[seat_bfs]["siege"].append(cid)
        for e in dated:
            where = mine[mine["url_simap"] == e["url_simap"]]
            at = _place(where, "order_postal_code", "order_city")
            bfs = localities.commune_of(*at) if at else None
            if bfs is not None:
                places[bfs]["marches"].append({"id": cid, "date": e["date"], "titre": e["titre"],
                                               "url": e["url_simap"]})
    communes = {}
    for bfs in sorted(places):
        p = places[bfs]
        # by official number only: the names are in the map's boundaries (communes_vs.json), and some official names
        # (« Saint-Maurice ») would look like persons to the sweep
        communes[str(bfs)] = {"siege": sorted(p["siege"]),
                              "marches": sorted(p["marches"], key=lambda m: (m["date"], m["id"], m["url"]),
                                                reverse=True)}
    town, company = example
    town_bfs = next((b for b, n in localities.communes.items() if n == town), None)
    if town_bfs is None or company not in kept or company not in communes.get(str(town_bfs), {}).get("siege", []):
        raise ValueError(f"l'exemple préparé ({town}, {company}) ne passe pas les contrôles")
    return {"schema": 1, "lundi": str(as_of), "source": {"nom": "simap.ch", "mention": mention},
            "controles": CHECKS, "exemple": {"commune": str(town_bfs), "entreprise": company},
            "communes": communes, "entreprises": kept, "exclues": left_out}
