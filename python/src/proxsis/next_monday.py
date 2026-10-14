"""Visit, time 2 « Le lundi suivant » (brief « à distance », 4.2): the list of the following Monday, by the same rule
and the same function as the frozen list of the first Monday (``call_list.build_call_list``, order by number of awards
over 52 weeks), with the next companies of the ranking to take the places freed by the director's decisions, and the
publications that appeared between the two Mondays in our data. Nothing is invented: the demonstration's collection
ends on a given day; after it, no new publication is shown.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from proxsis.call_list import CallListConfig, build_call_list, lot_table

RANKED = 15  # the ten of the list and five more, for the places freed by « Écarter »


def next_monday(records: list[dict[str, Any]], first: date, frozen: list[str], data_end: date) -> dict[str, Any]:
    """``frozen``: the ten ids of the first Monday's list, checked against the same function (it must give them
    back)."""
    if first.weekday() != 0:
        raise ValueError(f"{first} n'est pas un lundi")
    cfg = CallListConfig(as_of=first, specialty="batiment", region_cantons=("VS",), k=10, ranker="frequence")
    again = [e["id"] for e in build_call_list(records, cfg)["entreprises"]]
    if again != frozen:
        raise ValueError("la règle ne redonne pas la liste du premier lundi")
    second = first + timedelta(days=7)
    nxt = build_call_list(records, CallListConfig(as_of=second, specialty="batiment", region_cantons=("VS",), k=RANKED,
                                                  ranker="frequence"))
    lots = lot_table(records)
    new = lots[(lots["available_at"] >= first) & (lots["available_at"] < second)]
    return {
        "schema": 1, "premier": str(first), "lundi": str(second), "fin_des_donnees": str(data_end),
        "regle": "nombre de marchés de la spécialité en 52 semaines, puis le plus récent (la règle de la liste)",
        "classement": [{"id": e["id"], "nom": e["nom"], "ville": e.get("ville"), "rang": i + 1}
                       for i, e in enumerate(nxt["entreprises"])],
        "nouvelles_publications": sorted({str(p) for p in new["publication_id"]}),
    }
