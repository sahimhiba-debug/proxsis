"""Phasing of a chantier, learnt from real simap lots: « translate a chantier into labour needs ».

Many public buildings are tendered lot by lot (CFC / BKP codes): excavation, structural work, electricity,
sanitary, finishes… awarded at different dates. This module:

1. maps CFC/BKP codes to work phases (CFC structure: SN 506 500:2017, CRB; group labels as delivered by
   simap.ch with each code) and phases to trades of ``proxsis.taxonomy``;
2. groups the lots of the same building (same contracting authority and place, similar title once codes and
   trade words are removed);
3. measures the real delay between the structural-work award (anchor) and each other phase, with bootstrap
   confidence intervals;
4. turns one award into weekly needs per trade. Timing and the amount of each phase relative to the anchor
   are **measured**; the start delay after award, the phase durations, the labour share and the weekly cost
   of a worker are **assumptions**, listed in ``PhasingModel.assumptions`` and to be calibrated with Flexsis'
   order history;
5. validates the timing on chantiers more recent than those used to build it.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

# (phase, CFC code prefixes) in the usual order of a building site. 29 (fees), 5, 6, 9 are not work.
PHASES: list[tuple[str, tuple[str, ...]]] = [
    ("preparatoire", ("1",)), ("terrassement", ("20",)), ("gros_oeuvre", ("21",)), ("enveloppe", ("22",)),
    ("electricite", ("23",)), ("cvc", ("24",)), ("sanitaire", ("25",)), ("transport", ("26",)),
    ("amenagement_int", ("27",)), ("finitions", ("28",)), ("equipement", ("3",)), ("exterieur", ("4",)),
]
PHASE_ORDER = [p for p, _ in PHASES]
# Trades of proxsis.taxonomy per phase (envelope, HVAC, lifts: trades outside the taxonomy → none).
PHASE_TRADES: dict[str, tuple[str, ...]] = {
    "preparatoire": ("machiniste", "manoeuvre_construction"),
    "terrassement": ("machiniste", "manoeuvre_construction"),
    "gros_oeuvre": ("macon", "coffreur", "manoeuvre_construction", "grutier"),
    "enveloppe": (), "electricite": ("electricien",), "cvc": (), "sanitaire": ("installateur_sanitaire",),
    "transport": (), "amenagement_int": ("platrier",), "finitions": ("peintre",), "equipement": (),
    "exterieur": ("machiniste", "manoeuvre_construction"),
}
TRADE_WEIGHTS: dict[str, dict[str, float]] = {  # assumption: split of a phase's labour between its trades
    "gros_oeuvre": {"macon": 0.4, "manoeuvre_construction": 0.3, "coffreur": 0.2, "grutier": 0.1},
}

# Assumptions (not measurable with public data; to calibrate with Flexsis' history).
START_DELAY_WEEKS = 4
DURATION_WEEKS: dict[str, int] = {"preparatoire": 4, "terrassement": 6, "gros_oeuvre": 16, "enveloppe": 8,
                                  "electricite": 12, "cvc": 12, "sanitaire": 12, "transport": 6,
                                  "amenagement_int": 8, "finitions": 6, "equipement": 6, "exterieur": 6}
LABOUR_SHARE = (0.25, 0.35, 0.45)  # (low, mid, high) share of the contract price paid as labour
WEEKLY_COST_CHF = (2600.0, 2300.0, 2000.0)  # (low needs ↔ high cost, mid, high needs ↔ low cost)


def phase_of(codes: list[str]) -> str | None:
    found = []
    for c in codes or []:
        c = str(c).strip()
        if c.startswith("29"):
            continue
        for i, (_phase, prefixes) in enumerate(PHASES):
            if any(c.startswith(p) for p in prefixes):
                found.append(i)
                break
    return PHASE_ORDER[min(found)] if found else None


def _words(text: str) -> frozenset[str]:
    return frozenset(text.split())


_STOP = _words("le la les du de des d l et a au aux en sur pour par un une der die das dem den des und fur von vom "
              "im in am an zum zur bei mit the of and")
_TRADE_WORDS = _words("""maconnerie macon beton gros oeuvre second electricite electrique electricien installations
installation sanitaire sanitaires chauffage ventilation climatisation cvc cvse peinture peintre platrerie platre
plafonds faux menuiserie menuiseries charpente couverture ferblanterie etancheite etancheites fenetres fenetre
carrelage carrelages chapes chape revetements revetement sols sol serrurerie metallique metalliques echafaudages
echafaudage terrassement terrassements demolition demolitions travaux lot lots cfc bkp ccc npk ascenseurs ascenseur
nettoyage isolation crepis facade facades toiture vitrages portes porte estriche estrich baumeisterarbeiten
baumeister bauarbeiten elektro elektroinstallationen elektroanlagen sanitar sanitaranlagen heizung heizungsanlagen
luftung luftungsanlagen lueftung malerarbeiten maler gipser gipserarbeiten fenster bedachung spengler
spenglerarbeiten schreiner schreinerarbeiten bodenbelage bodenbelag plattenarbeiten metallbau gerust gerustbau
aushub abbruch arbeiten lieferung montage reinigung dach dachdecker""")


def _plain(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return s.replace("ß", "ss")


def title_stem(title: str) -> str:
    s = _plain(title or "")
    s = re.sub(r"\b(?:cfc|bkp|ccc|npk|ebkp[-\w]*)\s*[\d.]+", " ", s)
    s = re.sub(r"\blot\s*[\w.]+", " ", s)
    s = re.sub(r"[^a-z]+", " ", s)
    return " ".join(t for t in s.split() if t not in _STOP and t not in _TRADE_WORDS and len(t) > 1)


def _key(s: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", _plain(str(s or ""))).strip()


def _lot_date(r: dict[str, Any]) -> date | None:
    for k in ("decision_date", "publication_date"):
        v = r.get(k)
        if v:
            try:
                return date.fromisoformat(str(v)[:10])
            except ValueError:
                continue
    return None


def group_chantiers(records: list[dict[str, Any]], min_jaccard: float = 0.5) -> list[dict[str, Any]]:
    """Lots of the same building: same authority and place, title stems with Jaccard >= ``min_jaccard``."""
    lots: list[dict[str, Any]] = []
    for r in records:
        ph = phase_of(r.get("bkp_codes") or [])
        d = _lot_date(r)
        auth = _key(r.get("contracting_authority"))
        if ph is None or d is None or not auth or auth == "particulier":
            continue
        title = (r.get("title") or {})
        t = title.get("fr") or title.get("de") or next(iter(title.values()), "") if title else ""
        amount = sum(float(v.get("price_chf") or 0) for v in r.get("vendors") or []) or None
        lots.append({"project_id": r.get("project_id"), "phase": ph, "date": d, "amount": amount,
                     "codes": r.get("bkp_codes"), "stem": title_stem(t), "auth": auth,
                     "place": _key(r.get("order_city"))})
    by_key: dict[tuple[str, str], list[int]] = {}
    for i, lot in enumerate(lots):
        by_key.setdefault((lot["auth"], lot["place"]), []).append(i)
    parent = list(range(len(lots)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for idx in by_key.values():
        toks = {i: set(lots[i]["stem"].split()) for i in idx}
        for a_pos, a in enumerate(idx):
            for b in idx[a_pos + 1:]:
                ta, tb = toks[a], toks[b]
                close = abs((lots[a]["date"] - lots[b]["date"]).days) <= 3 * 365
                # at least two shared words: a generic stem (« rénovation ») must not merge different buildings
                if close and len(ta & tb) >= 2 and len(ta & tb) / len(ta | tb) >= min_jaccard:
                    parent[find(a)] = find(b)
    groups: dict[int, list[dict[str, Any]]] = {}
    for i in range(len(lots)):
        groups.setdefault(find(i), []).append(lots[i])
    out = []
    for gid, ls in enumerate(groups.values()):
        ls.sort(key=lambda x: x["date"])
        out.append({"id": gid, "authority": ls[0]["auth"], "place": ls[0]["place"], "stem": ls[0]["stem"], "lots": ls})
    return out


def _anchor(ch: dict[str, Any], anchor: str) -> tuple[date, float | None] | None:
    a = [lot for lot in ch["lots"] if lot["phase"] == anchor]
    if not a:
        return None
    first = min(a, key=lambda x: x["date"])
    return first["date"], first["amount"]


def _phase_lags(chantiers: list[dict[str, Any]],
                anchor: str) -> tuple[dict[str, list[float]], int, dict[str, list[float]]]:
    lags: dict[str, list[float]] = {p: [] for p in PHASE_ORDER if p != anchor}
    ratios: dict[str, list[float]] = {p: [] for p in PHASE_ORDER if p != anchor}
    n_anchor = 0
    for ch in chantiers:
        a = _anchor(ch, anchor)
        if a is None:
            continue
        n_anchor += 1
        a_date, a_amount = a
        for p in lags:
            ls = [lot for lot in ch["lots"] if lot["phase"] == p]
            if ls:
                first = min(ls, key=lambda x: x["date"])
                lags[p].append(float((first["date"] - a_date).days))
                if a_amount and first["amount"]:
                    ratios[p].append(float(first["amount"]) / float(a_amount))
    return lags, n_anchor, ratios


def _boot_median(x: np.ndarray, n_boot: int, rng: np.random.Generator) -> list[float]:
    if len(x) == 0:
        return [float("nan"), float("nan")]
    meds = [float(np.median(rng.choice(x, size=len(x), replace=True))) for _ in range(n_boot)]
    return [float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))]


def measure_lags(chantiers: list[dict[str, Any]], anchor: str = "gros_oeuvre", n_boot: int = 2000,
                 seed: int = 0) -> dict[str, Any]:
    lags, n_anchor, ratios = _phase_lags(chantiers, anchor)
    rng = np.random.default_rng(seed)
    out: dict[str, Any] = {"_ancre": anchor, "_chantiers_avec_ancre": n_anchor}
    for p, xs in lags.items():
        x = np.array(xs)
        if len(x) == 0:
            continue
        out[p] = {"n": len(x), "presence": len(x) / n_anchor if n_anchor else None,
                  "mediane_jours": float(np.median(x)), "p10_jours": float(np.percentile(x, 10)),
                  "p90_jours": float(np.percentile(x, 90)), "ic95_mediane": _boot_median(x, n_boot, rng),
                  "rapport_montant_median": float(np.median(ratios[p])) if ratios[p] else None}
    return out


@dataclass
class PhasingModel:
    anchor: str
    phases: dict[str, dict[str, float]]
    median_anchor_amount: float | None
    assumptions: list[str] = field(default_factory=list)

    @classmethod
    def fit(cls, chantiers: list[dict[str, Any]], anchor: str = "gros_oeuvre") -> PhasingModel:
        lags, n_anchor, ratios = _phase_lags(chantiers, anchor)
        phases: dict[str, dict[str, float]] = {anchor: {"presence": 1.0, "p10": 0.0, "p50": 0.0, "p90": 0.0,
                                                         "ratio": 1.0}}
        for p, xs in lags.items():
            if len(xs) >= 3:
                x = np.array(xs)
                phases[p] = {"presence": len(x) / n_anchor, "p10": float(np.percentile(x, 10)),
                             "p50": float(np.median(x)), "p90": float(np.percentile(x, 90)),
                             "ratio": float(np.median(ratios[p])) if ratios[p] else float("nan")}
        amounts = [a[1] for ch in chantiers if (a := _anchor(ch, anchor)) and a[1]]
        assumptions = [
            f"mesuré : délai entre l'adjudication de l'ancre ({anchor}) et celle de chaque phase (quantiles 10/50/90)",
            "mesuré : probabilité qu'une phase soit adjugée séparément dans le même chantier",
            "mesuré : montant de chaque phase rapporté au montant de l'ancre (médiane)",
            f"hypothèse : début des travaux {START_DELAY_WEEKS} semaines après l'adjudication",
            f"hypothèse : durées des phases en semaines {DURATION_WEEKS}",
            f"hypothèse : part de main-d'œuvre dans le prix {LABOUR_SHARE} (bas, milieu, haut)",
            f"hypothèse : coût hebdomadaire d'une personne en CHF {WEEKLY_COST_CHF}",
            "hypothèse : répartition de la main-d'œuvre d'une phase entre ses métiers (égale, sauf gros œuvre)",
        ]
        return cls(anchor, phases, float(np.median(amounts)) if amounts else None, assumptions)

    def needs(self, anchor: date, amount_chf: float | None) -> pd.DataFrame:
        """Weekly needs per trade (persons, low / mid / high) after an award of the anchor phase."""
        widen = 1.0
        if amount_chf is None:
            amount_chf, widen = (self.median_anchor_amount or 1_000_000.0), 2.0
        rows = []
        for p, s in self.phases.items():
            trades = PHASE_TRADES.get(p, ())
            if not trades:
                continue
            ratio = s["ratio"] if np.isfinite(s.get("ratio", float("nan"))) else 0.2
            amount = amount_chf * ratio
            dur = DURATION_WEEKS.get(p, 8)
            start = anchor + timedelta(days=max(0.0, s["p50"])) + timedelta(weeks=START_DELAY_WEEKS)
            weights = TRADE_WEIGHTS.get(p) or {t: 1 / len(trades) for t in trades}
            mid_pw = amount * LABOUR_SHARE[1] / WEEKLY_COST_CHF[1] * s["presence"]
            low_pw = amount * LABOUR_SHARE[0] / WEEKLY_COST_CHF[0] * s["presence"] / widen
            high_pw = amount * LABOUR_SHARE[2] / WEEKLY_COST_CHF[2] * widen
            for w in range(dur):
                wk = start + timedelta(weeks=w)
                wk = wk - timedelta(days=wk.weekday())
                for t in trades:
                    rows.append({"semaine": max(wk, anchor - timedelta(days=anchor.weekday())), "phase": p,
                                 "metier": t, "personnes_bas": low_pw * weights[t] / dur,
                                 "personnes_milieu": mid_pw * weights[t] / dur,
                                 "personnes_haut": high_pw * weights[t] / dur})
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df = df.groupby(["semaine", "metier"], as_index=False)[["personnes_bas", "personnes_milieu",
                                                               "personnes_haut"]].sum()
        df["semaine"] = df["semaine"].map(lambda d: max(d, anchor))
        return df.sort_values(["semaine", "metier"]).reset_index(drop=True)


def validate(chantiers: list[dict[str, Any]], cutoff: date, anchor: str = "gros_oeuvre") -> dict[str, Any]:
    """Fit on chantiers whose anchor is before ``cutoff``, test the timing on the more recent ones."""
    train = [ch for ch in chantiers if (a := _anchor(ch, anchor)) and a[0] < cutoff]
    test = [ch for ch in chantiers if (a := _anchor(ch, anchor)) and a[0] >= cutoff]
    model = PhasingModel.fit(train, anchor)
    tr_lags, _, _ = _phase_lags(train, anchor)
    all_train = [x for xs in tr_lags.values() for x in xs]
    ref = float(np.median(all_train)) if all_train else 0.0
    te_lags, _, _ = _phase_lags(test, anchor)
    covered, err, err_ref, by_phase = [], [], [], {}
    for p, xs in te_lags.items():
        s = model.phases.get(p)
        if s is None or not xs:
            continue
        c = [s["p10"] <= x <= s["p90"] for x in xs]
        e = [abs(x - s["p50"]) for x in xs]
        covered += c
        err += e
        err_ref += [abs(x - ref) for x in xs]
        by_phase[p] = {"n_test": len(xs), "couverture": float(np.mean(c)), "mae_jours": float(np.mean(e))}
    return {"coupure": str(cutoff), "n_chantiers_apprentissage": len(train), "n_chantiers_test": len(test),
            "n_lots_test": len(covered), "couverture_p10_p90": float(np.mean(covered)) if covered else None,
            "mae_mediane_jours": float(np.mean(err)) if err else None,
            "mae_reference_jours": float(np.mean(err_ref)) if err_ref else None,
            "reference": "un seul délai (médiane de toutes les phases)", "par_phase": by_phase}
