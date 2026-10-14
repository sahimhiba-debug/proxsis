"""Demo export for apps/web: one JSON file per screen, schema version 1.

REAL: companies, awards, lists, needs, phasing, compliance (simap.ch, swisstopo, Fedlex). FICTIONAL, flagged
``fictif: true`` and labelled « FICTIF »: consultants, candidates, proposals, redeployment, agency dashboard
figures that need Flexsis' data. Two automatic checks run before anything is written:

* « aucune donnée de particulier » — every displayed string goes through the PII filter (civility + name, role
  labels, streets, parcels, coordinates); company names through ``looks_like_private_person``. Any hit stops the
  export (``PiiFound``);
* « chaque chiffre a sa mesure » — every dashboard figure carries a CLAIMS.md id that must exist.
"""

from __future__ import annotations

import json
import math
import os
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from proxsis.call_list import (
    SIMAP_MENTION,
    CallListConfig,
    build_call_list,
    lot_table,
    reason_short,
    reason_text,
)
from proxsis.call_prep import build_call_prep
from proxsis.compliance import ORDINANCE, announcement_text, check, valais_holidays
from proxsis.connectors.swisstopo_localities import geocode
from proxsis.gazette_filter import has_person_marker
from proxsis.honesty import FICTIF_WARNING
from proxsis.llm.base import LLMProvider
from proxsis.pii import authority_looks_private, looks_like_private_person, redact_text
from proxsis.proposals import need_sites, needs_from_call_list, propose
from proxsis.redeploy import redeploy, slots_from_call_lists
from proxsis.specialty import SPECIALTIES
from proxsis.synth.geo import haversine_km
from proxsis.taxonomy import TRADES
from proxsis.values import optional_text

SCHEMA_VERSION = 1
AGENCIES: dict[str, dict[str, Any]] = {
    "martigny": {"nom": "Flexsis Martigny", "adresse": "Avenue de la Gare 38, 1920 Martigny", "lat": 46.102,
                 "lon": 7.072},
    "sion": {"nom": "Flexsis Sion", "adresse": "Avenue de Tourbillon 5, 1950 Sion", "lat": 46.233, "lon": 7.360},
    "monthey": {"nom": "Flexsis Monthey", "adresse": "Rue de Venise 10, 1870 Monthey", "lat": 46.255, "lon": 6.954},
}
AGENCY_SOURCE = "https://www.flexsis.ch/agences-de-placement/"
# FICTIONAL consultants: one per agency and specialty shown in the demo (codes, never names).
CONSULTANTS = {"martigny": [("M1", "batiment"), ("M2", "electricite"), ("M3", "technique")],
               "sion": [("S1", "batiment"), ("S2", "electricite"), ("S3", "industrie")],
               "monthey": [("O1", "batiment"), ("O2", "technique")]}
_SKIP_KEYS = {"adresse", "url", "url_simap", "url_api", "lien", "sources_urls", "source", "commande", "fichier"}


class PiiFound(ValueError):
    """The export would display something that looks like personal data."""


def clean_json(obj: Any) -> Any:
    """Strict JSON: NaN / infinity (pandas' missing values) become null."""
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean_json(v) for v in obj]
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    if isinstance(obj, np.generic):
        return clean_json(obj.item())
    return obj


def build_date() -> date:
    """The date written as « generated on »: SOURCE_DATE_EPOCH when set (reproducible builds: the same inputs give the
    same files, byte for byte; review 1, M5), else today."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    return datetime.fromtimestamp(int(epoch), UTC).date() if epoch else date.today()

def pii_sweep(obj: Any, path: str = "") -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in _SKIP_KEYS:
                continue
            if k == "nom" and isinstance(v, str) and looks_like_private_person(v):
                hits.append({"chemin": f"{path}.{k}", "motif": "nom ressemblant à une personne"})
            if k == "adjudicateur" and isinstance(v, str) and authority_looks_private(v):
                hits.append({"chemin": f"{path}.{k}", "motif": "adjudicateur ressemblant à une personne"})
            hits += pii_sweep(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += pii_sweep(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        masked, n = redact_text(obj)
        if n:
            hits.append({"chemin": path, "motif": f"filtre : {masked[:80]}"})
        elif has_person_marker(obj):
            hits.append({"chemin": path, "motif": "marqueur de personne (domicile, c/o, z. Hd., civilité)"})
    return hits


def parse_claims(path: Path) -> dict[str, dict[str, str]]:
    out = {}
    for line in Path(path).read_text("utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 7 and cells[0] and cells[0] not in {"ID", "---"} and not cells[0].startswith("-"):
            out[cells[0]] = {"affirmation": cells[1], "valeur": cells[2], "donnees": cells[3],
                             "commande": cells[4].strip("`"), "fichier": cells[5], "limite": cells[6]}
    return out


# The fictional pool names each candidate's agency by its town (data/fictif/candidats_300.csv); the export writes the
# agency id, the key every screen joins on (review 1, I8: the app compared display names). An unknown town fails.
CANDIDATE_AGENCY = {"Martigny": "martigny", "Sion": "sion", "Monthey": "monthey"}


def _agency_id(town: object) -> str:
    if town not in CANDIDATE_AGENCY:
        raise ValueError(f"agence inconnue pour un candidat : {town!r}")
    return CANDIDATE_AGENCY[str(town)]


def _nearest_agency(lat: float, lon: float) -> str:
    return min(AGENCIES, key=lambda a: haversine_km(lat, lon, AGENCIES[a]["lat"], AGENCIES[a]["lon"]))


def _nearest_first(ids: list[str], companies: dict[str, dict[str, Any]], agency: str) -> list[str]:
    """The companies, the town nearest to the agency first (kilometres rounded to the metre), their rank on a tie."""
    h = AGENCIES[agency]

    def key(i: str) -> tuple[float, int]:
        c = companies[i]
        return round(haversine_km(h["lat"], h["lon"], c["lat"], c["lon"]), 3), ids.index(i)
    return sorted(ids, key=key)


def _render(reasons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"code": r["code"], "fr": reason_text(r, "fr"), "de": reason_text(r, "de"),
             **({"court": {"fr": reason_short(r, "fr"), "de": reason_short(r, "de")}} if reason_short(r) else {}),
             **({"url": r["url"]} if r.get("url") else {})} for r in reasons]


def _chronology(lots: pd.DataFrame, cid: str, as_of: date) -> list[dict[str, Any]]:
    mine = lots[(lots["id"] == cid) & (lots["available_at"] < as_of)].sort_values("available_at", ascending=False)
    return [{"date": str(r["available_at"]), "titre": r["title"], "adjudicateur": optional_text(r["authority"]),
             "montant_chf": r["amount"] if r["amount"] and not math.isnan(r["amount"]) else None,
             "phase": r["phase"], "specialite": r["specialty"], "url_simap": r["url_simap"], "url_api": r["url_api"],
             "source": "simap.ch"} for _, r in mine.head(25).iterrows()]


def _dashboard(redep: dict[str, Any], candidates: pd.DataFrame, claims: dict[str, Any], seed: int,
               lists: dict[str, Any], backtest: dict[str, Any] | None = None) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    by_cand = {cid: _agency_id(town) for cid, town in candidates.set_index("candidate_id")["agence"].items()}
    per: dict[str, list[int]] = {a: [0, 0] for a in AGENCIES}
    for w in redep["travailleurs"]:
        ag = by_cand.get(w["candidate_id"], "")
        if ag in per:
            per[ag][0] += 1
            per[ag][1] += 1 if w.get("proposition") else 0
    agencies: dict[str, dict[str, dict[str, Any]]] = {}
    for a in AGENCIES:  # FICTIONAL figures for the mock-up: invented, reproducible with the seed
        calls = int(rng.integers(35, 60))
        meetings = int(rng.binomial(calls, 0.18))
        filled = int(rng.binomial(meetings, 0.45))
        agencies[a] = {"appels": {"valeur": calls, "type": "FICTIF", "claim": "TAB-FICTIF-1"},
                       "rendez_vous": {"valeur": meetings, "type": "FICTIF", "claim": "TAB-FICTIF-1"},
                       "missions_pourvues": {"valeur": filled, "type": "FICTIF", "claim": "TAB-FICTIF-1"},
                       "delai_moyen_jours": {"valeur": round(float(rng.uniform(2.5, 6.5)), 1), "type": "FICTIF",
                                             "claim": "TAB-FICTIF-1"},
                       "redeploiement": {"valeur": (per[a][1] / per[a][0]) if per[a][0] else None,
                                         "n": per[a][0], "type": "FICTIF", "claim": "REDEP-1"}}
    bat = lists.get("batiment", {})
    new_share = (backtest or {}).get("specialites", {}).get("batiment", {}).get("part_premiers_gagnants")
    indicators: list[dict[str, Any]] = [
        {"code": "precision_liste_batiment", "valeur": bat.get("backtest", {}).get("p_at_10"), "unite": "%",
         "type": "RÉEL", "claim": "REEL-SPEC-BAT"},
        {"code": "laureats_nouveaux", "valeur": round(100 * new_share, 1) if new_share is not None else None,
         "unite": "%", "type": "RÉEL", "claim": "REEL-SPEC-NOUVEAUX"},
        {"code": "redeploiement_global", "valeur": redep["taux_redeploiement"], "unite": "part", "type": "FICTIF",
         "claim": "REDEP-1"},
        {"code": "besoins_soumis_annonce", "valeur": None, "unite": "", "type": "RÉEL", "claim": "CONF-1"},
        {"code": "maquette_agences", "valeur": None, "unite": "", "type": "FICTIF", "claim": "TAB-FICTIF-1"},
    ]
    missing = [k["claim"] for k in indicators if k["claim"] not in claims]
    missing += [v["claim"] for ag in agencies.values() for v in ag.values() if v["claim"] not in claims]
    if missing:
        raise ValueError(f"chiffres sans mesure dans CLAIMS.md : {sorted(set(missing))}")
    return {"agences": agencies, "indicateurs": indicators,
            "note": "Les chiffres d'agence sont FICTIFS (maquette) tant que Flexsis n'a pas fourni son historique."}


def export_demo(out: Path, records: list[dict[str, Any]], as_of: date, places: list[dict[str, Any]],
                candidates: pd.DataFrame, claims_md: Path, specialties: tuple[str, ...] = ("batiment", "electricite",
                                                                                          "technique"),
                seed: int = 42, provider: LLMProvider | None = None, k_per_agency: int = 10,
                backtest: dict[str, Any] | None = None,
                permits: list[dict[str, Any]] | None = None, frozen: dict[str, Any] | None = None) -> dict[str, Path]:
    claims = parse_claims(claims_md)
    lots = lot_table(records)
    companies: dict[str, dict[str, Any]] = {}
    lists: dict[str, Any] = {}
    for spec in specialties:
        cl = build_call_list(records, CallListConfig(as_of=as_of, specialty=spec, k=60, n_surprises=10),
                             permits=permits)
        per_agency: dict[str, dict[str, list[str]]] = {a: {"entreprises": [], "surprises": []} for a in AGENCIES}
        for group, key in ((cl["entreprises"], "entreprises"), (cl["surprises"], "surprises")):
            for e in group:
                loc = geocode(str(e.get("ville") or ""), places)
                if loc is None:
                    continue
                ag = _nearest_agency(float(loc["lat"]), float(loc["lon"]))
                if len(per_agency[ag][key]) >= (k_per_agency if key == "entreprises" else 3):
                    continue
                per_agency[ag][key].append(e["id"])
                c = companies.setdefault(e["id"], {
                    "id": e["id"], "nom": e["nom"], "ville": e["ville"], "canton": e["canton"],
                    "lat": float(loc["lat"]), "lon": float(loc["lon"]), "agence": ag, "specialites": {},
                    "chronologie": _chronology(lots, e["id"], as_of)})
                c["specialites"][spec] = {"rang": e.get("rang"), "surprise": e["surprise"],
                                          "confiance": e["confiance"], "faiblesses": e["faiblesses"]}
                if spec == specialties[0] or "raisons" not in c:
                    c.update({"specialite_principale": spec, "raisons": _render(e["raisons"]), "besoin": e["besoin"],
                              "lots_attendus": e["lots_attendus"], "sources": e["sources"], "n_52s": e["n_52s"],
                              "confiance": e["confiance"], "surprise": e["surprise"]})
        if frozen is not None and spec == frozen["specialite"] and str(frozen["as_of"]) == str(as_of):
            # one list in the visit and in the application (questionnaire of Hiba, 07.10.2026, B7): every agency's
            # week is the ten of the frozen list the visit shows, ordered by the distance of each company's town to the
            # agency (as « Votre lundi à Martigny, Sion, Monthey » in the visit), the list's rank on a tie
            ten = [str(e["id"]) for e in frozen["entreprises"]]
            missing = [i for i in ten if i not in companies]
            if missing:
                raise ValueError(f"la liste gelée du {frozen['as_of']} n'est pas dans l'export : {missing}")
            for ag, part in per_agency.items():
                part["entreprises"] = _nearest_first(ten, companies, ag)
        bt = (backtest or {}).get("specialites", {}).get(spec, {})
        t0 = bt.get("cibles", {}).get("t0", {})
        p10 = t0.get("p_at_k", {}).get("frequence_52s", {}).get("moyenne")
        base = t0.get("taux_de_base")
        lists[spec] = {"libelle": {"fr": SPECIALTIES[spec].label_fr, "de": SPECIALTIES[spec].label_de},
                       "ordre": cl.get("ordre"), "par_agence": per_agency, "hypotheses": cl["hypotheses"],
                       "backtest": {"p_at_10": round(100 * p10, 1) if p10 is not None else None,
                                    "taux_de_base": round(100 * base, 1) if base is not None else None,
                                    "semaines": bt.get("n_semaines"),
                                    "claim": "REEL-SPEC-BAT" if spec == "batiment" else "REEL-SPEC-AUTRES"}}
    # proposals and compliance for the needs of the exported companies only
    shown_list = {"entreprises": [{"id": c["id"], "ville": c["ville"], "besoin": c.get("besoin")}
                                  for c in companies.values()]}
    needs, _ = needs_from_call_list(shown_list, places)
    sites = need_sites([shown_list])
    proposals: dict[str, list[dict[str, Any]]] = {}
    compliance: dict[str, list[dict[str, Any]]] = {}
    for n in needs:
        site = sites.get((n.company_id, n.trade), "batiment")
        p = propose(candidates, n, k=5, today=as_of, site=site)
        proposals.setdefault(n.company_id, []).append(p)
        c = companies[n.company_id]
        chk = check(n.trade, site=site, on=as_of)
        # an estimated need: a draft whose start date and rate the company alone can give (slots, never values)
        chk["annonce"] = {lang: announcement_text(n.trade, client=c["nom"], place=c["ville"], start=None,
                                                  duration=("durée déterminée" if lang == "fr" else "befristet"),
                                                  rate=None, agency=AGENCIES[c["agence"]]["nom"], lang=lang,
                                                  address=AGENCIES[c["agence"]]["adresse"], draft=True)
                          for lang in ("fr", "de")}
        chk["metier_libelle"] = {"fr": TRADES[n.trade].label_fr, "de": TRADES[n.trade].label_de}
        chk["debut"] = str(n.start)
        compliance.setdefault(n.company_id, []).append(chk)
    calls = {}
    for c in companies.values():
        best = max(proposals.get(c["id"], []), key=lambda p: len(p["propositions"]), default=None)
        summary = {"n_proposes": len(best["propositions"]), "metier": best["besoin"]["metier"], "fictif": True} \
            if best and best["propositions"] else None
        calls[c["id"]] = build_call_prep(c, summary, provider)
    # same input as `proxsis moteur-semaine1` (lists of 10 + 3 surprises), so the figure matches CLAIMS REDEP-1
    week_lists = [build_call_list(records, CallListConfig(as_of=as_of, specialty=s)) for s in specialties]
    red = redeploy(candidates, slots_from_call_lists(week_lists, places), as_of, weeks=3)
    # a redeployment target outside the per-agency cap still gets its page (audit week 2, M6: dead link)
    week_entries = {e["id"]: (e, spec) for spec, cl in zip(specialties, week_lists, strict=True)
                    for e in cl["entreprises"] + cl["surprises"]}
    for w in red["travailleurs"]:
        target = (w.get("proposition") or {}).get("entreprise")
        if target and target not in companies and target in week_entries:
            e, spec = week_entries[target]
            loc = geocode(str(e.get("ville") or ""), places)
            if loc is not None:
                ag = _nearest_agency(float(loc["lat"]), float(loc["lon"]))
                companies[target] = {
                    "id": e["id"], "nom": e["nom"], "ville": e["ville"], "canton": e["canton"],
                    "lat": float(loc["lat"]), "lon": float(loc["lon"]), "agence": ag,
                    "chronologie": _chronology(lots, e["id"], as_of), "specialite_principale": spec,
                    "specialites": {spec: {"rang": e.get("rang"), "surprise": e["surprise"],
                                           "confiance": e["confiance"], "faiblesses": e["faiblesses"]}},
                    "raisons": _render(e["raisons"]), "besoin": e["besoin"], "lots_attendus": e["lots_attendus"],
                    "sources": e["sources"], "n_52s": e["n_52s"], "confiance": e["confiance"],
                    "surprise": e["surprise"]}
                calls[target] = build_call_prep(companies[target], None, provider)
    used = {s["candidate_id"] for ps in proposals.values() for p in ps for s in p["propositions"]}
    used |= {w["candidate_id"] for w in red["travailleurs"]}
    cand_cols = ["candidate_id", "libelle", "specialite", "metier", "categorie_cct", "regle_cct", "permis_travail",
                 "langues", "localite", "agence", "statut", "fin_mission", "available_from", "fictif"]
    cands = {r["candidate_id"]: {k: (None if isinstance(r[k], float) and math.isnan(r[k]) else r[k])
                                 for k in cand_cols} | {"agence": _agency_id(r["agence"])}
             for r in candidates[candidates["candidate_id"].isin(used)][cand_cols].to_dict("records")}
    agencies = {a: v | {"id": a, "source": AGENCY_SOURCE,
                        "consultants": [{"code": code, "libelle": f"Consultant·e {code} (FICTIF)",
                                         "specialite": spec, "fictif": True} for code, spec in CONSULTANTS[a]]}
                for a, v in AGENCIES.items()}
    files = {
        "meta": {"schema": SCHEMA_VERSION, "semaine": str(as_of), "genere_le": str(build_date()),
                 "mention_simap": SIMAP_MENTION, "avertissement_fictif": FICTIF_WARNING,
                 "sources": {"simap": "simap.ch (API, CG du 30.09.2023)",
                             "localites": "Office fédéral de topographie swisstopo (OGD)",
                             "conformite": ORDINANCE, "flexsis": AGENCY_SOURCE},
                 "redaction": next(iter(calls.values()))["redaction"] if calls else None,
                 "metiers": {k: {"fr": t.label_fr, "de": t.label_de} for k, t in TRADES.items()},
                 "jours_feries_valais": sorted(str(d) for y in (as_of.year, as_of.year + 1)
                                               for d in valais_holidays(y))},
        "agences": agencies, "entreprises": companies, "listes": lists, "propositions": proposals,
        "candidats": cands, "redeploiement": red, "conformite": compliance, "appels": calls,
        "tableau": _dashboard(red, candidates, claims, seed, lists, backtest),
        "claims": claims,
    }
    hits = pii_sweep({k: v for k, v in files.items() if k != "claims"})
    if hits:
        raise PiiFound(f"{len(hits)} chaîne(s) bloquée(s) par le balayage : {hits[:5]}")
    out.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for name, data in files.items():
        target = out / f"{name}.json"
        text = json.dumps(clean_json(data), ensure_ascii=False, indent=1, default=str, allow_nan=False)
        target.write_text(text + "\n", "utf-8")
        written[name] = target
    return written
