"""M4 on real simap laureates: name variants, duplicates, and doubtful pairs for a human check.

simap does not publish the IDE of laureates (none observed on 2026-10-05), so matching relies on names:
exact match after normalisation (legal form, case, accents, punctuation) merges obvious variants; pairs in
the fuzzy « review » band of M4 are listed for a person to decide. Masked laureates (``[particulier]``) are
ignored.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import pandas as pd
from rapidfuzz import fuzz

from proxsis.entities import normalize_name, normalize_uid
from proxsis.pii import PRIVATE_PLACEHOLDER


def vendor_table(records: list[dict[str, Any]]) -> pd.DataFrame:
    names: dict[str, Counter[str]] = defaultdict(Counter)
    count: Counter[str] = Counter()
    cantons: dict[str, Counter[str]] = defaultdict(Counter)
    link: dict[str, str] = {}
    uids: dict[str, set[str]] = defaultdict(set)
    for r in records:
        for v in r.get("vendors") or []:
            name = (v.get("name") or "").strip()
            if not name or name == PRIVATE_PLACEHOLDER:
                continue
            key = normalize_name(name)
            if not key:
                continue
            names[key][name] += 1
            count[key] += 1
            cantons[key][str(r.get("order_canton") or "?")] += 1
            link.setdefault(key, (r.get("provenance") or {}).get("url", ""))
            uid = normalize_uid(v.get("uid"))
            if uid:
                uids[key].add(uid)
    rows = [{"cle": k, "nom": names[k].most_common(1)[0][0], "variantes": len(names[k]), "adjudications": count[k],
             "cantons": ",".join(c for c, _ in cantons[k].most_common(3)), "ide": ",".join(sorted(uids[k])),
             "lien": link[k]} for k in names]
    return pd.DataFrame(rows).sort_values("adjudications", ascending=False).reset_index(drop=True)


def doubtful_pairs(table: pd.DataFrame, low: float = 80.0, high: float = 93.0, n: int = 50) -> list[dict[str, Any]]:
    """Pairs of distinct normalised names with ``low <= token_sort_ratio < high`` (M4 review band)."""
    keys = list(table["cle"])
    rows = table.set_index("cle")
    blocks: dict[str, list[str]] = defaultdict(list)
    for k in keys:  # blocking: first 3 letters of the first word and of the longest word
        words = k.split()
        blocks[words[0][:3]].append(k)
        longest = max(words, key=len)
        if longest[:3] != words[0][:3]:
            blocks["~" + longest[:3]].append(k)
    seen: set[tuple[str, str]] = set()
    out = []
    for ks in blocks.values():
        for i, a in enumerate(ks):
            for b in ks[i + 1:]:
                pair = tuple(sorted((a, b)))
                if pair in seen:
                    continue
                seen.add(pair)  # type: ignore[arg-type]
                s = fuzz.token_sort_ratio(a, b)
                if low <= s < high:
                    ra, rb = rows.loc[pair[0]], rows.loc[pair[1]]
                    out.append({"score": round(float(s), 1), "nom_a": ra["nom"], "nom_b": rb["nom"],
                                "adjudications_a": int(ra["adjudications"]),
                                "adjudications_b": int(rb["adjudications"]),
                                "cantons_a": ra["cantons"], "cantons_b": rb["cantons"],
                                "lien_a": ra["lien"], "lien_b": rb["lien"]})
    out.sort(key=lambda p: (-p["score"], p["nom_a"]))
    return out[:n]
