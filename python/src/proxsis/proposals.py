"""Candidate proposals for the estimated needs of real companies — candidates are FICTIONAL.

Strict criteria first (trade or close trade, legally required licence, availability within 14 days of the
start, travel radius), then proximity (skill, experience, distance, availability): ``models.m5_matching``.
Every proposal carries its reasons, the CCT wage category and the 2026 minimum of the CCT Location de
services. The consultant decides: nothing is sent to a candidate or a company.
"""

from __future__ import annotations

import math
from datetime import date
from typing import Any

import pandas as pd

from proxsis.cct import CATEGORIES, MIN_WAGE_2026, SOURCE, applicable_cct
from proxsis.compliance import check, free_publication_date
from proxsis.connectors.swisstopo_localities import geocode
from proxsis.models.m5_matching import CandidateMatcher, Need

NOTE = ("Propositions FICTIVES : les candidats sont inventés. Le consultant décide ; l'outil explique. Salaire : "
        "minimum de la CCT Location de services 2026, sauf si l'entreprise de mission est soumise à une CCT étendue "
        "(CN, second-œuvre romand, CCT valaisannes) : ses salaires priment (art. 20 LSE).")


def needs_from_call_list(call_list: dict[str, Any],
                         places: list[dict[str, Any]]) -> tuple[list[Need], list[dict[str, str]]]:
    """One need per company and trade: first week of the estimated need, size = peak of the mid estimate."""
    needs, skipped = [], []
    for e in [*call_list.get("entreprises", []), *call_list.get("surprises", [])]:
        if not e.get("besoin"):
            continue
        loc = geocode(str(e.get("ville") or ""), places)
        if loc is None:
            skipped.append({"entreprise": e["id"], "motif": "localité introuvable dans le répertoire swisstopo"})
            continue
        by_trade: dict[str, list[dict[str, Any]]] = {}
        for r in e["besoin"]:
            by_trade.setdefault(r["metier"], []).append(r)
        for trade, rows in sorted(by_trade.items()):
            start = min(date.fromisoformat(r["semaine"]) for r in rows)
            peak = max(float(r["personnes_milieu"]) for r in rows)
            needs.append(Need(e["id"], trade, float(loc["lat"]), float(loc["lon"]), start, max(1, math.ceil(peak))))
    return needs, skipped


def need_sites(call_lists: list[dict[str, Any]]) -> dict[tuple[str, str], str]:
    """(company, trade) → « genie_civil » only if every source lot of that need is civil works, else « batiment »."""
    from proxsis.redeploy import site_of

    phases: dict[tuple[str, str], set[str]] = {}
    for cl in call_lists:
        for e in [*cl.get("entreprises", []), *cl.get("surprises", [])]:
            for r in e.get("besoin") or []:
                phases.setdefault((e["id"], r["metier"]), set()).update(r.get("phases") or [])
    return {k: site_of(sorted(v)) for k, v in phases.items()}


def propose(candidates: pd.DataFrame, need: Need, k: int = 5, today: date | None = None,
            site: str = "batiment") -> dict[str, Any]:
    """Proposals with their reasons. If the post is subject to the job-reporting obligation, a candidate who is not
    registered at the ORP may only be contacted after the restriction (SECO directive B8): the date is given,
    assuming the post is announced ``today``."""
    matcher = CandidateMatcher(candidates)
    funnel = matcher.funnel(need)
    by_id = candidates.set_index("candidate_id")
    chk = check(need.trade, site=site, on=today)
    free = free_publication_date(today) if (today and chk.get("annonce_requise")) else None
    cct = applicable_cct(need.trade)
    out = []
    for s in matcher.suggest(need, k):
        row = by_id.loc[s.candidate_id]
        cat = str(row["categorie_cct"])
        fr = [*s.reasons_fr, f"Catégorie CCT : {CATEGORIES[cat]['fr']}"]
        de = [*s.reasons_de, f"GAV-Kategorie: {CATEGORIES[cat]['de']}"]
        end = row.get("fin_mission")
        if isinstance(end, str) and end:
            d = date.fromisoformat(end)
            fr.append(f"Fin de sa mission en cours le {d:%d.%m.%Y}")
            de.append(f"Aktueller Einsatz endet am {d:%d.%m.%Y}")
        orp = bool(row.get("inscrit_orp", False))
        if free is not None:
            if orp:
                fr.append("Inscrit·e à l'ORP : contact possible tout de suite (art. 21a al. 5 LEI)")
                de.append("Beim RAV gemeldet: Kontakt sofort möglich (Art. 21a Abs. 5 AIG)")
            else:
                fr.append(f"Poste soumis à l'obligation d'annonce : contact possible dès le {free:%d.%m.%Y} "
                          f"(si annoncé le {today:%d.%m.%Y})")
                de.append(f"Meldepflichtige Stelle: Kontakt erst ab {free:%d.%m.%Y} möglich "
                          f"(bei Meldung am {today:%d.%m.%Y})")
        out.append({"candidate_id": s.candidate_id, "libelle": str(row["libelle"]), "score": round(s.score, 3),
                    "raisons_fr": fr, "raisons_de": de, "categorie_cct": cat, "regle_cct": str(row["regle_cct"]),
                    "cct_applicable": cct["cct"], "cct_applicable_de": cct["cct_de"],
                    "salaire_minimum_cct_ls_heure": MIN_WAGE_2026[cat]["heure"] if cct["minimum_cct_ls"] else None,
                    "permis_travail": str(row["permis_travail"]), "langues": str(row["langues"]).split(";"),
                    "localite": str(row["localite"]), "distance_km": round(s.distance_km, 1),
                    "fin_mission": end if isinstance(end, str) else None, "inscrit_orp": orp,
                    "contact_des": None if (free is None or orp) else str(free), "fictif": True})
    return {"besoin": {"entreprise": need.company_id, "metier": need.trade, "debut": str(need.start), "n": need.n},
            "propositions": out, "entonnoir": funnel, "fictif": True, "note": NOTE, "source_cct": SOURCE,
            "annonce": {"soumis": chk.get("soumis"), "annonce_requise": chk.get("annonce_requise"),
                        "genre": chk.get("genre"), "site": site,
                        "publication_libre": str(free) if free else None}}
