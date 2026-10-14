"""« Fin de mission, prochaine mission » — redeploying workers whose mission ends soon.

Workers (FICTIONAL) whose current mission ends within ``weeks`` are matched to the estimated needs of REAL
companies (call lists built on simap awards). Each estimated need is a slot: company, trade, coordinates, and
persons per week (mid estimate); its capacity is the peak of that estimate, rounded up. A worker can take a slot
when the trade is the same or close (M5 skill proximity), the site is within the worker's travel radius, and
the need is active in the week of availability or in the next ``horizon_days``.

The redeployment rate measured here is a property of the FICTIONAL pool facing real needs: it shows that the
mechanism works, not what Flexsis would obtain (that needs its candidate pool and order history).
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any

import pandas as pd

from proxsis.compliance import check, free_publication_date
from proxsis.connectors.swisstopo_localities import geocode
from proxsis.models.m5_matching import MIN_SKILL, REQUIRED_CERT, skill_proximity
from proxsis.synth.geo import haversine_km
from proxsis.taxonomy import trade_label

WARNING = ("FICTIF : travailleurs inventés face à des besoins estimés à partir de marchés publics réels (simap.ch). "
           "Le taux prouve que le mécanisme fonctionne, pas ce que Flexsis obtiendrait.")


MOTIFS = {"metier": "aucun besoin prévu compatible (métier)",
          "permis": "permis légalement requis manquant (ex. permis de grutier)",
          "annonce": "besoin soumis à l'obligation d'annonce, pas de semaine après la date de publication libre",
          "distance": "besoins compatibles hors de son rayon de déplacement",
          "moment": "pas de besoin prévu au moment de sa fin de mission",
          "capacite": "besoins compatibles déjà pourvus par d'autres fins de mission"}


def site_of(phases: list[str] | None) -> str:
    """« génie civil » only when every source lot of the need is civil works; otherwise the prudent « bâtiment »
    (a site labourer is then subject to the 2026 reporting obligation)."""
    return "genie_civil" if phases and set(phases) == {"genie_civil"} else "batiment"


def ending_missions(candidates: pd.DataFrame, today: date, weeks: int = 3) -> pd.DataFrame:
    def ends_soon(v: Any) -> bool:
        if not isinstance(v, str) or not v:
            return False
        d = date.fromisoformat(v)
        return today <= d <= today + timedelta(weeks=weeks)

    mask = (candidates["statut"] == "en_mission") & candidates["fin_mission"].map(ends_soon)
    return candidates[mask.astype(bool)]


def slots_from_call_lists(call_lists: list[dict[str, Any]], places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    slots: dict[tuple[str, str], dict[str, Any]] = {}
    for cl in call_lists:
        for e in [*cl.get("entreprises", []), *cl.get("surprises", [])]:
            loc = geocode(str(e.get("ville") or ""), places)
            if loc is None:
                continue
            for r in e.get("besoin") or []:
                s = slots.setdefault((e["id"], r["metier"]), {
                    "entreprise": e["id"], "nom": e["nom"], "ville": e.get("ville"), "metier": r["metier"],
                    "lat": float(loc["lat"]), "lon": float(loc["lon"]), "semaines": {}, "phases": set(),
                    "source": "simap.ch"})
                s["semaines"][r["semaine"]] = s["semaines"].get(r["semaine"], 0.0) + float(r["personnes_milieu"])
                s["phases"] |= set(r.get("phases") or [])
    for s in slots.values():
        s["phases"] = sorted(s["phases"])
    return list(slots.values())


def redeploy(candidates: pd.DataFrame, slots: list[dict[str, Any]], today: date, weeks: int = 3,
             horizon_days: int = 21) -> dict[str, Any]:
    ending = ending_missions(candidates, today, weeks).sort_values(["fin_mission", "candidate_id"])
    capacity = {i: math.ceil(max(s["semaines"].values())) if s["semaines"] else 0 for i, s in enumerate(slots)}
    free_date = free_publication_date(today)
    subject = {i: bool(check(s["metier"], site=site_of(s.get("phases")), on=today).get("annonce_requise"))
               for i, s in enumerate(slots)}
    out = []
    for r in ending.to_dict("records"):
        trades = [t for t in str(r["trades"]).split(";") if t]
        avail = date.fromisoformat(str(r["available_from"]))
        radius = float(r["max_travel_km"]) if r["driving_licence"] else min(float(r["max_travel_km"]), 25.0)
        skill_ok, cert_ok, near_ok, timing, time_ok = [], [], [], [], []
        certs = [c for c in str(r.get("certifications") or "").split(";") if c]
        orp = bool(r.get("inscrit_orp", False))
        for i, s in enumerate(slots):
            sk = skill_proximity(s["metier"], trades)
            if sk < MIN_SKILL:
                continue
            skill_ok.append(i)
            needed = REQUIRED_CERT.get(s["metier"])
            if needed and needed not in certs:
                continue
            cert_ok.append(i)
            dist = haversine_km(float(r["lat"]), float(r["lon"]), s["lat"], s["lon"])
            if dist > radius:
                continue
            near_ok.append(i)
            start = max(avail, free_date) if (subject[i] and not orp) else avail  # SECO directive B8
            weeks_ok = sorted(w for w, v in s["semaines"].items() if v > 0
                              and date.fromisoformat(w) + timedelta(days=6) >= avail
                              and date.fromisoformat(w) <= avail + timedelta(days=horizon_days))
            if weeks_ok:
                timing.append(i)
            weeks_ok = [w for w in weeks_ok if date.fromisoformat(w) + timedelta(days=6) >= start]
            if weeks_ok:
                time_ok.append((-sk, dist, weeks_ok[0], i))
        free = sorted(x for x in time_ok if capacity[x[3]] > 0)
        row: dict[str, Any] = {"candidate_id": r["candidate_id"], "libelle": r["libelle"],
                               "fin_mission": r["fin_mission"], "metier": trades[0] if trades else None,
                               "fictif": True}
        if free:
            sk, dist, week, i = free[0]
            capacity[i] -= 1
            s = slots[i]
            end = date.fromisoformat(r["fin_mission"])
            row["proposition"] = {
                "entreprise": s["entreprise"], "nom": s["nom"], "ville": s.get("ville"), "metier": s["metier"],
                "semaine": week, "distance_km": round(dist, 1), "source": s["source"],
                "contact_des": str(free_date) if (subject[i] and not orp) else None,
                "raison_fr": f"Fin de mission le {end:%d.%m.%Y} ; besoin estimé de "
                             f"{trade_label(s['metier'], 'fr').lower()} chez {s['nom']} dès la semaine du "
                             f"{date.fromisoformat(week):%d.%m.%Y}, à {dist:.0f} km",
                "raison_de": f"Einsatzende am {end:%d.%m.%Y}; geschätzter Bedarf "
                             f"({trade_label(s['metier'], 'de')}) bei {s['nom']} ab der Woche vom "
                             f"{date.fromisoformat(week):%d.%m.%Y}, {dist:.0f} km entfernt"}
        else:
            code = ("metier" if not skill_ok else "permis" if not cert_ok else "distance" if not near_ok
                    else "moment" if not timing else "annonce" if not time_ok else "capacite")
            row["motif_code"] = code
            row["motif"] = MOTIFS[code]
        out.append(row)
    placed = sum(1 for x in out if x.get("proposition"))
    motifs: dict[str, int] = {}
    for x in out:
        if "motif" in x:
            motifs[x["motif"]] = motifs.get(x["motif"], 0) + 1
    return {"fictif": True, "avertissement": WARNING, "date": str(today), "fenetre_semaines": weeks,
            "fins_de_mission": len(out), "redeployes": placed,
            "taux_redeploiement": placed / len(out) if out else None, "motifs_non_redeploye": motifs,
            "besoins": len(slots), "travailleurs": out}
