"""Ingestion: raw connector records → personal-data filter → entity resolution
→ normalised ``Signal`` rows (with provenance), validated by the schema.

Text-only fields (official gazette texts) are completed by the M3 extractor
(rules by default, Apertus if configured). Private applicants never become
companies; their permits are kept only as regional signals without a name.
"""

from __future__ import annotations

import hashlib
from typing import Any

import pandas as pd

from proxsis.connectors.base import RawRecord, apply_pii
from proxsis.entities import is_legal_entity_name, normalize_uid
from proxsis.models.m3_extraction import RulesExtractor
from proxsis.models.m4_entity_resolution import EntityResolver
from proxsis.schema import Signal

_CATEGORY_TO_FAMILY = {
    "adjudication": ("marche_attribue", "adjudication"),
    "permis_construire": ("permis_construire", "mise_a_l_enquete"),
    "registre_commerce": ("mutation_rc", None),
}
_RC_OK = {
    "nouvelle_inscription",
    "succursale",
    "augmentation_capital",
    "changement_but",
    "transfert_siege",
    "fusion",
    "liquidation",
    "radiation",
}


def _company_id(uid: str | None, name: str) -> str:
    key = uid or name.lower()
    return "r" + hashlib.sha1(key.encode()).hexdigest()[:10]


def ingest(
    records: list[RawRecord], companies: pd.DataFrame | None = None, extractor: Any | None = None
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Return (signals, new_companies, log)."""
    extractor = extractor or RulesExtractor()
    kept, log = apply_pii(records)
    known = (
        companies
        if companies is not None and not companies.empty
        else pd.DataFrame(columns=["company_id", "uid", "name", "canton", "commune"])
    )
    resolver = EntityResolver(known) if not known.empty else None
    new_companies: dict[str, dict[str, Any]] = {}
    signals: list[dict[str, Any]] = []
    for r in kept:
        if r.category not in _CATEGORY_TO_FAMILY:
            continue
        family, subtype = _CATEGORY_TO_FAMILY[r.category]
        f = r.fields
        ext = extractor.extract(f.get("text") or f.get("title") or "") if (f.get("text") or f.get("title")) else {}
        name = f.get("company_name") or f.get("applicant") or ext.get("company_name")
        if name and not is_legal_entity_name(str(name)):
            name = None  # private person: never a company
        uid = normalize_uid(f.get("uid")) or ext.get("uid")
        if family == "mutation_rc":
            subtype = f.get("subtype") if f.get("subtype") in _RC_OK else ext.get("rc_subtype")
            if subtype not in _RC_OK:
                log.append(f"{r.source}:{r.record_id}: sous-type RC non reconnu, ignoré")
                continue
        company_id = None
        if name:
            m = resolver.resolve(str(name), uid, f.get("canton"), f.get("commune")) if resolver else None
            if m is not None and m.method in ("uid", "name"):
                company_id = m.company_id
            else:
                company_id = _company_id(uid, str(name))
                new_companies.setdefault(
                    company_id,
                    {
                        "company_id": company_id,
                        "uid": uid,
                        "name": str(name),
                        "canton": f.get("canton"),
                        "commune": f.get("commune"),
                        "source": r.source,
                        "url": r.url,
                        "license": r.license,
                        "retrieved_at": r.retrieved_at,
                        "fictif": False,
                        "needs_review": m is not None and m.method == "review",
                    },
                )
        elif family != "permis_construire":
            log.append(f"{r.source}:{r.record_id}: pas d'entreprise identifiable, ignoré")
            continue
        canton = f.get("canton") or "VS"
        row = {
            "signal_id": f"{r.source}:{r.record_id}",
            "company_id": company_id,
            "family": family,
            "subtype": subtype,
            "event_date": r.event_date or r.available_at,
            "available_at": r.available_at,
            "canton": canton,
            "commune": f.get("commune") or ext.get("commune"),
            "value_chf": f.get("value_chf") or ext.get("amount_chf"),
            "trades": ext.get("trades", []),
            "title": f.get("title", ""),
            "summary": (f.get("text") or "")[:500],
            "source": r.source,
            "url": r.url,
            "retrieved_at": r.retrieved_at,
            "license": r.license,
            "fictif": False,
        }
        Signal.model_validate(row)  # contract: raises on any violation
        signals.append(row)
    return pd.DataFrame(signals), pd.DataFrame(list(new_companies.values())), log
