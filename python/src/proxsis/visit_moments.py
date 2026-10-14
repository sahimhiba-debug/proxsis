"""Visit, the new moments of the brief of 07.10.2026 (§ 3.2 to 3.4). Only their data: the screens are written elsewhere
(apps/web/src/visite/). Every figure comes from a line of CLAIMS.md and is recomputed here; a file that would differ
from its line is refused and nothing is written (``proxsis moments-presentation``).

« La semaine du … » (§ 3.3, CLAIMS PRES-SEMAINE-1). The first Monday of the visit is the frozen list of Monday
05.10.2026 (Bâtiment, Valais, ``data/terrain/liste_2026-10-05_batiment.json``, built by ``proxsis dix-entreprises``).
The week is the last complete one in both sources before that Monday, Monday to Sunday (Hiba, questionnaire of
07.10.2026, A3: the week before the Monday, 28.09 to 04.10, is cut by the end of the data; the one shown is 21 to
27.09.2026):

* **read** — the publications of the list's two sources published that week: the simap award publications of the
  collected files (one per publication) and the accepted building-permit publications of the Bulletin officiel import
  (one per request; the list reads them as context);
* **retained** — those that enter the ranking of the list: a simap award of the Bâtiment specialty won by a company
  named by its legal form (masked or private laureates are dropped by ``call_list.lot_table``) whose most frequent
  published canton before the Monday is Valais — the population of ``call_list.build_call_list``, checked against the
  number of companies the frozen list ranked. The Bulletin officiel never enters the order of the list (no history to
  measure it): none of its publications is retained;
* **calls** — the ten companies of the list (they come from 52 weeks of awards, not from the week alone).

The demonstration's data stop on 30.09.2026 (simap) and on the last date of the Bulletin officiel import: the week
shown ends before both, so it is whole; nothing is ever completed. Publications, neither projects nor companies.

« Celles qui accélèrent » (§ 3.4, CLAIMS REEL-SURPRISE). In the measure of the Bâtiment list (57 Mondays), outside the
ten of the list: how often the companies whose activity accelerates (« rythme_double »: at least 2 awards in the last
8 weeks and at least twice their usual pace of the 44 weeks before, ``real_backtest.surprise_flags``) won a new public
award in the 8 following weeks, against all the companies outside the ten (mean of the weekly rates, the accelerating
ones included). Repeated from ``docs/backtest/specialites_v1.json``; descriptive rates: one company can be counted
several weeks in a row.

« Plusieurs faits vont dans le même sens » (§ 3.2, CLAIMS PRES-CARRON-1, PRES-BITZ-1, PRES-THELER-1). For each guided
dossier, the published facts its CLAIMS line states, nothing more, each with its date and its source, read from the
files the line names (the frozen list; the Bulletin officiel import for the roles,
``presentation_stories.bo_citations``) and checked against the line. For the Bulletin officiel: the company's role, the
commune and the date only; never the applicant, never a link to the publication nor its identifier (the published
request names the applicant).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from proxsis.call_list import _events, _mode, company_id, lot_table
from proxsis.connectors import simap
from proxsis.date_choice import HORIZON_DAYS, _pct
from proxsis.live_week import previous_week
from proxsis.presentation_stories import bo_citations

SCHEMA = 1
COMMAND = "proxsis moments-presentation"
PREPARED = "2026-10-07"  # date of the computation written in the files (the command's --date)
WEEK_CLAIMS = "PRES-SEMAINE-1"
SURGE_CLAIMS = "REEL-SURPRISE"
FACTS_CLAIMS = ("PRES-CARRON-1", "PRES-BITZ-1", "PRES-THELER-1")
SIMAP_NAME = {"fr": "simap.ch", "de": "simap.ch"}
BO_NAME = {"fr": "Bulletin officiel du Valais", "de": "Amtsblatt des Kantons Wallis"}
BO_MENTION = {"fr": "relevé manuel pendant le prototype", "de": "während des Prototyps von Hand erfasst"}
PLANS_ROLE = "auteur_plans_entreprise"


def _fmt(iso: str) -> str:
    """« 2026-09-28 » → « 28.09.2026 », as CLAIMS.md writes dates."""
    return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}"


def _provenance(claims_id: str | list[str], prepared: str) -> dict[str, Any]:
    return {"commande": COMMAND, "calcule_le": prepared, "claims": claims_id}


# ---------------------------------------------------------------- « Cette semaine »

def check_week_line(data: dict[str, Any], line: dict[str, str]) -> None:
    """Refuse a week that its CLAIMS line (PRES-SEMAINE-1) does not state word for word."""
    read, kept = data["lues"], data["retenues"]
    wanted = [(f"{read['total']} publications lues ({read['simap']} adjudications simap, {read['bulletin_officiel']} "
               f"demandes d'autorisation du Bulletin officiel)", "valeur"),
              (f"{kept['total']} retenues ({kept['simap']} adjudications simap, {kept['bulletin_officiel']} du "
               f"Bulletin officiel)", "valeur"),
              (f"{data['appels']} appels", "valeur"),
              (f"du {_fmt(data['semaine']['du'])} au {_fmt(data['semaine']['au'])}", "affirmation"),
              (_fmt(data["fin_des_donnees"]["simap"]), "limite"),
              (_fmt(data["fin_des_donnees"]["bulletin_officiel"]), "limite")]
    missing = [w for w, col in wanted if w not in line[col]]
    if missing or line["donnees"] != "RÉEL":
        raise ValueError(f"la semaine diffère de la ligne CLAIMS {WEEK_CLAIMS} : {missing}")


def week_counts(records: list[dict[str, Any]], permits: list[dict[str, Any]], frozen: dict[str, Any], data_end: date,
                line: dict[str, str] | None = None, check_ten: bool = True, prepared: str = PREPARED) -> dict[str, Any]:
    """``records``: the simap award records the list reads (``commands.io.load_simap``); ``permits``: the Bulletin
    officiel import (only the accepted publications are read, as by the list); ``frozen``: the frozen list."""
    monday = date.fromisoformat(str(frozen["as_of"]))
    start, end = previous_week(monday)  # refuses a day that is not a Monday
    specialty, cantons = str(frozen["specialite"]), set(frozen["region"])
    accepted = [p for p in permits if p.get("statut") == "acceptée"]
    bo_end = max(str(p["date_publication"])[:10] for p in accepted if p.get("date_publication"))
    # the last week that both sources hold whole: a week cut by the end of the data is never shown (A3)
    while str(end) > min(str(data_end), bo_end):
        start, end = start - timedelta(days=7), end - timedelta(days=7)

    def in_week(day: Any) -> bool:
        return str(start) <= str(day or "")[:10] <= str(end)

    simap_read = {str(r["publication_id"]) for r in records if in_week(r.get("publication_date"))}
    late = sorted({str(r["publication_date"])[:10] for r in records
                   if in_week(r.get("publication_date")) and str(r["publication_date"])[:10] > str(data_end)})
    if late:
        raise ValueError(f"publications de la semaine après la fin des données ({data_end}) : {late}")
    lots = lot_table(records)
    past = lots[lots["available_at"] < monday]
    canton = past.groupby("company")["canton"].agg(_mode).to_dict()  # as call_list.build_call_list
    ranked = {c for c in set(_events(past, specialty)["company"]) if canton.get(c) in cantons}
    if len(ranked) != int(frozen["entreprises_classees"]):
        raise ValueError(f"population de {len(ranked)} entreprises, la liste gelée en classe "
                         f"{frozen['entreprises_classees']}")
    if check_ten and not {e["id"] for e in frozen["entreprises"]} <= {company_id(c) for c in ranked}:
        raise ValueError("les dix entreprises de la liste ne sont pas dans sa population")
    in_list = past["company"].isin(sorted(ranked))
    in_week_lots = (past["available_at"] >= start) & (past["available_at"] <= end)
    week = past[in_week_lots & (past["specialty"] == specialty) & in_list]
    simap_kept = {str(p) for p in week["publication_id"]}
    bo_read = [p for p in accepted if in_week(p.get("date_publication"))]
    data = {
        "schema": SCHEMA,
        "claims": WEEK_CLAIMS,
        "lundi": str(monday),
        "semaine": {"du": str(start), "au": str(end)},
        "liste": {"fichier": f"data/terrain/liste_{monday}_{specialty}.json", "liste_id": frozen.get("liste_id"),
                  "specialite": specialty, "region": sorted(cantons)},
        "fin_des_donnees": {"simap": str(data_end), "bulletin_officiel": bo_end},
        "lues": {"total": len(simap_read) + len(bo_read), "simap": len(simap_read), "bulletin_officiel": len(bo_read)},
        "retenues": {"total": len(simap_kept), "simap": len(simap_kept), "bulletin_officiel": 0},
        "appels": len(frozen["entreprises"]),
        "sources": {"simap": {"nom": SIMAP_NAME, "mention": simap.MANDATORY_NOTICE},
                    "bulletin_officiel": {"nom": BO_NAME, "mention": BO_MENTION}},
        "provenance": _provenance(WEEK_CLAIMS, prepared),
    }
    if line is not None:
        check_week_line(data, line)
    return data


# ---------------------------------------------------------------- « Celles qui accélèrent »

def accelerating(measure_file: dict[str, Any], claims: dict[str, dict[str, str]],
                 prepared: str = PREPARED) -> dict[str, Any]:
    """``measure_file``: ``docs/backtest/specialites_v1.json``; ``claims``: CLAIMS.md (REEL-SURPRISE, and REEL-SPEC-BAT
    for the Mondays of the measure, the line REEL-SURPRISE repeats with « idem »)."""
    m = measure_file["specialites"]["batiment"]
    rd = m["drapeaux_surprise"]["rythme_double"]["hors_top_k"]
    line, scope = claims[SURGE_CLAIMS], claims["REEL-SPEC-BAT"]
    shown = {"accelerent": _pct(rd["taux_t0"]), "hors_des_dix": _pct(rd["taux_de_base_t0"])}
    wanted = (f"« activité qui bondit » {shown['accelerent']} ({rd['signalements']} cas repérés) contre "
              f"{shown['hors_des_dix']} de base hors top {m['k']}")
    weeks = f"{m['n_semaines']} semaines ({m['semaines'][0]} à {m['semaines'][1]})"
    if wanted not in line["valeur"] or weeks not in scope["affirmation"] or line["fichier"] != "idem":
        raise ValueError(f"la mesure diffère de la ligne CLAIMS {SURGE_CLAIMS} : {wanted}, {weeks}")
    if "non indépendants" not in line["limite"] or "taux descriptifs" not in line["limite"]:
        raise ValueError(f"la nuance de la ligne CLAIMS {SURGE_CLAIMS} manque")
    return {
        "schema": SCHEMA,
        "claims": SURGE_CLAIMS,
        "perimetre": {"specialite": "batiment", "region": list(measure_file["region"]), "dix": m["k"],
                      "semaines": m["n_semaines"], "premiere": m["semaines"][0], "derniere": m["semaines"][1],
                      "horizon_semaines": HORIZON_DAYS // 7},
        "regle": {"fr": "au moins 2 marchés publics en 8 semaines, et au moins deux fois son rythme habituel des 44 "
                        "semaines précédentes",
                  "de": "mindestens 2 öffentliche Aufträge in 8 Wochen und mindestens doppelt so viele wie üblich in "
                        "den 44 Wochen davor"},
        "accelerent": {"cas": rd["signalements"], "taux": rd["taux_t0"],
                       "affiche": {"fr": shown["accelerent"], "de": shown["accelerent"]}},
        "hors_des_dix": {"taux": rd["taux_de_base_t0"],
                         "affiche": {"fr": shown["hors_des_dix"], "de": shown["hors_des_dix"]}},
        "nuance": {"fr": "Des taux observés sur le passé, pas une prévision : une même entreprise peut compter "
                         "plusieurs semaines de suite.",
                   "de": "Auf der Vergangenheit beobachtete Anteile, keine Vorhersage: Dasselbe Unternehmen kann "
                         "mehrere Wochen nacheinander zählen."},
        "de_a_relire": True,
        "source": {"nom": "simap.ch", "mention": simap.MANDATORY_NOTICE, "mesure": "docs/backtest/specialites_v1.json",
                   "mesure_le": measure_file["mesure_le"]},
        "provenance": _provenance(SURGE_CLAIMS, prepared),
    }


# ---------------------------------------------------------------- « Plusieurs faits vont dans le même sens »

@dataclass(frozen=True)
class Guided:
    """A guided dossier and what its CLAIMS line states about its latest award, in the line's words (``authority`` in
    French as the line words it, in German as simap publishes it; ``subject`` as the line words it)."""

    claims: str
    company: str
    authority: dict[str, str]
    subject: dict[str, str] | None = None
    original_title: bool = False  # the line quotes the title of the latest award as published
    series: str | None = None  # a series of awards the line counts, recognised in their titles
    series_label: dict[str, str] | None = None
    series_phrase: str = ""  # how the line states the series (« {n} … publiés les {dates} »)
    permits: bool = False  # the line states the company's roles in Bulletin officiel requests
    others: int = 0  # the line states the dates of this many other recent awards (« {n} autres marchés récents … »)


GUIDED = (
    Guided("PRES-CARRON-1", "ent-1ef761b229",
           authority={"fr": "Service de la mobilité, arrondissement 3 Bas-Valais",
                      "de": "Dienststelle für Mobilität, Kreis 3 Unterwallis"},
           others=3),  # questionnaire of Hiba, 07.10.2026, A4: its other dated awards, not only the latest
    Guided("PRES-BITZ-1", "ent-734d5f7d45",
           authority={"fr": "Foyer Saint-Jacques", "de": "Foyer Saint-Jacques"},
           subject={"fr": "terrassement d'un EMS à Saint-Maurice",
                    "de": "Aushub für ein Alters- und Pflegeheim in Saint-Maurice"},
           permits=True),
    Guided("PRES-THELER-1", "ent-866876591f",
           authority={"fr": "Dienststelle für Mobilität - Kreis 1 Oberwallis",
                      "de": "Dienststelle für Mobilität - Kreis 1 Oberwallis"},
           original_title=True, series="NG24",
           series_label={"fr": "Tronçon de la nouvelle route cantonale NG24 attribué",
                         "de": "Abschnitt der neuen Kantonsstrasse NG24 vergeben"},
           series_phrase="{n} tronçons NG24 attribués, publiés les {dates}"),
)
AWARD_LABEL = {"fr": "Marché public remporté", "de": "Öffentlicher Auftrag gewonnen"}
PERMIT_LABEL = {"fr": "Demande d'autorisation de construire : auteure des plans", "de": "Baugesuch: Planverfasserin"}


def _words(text: str) -> set[str]:
    return {w.casefold() for w in re.findall(r"[\w]+", text)}


def _dates(isos: list[str]) -> str:
    """« 26.06.2026, 03.07.2026 et 21.09.2026 »."""
    shown = [_fmt(d) for d in isos]
    return shown[0] if len(shown) == 1 else ", ".join(shown[:-1]) + " et " + shown[-1]


def _dossier(spec: Guided, entry: dict[str, Any], bo_rows: list[dict[str, Any]], line: dict[str, str],
             as_of: str) -> dict[str, Any]:
    refused = f"le dossier {spec.claims} diffère de sa ligne CLAIMS"
    sources = entry["sources"]
    latest = sources[0]
    if not line["valeur"].startswith(f"{entry['n_52s']} ; dernier publié le {_fmt(latest['date'])} ("):
        raise ValueError(f"{refused} : nombre de marchés ou date du dernier")
    published = _words(latest["adjudicateur"] or "")
    if spec.authority["fr"] not in line["valeur"] or not all(
            _words(v) <= published for v in spec.authority.values()):
        raise ValueError(f"{refused} : adjudicateur")
    if spec.subject and spec.subject["fr"] not in line["valeur"]:
        raise ValueError(f"{refused} : objet")
    if spec.original_title and f"« {latest['titre']} »" not in line["valeur"]:
        raise ValueError(f"{refused} : titre")
    in_series = [s for s in sources if spec.series and re.search(rf"\b{spec.series}\b", s["titre"] or "")]
    if spec.series and spec.series_phrase.format(n=len(in_series), dates=_dates(sorted(s["date"] for s in in_series))) \
            not in line["valeur"]:
        raise ValueError(f"{refused} : série {spec.series}")
    series_urls = {s["url_simap"] for s in in_series}

    def award(s: dict[str, Any], last: bool) -> dict[str, Any]:
        part = s["url_simap"] in series_urls
        return {"type": "marche", "date": s["date"], "dernier": last,
                "libelle": (spec.series_label if part and spec.series_label else AWARD_LABEL),
                "serie": spec.series if part else None,
                "adjudicateur": spec.authority if last else None, "objet": spec.subject if last else None,
                "titre_original": s["titre"] if last and spec.original_title else None,
                "source": "simap", "url": s["url_simap"]}

    facts = [award(latest, True)] + [award(s, False) for s in in_series if s["url_simap"] != latest["url_simap"]]
    if spec.others:
        recent = [s for s in sources[1:] if s["url_simap"] not in series_urls][:spec.others]
        stated = f"{len(recent)} autres marchés récents publiés les {_dates(sorted(s['date'] for s in recent))}"
        if len(recent) != spec.others or stated not in line["valeur"]:
            raise ValueError(f"{refused} : autres marchés")
        facts += [award(s, False) for s in recent]
    if spec.permits:
        cited = bo_citations(bo_rows, entry["nom"])
        stated = f"{len(cited)} demandes d'autorisation où elle est **auteure des plans**"
        if (stated not in line["valeur"] or "aucun autre rôle" not in line["valeur"]
                or any(c["role"] != PLANS_ROLE for c in cited)
                or not all(_fmt(c["date"]) in line["valeur"] and str(c["commune"]) in line["valeur"] for c in cited)):
            raise ValueError(f"{refused} : demandes d'autorisation du Bulletin officiel")
        # no identifier of the publication either: it leads to the published request, which names the applicant
        facts += [{"type": "demande_autorisation", "date": c["date"], "commune": c["commune"], "role": PLANS_ROLE,
                   "libelle": PERMIT_LABEL, "source": "bulletin_officiel"} for c in cited]
    # newest first; on the same day, the latest award (the publication shown above) before the others
    facts.sort(key=lambda f: (f["date"], f.get("dernier", False), f.get("url") or f.get("commune") or ""), reverse=True)
    return {"claims": spec.claims, "nom": entry["nom"], "ville": entry.get("ville"),
            "marches_52s": {"nombre": entry["n_52s"], "au": as_of, "source": "simap"}, "faits": facts}


def guided_facts(frozen: dict[str, Any], bo_rows: list[dict[str, Any]], claims: dict[str, dict[str, str]],
                 prepared: str = PREPARED) -> dict[str, Any]:
    """``frozen``: the frozen list of the first Monday; ``bo_rows``: the Bulletin officiel import (filtered, accepted
    publications only are read by ``bo_citations``); ``claims``: CLAIMS.md (``demo_export.parse_claims``)."""
    entries = {e["id"]: e for e in frozen["entreprises"]}
    missing = [g.company for g in GUIDED if g.company not in entries]
    if missing:
        raise ValueError(f"dossiers guidés absents de la liste gelée : {missing}")
    return {
        "schema": SCHEMA,
        "lundi": str(frozen["as_of"]),
        "dossiers": {g.company: _dossier(g, entries[g.company], bo_rows, claims[g.claims], str(frozen["as_of"]))
                     for g in GUIDED},
        "sources": {"simap": {"nom": SIMAP_NAME, "mention": simap.MANDATORY_NOTICE},
                    "bulletin_officiel": {"nom": BO_NAME, "mention": BO_MENTION}},
        "de_a_relire": True,
        "provenance": _provenance(list(FACTS_CLAIMS), prepared),
    }
