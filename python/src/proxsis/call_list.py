"""The weekly call list of an agency specialty: which companies to call this week, why, with which needs.

Everything is computed « as seen on Monday ``as_of`` »: only awards published before that date are read.

* **Score** (« probabilité d'activité ») — combined model of the real backtest (``real_backtest``): logistic
  regression on frequency and recency of the company's awards in the specialty, plus the radar's award
  signals (amounts, number of contracting authorities, trend). Target T0 = at least one new public award in
  the specialty in the next 8 weeks. It is trained on past weeks whose labels were complete before
  ``as_of``. It is a proxy of activity, **not** a probability of an order to Flexsis.
* **Surprise detector** — « rythme_double » (at least 2 awards in 8 weeks and twice the usual pace of the
  previous 44 weeks), « nouveau_venu » (first award in the specialty less than 8 weeks ago), and a
  logistic score on the « pic » target of the backtest. Surprises outside the top k are listed apart.
* **Needs per trade and week** — the company's own lots of the last 26 weeks, turned into persons per
  week with the declared assumptions of ``phasing`` (start delay, phase durations, labour share, weekly
  cost). A missing amount is estimated only with the measured phasing (amount ratio to the structural-work
  lot of the same chantier); otherwise the lot's labour is not quantified. Both lower the confidence.
* **Confidence** — a documented rule, not a calibrated probability: one point lost per weakness (last award
  more than 13 weeks old, estimated amount, generic CPV code, no recent lot).

Radar signals that have no history yet (building permits imported by hand since August 2026) are shown
as context and do not enter the score until they can be backtested.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

from proxsis.connectors import simap
from proxsis.entities import is_legal_entity_name, normalize_name
from proxsis.phasing import (
    DURATION_WEEKS,
    LABOUR_SHARE,
    START_DELAY_WEEKS,
    TRADE_WEIGHTS,
    WEEKLY_COST_CHF,
    PhasingModel,
    group_chantiers,
)
from proxsis.pii import PRIVATE_PLACEHOLDER
from proxsis.real_backtest import FEATURES, _x, snapshot, surprise_flags
from proxsis.specialty import PHASE_SPECIALTY, SPECIALTIES, lot_phase, phase_trades
from proxsis.taxonomy import TRADES
from proxsis.values import optional_text

SIMAP_MENTION = simap.MANDATORY_NOTICE
# Assumptions with the same status as phasing.DURATION_WEEKS (not measurable with public data; to calibrate with
# Flexsis' order history): duration of the phases outside the building CFC, and of a phase that has none.
EXTRA_DURATION_WEEKS = {"genie_civil": 12, "industrie": 8}
DEFAULT_DURATION_WEEKS = 8
# Assumption (audit of week 1, M1): a lot is carried out by a team of plausible size; a larger lot lasts longer
# instead of inflating the weekly headcount. Persons per week (mid estimate) at most:
TEAM_CAP = {"gros_oeuvre": 12, "genie_civil": 10, "terrassement": 8, "preparatoire": 6}
DEFAULT_TEAM_CAP = 6
LOT_COLUMNS = ["company", "id", "name", "city", "canton", "available_at", "decision_date", "phase", "phase_source",
               "specialty", "amount", "authority", "title", "project_id", "publication_id", "url_api", "url_simap",
               "order_city", "postal_code", "order_postal_code"]


@dataclass(frozen=True)
class CallListConfig:
    as_of: date
    specialty: str = "batiment"
    region_cantons: tuple[str, ...] = ("VS",)
    k: int = 10
    horizon_days: int = 56
    need_weeks: int = 8
    lookback_days: int = 182
    train_years: float = 2.0
    retrain_every: int = 1
    n_surprises: int = 3
    ranker: str = "frequence"  # "frequence" (52-week award count, then recency) or "combine" (logistic model)
    seed: int = 0
    extra: dict[str, Any] = field(default_factory=dict)


def company_id(key: str) -> str:
    return "ent-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]


def lot_table(records: list[dict[str, Any]]) -> pd.DataFrame:
    """One row per (company, award publication), legal entities only (masked or private names dropped)."""
    rows = []
    for r in records:
        if not str(r.get("pub_type", "")).startswith(("award", "direct")) or not r.get("publication_date"):
            continue
        phase, src = lot_phase(r)
        title = r.get("title") or {}
        t = title.get("fr") or title.get("de") or next(iter(title.values()), "")
        try:
            dec = date.fromisoformat(str(r.get("decision_date"))[:10]) if r.get("decision_date") else None
        except ValueError:
            dec = None
        for v in r.get("vendors") or []:
            name = (v.get("name") or "").strip()
            if not name or name == PRIVATE_PLACEHOLDER or not is_legal_entity_name(name):
                continue
            key = normalize_name(name)
            if not key:
                continue
            price = v.get("price_chf")
            authority = r.get("contracting_authority")
            rows.append({"company": key, "id": company_id(key), "name": name, "city": v.get("city"),
                         "canton": v.get("canton"),
                         "available_at": date.fromisoformat(str(r["publication_date"])[:10]), "decision_date": dec,
                         "phase": phase, "phase_source": src, "specialty": PHASE_SPECIALTY.get(phase or ""),
                         "amount": float(price) if price else None,
                         "authority": authority if isinstance(authority, str) and authority.strip() else None,
                         "title": t, "project_id": r.get("project_id"), "publication_id": r.get("publication_id"),
                         "url_api": (r.get("provenance") or {}).get("url"),
                         "url_simap": simap.project_page(r.get("project_id")),
                         "order_city": r.get("order_city"), "postal_code": v.get("postal_code"),
                         "order_postal_code": r.get("order_postal_code")})
    df = pd.DataFrame(rows, columns=LOT_COLUMNS)
    return df.drop_duplicates(["company", "publication_id"]).reset_index(drop=True)


def own_lot_needs(phase: str, award_date: date, amount: float, widen: float = 1.0) -> pd.DataFrame:
    """Persons per week and trade (low / mid / high) for one awarded lot — assumptions of ``phasing``."""
    trades = phase_trades(phase)
    cols = ["semaine", "metier", "personnes_bas", "personnes_milieu", "personnes_haut"]
    if not trades or not amount:
        return pd.DataFrame(columns=[*cols, "phase"])
    mid = amount * LABOUR_SHARE[1] / WEEKLY_COST_CHF[1]
    base = DURATION_WEEKS.get(phase) or EXTRA_DURATION_WEEKS.get(phase, DEFAULT_DURATION_WEEKS)
    dur = max(base, math.ceil(mid / TEAM_CAP.get(phase, DEFAULT_TEAM_CAP)))
    start = award_date + timedelta(weeks=START_DELAY_WEEKS)
    start = start + timedelta(days=(7 - start.weekday()) % 7)  # next Monday
    weights = TRADE_WEIGHTS.get(phase) or {t: 1 / len(trades) for t in trades}
    low = amount * LABOUR_SHARE[0] / WEEKLY_COST_CHF[0] / widen
    high = amount * LABOUR_SHARE[2] / WEEKLY_COST_CHF[2] * widen
    rows = [{"semaine": start + timedelta(weeks=w), "metier": t, "personnes_bas": low * weights[t] / dur,
             "personnes_milieu": mid * weights[t] / dur, "personnes_haut": high * weights[t] / dur, "phase": phase}
            for w in range(dur) for t in trades]
    return pd.DataFrame(rows, columns=[*cols, "phase"])


def _events(lots: pd.DataFrame, specialty: str) -> pd.DataFrame:
    s = lots[lots["specialty"] == specialty]
    return s.rename(columns={"amount": "value_chf"})[["company", "name", "available_at", "canton", "value_chf",
                                                       "authority", "publication_id", "url_api"]]


def _fit(ev: pd.DataFrame, as_of: date, cfg: CallListConfig) -> tuple[dict[str, Any], dict[str, Any]]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    first = ev["available_at"].min() if not ev.empty else as_of
    train_from = max(first + timedelta(days=182), as_of - timedelta(days=int(365 * cfg.train_years)))
    train_from = train_from - timedelta(days=train_from.weekday())
    weeks = []
    w = train_from
    while w + timedelta(days=cfg.horizon_days) <= as_of:
        weeks.append(w)
        w += timedelta(days=7)
    snaps = [s for s in (snapshot(ev, W, cfg.horizon_days) for W in weeks) if len(s)]
    models: dict[str, Any] = {}
    info: dict[str, Any] = {"type": "régression logistique (variables standardisées, log)",
                            "variables": [*FEATURES, "tendance"], "depuis": str(train_from),
                            "semaines_apprentissage": len(snaps),
                            "dernier_label_avant_as_of_jours": (as_of - weeks[-1]).days if weeks else None,
                            "repli_frequence": {}}
    tr = pd.concat(snaps) if snaps else pd.DataFrame()
    for name, col in (("activite", "target"), ("pic", "surge")):
        if len(tr) and tr[col].astype(bool).nunique() == 2:
            sc = StandardScaler().fit(_x(tr))
            models[name] = (sc, LogisticRegression(max_iter=2000).fit(sc.transform(_x(tr)), tr[col].astype(bool)))
            info["repli_frequence"][name] = False
        else:
            info["repli_frequence"][name] = True
    return models, info


def _predict(models: dict[str, Any], name: str, snap: pd.DataFrame) -> pd.Series:
    if name in models:
        sc, m = models[name]
        return pd.Series(m.predict_proba(sc.transform(_x(snap)))[:, 1], index=snap.index)
    r = snap["n_52s"].rank(pct=True)  # fallback: frequency rank, flagged in the model info
    return r.astype(float)


def _mode(values: pd.Series) -> Any:
    c = Counter(v for v in values if v)
    return c.most_common(1)[0][0] if c else None


REASONS: dict[str, tuple[str, str]] = {
    "marches_52s": ("{n} marchés publics gagnés dans la spécialité en 52 semaines",
                    "{n} öffentliche Aufträge im Fachbereich in 52 Wochen gewonnen"),
    "dernier_marche": ("Dernier marché il y a {jours} jours : « {titre} » ({adjudicateur})",
                       "Letzter Zuschlag vor {jours} Tagen: «{titre}» ({adjudicateur})"),
    "dernier_marche_sans_adjudicateur": ("Dernier marché il y a {jours} jours : « {titre} »",
                                         "Letzter Zuschlag vor {jours} Tagen: «{titre}»"),
    "rythme_double": ("Activité qui bondit : {n8} marchés en 8 semaines, contre {habituel} d'habitude",
                      "Sprunghafte Aktivität: {n8} Zuschläge in 8 Wochen statt üblich {habituel}"),
    "nouveau_venu": ("Nouveau venu : premier marché de la spécialité il y a moins de 8 semaines (un repère pour "
                     "prospecter : il ne prédit pas un nouveau marché)",
                     "Neu im Markt: erster Zuschlag im Fachbereich vor weniger als 8 Wochen (ein Hinweis für die "
                     "Akquise: er sagt keinen neuen Zuschlag voraus)"),
    # trades and period only, never a headcount: no measured reliability (audit week 2, M3; CLAIMS BESOIN-1)
    "besoin": ("Métiers probables dès la semaine du {debut}, à confirmer : {metiers} ; nombre de personnes non estimé",
               "Wahrscheinliche Berufe ab der Woche vom {debut}, zu bestätigen: {metiers}; Anzahl Personen nicht "
               "geschätzt"),
    "besoin_en_cours": ("Lot en cours, métiers probables à confirmer : {metiers} ; nombre de personnes non estimé",
                        "Los läuft, wahrscheinliche Berufe zu bestätigen: {metiers}; Anzahl Personen nicht geschätzt"),
    "montant_estime": ("Montant non publié : besoin estimé ({methode}), confiance réduite",
                       "Betrag nicht veröffentlicht: Bedarf geschätzt ({methode}), geringere Sicherheit"),
    "montant_non_publie": ("Montant non publié : main-d'œuvre de ce lot non chiffrée",
                           "Betrag nicht veröffentlicht: Personaleinsatz dieses Loses nicht beziffert"),
    "lots_attendus": ("{n} lots encore attendus sur ses chantiers selon le phasage mesuré",
                      "{n} weitere Lose auf ihren Baustellen laut gemessener Phasenfolge erwartet"),
    "permis_commune": ("{n} demandes d'autorisation de construire publiées dans sa commune en 8 semaines",
                       "{n} Baugesuche in der Gemeinde in 8 Wochen publiziert"),
    "permis_entreprise": ("Citée dans une demande d'autorisation de construire du {date} (Bulletin officiel)",
                          "In einem Baugesuch vom {date} genannt (Amtsblatt)"),
    "pas_de_lot_recent": ("Aucun lot dans les 26 dernières semaines : besoin non chiffré",
                          "Kein Los in den letzten 26 Wochen: Bedarf nicht beziffert"),
}
METHODS = {"phasage": ("rapport mesuré au gros œuvre du même chantier",
                       "gemessenes Verhältnis zum Rohbau derselben Baustelle")}


SINGULAR: dict[str, tuple[str, str]] = {
    "marches_52s": ("1 marché public gagné dans la spécialité en 52 semaines",
                    "1 öffentlicher Auftrag im Fachbereich in 52 Wochen gewonnen"),
    "lots_attendus": ("1 lot encore attendu sur ses chantiers selon le phasage mesuré",
                      "1 weiteres Los auf ihren Baustellen laut gemessener Phasenfolge erwartet"),
    "permis_commune": ("1 demande d'autorisation de construire publiée dans sa commune en 8 semaines",
                       "1 Baugesuch in der Gemeinde in 8 Wochen publiziert"),
    "dernier_marche": ("Dernier marché il y a 1 jour : « {titre} » ({adjudicateur})",
                       "Letzter Zuschlag vor 1 Tag: «{titre}» ({adjudicateur})"),
    "dernier_marche_sans_adjudicateur": ("Dernier marché il y a 1 jour : « {titre} »",
                                         "Letzter Zuschlag vor 1 Tag: «{titre}»"),
}


def _num(v: Any, lang: str) -> Any:
    """Decimal comma in French for numbers shown in a sentence."""
    if lang == "fr" and isinstance(v, float):
        return f"{v:g}".replace(".", ",")
    if lang == "fr" and isinstance(v, str) and re.fullmatch(r"\d+\.\d+", v):
        return v.replace(".", ",")
    return v


# Short forms shown on a card (« Dernier marché il y a 13 jours »): the title and the authority are on the dossier's
# paper. Exported as such, so that no screen has to cut the full sentence (review 1, I8).
SHORT: dict[str, tuple[tuple[str, str], tuple[str, str]]] = {  # code: ((fr, de) plural, (fr, de) singular)
    "dernier_marche": (("Dernier marché il y a {jours} jours", "Letzter Zuschlag vor {jours} Tagen"),
                       ("Dernier marché il y a 1 jour", "Letzter Zuschlag vor 1 Tag")),
}


def reason_short(reason: dict[str, Any], lang: str = "fr") -> str | None:
    """The short form of a reason, for the reasons that have one."""
    forms = SHORT.get(reason["code"])
    if forms is None:
        return None
    fr, de = forms[1] if reason.get("jours") == 1 else forms[0]
    return (fr if lang == "fr" else de).format(jours=_num(reason.get("jours"), lang))


def reason_text(reason: dict[str, Any], lang: str = "fr") -> str:
    code = reason["code"]
    if code == "dernier_marche" and not optional_text(reason.get("adjudicateur")):
        code = "dernier_marche_sans_adjudicateur"
    if code == "besoin" and reason.get("en_cours"):
        code = "besoin_en_cours"
    one = reason.get("n", reason.get("jours")) == 1
    fr, de = SINGULAR[code] if one and code in SINGULAR else REASONS[code]
    params = {k: _num(v, lang) for k, v in reason.items()}
    if reason["code"] == "montant_estime":
        params["methode"] = METHODS[reason.get("methode", "phasage")][0 if lang == "fr" else 1]
    if reason["code"] in ("besoin", "besoin_en_cours"):
        labels = [TRADES[t].label_fr if lang == "fr" else TRADES[t].label_de for t in reason.get("metiers", [])]
        params["metiers"] = ", ".join(labels)
        params["debut"] = date.fromisoformat(reason["debut"]).strftime("%d.%m.%Y")
    return (fr if lang == "fr" else de).format(**params)


def _phasing(records: list[dict[str, Any]], as_of: date) -> tuple[PhasingModel, dict[str, int], list[dict[str, Any]]]:
    past = [r for r in records if r.get("publication_date") and str(r["publication_date"])[:10] < str(as_of)]
    chantiers = group_chantiers(past)
    model = PhasingModel.fit(chantiers)
    by_project = {lot["project_id"]: ch["id"] for ch in chantiers for lot in ch["lots"]}
    return model, by_project, chantiers


def build_call_list(records: list[dict[str, Any]], cfg: CallListConfig,
                    permits: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if cfg.specialty not in SPECIALTIES:
        raise ValueError(f"spécialité inconnue : {cfg.specialty}")
    as_of = cfg.as_of
    lots_all = lot_table(records)
    lots = lots_all[lots_all["available_at"] < as_of]
    ev = _events(lots, cfg.specialty)
    models, info = _fit(ev, as_of, cfg)
    snap = snapshot(ev, as_of, cfg.horizon_days)
    if snap.empty:
        return {"as_of": str(as_of), "specialite": cfg.specialty, "entreprises": [], "surprises": [],
                "modele": info, "mention_obligatoire": SIMAP_MENTION, "hypotheses": []}
    p_act = _predict(models, "activite", snap)
    p_pic = _predict(models, "pic", snap)
    sflags = surprise_flags(snap, cfg.horizon_days)
    comp = lots.groupby("company").agg(name=("name", _mode), city=("city", _mode), canton=("canton", _mode),
                                       id=("id", "first"))
    region = [c for c in snap.index if not cfg.region_cantons or comp.loc[c, "canton"] in cfg.region_cantons]
    phasing, by_project, chantiers = _phasing(records, as_of)
    ch_by_id = {ch["id"]: ch for ch in chantiers}
    spec_lots = lots[lots["specialty"] == cfg.specialty]
    permit_rows = _permit_signals(permits or [], as_of)

    def describe(c: str) -> dict[str, Any]:
        s = snap.loc[c]
        mine = spec_lots[spec_lots["company"] == c].sort_values("available_at", ascending=False)
        recent = mine[mine["available_at"] >= as_of - timedelta(days=cfg.lookback_days)]
        reasons: list[dict[str, Any]] = [{"code": "marches_52s", "n": int(s["n_52s"])}]
        last = mine.iloc[0]
        reasons.append({"code": "dernier_marche", "jours": int(s["last_days"]), "titre": last["title"],
                        "adjudicateur": optional_text(last["authority"]), "montant": last["amount"]})
        flags = []
        if sflags.loc[c, "rythme_double"]:
            flags.append("rythme_double")
            prior = (int(s["n_52s"]) - int(s["n_8s"])) * 8 / 44
            reasons.append({"code": "rythme_double", "n8": int(s["n_8s"]), "habituel": round(prior, 1)})
        if sflags.loc[c, "nouveau_venu"]:
            flags.append("nouveau_venu")
            reasons.append({"code": "nouveau_venu"})
        weak = []
        if float(s["last_days"]) > 91:
            weak.append("dernier_marche_ancien")
        need_frames: list[pd.DataFrame] = []
        expected: list[dict[str, Any]] = []
        for _, lot in recent.iterrows():
            amount, widen = lot["amount"], 1.0
            if not amount or not np.isfinite(amount):
                # Only the measured phasing may stand in for a missing price (ratio to the structural-work lot of
                # the same chantier). A phase median would print numbers with no link to this lot: not shown.
                amount, widen = None, 2.0
                ch = ch_by_id.get(by_project.get(lot["project_id"], -1))
                ratio = phasing.phases.get(lot["phase"], {}).get("ratio")
                anchor_amounts = [x["amount"] for x in (ch or {}).get("lots", [])
                                  if x["phase"] == phasing.anchor and x["amount"]]
                if anchor_amounts and ratio and np.isfinite(ratio):
                    amount = float(anchor_amounts[0]) * float(ratio)
                    if "montant_estime" not in weak:
                        weak.append("montant_estime")
                        reasons.append({"code": "montant_estime", "methode": "phasage"})
                elif "montant_non_publie" not in weak:
                    weak.append("montant_non_publie")
                    reasons.append({"code": "montant_non_publie"})
            if lot["phase_source"] == "cpv_generique" and "code_generique" not in weak:
                weak.append("code_generique")
            start = lot["decision_date"] or lot["available_at"]
            if amount:
                need_frames.append(own_lot_needs(lot["phase"], start, float(amount), widen))
            ch = ch_by_id.get(by_project.get(lot["project_id"], -1))
            if ch and lot["phase"] == phasing.anchor:
                done = {x["phase"] for x in ch["lots"]}
                for p, st in phasing.phases.items():
                    if p in done or p == phasing.anchor or start + timedelta(days=st["p90"]) < as_of:
                        continue  # already awarded, or later than the measured 90th percentile
                    if any(x["phase"] == p for x in expected):
                        continue  # one line per phase, even across twin chantiers (audit m3)
                    expected.append({"phase": p, "chantier": ch["id"], "presence": round(st["presence"], 2),
                                     "date_p10": str(start + timedelta(days=st["p10"])),
                                     "date_p50": str(start + timedelta(days=st["p50"])),
                                     "date_p90": str(start + timedelta(days=st["p90"]))})
        if recent.empty:
            weak.append("pas_de_lot_recent")
            reasons.append({"code": "pas_de_lot_recent"})
        need = _weekly(need_frames, as_of, cfg.need_weeks)
        if need:
            tot_low = max(r["personnes_bas"] for r in _by_week(need))
            tot_high = max(r["personnes_haut"] for r in _by_week(need))
            first_week = min(r["semaine"] for r in need)
            started = any(not f.empty and f["semaine"].min() < as_of for f in need_frames)
            reasons.append({"code": "besoin", "bas": _fmt(tot_low), "haut": _fmt(tot_high), "debut": first_week,
                            "metiers": sorted({r["metier"] for r in need}), "en_cours": started})
        if expected:
            reasons.append({"code": "lots_attendus", "n": len(expected)})
        city = comp.loc[c, "city"]
        n_perm = sum(1 for pm in permit_rows if city and pm["commune_key"] == normalize_name(str(city)))
        if n_perm:
            reasons.append({"code": "permis_commune", "n": n_perm})
        for pm in permit_rows:
            if c in pm["entreprises"]:
                reasons.append({"code": "permis_entreprise", "date": pm["date"], "url": pm["url"]})
        level = ("elevee", "moyenne", "faible")[min(len(weak), 2)]
        sources = [{"date": str(r["available_at"]), "titre": r["title"], "adjudicateur": optional_text(r["authority"]),
                    "montant_chf": r["amount"], "phase": r["phase"], "url_simap": r["url_simap"],
                    "url_api": r["url_api"], "source": "simap.ch"}
                   for _, r in mine[mine["available_at"] >= as_of - timedelta(days=364)].head(10).iterrows()]
        return {"id": comp.loc[c, "id"], "nom": comp.loc[c, "name"], "ville": city, "canton": comp.loc[c, "canton"],
                "specialite": cfg.specialty, "score": round(float(p_act[c]), 4),
                "score_surprise": round(float(p_pic[c]), 4), "surprise": flags, "confiance": level,
                "faiblesses": weak, "raisons": reasons, "besoin": need, "lots_attendus": expected[:6],
                "sources": sources, "n_52s": int(s["n_52s"]), "dernier_marche_jours": int(s["last_days"])}

    n52 = snap["n_52s"].astype(int).to_dict()
    last = snap["last_days"].astype(float).to_dict()
    if cfg.ranker == "combine":
        order = sorted(region, key=lambda c: (-float(p_act[c]), -n52[c], c))
    elif cfg.ranker == "frequence":
        order = sorted(region, key=lambda c: (-n52[c], last[c], c))
    else:
        raise ValueError(f"classement inconnu : {cfg.ranker}")
    top = [describe(c) for c in order[: cfg.k]]
    for i, e in enumerate(top, 1):
        e["rang"] = i
    rest = [describe(c) for c in order[cfg.k:]]
    surprises = sorted([e for e in rest if e["surprise"]], key=lambda e: (-e["score_surprise"], e["nom"]))
    return {"as_of": str(as_of), "specialite": cfg.specialty, "region": list(cfg.region_cantons),
            "k": cfg.k, "entreprises_classees": len(region), "entreprises": top,
            "ordre_code": cfg.ranker,
            "ordre": {"frequence": "nombre de marchés de la spécialité en 52 semaines, puis le plus récent",
                      "combine": "modèle combiné (probabilité d'un nouveau marché dans les 8 semaines)"}[cfg.ranker],
            "surprises": surprises[: cfg.n_surprises], "modele": info,
            "cible": "T0 : au moins un nouveau marché public (simap) dans la spécialité dans les 8 semaines",
            "mention_obligatoire": SIMAP_MENTION, "source": "simap.ch (API, CG du 30.09.2023)",
            "hypotheses": [*phasing.assumptions,
                           "hypothèse : le besoin chiffré est la main-d'œuvre mobilisée par le lot ; la part confiée "
                           "à des temporaires est inconnue sans l'historique des commandes de Flexsis",
                           "règle : confiance élevée sans faiblesse, moyenne avec une, faible avec deux ou plus "
                           "(dernier marché > 13 semaines, montant estimé ou non publié, code CPV générique, "
                           "pas de lot récent)",
                           "le score mesure une activité (nouveau marché public), pas une commande à Flexsis"],
            "phasage": {p: {k2: (round(v, 2) if isinstance(v, float) and np.isfinite(v) else None)
                            for k2, v in st.items()} for p, st in phasing.phases.items()}}


def _fmt(x: float) -> str:
    return f"{x:.0f}" if x >= 1.5 else f"{x:.1f}"


def _weekly(frames: list[pd.DataFrame], as_of: date, n_weeks: int) -> list[dict[str, Any]]:
    frames = [f for f in frames if not f.empty]
    if not frames:
        return []
    df = pd.concat(frames)
    df = df[(df["semaine"] >= as_of) & (df["semaine"] < as_of + timedelta(weeks=n_weeks))]
    if df.empty:
        return []
    g = df.groupby(["semaine", "metier"], as_index=False).agg(
        personnes_bas=("personnes_bas", "sum"), personnes_milieu=("personnes_milieu", "sum"),
        personnes_haut=("personnes_haut", "sum"), phases=("phase", lambda x: sorted(set(x))))
    return [{"semaine": str(r["semaine"]), "metier": r["metier"], "personnes_bas": round(float(r["personnes_bas"]), 2),
             "personnes_milieu": round(float(r["personnes_milieu"]), 2),
             "personnes_haut": round(float(r["personnes_haut"]), 2), "phases": list(r["phases"])}
            for r in g.sort_values(["semaine", "metier"]).to_dict("records")]


def _by_week(need: list[dict[str, Any]]) -> list[dict[str, float]]:
    weeks: dict[str, dict[str, float]] = {}
    for r in need:
        w = weeks.setdefault(r["semaine"], {"personnes_bas": 0.0, "personnes_haut": 0.0})
        w["personnes_bas"] += r["personnes_bas"]
        w["personnes_haut"] += r["personnes_haut"]
    return list(weeks.values())


def _permit_signals(permits: list[dict[str, Any]], as_of: date) -> list[dict[str, Any]]:
    """Permits published in the 8 weeks before ``as_of``: commune key and companies (legal entities) cited."""
    out = []
    for p in permits:
        d = str(p.get("date_publication") or p.get("date") or "")[:10]
        if not d or not (str(as_of - timedelta(days=56)) <= d < str(as_of)):
            continue
        names = [n for n in p.get("entreprises_citees") or [] if is_legal_entity_name(n)]
        out.append({"date": d, "url": p.get("url"), "commune_key": normalize_name(str(p.get("commune") or "")),
                    "entreprises": {normalize_name(n) for n in names}})
    return out
