"""Overview of the collected simap awards: volume, period, Valais share, trades, quarters, masking.

Valais localisation crosses three criteria, because 47 % of simap projects have no canton of execution:
1. canton of execution = VS;
2. issued by a Valais authority (search filtered on the « Valais » root institution and its children);
3. a Valais commune or locality cited in the place, title or description (OpenPLZ list).
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from datetime import date
from typing import Any

import numpy as np

from proxsis.connectors import simap
from proxsis.phasing import PHASE_TRADES, phase_of
from proxsis.pii import PRIVATE_PLACEHOLDER


def _plain(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def _texts(r: dict[str, Any]) -> str:
    parts = [str(r.get("order_city") or "")]
    for k in ("title", "description"):
        parts += [str(v) for v in (r.get(k) or {}).values()]
    return _plain(" ".join(parts))


def place_pattern(places: set[str]) -> re.Pattern[str] | None:
    names = sorted({_plain(p) for p in places if len(p) >= 4}, key=len, reverse=True)
    if not names:
        return None
    return re.compile(r"(?<![a-z])(?:" + "|".join(re.escape(n) for n in names) + r")(?![a-z])")


def overview(romandie: list[dict[str, Any]], vs_issuer: list[dict[str, Any]], places: set[str], sample: int = 20,
             seed: int = 0) -> dict[str, Any]:
    by_id: dict[str, dict[str, Any]] = {}
    for r in [*romandie, *vs_issuer]:
        by_id.setdefault(r["publication_id"], r)
    recs = list(by_id.values())
    vs_ids = {r["publication_id"] for r in vs_issuer}
    pat = place_pattern(places)
    c_canton = c_issuer = c_place = c_any = 0
    quarters: Counter[str] = Counter()
    trades: Counter[str] = Counter()
    trades_q: dict[str, Counter[str]] = {}
    dates = []
    for r in recs:
        d = date.fromisoformat(str(r["publication_date"])[:10])
        dates.append(d)
        q = f"{d.year}-T{(d.month - 1) // 3 + 1}"
        quarters[q] += 1
        a = r.get("order_canton") == "VS"
        b = r["publication_id"] in vs_ids
        c = bool(pat.search(_texts(r))) if pat else False
        c_canton += a
        c_issuer += b
        c_place += c
        c_any += a or b or c
        ph = phase_of(r.get("bkp_codes") or [])
        for t in PHASE_TRADES.get(ph or "", ()) or (("sans_metier_de_la_taxonomie",) if ph else ("sans_code_cfc",)):
            trades[t] += 1
            trades_q.setdefault(q, Counter())[t] += 1
    vendors = [(r, v) for r in recs for v in r.get("vendors") or []]
    masked = [(r, v) for r, v in vendors if v.get("name") == PRIVATE_PLACEHOLDER]
    rng = np.random.default_rng(seed)
    pick = [masked[i] for i in sorted(rng.choice(len(masked), size=min(sample, len(masked)), replace=False))] \
        if masked else []
    return {
        "n_adjudications": len(recs),
        "sans_canton_des_travaux": sum(not r.get("order_canton") for r in recs),
        "periode": [str(min(dates)), str(max(dates))] if dates else None,
        "valais": {"par_canton_des_travaux": c_canton, "par_adjudicateur_valaisan": c_issuer, "par_lieu_cite": c_place,
                   "au_moins_un_critere": c_any, "part": c_any / len(recs) if recs else None},
        "par_trimestre": dict(sorted(quarters.items())),
        "par_metier": dict(trades.most_common()),
        "metiers_par_trimestre": {k: dict(v.most_common()) for k, v in sorted(trades_q.items())},
        "masquage": {"laureats_total": len(vendors), "laureats_masques": len(masked),
                     "adjudicateurs_masques": sum(r.get("contracting_authority") == PRIVATE_PLACEHOLDER for r in recs),
                     "echantillon_a_verifier": [
                         {"publication": r["publication_id"], "date": r["publication_date"],
                          "titre": next(iter((r.get("title") or {}).values()), ""),
                          "adjudicateur": r.get("contracting_authority"),
                          "lien_simap": simap.project_page(r.get("project_id"))}
                         for r, _ in pick]},
    }
