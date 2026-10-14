"""M4 — entity resolution: link a mention (name, UID?, commune, canton) to a
known company.

1. UID (IDE) exact match after checksum validation — decisive.
2. Otherwise: blocking by canton, then a score combining name similarity
   (rapidfuzz on normalised names, legal form removed) and commune agreement.
   ``score >= auto_threshold`` → automatic link; between ``review_threshold``
   and ``auto_threshold`` → proposed to a human; below → no link.

The baseline is the exact match of normalised names.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

from proxsis.entities import legal_form, normalize_name, normalize_uid

# Generic words carry no identity ("Constructions X SA" vs "Constructions Y SA").
GENERIC_WORDS = frozenset(
    [
        "construction",
        "constructions",
        "batiment",
        "maconnerie",
        "electricite",
        "sanitaire",
        "peinture",
        "platrerie",
        "charpente",
        "genie",
        "civil",
        "terrassements",
        "travaux",
        "publics",
        "industrie",
        "mecanique",
        "metal",
        "horlogerie",
        "microtechnique",
        "precision",
        "logistique",
        "transports",
        "distribution",
        "pharma",
        "life",
        "sciences",
        "biotech",
        "bau",
        "hochbau",
        "baugeschaft",
        "elektro",
        "haustechnik",
        "malerei",
        "gipserei",
        "holzbau",
        "tiefbau",
        "strassenbau",
        "erdbau",
        "maschinenbau",
        "metallbau",
        "uhren",
        "mikrotechnik",
        "prazision",
        "logistik",
        "transporte",
        "et",
        "de",
        "du",
        "des",
        "la",
        "le",
        "les",
        "und",
        "constr",
        "log",
        "electr",
        "gc",
        "ht",
        "transp",
        "mikrotech",
    ]
)


def distinctive(norm_name: str) -> str:
    toks = [t for t in norm_name.split() if t not in GENERIC_WORDS]
    return " ".join(toks) if toks else norm_name


@dataclass
class Match:
    company_id: str | None
    score: float
    method: str  # "uid" | "name" | "review" | "none"


class EntityResolver:
    def __init__(
        self,
        companies: pd.DataFrame,
        auto_threshold: float = 93.0,
        review_threshold: float = 80.0,
        ambiguity_margin: float = 4.0,
    ) -> None:
        self.c = companies.reset_index(drop=True)
        self.auto = auto_threshold
        self.review = review_threshold
        self.by_uid = {u: cid for u, cid in zip(self.c["uid"], self.c["company_id"], strict=True) if isinstance(u, str)}
        self.margin = ambiguity_margin
        self.norm = self.c["name"].map(normalize_name).to_numpy()
        self.dist = np.array([distinctive(n) for n in self.norm])
        self.forms = self.c["name"].map(legal_form).to_numpy()
        self.blocks: dict[str, np.ndarray] = {str(k): g.index.to_numpy() for k, g in self.c.groupby("canton")}

    def resolve(
        self, name: str, uid: str | None = None, canton: str | None = None, commune: str | None = None
    ) -> Match:
        u = normalize_uid(uid) if uid else None
        if u and u in self.by_uid:
            return Match(self.by_uid[u], 100.0, "uid")
        idx = self.blocks.get(canton or "", np.arange(len(self.c)))
        if len(idx) == 0:
            return Match(None, 0.0, "none")
        q = normalize_name(name)
        if not q:
            return Match(None, 0.0, "none")
        cands = process.extract(q, list(self.norm[idx]), scorer=fuzz.token_sort_ratio, limit=8)
        qd = distinctive(q)
        qform = legal_form(name)
        scored: list[tuple[float, str]] = []
        for _, s_full, j in cands:
            i = idx[j]
            score = 0.4 * float(s_full) + 0.6 * float(fuzz.ratio(qd, self.dist[i]))
            if commune and commune == self.c.at[i, "commune"]:
                score += 3.0
            if qform and self.forms[i] and qform != self.forms[i]:
                score -= 4.0
            scored.append((score, str(self.c.at[i, "company_id"])))
        scored.sort(reverse=True)
        best_s, best_id = scored[0]
        second = scored[1][0] if len(scored) > 1 else -1.0
        if best_s >= self.auto and best_s - second >= self.margin:
            return Match(best_id, best_s, "name")
        if best_s >= self.review:
            return Match(best_id, best_s, "review")
        return Match(None, best_s, "none")


class ExactNameResolver:
    """Baseline: identical normalised name (and same canton)."""

    def __init__(self, companies: pd.DataFrame) -> None:
        self.map: dict[tuple[str, str], str] = {}
        for cid, n, ca in zip(companies["company_id"], companies["name"], companies["canton"], strict=True):
            self.map.setdefault((normalize_name(n), ca), cid)

    def resolve(
        self, name: str, uid: str | None = None, canton: str | None = None, commune: str | None = None
    ) -> Match:
        cid = self.map.get((normalize_name(name), canton or ""))
        return Match(cid, 100.0 if cid else 0.0, "name" if cid else "none")


# ---------------------------------------------------------------- benchmark
_ABBR = {
    "Construction": "Constr.",
    "Logistique": "Log.",
    "Électricité": "Électr.",
    "Génie Civil": "GC",
    "Haustechnik": "HT",
    "Logistik": "Log.",
    "Transports": "Transp.",
    "Mikrotechnik": "Mikrotech.",
}


def make_mentions(
    companies: pd.DataFrame, n: int, seed: int = 0, p_uid: float = 0.35, p_unknown: float = 0.2
) -> pd.DataFrame:
    """Noisy mentions of known companies + mentions of unknown companies (FICTIONAL benchmark)."""
    rng = np.random.default_rng(seed)
    rows = []
    for k in range(n):
        if rng.random() < p_unknown:
            base = companies.iloc[int(rng.integers(len(companies)))]
            name = "Neo" + base["name"].split(" ", 1)[0].lower() + " " + base["name"].split(" ", 1)[1]
            rows.append(
                {
                    "mention_id": f"m{k}",
                    "name": name,
                    "uid": None,
                    "canton": base["canton"],
                    "commune": base["commune"],
                    "truth": None,
                }
            )
            continue
        c = companies.iloc[int(rng.integers(len(companies)))]
        name = str(c["name"])
        ops = rng.random(5)
        if ops[0] < 0.3:
            name = (
                name.replace(" SA", " S.A.")
                .replace(" AG", " A.G.")
                .replace(" Sàrl", " SARL")
                .replace(" GmbH", " G.m.b.H.")
            )
        if ops[1] < 0.3:
            name = name.upper()
        if ops[2] < 0.25:
            for a, b in _ABBR.items():
                name = name.replace(a, b)
        if ops[3] < 0.25 and len(name) > 6:
            i = int(rng.integers(1, len(name) - 1))
            name = name[:i] + name[i + 1 :]  # typo: deletion
        if ops[4] < 0.2:
            name = " ".join(name.split(" ")[:-1])  # legal form dropped
        uid = c["uid"] if rng.random() < p_uid else None
        rows.append(
            {
                "mention_id": f"m{k}",
                "name": name,
                "uid": uid,
                "canton": c["canton"],
                "commune": c["commune"],
                "truth": c["company_id"],
            }
        )
    return pd.DataFrame(rows)


def benchmark(
    resolver: EntityResolver | ExactNameResolver, mentions: pd.DataFrame, count_review_as_link: bool = False
) -> dict[str, float]:
    tp = fp = fn = review = 0
    for r in mentions.itertuples():
        m = resolver.resolve(str(r.name), *(x if isinstance(x, str) else None for x in (r.uid, r.canton, r.commune)))
        linked = (
            m.company_id if (m.method in ("uid", "name") or (count_review_as_link and m.method == "review")) else None
        )
        review += m.method == "review"
        # an unknown company has no truth; pandas 3 reads its None as NaN, which is « not None »: only a string is a
        # truth (docs/backtest/reproductibilite.md, M4-1)
        truth = r.truth if isinstance(r.truth, str) else None
        if linked is not None and linked == truth:
            tp += 1
        elif linked is not None:
            fp += 1
            if truth is not None:
                fn += 1
        elif truth is not None:
            fn += 1
    p = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return {
        "precision": p,
        "recall": rc,
        "f1": 2 * p * rc / (p + rc) if p + rc else 0.0,
        "review_share": review / len(mentions),
        "n": len(mentions),
    }
