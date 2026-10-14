"""Act 4 of « Votre prochain lundi »: three dated stories replayed « at date T », and the measurement screen.

Rule (the same as the first examination, ``real_backtest``): at the Monday T, only simap publications published
before T are shown. Each story has three stops: (a) what was published before T, (b) the signal those pieces alone
allow, (c) what happened afterwards (date, source). Every interval is named and computed in days. A story whose
signal is not followed by a new award within the 8 weeks of the measure is a **limit**, told as clearly as the
others. No staffing need is ever documented here: every story says so.

Initial tenders are read through the simap API only (``past-publications`` then the tender's publication details,
``store_raw=False``): only dates, the title (person filter applied) and the contracting authority are kept, never a
contact. The measurement block repeats the CLAIMS line REEL-T0 and refuses to differ from it.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from proxsis.connectors import simap
from proxsis.entities import normalize_name
from proxsis.http import PoliteClient
from proxsis.pii import PRIVATE_PLACEHOLDER, authority_looks_private, redact_text

HORIZON_DAYS = 56  # the first examination: a new public award within 8 weeks
LIMIT_SENTENCE = {"fr": "Le besoin de personnel reste à confirmer.",
                  "de": "Der Personalbedarf ist noch zu bestätigen."}
MEASURE_SENTENCE = {
    "fr": "Sur notre premier examen des marchés publics, la sélection proposée n'a pas fait mieux qu'une règle "
          "simple.",
    "de": "Bei unserer ersten Prüfung der öffentlichen Aufträge hat die vorgeschlagene Auswahl nicht besser "
          "abgeschnitten als eine einfache Regel.",
}
_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_SWISS = re.compile(r"\b(\d{2})\.(\d{2})\.(\d{4})\b")
# Planned dates published in a tender (offer deadline, execution period) are known at T even when they lie after it.
_PLANNED_KEYS = {"delai_offres", "execution"}


def fmt(iso: str) -> str:
    return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}"


def _day(v: Any) -> str | None:
    m = re.match(r"\s*(\d{4}-\d{2}-\d{2})", str(v or ""))
    return m.group(1) if m else None


def _days(a: str, b: str) -> int:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


@dataclass(frozen=True)
class StorySpec:
    """A curated story: the company, the replayed Monday T and the award that triggers the signal (``pivot``).
    ``open_tenders``: awards (publication numbers) whose tender was already published and not yet awarded at T;
    only the tender is shown before T. ``objets``: short FR/DE descriptions of publications (the original title is
    always shown next to them, never translated)."""

    id: str
    company_id: str
    company: str
    ville: str
    T: date
    pivot: str
    region: dict[str, str]
    objets: dict[str, dict[str, str]]
    kind: str  # « reussite » or « limite »: checked against the data
    open_tenders: tuple[str, ...] = ()
    signal_extra: dict[str, str] = field(default_factory=dict)
    claims: str = ""


# ---------------------------------------------------------------- simap API: initial tenders

def tender_from_past(past: dict[str, Any]) -> dict[str, str] | None:
    """The project's initial tender: the earliest ``tender`` publication of its past publications."""
    tenders = [e for e in past.get("pastPublications") or []
               if str(e.get("pubType") or e.get("type") or "") == "tender" and _day(e.get("publicationDate"))]
    if not tenders:
        return None
    t = min(tenders, key=lambda e: (_day(e["publicationDate"]), str(e.get("publicationNumber") or "")))
    return {"publication_id": str(t["id"]), "numero": str(t.get("publicationNumber") or ""),
            "date": str(_day(t["publicationDate"]))}


def _period(p: Any) -> tuple[str | None, str | None]:
    if not isinstance(p, dict):
        return None, None
    if isinstance(p.get("dateRange"), list):  # observed on 2026-10-06: {"dateRange": [start, end]}
        rng = [*p["dateRange"], None, None]
        return _day(rng[0]), _day(rng[1])
    start = next((p[k] for k in p if re.search("from|start|begin", k, re.I)), None)
    end = next((p[k] for k in p if re.search(r"to$|until|end", k, re.I)), None)
    return _day(start), _day(end)


def tender_facts(detail: dict[str, Any]) -> dict[str, Any]:
    """Allowlist of a tender's publication details: dates, title (person filter), contracting authority (masked when
    it looks like a person). Contacts, addresses and free notes are never read."""
    info = detail.get("project-info") or {}
    base = detail.get("base") or {}
    dates = detail.get("dates") or {}
    proc = detail.get("procurement") or {}
    titles = simap._ml(info.get("title")) or simap._ml(base.get("title"))
    titre = {lang: redact_text(t)[0] for lang, t in titles.items()}
    lang = base.get("creationLanguage") if base.get("creationLanguage") in titre else next(iter(titre), None)
    authority = simap._first((info.get("procurementRecipientAddress") or {}).get("name"))
    if authority and authority_looks_private(authority):
        authority = PRIVATE_PLACEHOLDER
    kind = proc.get("executionDeadlineType")
    start, end = _period(proc.get("executionPeriod"))
    days = proc.get("executionDays") if isinstance(proc.get("executionDays"), int) else None
    execution = ({"type": kind, "debut": start, "fin": end, "jours": days}
                 if (kind and kind != "none") or start or end or days else None)
    return {"date": _day(dates.get("publicationDate") or base.get("publicationDate")), "titre": titre,
            "langue": lang, "adjudicateur": authority, "delai_offres": _day(dates.get("offerDeadline")),
            "execution": execution}


def fetch_tenders(client: PoliteClient, awards: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any] | None]:
    """Initial tender of each award's project, by the simap API only (two calls per award, nothing raw stored).
    Key: the award's publication number."""
    out: dict[str, dict[str, Any] | None] = {}
    for r in awards:
        res = client.get(simap.past_publications_url(r["publication_id"]), source=simap.SOURCE,
                         license=simap.LICENSE, store_raw=False)
        if res.status != 200:
            raise RuntimeError(f"simap past-publications : HTTP {res.status}")
        t = tender_from_past(res.json())
        if t is None:
            out[r["publication_number"]] = None
            continue
        url_api = simap.detail_url(r["project_id"], t["publication_id"])
        det = client.get(url_api, source=simap.SOURCE, license=simap.LICENSE, store_raw=False)
        if det.status != 200:
            raise RuntimeError(f"simap publication-details : HTTP {det.status}")
        facts = tender_facts(det.json())
        if facts["date"] and facts["date"] != t["date"]:
            raise ValueError(f"date de l'appel d'offres incohérente pour {r['publication_number']}")
        out[r["publication_number"]] = {
            **t, **{k: v for k, v in facts.items() if k != "date"},
            "url": simap.project_page(r["project_id"]), "url_api": url_api,
            "provenance": {"source": simap.SOURCE, "url": det.provenance.url,
                           "retrieved_at": det.provenance.retrieved_at.isoformat(),
                           "sha256": det.provenance.content_sha256, "licence": simap.LICENSE}}
    return out


# ---------------------------------------------------------------- local data (filtered simap awards, BO index)

def company_awards(records: Iterable[dict[str, Any]], company: str) -> list[dict[str, Any]]:
    """Awards won by the company (normalised name), once per publication, oldest first."""
    key = normalize_name(company)
    seen: set[str] = set()
    out = []
    for r in sorted(records, key=lambda r: (str(r.get("publication_date")), str(r.get("publication_number")))):
        if not str(r.get("pub_type", "")).startswith(("award", "direct")) or r["publication_id"] in seen:
            continue
        v = next((v for v in r.get("vendors") or [] if normalize_name(v.get("name") or "") == key), None)
        if v is None:
            continue
        seen.add(r["publication_id"])
        title = {k: t for k, t in (r.get("title") or {}).items() if t}
        lang = r.get("creation_language") if r.get("creation_language") in title else next(iter(title), None)
        out.append({"numero": r["publication_number"], "publication_id": r["publication_id"],
                    "project_id": r["project_id"], "date": str(r["publication_date"])[:10],
                    "decision": _day(r.get("decision_date")), "titre": title.get(lang) if lang else None,
                    "langue": lang, "adjudicateur": r.get("contracting_authority"),
                    "montant_chf": v.get("price_chf") or None, "offres": r.get("number_of_submissions"),
                    "procedure": r.get("process_type"), "url": simap.project_page(r["project_id"]),
                    "url_api": simap.detail_url(r["project_id"], r["publication_id"]), "source": simap.SOURCE})
    return out


def bo_citations(rows: Iterable[dict[str, Any]], company: str) -> list[dict[str, Any]]:
    """Accepted Bulletin officiel publications (filtered import) where the company holds an established role
    (applicant, author of plans…). A company only « cited » without a role is not counted."""
    key = normalize_name(company)
    out = []
    for r in rows:
        if r.get("statut") != "acceptée":
            continue
        role = next((k for k, names in sorted((r.get("roles") or {}).items())
                     if any(normalize_name(n) == key for n in names or [])), None)
        if role:
            out.append({"id": r["id"], "date": str(r["date_publication"])[:10], "commune": r.get("commune"),
                        "role": role, "url": r.get("url")})
    return sorted(out, key=lambda x: (x["date"], x["id"]))


# ---------------------------------------------------------------- stories

def _award_piece(a: dict[str, Any], objet: dict[str, str] | None) -> dict[str, Any]:
    return {"type": "adjudication", "numero": a["numero"], "date": a["date"], "decision": a["decision"],
            "titre": a["titre"], "langue": a["langue"], "objet": objet, "adjudicateur": a["adjudicateur"],
            "montant_chf": a["montant_chf"], "offres": a["offres"], "procedure": a["procedure"], "url": a["url"],
            "source": simap.SOURCE}


def _tender_piece(t: dict[str, Any], award_numero: str, objet: dict[str, str] | None,
                  open_at_T: bool) -> dict[str, Any]:
    titre = t.get("titre") or {}
    lang = t.get("langue")
    return {"type": "appel_offres", "numero": t["numero"], "projet_de": award_numero, "date": t["date"],
            "titre": titre.get(lang) if lang else next(iter(titre.values()), None), "langue": lang, "objet": objet,
            "adjudicateur": t.get("adjudicateur"), "delai_offres": t.get("delai_offres"),
            "execution": t.get("execution"), "ouvert_a_T": open_at_T, "url": t["url"], "source": simap.SOURCE}


def _interval(code: str, fr: str, de: str, start: str, end: str, stop: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "nom": {"fr": fr, "de": de}, "debut": start, "fin": end, "jours": _days(start, end),
            "arret": stop, **extra}


def _desc(spec: StorySpec, a: dict[str, Any], lang: str) -> str:
    o = spec.objets.get(a["numero"])
    return o[lang] if o else f"« {a['titre']} »"


def _planned(p: dict[str, Any], lang: str) -> str:
    """Works period planned in a tender (published before T, hence known at T even if it lies after T)."""
    ex = p.get("execution") or {}
    if not (ex.get("debut") and ex.get("fin")):
        return ""
    return (f" Travaux prévus par l'appel d'offres : du {fmt(ex['debut'])} au {fmt(ex['fin'])}." if lang == "fr"
            else f" Laut Ausschreibung geplante Arbeiten: {fmt(ex['debut'])} bis {fmt(ex['fin'])}.")


def build_story(spec: StorySpec, awards: list[dict[str, Any]], tenders: dict[str, dict[str, Any] | None],
                data_end: date, bo: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    T = spec.T.isoformat()
    by_num = {a["numero"]: a for a in awards}
    pivot = by_num.get(spec.pivot)
    if pivot is None or pivot["date"] >= T:
        raise ValueError(f"{spec.id} : l'adjudication {spec.pivot} n'était pas publiée avant le {T}")
    known = [a for a in awards if a["date"] < T]
    n52 = sum(1 for a in known if _days(a["date"], T) <= 364)

    pieces = [_award_piece(pivot, spec.objets.get(pivot["numero"]))]
    intervals = []
    tender = tenders.get(spec.pivot)
    if tender:
        if tender["date"] >= T:
            raise ValueError(f"{spec.id} : appel d'offres publié après le {T}")
        pieces.append(_tender_piece(tender, spec.pivot, spec.objets.get(spec.pivot), open_at_T=False))
        intervals.append(_interval("appel_offres_adjudication",
                                   "entre la publication de l'appel d'offres et celle de l'adjudication",
                                   "zwischen Publikation der Ausschreibung und des Zuschlags", tender["date"],
                                   pivot["date"], "connu",
                                   numero=spec.pivot))
    if pivot["decision"] and pivot["decision"] <= pivot["date"]:
        intervals.append(_interval("decision_publication", "entre la décision d'adjudication et sa publication",
                                   "zwischen Zuschlagsentscheid und Publikation", pivot["decision"], pivot["date"],
                                   "connu", numero=spec.pivot))
    for num in spec.open_tenders:
        t = tenders.get(num)
        if not t or t["date"] >= T:
            raise ValueError(f"{spec.id} : l'appel d'offres de {num} n'était pas publié avant le {T}")
        if num in by_num and by_num[num]["date"] < T:
            raise ValueError(f"{spec.id} : {num} était déjà adjugé avant le {T}")
        pieces.append(_tender_piece(t, num, spec.objets.get(num), open_at_T=True))
    pieces.sort(key=lambda p: (p["date"], p["numero"]))

    later = [a for a in awards if T <= a["date"] <= data_end.isoformat()]
    in_horizon = [a for a in later if _days(T, a["date"]) < HORIZON_DAYS]
    kind = "reussite" if in_horizon else "limite"
    if kind != spec.kind:
        raise ValueError(f"{spec.id} : histoire déclarée « {spec.kind} », les données disent « {kind} »")

    for p in pieces:
        ex = p.get("execution") or {}
        if p["type"] == "appel_offres" and ex.get("debut") and ex.get("fin"):
            intervals.append(_interval("travaux_prevus", "entre le début et la fin des travaux prévus par l'appel "
                                       "d'offres", "zwischen geplantem Beginn und Ende der Arbeiten (Ausschreibung)",
                                       ex["debut"], ex["fin"], "connu", numero=p["projet_de"], prevu=True))
    name = spec.company
    ctx_fr = f"{n52} marchés publics de construction remportés en 52 semaines, le dernier le {fmt(known[-1]['date'])}."
    ctx_de = f"{n52} öffentliche Bauaufträge in 52 Wochen gewonnen, der letzte am {fmt(known[-1]['date'])}."
    open_fr = "".join(f" En appel d'offres depuis le {fmt(p['date'])}, sans adjudication publiée : "
                      f"{(p['objet'] or {}).get('fr') or '« ' + str(p['titre']) + ' »'}.{_planned(p, 'fr')}"
                      for p in pieces if p["type"] == "appel_offres" and p["ouvert_a_T"])
    open_de = "".join(f" Seit {fmt(p['date'])} ausgeschrieben, noch ohne publizierten Zuschlag: "
                      f"{(p['objet'] or {}).get('de') or '«' + str(p['titre']) + '»'}.{_planned(p, 'de')}"
                      for p in pieces if p["type"] == "appel_offres" and p["ouvert_a_T"])
    own = next((p for p in pieces if p["type"] == "appel_offres" and not p["ouvert_a_T"]), None)
    own_fr = _planned(own, "fr") if own else ""
    own_de = _planned(own, "de") if own else ""
    ao_fr = f" ; appel d'offres publié le {fmt(tender['date'])}" if tender else ""
    ao_de = f"; Ausschreibung vom {fmt(tender['date'])}" if tender else ""
    known_text = {
        "fr": f"Publié avant le lundi {fmt(T)} : adjudication à {name}, publiée le {fmt(pivot['date'])}, pour "
              f"{_desc(spec, pivot, 'fr')}{ao_fr}.{own_fr}{open_fr}",
        "de": f"Vor Montag, {fmt(T)}, publiziert: Zuschlag an {name} für {_desc(spec, pivot, 'de')}, publiziert am "
              f"{fmt(pivot['date'])}{ao_de}.{own_de}{open_de}",
    }
    signal_text = {
        "fr": f"Entreprise à examiner : {name}. Raison : adjudication publiée le {fmt(pivot['date'])} pour "
              f"{_desc(spec, pivot, 'fr')}.{(' ' + spec.signal_extra['fr']) if spec.signal_extra else ''} Des travaux "
              f"sont probables ; leurs dates réelles restent à confirmer. {LIMIT_SENTENCE['fr']}",
        "de": f"Zu prüfendes Unternehmen: {name}. Grund: Zuschlag für {_desc(spec, pivot, 'de')}, publiziert am "
              f"{fmt(pivot['date'])}.{(' ' + spec.signal_extra['de']) if spec.signal_extra else ''} Arbeiten sind "
              f"wahrscheinlich; ihre tatsächlichen Daten sind noch zu bestätigen. {LIMIT_SENTENCE['de']}",
    }

    events = [_award_piece(a, spec.objets.get(a["numero"])) for a in later]
    if later:
        first = later[0]
        intervals.append(_interval("signalement_adjudication_suivante",
                                   "entre le lundi de la liste et la publication de l'adjudication suivante",
                                   "zwischen dem Montag der Liste und der Publikation des nächsten Zuschlags",
                                   T, first["date"], "ensuite",
                                   numero=first["numero"]))
        for num in spec.open_tenders:
            t = tenders[num]
            won = by_num.get(num)
            if t and won and won["date"] >= T:
                intervals.append(_interval("appel_offres_adjudication_ouvert",
                                           "entre la publication de l'appel d'offres et celle de l'adjudication",
                                           "zwischen Publikation der Ausschreibung und des Zuschlags", t["date"],
                                           won["date"], "ensuite",
                                           numero=num))
        n_more = len(later) - 1
        more_fr = (f" Puis {n_more} autre{'s' if n_more > 1 else ''} adjudication{'s' if n_more > 1 else ''} "
                   f"publiée{'s' if n_more > 1 else ''} jusqu'au {fmt(data_end.isoformat())}." if n_more else "")
        more_de = (f" Danach {n_more} weitere{'r' if n_more == 1 else ''} publizierte{'r' if n_more == 1 else ''} "
                   f"Zuschl{'äge' if n_more > 1 else 'ag'} bis {fmt(data_end.isoformat())}." if n_more else "")
        for num in spec.open_tenders:
            t, won = tenders[num], by_num.get(num)
            if t and won and won["date"] >= T and won["numero"] != first["numero"]:
                n = _days(t["date"], won["date"])
                more_fr += (f" Pour {_desc(spec, won, 'fr')} : adjudication publiée le {fmt(won['date'])}, {n} jours "
                            f"après l'appel d'offres.")
                more_de += (f" Für {_desc(spec, won, 'de')}: Zuschlag publiziert am {fmt(won['date'])}, {n} Tage nach "
                            f"der Ausschreibung.")
        after_text = {
            "fr": f"Le {fmt(first['date'])}, une nouvelle adjudication à {name} est publiée : "
                  f"{_desc(spec, first, 'fr')}, {_days(T, first['date'])} jours après le lundi de la liste.{more_fr} "
                  f"{LIMIT_SENTENCE['fr']}",
            "de": f"Am {fmt(first['date'])} wird ein neuer Zuschlag an {name} publiziert: {_desc(spec, first, 'de')}, "
                  f"{_days(T, first['date'])} Tage nach dem Montag der Liste.{more_de} {LIMIT_SENTENCE['de']}",
        }
    else:
        end = data_end.isoformat()
        intervals.append(_interval("signalement_sans_adjudication",
                                   "entre le lundi de la liste et la fin des données, sans nouvelle adjudication",
                                   "zwischen dem Montag der Liste und dem Datenende, ohne neuen Zuschlag",
                                   T, end, "ensuite"))
        after_text = {
            "fr": f"Dans les 8 semaines suivantes, aucune nouvelle adjudication publiée pour {name}, ni jusqu'au "
                  f"{fmt(end)} (fin des données). Après le lundi de la liste, aucun nouveau marché public publié. "
                  f"{LIMIT_SENTENCE['fr']}",
            "de": f"In den folgenden 8 Wochen kein neuer publizierter Zuschlag für {name}, auch nicht bis {fmt(end)} "
                  f"(Ende der Daten). Nach dem Montag der Liste kein neuer publizierter öffentlicher Auftrag. "
                  f"{LIMIT_SENTENCE['de']}",
        }
    after: dict[str, Any] = {"evenements": events, "texte": after_text,
                             "dans_les_8_semaines": bool(in_horizon)}
    traces = [b for b in (bo or []) if b["date"] >= T]
    if traces:
        dates_fr = " et ".join(sorted({fmt(b["date"]) for b in traces}))
        dates_de = " und ".join(sorted({fmt(b["date"]) for b in traces}))
        roles = {b["role"] for b in traces}
        if roles != {"auteur_plans_entreprise"}:
            raise ValueError(f"{spec.id} : rôle non prévu dans le texte : {sorted(roles)}")
        after["autres_traces"] = {
            "source": {"fr": "Bulletin officiel du Valais", "de": "Amtsblatt des Kantons Wallis"},
            "publications": traces,
            "texte": {
                "fr": f"Autre trace publiée ensuite : {name} est citée comme auteure des plans dans {len(traces)} "
                      f"demandes d'autorisation de construire (Bulletin officiel du Valais, {dates_fr}). Cela ne dit "
                      f"ni qui réalisera les travaux, ni s'il faut du personnel.",
                "de": f"Weitere spätere Spur: {name} wird in {len(traces)} Baugesuchen als Planverfasserin genannt "
                      f"(Amtsblatt des Kantons Wallis, {dates_de}). Das sagt weder, wer die Arbeiten ausführt, noch "
                      f"ob Personal nötig ist.",
            }}

    return {
        "id": spec.id, "type": kind, "claims": spec.claims,
        "entreprise": {"id": spec.company_id, "nom": name, "ville": spec.ville}, "region": spec.region,
        "date_T": T,
        "arrets": {
            "connu": {"date": T, "pieces": pieces, "texte": known_text,
                      "contexte": {"n_52s": n52, "dernier": known[-1]["date"],
                                   "texte": {"fr": ctx_fr, "de": ctx_de}}},
            "signalement": {"texte": signal_text},
            "ensuite": after,
        },
        "intervalles": intervals,
        "besoin_personnel": dict(LIMIT_SENTENCE),
    }


def _dates_in(o: Any, skip_planned: bool = True) -> list[str]:
    if isinstance(o, dict):
        return [d for k, v in o.items() if not (skip_planned and k in _PLANNED_KEYS) for d in _dates_in(v)]
    if isinstance(o, list):
        return [d for v in o for d in _dates_in(v)]
    if isinstance(o, str):
        return [m.group(0) for m in _ISO.finditer(o)] + [f"{y}-{mo}-{d}" for d, mo, y in _SWISS.findall(o)]
    return []


def hindsight_leaks(story: dict[str, Any]) -> list[str]:
    """Information from after T in the first two stops: a date after T anywhere (planned dates published in a
    tender excepted), or a piece or a context published on T or later."""
    T = story["date_T"]
    stops = story["arrets"]
    planned_dates = {d for p in stops["connu"]["pieces"] if p["date"] < T
                     for d in _dates_in({k: p.get(k) for k in _PLANNED_KEYS}, skip_planned=False)}
    out = []
    for stop in ("connu", "signalement"):
        part = {k: v for k, v in stops[stop].items() if k != "date"}
        out += [f"{stop} : {d}" for d in _dates_in(part) if d > T and d not in planned_dates]
    out += [f"pièce du {p['date']}" for p in stops["connu"]["pieces"] if p["date"] >= T]
    if stops["connu"]["contexte"]["dernier"] >= T:
        out.append(f"contexte : {stops['connu']['contexte']['dernier']}")
    return out


# ---------------------------------------------------------------- measurement screen (CLAIMS REEL-T0)

def _pct(x: float) -> float:
    return round(100 * x + 1e-9, 1)


def _num(x: float, sign: bool = False) -> str:
    s = f"{abs(x):.1f}".replace(".", ",")
    return ("−" if x < 0 else "+" if sign else "") + s


def measure_block(reel: dict[str, Any], claim: dict[str, str]) -> dict[str, Any]:
    """The first examination as the CLAIMS line REEL-T0 states it; any difference stops the export."""
    p = reel["p_at_k"]
    freq_ci = [_pct(c) for c in p["frequence_52s"]["ic95"]]
    gap = reel["m0_moins_meilleure_naive"]
    gap_pts = _pct(gap["moyenne"])
    gap_ci = [_pct(c) for c in gap["ic95"]]
    names = {
        "hasard": ({"fr": "20 entreprises tirées au hasard", "de": "20 zufällig gezogene Unternehmen"}, None),
        "recence": ({"fr": "les 20 dont le dernier marché est le plus récent",
                     "de": "die 20 mit dem jüngsten letzten Auftrag"}, None),
        "frequence_52s": ({"fr": "les 20 qui ont obtenu le plus de marchés en 52 semaines (règle simple)",
                           "de": "die 20 mit den meisten Aufträgen in 52 Wochen (einfache Regel)"}, freq_ci),
        "m0_marches": ({"fr": "la liste de Proxsis, limitée aux marchés publics",
                        "de": "die Liste von Proxsis, beschränkt auf öffentliche Aufträge"}, None),
    }
    values = []
    for code, (nom, ci) in names.items():
        v: dict[str, Any] = {"code": code, "nom": nom, "pct": _pct(p[code]["moyenne"])}
        v["affiche"] = {lang: f"{_num(v['pct'])} %" for lang in ("fr", "de")}
        if ci:
            v["ic95"] = ci
            v["affiche_ic"] = {"fr": f"{_num(ci[0])}–{_num(ci[1])} %", "de": f"{_num(ci[0])}–{_num(ci[1])} %"}
        values.append(v)
    d = reel["donnees"]
    n_fr = f"{d['adjudications']:,}".replace(",", " ")
    n_de = f"{d['adjudications']:,}".replace(",", "'")
    gap_text = f"{_num(gap_pts)} points"
    gap_ci_text = f"{_num(gap_ci[0])} à {_num(gap_ci[1], sign=True)}"
    expected = [v["affiche"]["fr"] for v in values] + [values[2]["affiche_ic"]["fr"], gap_text, gap_ci_text]
    missing = [e for e in expected if e not in claim["valeur"]]
    if f"{d['entreprises']} entreprises" not in claim["affirmation"] or \
            f"{reel['n_semaines']} semaines" not in claim["affirmation"] or \
            n_fr not in claim["limite"]:
        missing.append("périmètre")
    if missing or gap["naive"] != "frequence_52s":
        raise ValueError(f"la mesure diffère de la ligne CLAIMS REEL-T0 : {missing}")
    return {
        "claims": "REEL-T0",
        "phrase": dict(MEASURE_SENTENCE),
        "definition": {
            "fr": "Sur 20 entreprises proposées chaque semaine, part qui a obtenu un nouveau marché public dans les "
                  "8 semaines.",
            "de": "Von 20 jede Woche vorgeschlagenen Unternehmen: Anteil, der in den folgenden 8 Wochen einen neuen "
                  "öffentlichen Auftrag erhalten hat.",
        },
        "portee": {
            "fr": "Ces valeurs portent sur de futurs marchés publics, pas sur des embauches ni sur des commandes "
                  "passées à Flexsis.",
            "de": "Diese Werte betreffen künftige öffentliche Aufträge, nicht Einstellungen und nicht Aufträge an "
                  "Flexsis.",
        },
        "perimetre": {
            "adjudications": d["adjudications"], "entreprises": d["entreprises"], "semaines": reel["n_semaines"],
            "premiere_semaine": reel["semaines"][0], "derniere_semaine": reel["semaines"][1],
            "fin_des_donnees": d["fin_des_donnees"],
            "texte": {
                "fr": f"{n_fr} adjudications de construction en Suisse romande, {d['entreprises']} entreprises, "
                      f"{reel['n_semaines']} semaines (du {fmt(reel['semaines'][0])} au {fmt(reel['semaines'][1])}).",
                "de": f"{n_de} Bauzuschläge in der Westschweiz, {d['entreprises']} Unternehmen, {reel['n_semaines']} "
                      f"Wochen ({fmt(reel['semaines'][0])} bis {fmt(reel['semaines'][1])}).",
            },
        },
        "valeurs": values,
        "ecart": {
            "nom": {"fr": "Écart entre la liste de Proxsis et la règle simple",
                    "de": "Abstand zwischen der Liste von Proxsis und der einfachen Regel"},
            "points": gap_pts, "ic95": gap_ci,
            "affiche": {"fr": f"{gap_text} (marge à 95 % : {gap_ci_text})",
                        "de": f"{_num(gap_pts)} Prozentpunkte (95-%-Bereich: {_num(gap_ci[0])} bis "
                              f"{_num(gap_ci[1], sign=True)})"},
            "lecture": {
                "fr": f"La marge va de {_num(gap_ci[0])} à {_num(gap_ci[1], sign=True)} point et contient zéro : "
                      f"la différence entre {values[2]['affiche']['fr']} et {values[3]['affiche']['fr']} n'est pas "
                      f"établie, ni dans un sens ni dans l'autre.",
                "de": f"Der Bereich reicht von {_num(gap_ci[0])} bis {_num(gap_ci[1], sign=True)} Punkten und "
                      f"enthält null: Der Unterschied zwischen {values[2]['affiche']['de']} und "
                      f"{values[3]['affiche']['de']} ist nicht belegt, weder in die eine noch in die andere Richtung.",
            },
        },
    }


# ---------------------------------------------------------------- the three stories of the presentation

STORIES = (
    StorySpec(
        id="carron-martigny-2026-05", company_id="ent-1ef761b229",
        company="Société de Travaux Publics, Joseph Carron SA", ville="Saxon", T=date(2026, 5, 18), pivot="34068-02",
        region={"fr": "Région de Martigny", "de": "Region Martigny"}, kind="reussite", claims="PRES-HIST-1",
        objets={
            "34068-02": {"fr": "la réfection d'une rue et de ses canalisations à Martigny (Commune de Martigny)",
                         "de": "die Sanierung einer Strasse und ihrer Leitungen in Martigny (Gemeinde Martigny)"},
            "38218-01": {"fr": "un chemin à Chemin-Dessus (Commune de Val de Bagnes, procédure sur invitation)",
                         "de": "ein Weg in Chemin-Dessus (Gemeinde Val de Bagnes, Einladungsverfahren)"},
            "37301-02": {"fr": "une restructuration routière au Cotterg (Service de la mobilité)",
                         "de": "ein Strassenumbau in Le Cotterg (Dienststelle für Mobilität)"},
            "39123-02": {"fr": "des revêtements entre Merdenson et Le Châble (Service de la mobilité)",
                         "de": "Beläge zwischen Merdenson und Le Châble (Dienststelle für Mobilität)"},
        }),
    StorySpec(
        id="theler-ng24-2026-06", company_id="ent-866876591f", company="Theler AG, Bauunternehmung", ville="Raron",
        T=date(2026, 6, 29), pivot="39433-01", open_tenders=("35573-02", "36814-02"),
        region={"fr": "Haut-Valais", "de": "Oberwallis"}, kind="reussite", claims="PRES-HIST-2",
        objets={
            "39433-01": {"fr": "le tronçon 1 de la nouvelle route cantonale NG24 (procédure de gré à gré)",
                         "de": "Abschnitt 1 der neuen Kantonsstrasse NG24 (freihändiges Verfahren)"},
            "35573-02": {"fr": "le tronçon 2 de la NG24, un pont", "de": "Abschnitt 2 der NG24, eine Brücke"},
            "36814-02": {"fr": "le tronçon 3 de la NG24", "de": "Abschnitt 3 der NG24"},
            "41669-01": {"fr": "une station de téléphérique (NG 702, procédure de gré à gré)",
                         "de": "eine Seilbahnstation (NG 702, freihändiges Verfahren)"},
        },
        signal_extra={"fr": "Deux autres tronçons du même axe sont en appel d'offres : aucune adjudication n'est "
                            "publiée à cette date.",
                      "de": "Zwei weitere Abschnitte derselben Strasse sind ausgeschrieben: Zu diesem Zeitpunkt ist "
                            "kein Zuschlag publiziert."}),
    StorySpec(
        id="bitz-st-maurice-2026-05", company_id="ent-734d5f7d45", company="Bitz travaux publics SA", ville="Sion",
        T=date(2026, 5, 4), pivot="28041-02", region={"fr": "Sion et Saint-Maurice", "de": "Sitten und Saint-Maurice"},
        kind="limite", claims="PRES-HIST-3",
        objets={"28041-02": {"fr": "le terrassement d'un EMS à Saint-Maurice",
                             "de": "die Erdarbeiten für ein Alters- und Pflegeheim (EMS) in Saint-Maurice"}}),
)


def presentation_stories(records: list[dict[str, Any]], tenders: dict[str, dict[str, Any] | None],
                         bo_rows: list[dict[str, Any]], reel: dict[str, Any], claims: dict[str, dict[str, str]],
                         prepared: date, data_end: date,
                         specs: tuple[StorySpec, ...] = STORIES) -> dict[str, Any]:
    """histoires.json: the three stories (each checked for hindsight) and the measurement screen."""
    stories = []
    for spec in specs:
        s = build_story(spec, company_awards(records, spec.company), tenders, data_end,
                        bo=bo_citations(bo_rows, spec.company))
        leaks = hindsight_leaks(s)
        if leaks:
            raise ValueError(f"{spec.id} : information postérieure à T : {leaks}")
        stories.append(s)
    first = min(str(r.get("publication_date") or "9")[:10] for r in records)
    return {
        "schema": 1, "prepare_le": prepared.isoformat(),
        # the stories are shown as « à valider » until Hiba ticks their review sheets (working notes)
        "validation": "a_valider",
        "source": {
            "nom": simap.SOURCE, "mention": simap.MANDATORY_NOTICE, "fin_des_donnees": data_end.isoformat(),
            "perimetre": {
                "fr": f"Adjudications de construction publiées sur simap.ch (Suisse romande et adjudicateurs "
                      f"valaisans), du {fmt(first)} au {fmt(data_end.isoformat())}.",
                "de": f"Auf simap.ch publizierte Bauzuschläge (Westschweiz und Walliser Vergabestellen), vom "
                      f"{fmt(first)} bis {fmt(data_end.isoformat())}.",
            },
            "appels_offres": {"fr": "Dates des appels d'offres : simap.ch, lues par son accès officiel.",
                              "de": "Daten der Ausschreibungen: simap.ch, über den offiziellen Zugang gelesen."},
        },
        "regle": {
            "fr": "Rejeu à une date passée (un lundi) : aux deux premiers arrêts, seules les publications parues "
                  "avant cette date sont montrées.",
            "de": "Rückblick auf ein vergangenes Datum (einen Montag): An den ersten beiden Halten werden nur "
                  "Publikationen gezeigt, die vor diesem Datum erschienen sind.",
        },
        "choix": {
            "fr": "Trois histoires choisies pour illustrer, dont une limite. Elles ne mesurent rien : la mesure "
                  "générale suit.",
            "de": "Drei zur Veranschaulichung gewählte Geschichten, darunter eine Grenze. Sie messen nichts: Die "
                  "allgemeine Messung folgt.",
        },
        "histoires": stories,
        "mesure": measure_block(reel, claims["REEL-T0"]),
    }
