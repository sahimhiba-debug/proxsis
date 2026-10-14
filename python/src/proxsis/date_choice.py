"""Act 4, « Choisissez une date »: the director picks a past Monday; the presentation shows the ten companies the
simple rule would have proposed that day, then what happened in the 8 following weeks.

The computation IS the one of the specialty backtest (``proxsis backtest-specialites``, CLAIMS REEL-SPEC-BAT),
with the same functions: Bâtiment events (``call_list._events``), firms of Valais at T (``real_backtest.region_at``),
features seen at T (``real_backtest.snapshot``: publications published before T only, by publication date, never by
decision date), ranking by number of awards over 52 weeks (``_rank(…, "frequence_52s")``), target « a new public
award published in [T, T + 8 weeks[ ». Every Monday of the measure is exported, good and bad alike, so the mean of
the file is the CLAIMS figure (checked here, and again by the tests).

A Monday can be **chosen** only with 52 weeks of data before it and 8 full weeks after it; the first Mondays of the
measure (fewer than 52 weeks after the start of the collection) stay in the file for the mean, not in the choice.
No staffing need, no order to Flexsis: a new public award is not an order (the presentation says so).
"""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

import pandas as pd

from proxsis.call_list import _events, company_id
from proxsis.connectors import simap
from proxsis.real_backtest import _rank, region_at, snapshot

SPECIALTY = "batiment"
CANTONS = frozenset({"VS"})
K = 10
HORIZON_DAYS = 56  # 8 weeks, the target of the measure
HISTORY_DAYS = 364  # 52 weeks of data before a Monday that can be chosen
FIRST_WEEK = date(2025, 7, 7)  # the measure REEL-SPEC-BAT (docs/backtest/specialites_v1.json)
LAST_WEEK = date(2026, 8, 3)
CLAIMS_ID = "REEL-SPEC-BAT"
# The prepared example of the visit (Hiba, brief « à distance », 4.3): Monday 2 March 2026 if it can be chosen, else the
# nearest Monday that can (the earlier one on a tie).
EXAMPLE = date(2026, 3, 2)


def monday_of(d: date) -> date:
    """Any date is brought back to the Monday of its week."""
    return d - timedelta(days=d.weekday())


def _mode_name(values: pd.Series) -> str | None:
    """The most frequent published form, ties broken alphabetically (stable whatever the order of the files)."""
    c = Counter(v for v in values if isinstance(v, str) and v.strip())
    return min(c.items(), key=lambda kv: (-kv[1], kv[0]))[0] if c else None


def monday_list(lots: pd.DataFrame, T: date, k: int = K, cantons: frozenset[str] = CANTONS,
                horizon_days: int = HORIZON_DAYS) -> dict[str, Any]:
    """The list of the simple rule at the Monday T, and what each company obtained in [T, T + horizon[.

    Only the reveal (``nouveau_marche``) reads publications from T on; the ten companies, their order and every
    figure shown before the reveal come from publications published before T."""
    ev = _events(lots, SPECIALTY)
    past = ev[ev["available_at"] < T]
    snap = snapshot(ev, T, horizon_days)
    region = region_at(lots, set(cantons), T, past)
    snap = snap.loc[snap.index.isin(region)]
    top = list(_rank(snap, "frequence_52s")[:k])
    spec_lots = lots[lots["specialty"] == SPECIALTY]
    later = spec_lots[(spec_lots["available_at"] >= T) & (spec_lots["available_at"] < T + timedelta(days=horizon_days))]
    rows = []
    for rank, c in enumerate(top, start=1):
        mine_before = past[past["company"] == c]
        all_before = lots[(lots["company"] == c) & (lots["available_at"] < T)]
        nxt = later[later["company"] == c].sort_values(["available_at", "publication_id"])
        if bool(snap.loc[c, "target"]) != (len(nxt) > 0):  # the reveal must be the target of the measure
            raise ValueError(f"{c} : la révélation diffère de la cible de la mesure au {T}")
        first = nxt.iloc[0] if len(nxt) else None
        rows.append({
            "rang": rank, "id": company_id(c), "nom": _mode_name(mine_before["name"]),
            "ville": _mode_name(all_before["city"]),
            "marches_52s": int(snap.loc[c, "n_52s"]),
            "dernier_marche": str(mine_before["available_at"].max()),
            "nouveau_marche": None if first is None else {
                "date": str(first["available_at"]), "titre": first["title"] or None, "url": first["url_simap"],
                "nombre": len(nxt)},
        })
    # Two entries of one firm (a branch: « X AG » and « X AG, Filiale Visp ») are counted apart by the measure; the
    # screen says so instead of merging them (the figures stay those of the measure).
    for r, c in zip(rows, top, strict=True):
        parent = next((o for o, oc in zip(rows, top, strict=True) if oc != c and c.startswith(oc + " ")), None)
        r["autre_inscription_de"] = parent["rang"] if parent else None
    return {"lundi": str(T), "entreprises_classees": len(snap), "entreprises_actives": int(snap["target"].sum()),
            "dix": rows, "obtenu": sum(r["nouveau_marche"] is not None for r in rows)}


def _pct(x: float) -> str:
    """As in the CLAIMS line and the rest of the presentation: « 66,8 % » in both languages."""
    return f"{100 * x + 1e-9:.1f}".replace(".", ",") + " %"


def build(lots: pd.DataFrame, measure: dict[str, Any], claim: dict[str, str], data_end: date) -> dict[str, Any]:
    """Every Monday of the measure, the mean recomputed from them, and the refusal to differ from the measure
    (``measure``: the Bâtiment block of ``docs/backtest/specialites_v1.json``; ``claim``: its CLAIMS line)."""
    start = lots["available_at"].min()
    if LAST_WEEK + timedelta(days=HORIZON_DAYS) > data_end + timedelta(days=1):
        raise ValueError("les 8 semaines du dernier lundi dépassent les données")
    mondays = []
    T = FIRST_WEEK
    while T <= LAST_WEEK:
        m = monday_list(lots, T)
        history = (T - start).days
        m["historique_jours"] = history
        m["choisissable"] = history >= HISTORY_DAYS and T + timedelta(days=HORIZON_DAYS) <= data_end + timedelta(days=1)
        mondays.append(m)
        T += timedelta(days=7)
    p_at_k = sum(m["obtenu"] for m in mondays) / (K * len(mondays))
    base = sum(m["entreprises_actives"] / m["entreprises_classees"] for m in mondays) / len(mondays)
    t0 = measure["cibles"]["t0"]
    expected = (t0["p_at_k"]["frequence_52s"]["moyenne"], t0["taux_de_base"])
    same_weeks = (K, len(mondays), [str(FIRST_WEEK), str(LAST_WEEK)])
    if (measure["k"], measure["n_semaines"], measure["semaines"]) != same_weeks:
        raise ValueError("la mesure de référence ne porte pas sur les mêmes lundis")
    if abs(p_at_k - expected[0]) > 1e-12 or abs(base - expected[1]) > 1e-12:
        raise ValueError(f"les lundis ne redonnent pas la mesure {CLAIMS_ID} : {p_at_k} / {base} ≠ {expected}")
    shown = {"regle": _pct(p_at_k), "hasard": _pct(base)}
    wanted = [f"hasard {shown['hasard']}", f"fréquence 52 sem. {shown['regle']}"]
    if any(w not in claim["valeur"] for w in wanted) or f"{len(mondays)} semaines" not in claim["affirmation"]:
        raise ValueError(f"les lundis diffèrent de la ligne CLAIMS {CLAIMS_ID} : {shown}")
    chosen = [m["lundi"] for m in mondays if m["choisissable"]]
    example = min(chosen, key=lambda d: (abs((date.fromisoformat(d) - EXAMPLE).days), d))
    # The same mean on the Mondays that can be chosen only (the first ones of the measure have fewer than 52 weeks of
    # data before them): what the screen may show next to the dates it offers. Computed here, never by hand.
    offered = [m for m in mondays if m["choisissable"]]
    won = sum(m["obtenu"] for m in offered)
    p_offered = won / (K * len(offered))
    base_offered = sum(m["entreprises_actives"] / m["entreprises_classees"] for m in offered) / len(offered)
    return {
        "schema": 1,
        "claims": CLAIMS_ID,
        "source": {"nom": "simap.ch", "mention": simap.MANDATORY_NOTICE, "debut_des_donnees": str(start),
                   "fin_des_donnees": str(data_end)},
        "regle": {"specialite": SPECIALTY, "region": sorted(CANTONS), "k": K, "ordre": "frequence_52s",
                  "horizon_jours": HORIZON_DAYS, "historique_jours": HISTORY_DAYS},
        "choix": {"premier": chosen[0], "dernier": chosen[-1], "nombre": len(chosen), "exemple": example},
        "mesure": {"semaines": len(mondays), "premiere": str(FIRST_WEEK), "derniere": str(LAST_WEEK),
                   "regle": p_at_k, "hasard": base,
                   "affiche": {k: {"fr": v, "de": v} for k, v in shown.items()}},
        "au_choix": {"semaines": len(offered), "premiere": offered[0]["lundi"], "derniere": offered[-1]["lundi"],
                     "obtenu": won, "sur": K * len(offered), "regle": p_offered, "hasard": base_offered,
                     "affiche": {k: {"fr": _pct(v), "de": _pct(v)}
                                 for k, v in (("regle", p_offered), ("hasard", base_offered))}},
        "lundis": mondays,
    }
