"""Inter-annotator agreement, arbitration merge and freezing of the real test set.

* :func:`assign` — each item gets a primary annotator (not its collector when
  possible); ``n_double`` items drawn at random, stratified, get a second,
  different annotator who does not see the first one's work.
* :func:`agreement` — Cohen's kappa for categorical fields and for each trade
  (present / absent); **exact** agreement for amounts, dates and names (names
  and communes after normalisation of case, accents and punctuation); mean
  Jaccard on the trade sets; lists every item where the two annotators differ.
* :func:`reliability` — a field on which humans do not agree (kappa < 0.6 or
  exact agreement < 0.8: conventional thresholds, e.g. Landis & Koch 1977 for
  kappa) must not be used to judge a model without caution.
* :func:`merge_gold` — reference = agreed values; disagreements are taken
  from the arbitration file (a third person). An unresolved disagreement is an
  error.
* :func:`freeze` — writes the reference (text + gold) once and records its
  SHA-256 in ``FROZEN.md``. A frozen file is never overwritten.

Profiles (:data:`PROFILES`): the compared fields depend on what the page asks.
``simap`` (default) is the original set. ``bo_fr`` and ``bo_de_structure``
are the Bulletin officiel building permits (decision of 2026-10-06): parcels
and coordinates are masked by the filter before any write, so only their
PRESENCE is annotated; nobody reads German, so the German lot is measured on
the structured fields only (never the trades), separately from French.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from proxsis.taxonomy import TRADES

CATEGORICAL = ("doc_type", "rc_subtype", "private_person", "besoin_temporaire", "parcelle_mentionnee",
               "coordonnees_mentionnees")
TEXTUAL = ("company_name", "commune", "uid")
EXACT = ("company_name", "uid", "commune", "amount_chf", "date_evenement", "date_debut_travaux", "date_expiration")
COMPARED = ("doc_type", "company_name", "uid", "commune", "amount_chf", "rc_subtype", "trades", "private_person",
            "besoin_temporaire", "date_evenement", "date_debut_travaux")
BO_STRUCTURE = ("company_name", "private_person", "commune", "date_evenement", "date_expiration",
                "parcelle_mentionnee", "coordonnees_mentionnees")
DEFAULT_PROFILE = "simap"
PROFILES: dict[str, tuple[str, ...]] = {
    DEFAULT_PROFILE: COMPARED,
    "bo_fr": (*BO_STRUCTURE, "amount_chf", "date_debut_travaux", "trades", "besoin_temporaire"),
    "bo_de_structure": BO_STRUCTURE,
}
FIXED: dict[str, dict[str, str]] = {"bo_fr": {"doc_type": "permis_construire"},
                                    "bo_de_structure": {"doc_type": "permis_construire"}}
NOT_COMPARED = ("commentaire",)
KAPPA_MIN = 0.6
EXACT_MIN = 0.8


def compared_fields(profile: str = DEFAULT_PROFILE) -> tuple[str, ...]:
    if profile not in PROFILES:
        raise ValueError(f"profil d'annotation inconnu : {profile!r} (connus : {', '.join(PROFILES)})")
    return PROFILES[profile]


def _check_profile(rows: list[dict[str, Any]], profile: str) -> None:
    """A Bulletin officiel export may only hold its profile's fields: a German export with trades (or any other
    field the German page does not ask) comes from a wrong page and is refused, not measured."""
    fields = compared_fields(profile)
    if profile == DEFAULT_PROFILE:
        return
    allowed = {*fields, *FIXED.get(profile, {}), *NOT_COMPARED}
    for r in rows:
        extra = sorted(set(r["gold"]) - allowed)
        if extra:
            raise ValueError(f"champ hors profil {profile} dans {r['id']} : {', '.join(extra)}")


def _norm(v: Any) -> str:
    if v is None:
        return ""
    s = unicodedata.normalize("NFKD", str(v))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[\s.,;:'’\-]+", " ", s).strip()


def same(field: str, a: Any, b: Any) -> bool:
    if field == "amount_chf":  # exact (to the centime): instruction of 2026-10-05
        if a is None or b is None:
            return a is None and b is None
        return abs(float(a) - float(b)) < 0.005
    if field == "trades":
        return sorted(a or []) == sorted(b or [])
    if field in TEXTUAL:
        return _norm(a) == _norm(b)
    return bool(a == b)


def cohen_kappa(x: list[Any], y: list[Any]) -> float | None:
    n = len(x)
    if n == 0:
        return None
    po = sum(a == b for a, b in zip(x, y, strict=True)) / n
    cx, cy = Counter(x), Counter(y)
    pe = sum(cx[k] * cy[k] for k in set(cx) | set(cy)) / (n * n)
    if pe == 1.0:
        return None  # audit m7: no variation (e.g. a pre-filled field) → kappa is undefined, not 1
    return float((po - pe) / (1 - pe))


def agreement(a_rows: list[dict[str, Any]], b_rows: list[dict[str, Any]],
              profile: str = DEFAULT_PROFILE) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    compared = compared_fields(profile)
    _check_profile([*a_rows, *b_rows], profile)
    A = {r["id"]: r["gold"] for r in a_rows}
    B = {r["id"]: r["gold"] for r in b_rows}
    ids = sorted(set(A) & set(B))
    exact = {f: sum(same(f, A[i].get(f), B[i].get(f)) for i in ids) / len(ids) if ids else None for f in compared}
    kappa = {f: cohen_kappa([A[i].get(f) for i in ids], [B[i].get(f) for i in ids])
             for f in CATEGORICAL if f in compared}
    dis = []
    for i in ids:
        fields = [f for f in compared if not same(f, A[i].get(f), B[i].get(f))]
        if fields:
            dis.append({"id": i, "champs": fields, "A": {f: A[i].get(f) for f in fields},
                        "B": {f: B[i].get(f) for f in fields}})
    rep: dict[str, Any] = {"profil": profile, "n_A": len(A), "n_B": len(B), "n_commun": len(ids),
                           "accord_exact": exact, "kappa": kappa}
    if "trades" in compared:
        jac = []
        for i in ids:
            sa, sb = set(A[i].get("trades") or []), set(B[i].get("trades") or [])
            jac.append(1.0 if not sa and not sb else len(sa & sb) / len(sa | sb))
        rep["kappa_par_metier"] = {t: cohen_kappa([t in (A[i].get("trades") or []) for i in ids],
                                                  [t in (B[i].get("trades") or []) for i in ids]) for t in TRADES}
        rep["trades_jaccard_moyen"] = sum(jac) / len(jac) if jac else None
    rep["n_desaccords"] = len(dis)
    return rep, dis


def reliability(rep: dict[str, Any], kappa_min: float = KAPPA_MIN, exact_min: float = EXACT_MIN) -> dict[str, Any]:
    """Field by field, for the fields of the report's profile (a report without profile is the default one)."""
    out: dict[str, Any] = {}
    n = rep["n_commun"]
    for f in compared_fields(rep.get("profil", DEFAULT_PROFILE)):
        if f in CATEGORICAL and rep["kappa"].get(f) is None:
            v, measure = rep["accord_exact"].get(f), "accord_brut (kappa indéfini : aucune variation)"
            ok = v is not None and v >= exact_min
        elif f in CATEGORICAL:
            v, measure = rep["kappa"].get(f), "kappa"
            ok = v is not None and v >= kappa_min
        elif f == "trades":
            v, measure = rep["trades_jaccard_moyen"], "jaccard_moyen"
            ok = v is not None and v >= exact_min
        else:
            v, measure = rep["accord_exact"].get(f), "accord_exact"
            ok = v is not None and v >= exact_min
        out[f] = {"mesure": measure, "valeur": v, "n": n, "fiable": bool(ok),
                  "consigne": None if ok else "les humains ne s'accordent pas : ne pas juger un modèle sur ce champ "
                                              "sans précaution"}
    return out


def assign(items: list[dict[str, Any]], annotators: list[str], n_double: int = 20,
           seed: int = 20261005) -> dict[str, dict[str, str | None]]:
    """Primary annotator for every item (round robin, not the collector when possible); ``n_double`` items,
    stratified by ``strate``, get a second annotator different from the primary one (and from the collector)."""
    import numpy as np

    rng = np.random.default_rng(seed)
    order = [items[i] for i in rng.permutation(len(items))]
    load = dict.fromkeys(annotators, 0)
    out: dict[str, dict[str, str | None]] = {}

    def pick(exclude: set[str]) -> str:
        choices = [a for a in annotators if a not in exclude] or annotators
        return min(choices, key=lambda a: (load[a], annotators.index(a)))

    for it in order:
        a = pick({str(it.get("collecteur"))})
        load[a] += 1
        out[it["id"]] = {"primaire": a, "second": None}
    strata: dict[str, list[dict[str, Any]]] = {}
    for it in order:
        strata.setdefault(str(it.get("strate")), []).append(it)
    keys = sorted(strata)
    chosen: list[dict[str, Any]] = []
    while len(chosen) < min(n_double, len(items)):
        for k in keys:
            if strata[k] and len(chosen) < n_double:
                chosen.append(strata[k].pop(0))
    for it in chosen:
        b = pick({out[it["id"]]["primaire"] or "", str(it.get("collecteur"))})
        load[b] += 1
        out[it["id"]]["second"] = b
    return dict(sorted(out.items()))


def merge_gold_partial(primary: list[dict[str, Any]], second: list[dict[str, Any]],
                       arbitration: list[dict[str, Any]], profile: str = DEFAULT_PROFILE) -> list[dict[str, Any]]:
    """Reference = primary annotation; on double-annotated items, agreed values, and arbitration otherwise (on the
    profile's compared fields)."""
    compared = compared_fields(profile)
    _check_profile([*primary, *second, *arbitration], profile)
    B = {r["id"]: r["gold"] for r in second}
    who_b = {r["id"]: r.get("annotateur") for r in second}
    C = {r["id"]: r["gold"] for r in arbitration}
    for r in primary:  # audit M8: a double annotation needs two different people
        if r["id"] in who_b and who_b[r["id"]] == r.get("annotateur"):
            raise ValueError(f"même annotateur deux fois sur {r['id']} : la double annotation n'est pas valide")
    out = []
    for r in sorted(primary, key=lambda x: x["id"]):
        i, ga = r["id"], r["gold"]
        gold = dict(ga)
        if i in B:
            for f in compared:
                if not same(f, ga.get(f), B[i].get(f)):
                    if i not in C:
                        raise ValueError(f"désaccord non arbitré : {i} ({f})")
                    gold[f] = C[i].get(f)
        out.append({"id": i, "lang": r.get("lang"), "gold": gold, "double_annotation": i in B})
    return out


def merge_gold(a_rows: list[dict[str, Any]], b_rows: list[dict[str, Any]],
               arbitration: list[dict[str, Any]], profile: str = DEFAULT_PROFILE) -> list[dict[str, Any]]:
    compared = compared_fields(profile)
    _check_profile([*a_rows, *b_rows, *arbitration], profile)
    A = {r["id"]: r for r in a_rows}
    B = {r["id"]: r["gold"] for r in b_rows}
    who_b = {r["id"]: r.get("annotateur") for r in b_rows}
    C = {r["id"]: r["gold"] for r in arbitration}
    out = []
    for i in sorted(set(A) & set(B)):
        ga, gb = A[i]["gold"], B[i]
        gold = {}
        for f in ga:
            if f in compared and not same(f, ga.get(f), gb.get(f)):
                if i not in C:
                    raise ValueError(f"désaccord non arbitré : {i} ({f})")
                gold[f] = C[i].get(f)
            else:
                gold[f] = ga.get(f)
        out.append({"id": i, "lang": A[i].get("lang"), "gold": gold,
                    "annotateurs": [A[i].get("annotateur"), who_b.get(i)]})
    return out


def freeze(items: list[dict[str, Any]], gold: list[dict[str, Any]], out: Path, frozen_md: Path,
           note: str) -> tuple[Path, str]:
    if out.exists():
        raise FileExistsError(f"{out} est gelé : créer une nouvelle version")
    text = {it["id"]: it for it in items}
    lines = []
    for g in sorted(gold, key=lambda r: r["id"]):
        it = text[g["id"]]
        lines.append(json.dumps({"id": g["id"], "lang": it.get("lang"), "text": it["text"],
                                 "source_url": it.get("source_url"), "gold": g["gold"]}, ensure_ascii=False))
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(payload)
    sha = hashlib.sha256(payload).hexdigest()
    day = datetime.now(UTC).date().isoformat()
    row = f"| `{out.name}` | `{sha}` | {day}, **avant** toute mesure | {note} |\n"
    md = frozen_md.read_text("utf-8")
    marker = "|---|---|---|---|\n"
    frozen_md.write_text(md.replace(marker, marker + row, 1) if marker in md else md + row, "utf-8")
    return out, sha


def _register(frozen_md: Path, name: str, sha: str, note: str, label: str = "") -> None:
    day = datetime.now(UTC).date().isoformat()
    row = f"| `{name}`{label} | `{sha}` | {day}, **avant** toute mesure | {note} |\n"
    md = frozen_md.read_text("utf-8")
    marker = "|---|---|---|---|\n"
    frozen_md.write_text(md.replace(marker, marker + row, 1) if marker in md else md + row, "utf-8")


def freeze_private(items: list[dict[str, Any]], gold: list[dict[str, Any]], private_out: Path, public_out: Path,
                   frozen_md: Path, note: str) -> tuple[Path, Path, str, str]:
    """Texts stay out of git: ``private_out`` (text + gold, git-ignored folder) and ``public_out`` (link, SHA-256 of
    the text, gold — committed). Both hashes are registered in FROZEN.md. A frozen file is never overwritten."""
    for f in (private_out, public_out):
        if f.exists():
            raise FileExistsError(f"{f} est gelé : créer une nouvelle version")
    text = {it["id"]: it for it in items}
    priv, pub = [], []
    for g in sorted(gold, key=lambda r: r["id"]):
        it = text[g["id"]]
        sha_text = hashlib.sha256(it["text"].encode("utf-8")).hexdigest()
        base = {"id": g["id"], "lang": it.get("lang"), "source_url": it.get("source_url"), "gold": g["gold"],
                "double_annotation": g.get("double_annotation", False)}
        priv.append(json.dumps(base | {"text": it["text"]}, ensure_ascii=False))
        pub.append(json.dumps(base | {"sha256_texte": sha_text}, ensure_ascii=False))
    shas = []
    for path, lines in ((private_out, priv), (public_out, pub)):
        payload = ("\n".join(lines) + "\n").encode("utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        shas.append(hashlib.sha256(payload).hexdigest())
    _register(frozen_md, public_out.name, shas[1], note, label=" (sans texte, commité)")
    _register(frozen_md, private_out.name, shas[0], note, label=" (avec textes, hors git)")
    return private_out, public_out, shas[0], shas[1]
