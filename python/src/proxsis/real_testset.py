"""Real test set v2 for M3: a reproducible, stratified draw of real simap awards.

* Frame: every award (``award_tender``, ``direct_award``) published on simap.ch
  in a period, for the given order types (summaries only: ids, date, canton).
* Draw: the frame is split by a language proxy (canton of execution), each part
  is shuffled with a fixed seed, details are fetched in that order and kept
  until the quota of each *creation language* (fr / de, from ``base``) is met.
  Every fetched item and the reason it was kept or not is logged.
* Items are filtered by the simap connector (allowlist + personal-data filter)
  before anything is written, and rendered as plain text in the creation
  language. They carry **no gold and no model output**: the team annotates,
  the set is frozen (SHA-256), and only then are the extractors run.

No Apertus or rule output is ever computed on these texts before
the freeze (docs/annotation/guide_reel_v2.md).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from proxsis.connectors import simap
from proxsis.http import PoliteClient
from proxsis.pii import redact_text

LANG_PROXY_FR = frozenset({"GE", "VD", "NE", "JU", "FR", "VS"})
AWARD_PUB_TYPES = ("award_tender", "direct_award")

_LABELS = {
    "fr": {"head": "Adjudication", "obj": "Objet", "desc": "Description", "type": "Type de marché",
           "place": "Lieu d'exécution", "auth": "Adjudicateur", "vendor": "Adjudicataire", "price": "prix",
           "dec": "Décision du", "offers": "offres reçues", "pub": "publiée le", "cfc": "CFC",
           "types": {"construction": "travaux", "service": "services", "supply": "fournitures"}},
    "de": {"head": "Zuschlag", "obj": "Gegenstand", "desc": "Beschreibung", "type": "Auftragsart",
           "place": "Ausführungsort", "auth": "Vergabestelle", "vendor": "Zuschlagsempfänger", "price": "Preis",
           "dec": "Zuschlagsentscheid vom", "offers": "eingegangene Angebote", "pub": "publiziert am", "cfc": "BKP",
           "types": {"construction": "Bauauftrag", "service": "Dienstleistung", "supply": "Lieferung"}},
}


def _chf(v: float | None) -> str:
    if v is None:
        return "—"
    return f"CHF {v:,.2f}".replace(",", "'").replace(".00", ".–")


def _pick(ml: dict[str, str], lang: str) -> str:
    return ml.get(lang) or next(iter(ml.values()), "")


def render_text(rec: dict[str, Any], max_desc: int = 2500) -> str:
    """Plain-text sheet of a filtered award, in its creation language (fr or de)."""
    lang = str(rec.get("creation_language")) if rec.get("creation_language") in _LABELS else "fr"
    L: dict[str, Any] = _LABELS[lang]
    lines = [f"{L['head']} — simap.ch, n° {rec.get('publication_number') or '?'}, {L['pub']} "
             f"{rec.get('publication_date') or '?'}",
             f"{L['obj']} : {_pick(rec.get('title') or {}, lang)}"]
    desc = _pick(rec.get("description") or {}, lang)
    if desc:
        lines.append(f"{L['desc']} : {desc[:max_desc]}{'…' if len(desc) > max_desc else ''}")
    codes = []
    if rec.get("cpv_code"):
        codes.append(f"CPV {rec['cpv_code']} {_pick(rec.get('cpv_label') or {}, lang)}".strip())
    if rec.get("bkp_codes"):
        codes.append(f"{L['cfc']} " + ", ".join(rec["bkp_codes"]))
    kind = L["types"].get(str(rec.get("order_type")), str(rec.get("order_type") or "?"))
    lines.append(f"{L['type']} : {kind}" + (f" ; {' ; '.join(codes)}" if codes else ""))
    place = " ".join(str(x) for x in (rec.get("order_postal_code"), rec.get("order_city")) if x)
    if place or rec.get("order_canton"):
        lines.append(f"{L['place']} : {place}" + (f" ({rec['order_canton']})" if rec.get("order_canton") else ""))
    if rec.get("contracting_authority"):
        lines.append(f"{L['auth']} : {rec['contracting_authority']}")
    for v in rec.get("vendors") or []:
        lines.append(f"{L['vendor']} : {v['name']} — {L['price']} : {_chf(v.get('price_chf'))}")
        note = _pick(v.get("note") or {}, lang)
        if note:
            lines.append(f"  {note}")
    tail = []
    if rec.get("decision_date"):
        tail.append(f"{L['dec']} {rec['decision_date']}")
    if rec.get("number_of_submissions") is not None:
        tail.append(f"{rec['number_of_submissions']} {L['offers']}")
    if tail:
        lines.append(" ; ".join(tail) + ".")
    return "\n".join(lines)


def to_annotation_item(rec: dict[str, Any]) -> dict[str, Any]:
    lang = rec.get("creation_language")
    return {
        "id": rec["id"],
        "lang": lang,
        "order_type": rec.get("order_type"),
        "publication_date": rec.get("publication_date"),
        "text": render_text(rec),
        "source_url": simap.project_page(rec.get("project_id"), str(lang or "fr")),
        "source_api": (rec.get("provenance") or {}).get("url"),
        "mention_obligatoire": simap.MANDATORY_NOTICE,
    }


def frame_entry(s: dict[str, Any], sub_type: str) -> dict[str, Any]:
    """Summary fields kept in the frame (ids, dates, place, title) — enough to rebuild a draw without searching
    again, and no contact data."""
    addr = s.get("orderAddress") or {}
    return {"project_id": s["id"], "publication_id": s["publicationId"], "publication_date": s.get("publicationDate"),
            "publication_number": s.get("publicationNumber"), "pub_type": s.get("pubType"), "sub_type": sub_type,
            "order_canton": addr.get("cantonId"), "order_postal_code": addr.get("postalCode"),
            "order_city": addr.get("city"),
            # Audit M2: titles are filtered before being written, like every other text.
            "title": {k: redact_text(v)[0] for k, v in (s.get("title") or {}).items() if isinstance(v, str) and v}}


def summary_from_frame(e: dict[str, Any]) -> dict[str, Any]:
    return {"id": e["project_id"], "publicationId": e["publication_id"], "publicationDate": e.get("publication_date"),
            "publicationNumber": e.get("publication_number"), "pubType": e.get("pub_type"),
            "projectSubType": e.get("sub_type"), "title": e.get("title"),
            "orderAddress": {"cantonId": e.get("order_canton"), "postalCode": e.get("order_postal_code"),
                             "city": e.get("order_city")}}


def build_frame(client: PoliteClient, date_from: str, date_to: str, sub_types: tuple[str, ...],
                max_pages: int = 80) -> list[dict[str, Any]]:
    """All award summaries of the period (ids, date, place, title — no names of persons)."""
    frame: dict[str, dict[str, Any]] = {}
    for sub in sub_types:
        params = simap.search_params("fr", AWARD_PUB_TYPES, (sub,), date_from, date_to)
        for s in simap.search(client, params, max_pages=max_pages):
            frame[s["publicationId"]] = frame_entry(s, sub)
    return sorted(frame.values(), key=lambda x: (x["publication_date"] or "", x["publication_id"]))


def draw(frame: list[dict[str, Any]], fetch: Callable[[dict[str, Any]], dict[str, Any] | None],
         n_per_lang: dict[str, int], seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Each part (FR proxy, then DE proxy) is read in its shuffled order **until the quota of its own language is
    full** (items in the other language are kept while that quota is open); then, if a quota is still open, the
    remaining items are read in the same order."""
    rng = np.random.default_rng(seed)
    fr_part = [f for f in frame if f.get("order_canton") in LANG_PROXY_FR]
    de_part = [f for f in frame if f.get("order_canton") not in LANG_PROXY_FR]
    parts = [("fr", [fr_part[i] for i in rng.permutation(len(fr_part))]),
             ("de", [de_part[i] for i in rng.permutation(len(de_part))])]
    kept: list[dict[str, Any]] = []
    log: list[dict[str, Any]] = []
    count = dict.fromkeys(n_per_lang, 0)
    seen: set[str] = set()

    def full(lang: str | None = None) -> bool:
        if lang is not None:
            return count.get(lang, 0) >= n_per_lang.get(lang, 0)
        return all(count[k] >= n for k, n in n_per_lang.items())

    def read(item: dict[str, Any]) -> None:
        seen.add(item["publication_id"])
        rec = fetch(item)
        if rec is None:
            log.append({"publication_id": item["publication_id"], "langue": None, "decision": "écarté : erreur"})
            return
        lang = rec.get("creation_language")
        if lang not in n_per_lang:
            decision = "écarté : langue hors FR/DE"
        elif not any(v.get("name") for v in rec.get("vendors") or []):
            decision = "écarté : pas d'adjudicataire"
        elif count[lang] >= n_per_lang[lang]:
            decision = "écarté : quota de langue atteint"
        else:
            decision = "retenu"
            count[lang] += 1
            kept.append(rec)
        log.append({"publication_id": item["publication_id"], "langue": lang, "decision": decision})

    for proxy, items in parts:
        for item in items:
            if full(proxy) or full():
                break
            if item["publication_id"] not in seen:
                read(item)
    for _proxy, items in parts:  # second pass only if a quota is still open
        for item in items:
            if full():
                break
            if item["publication_id"] not in seen:
                read(item)
    return kept, log


def write_set(out_dir: Path, kept: list[dict[str, Any]], log: list[dict[str, Any]], frame: list[dict[str, Any]],
              meta: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "publications_filtrees.jsonl").open("w", encoding="utf-8") as fh:
        for r in kept:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (out_dir / "a_annoter.jsonl").open("w", encoding="utf-8") as fh:
        for r in kept:
            fh.write(json.dumps(to_annotation_item(r), ensure_ascii=False) + "\n")
    with (out_dir / "tirage_journal.jsonl").open("w", encoding="utf-8") as fh:
        for e in log:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    with (out_dir / "cadre.jsonl").open("w", encoding="utf-8") as fh:
        for f in frame:
            fh.write(json.dumps(f, ensure_ascii=False) + "\n")
    meta = meta | {"ecrit_le": datetime.now(UTC).isoformat(timespec="seconds"), "n_cadre": len(frame),
                   "n_retenus": len(kept), "n_details_lus": len(log)}
    (out_dir / "TIRAGE.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", "utf-8")
