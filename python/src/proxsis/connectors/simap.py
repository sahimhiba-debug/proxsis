"""simap.ch connector — public procurement (tenders and awards), API only.

Access rules (docs/recherche/conditions_2026-10-05.md):
* API without account, allowed by robots.txt and by the API terms (version
  of 2023-09-30): commercial use allowed; content must not be presented as
  modified; every display carries :data:`MANDATORY_NOTICE`.
* Raw responses contain contact persons (name, phone, e-mail). They are
  fetched with ``store_raw=False`` and never written: :func:`normalize` copies
  an **allowlist** of fields, then the personal-data filter runs on the
  remaining free text and on the vendor name, *before* anything is stored.
* Field paths were checked on real responses on 2026-10-05 (the first
  version of this connector, written while the domain was blocked, guessed
  ``vendors[].name`` and ``decision.decisionDate``; the real fields are
  ``vendors[].vendorName`` and ``decision.awardDecisionDate``; the
  publication date and original language are in ``base``).

:class:`SimapConnector` exposes the same records through the common
:class:`~proxsis.connectors.base.Connector` contract (one ``RawRecord`` per
awarded vendor), for :mod:`proxsis.ingest`.
"""

from __future__ import annotations

import html
import json
import re
from collections.abc import Iterator
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from proxsis.connectors.base import Connector, RawRecord
from proxsis.entities import normalize_uid
from proxsis.http import FetchResult, PoliteClient
from proxsis.pii import (
    PRIVATE_PLACEHOLDER,
    FilterResult,
    PiiFilter,
    authority_looks_private,
    looks_like_private_person,
    redact_text,
)

BASE = "https://www.simap.ch/api"
SEARCH_URL = f"{BASE}/publications/v2/project/project-search"
SOURCE = "simap.ch"
MANDATORY_NOTICE = ("Ceci n'est pas une publication officielle. Les données publiées sur la plateforme "
                    "www.simap.ch font foi.")
LICENSE = ("CG API simap.ch (version du 30.09.2023) : usage commercial autorisé ; contenu non modifié ; "
           f"mention obligatoire : « {MANDATORY_NOTICE} »")
# The search filters of simap (simap.yaml, ProjectSearchPubTypeFilter). « correction » is not one of them (HTTP 400,
# E0025, checked on 13.10.2026): a correction is a new version of a publication, marked « corrected » in the search.
PUB_TYPES = frozenset({"tender", "award_tender", "award_study_contract", "award_competition", "direct_award",
                       "advance_notice", "selective_offering_phase", "participant_selection", "revocation",
                       "abandonment"})
WITHDRAWAL_TYPES = ("revocation", "abandonment")
SUB_TYPES = frozenset({"construction", "service", "supply", "project_competition", "idea_competition",
                       "overall_performance_competition", "project_study", "idea_study", "overall_performance_study"})
LANGS = ("de", "fr", "it", "en")
AWARD_TYPES = ("award_tender", "award_study_contract", "award_competition", "direct_award")
# Root institution « Valais » (GET /institutions/v1/institutions, 2026-10-05); the filter includes its children
# (cantonal offices, communes).
VALAIS_ROOT = "f8e02dc2-fd1f-4d80-85ab-21878cb328c8"

_PII = PiiFilter()


def project_page(project_id: object, lang: str = "fr") -> str | None:
    """The human page of a project on simap.ch (the API address stays in the provenance); None without a project id,
    never « …/project-detail/None »."""
    if not project_id:
        return None
    return f"https://www.simap.ch/{lang if lang in ('fr', 'de') else 'fr'}/project-detail/{project_id}"


def detail_url(project_id: str, publication_id: str) -> str:
    return f"{BASE}/publications/v1/project/{project_id}/publication-details/{publication_id}"


def search_params(lang: str, pub_types: tuple[str, ...], sub_types: tuple[str, ...], date_from: str, date_to: str,
                  cantons: tuple[str, ...] = (), issued_by: tuple[str, ...] = ()) -> dict[str, Any]:
    """Validated query: unknown values are rejected here (the API would answer 400 or ignore them)."""
    if lang not in LANGS:
        raise ValueError(f"langue inconnue : {lang}")
    bad = [p for p in pub_types if p not in PUB_TYPES] + [s for s in sub_types if s not in SUB_TYPES]
    if bad:
        raise ValueError(f"valeurs refusées : {bad}")
    params: dict[str, Any] = {"lang": lang, "newestPubTypes": list(pub_types), "projectSubTypes": list(sub_types),
                              "newestPublicationFrom": date_from, "newestPublicationUntil": date_to}
    if cantons:
        params["orderAddressCantons"] = list(cantons)
    if issued_by:
        params["issuedByOrganizations"] = list(issued_by)
    return params


def search(client: PoliteClient, params: dict[str, Any], max_pages: int = 50) -> Iterator[dict[str, Any]]:
    """Project summaries, page by page (``lastItem`` pagination)."""
    last: str | None = None
    for _ in range(max_pages):
        q = dict(params) | ({"lastItem": last} if last else {})
        res = client.get(SEARCH_URL, params=q, source=SOURCE, license=LICENSE, store_raw=False)
        if res.status != 200:
            raise RuntimeError(f"simap project-search : HTTP {res.status}")
        body = res.json()
        projects = body.get("projects") or []
        yield from projects
        last = (body.get("pagination") or {}).get("lastItem")
        if not projects or not last:
            return


def _ml(value: Any) -> dict[str, str]:
    """Multilingual field -> {lang: plain text} without empty languages nor HTML."""
    if not isinstance(value, dict):
        return {}
    out = {}
    for lang in LANGS:
        v = value.get(lang)
        if isinstance(v, str) and v.strip():
            text = re.sub(r"<[^>]+>", " ", v)
            out[lang] = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return out


def _first(value: Any) -> str | None:
    ml = _ml(value)
    return next(iter(ml.values()), None)


def _codes(items: Any) -> list[str]:
    return [str(i["code"]) for i in items or [] if isinstance(i, dict) and i.get("code")]


def _labels(items: Any, lang: str) -> list[str]:
    out = []
    for i in items or []:
        if isinstance(i, dict):
            lab = _ml(i.get("label"))
            if lab:
                out.append(lab.get(lang) or next(iter(lab.values())))
    return out


def normalize(summary: dict[str, Any], detail: dict[str, Any], retrieved_at: datetime,
              raw_sha256: str) -> tuple[dict[str, Any], FilterResult]:
    """Allowlisted, filtered record. Returns (record, filter report)."""
    base = detail.get("base") or {}
    summary = {"id": base.get("projectId"), "publicationId": base.get("id") or detail.get("id"),
               "publicationDate": base.get("publicationDate"), "publicationNumber": base.get("publicationNumber"),
               "projectType": base.get("projectType"), "processType": base.get("processType"),
               "title": base.get("title"), "pubType": base.get("type")} | {k: v for k, v in summary.items() if v}
    proc = detail.get("procurement") or {}
    info = detail.get("project-info") or {}
    dec = detail.get("decision") or {}
    order = summary.get("orderAddress") or {}
    project_id, publication_id = summary["id"], summary["publicationId"]

    vendors_raw = []
    for v in dec.get("vendors") or []:
        addr = v.get("vendorAddress") or {}
        price = (v.get("price") or {}).get("price")
        # Rule of 2026-10-05: a laureate with an IDE is a registered company, even if named after a person.
        uid = normalize_uid(json.dumps(v, ensure_ascii=False))
        vendors_raw.append({"name": v.get("vendorName") or "", "uid": uid, "canton": addr.get("cantonId"),
                            "city": addr.get("city"), "postal_code": addr.get("postalCode"),
                            "country": addr.get("countryId"),
                            # real responses write the currency in lower case ("chf")
                            "price_chf": float(price) if price is not None and str(
                                (v.get("price") or {}).get("currency") or "chf").lower() == "chf" else None,
                            "note": _ml(v.get("note"))})

    authority = _first((info.get("procurementRecipientAddress") or {}).get("name")) or _first(
        summary.get("procOfficeName"))
    record: dict[str, Any] = {
        "id": f"simap:{publication_id}",
        "project_id": project_id,
        "publication_id": publication_id,
        "publication_number": summary.get("publicationNumber"),
        "pub_type": detail.get("type") or summary.get("pubType"),
        "project_type": summary.get("projectType"),
        "order_type": proc.get("orderType") or summary.get("projectSubType"),
        "process_type": summary.get("processType"),
        "publication_date": summary.get("publicationDate"),
        "corrected": bool(summary.get("corrected")),  # this publication corrects an earlier one (simap's search)
        "creation_language": base.get("creationLanguage"),
        "decision_date": dec.get("awardDecisionDate"),
        "title": _ml(summary.get("title")) or _ml(info.get("title")),
        "description": _ml(proc.get("orderDescription")),
        "cpv_code": (proc.get("cpvCode") or {}).get("code"),
        "cpv_label": _ml((proc.get("cpvCode") or {}).get("label")),
        "bkp_codes": _codes(proc.get("bkpCodes")),
        "bkp_labels_fr": _labels(proc.get("bkpCodes"), "fr"),
        "npk_codes": _codes(proc.get("npkCodes")),
        "order_canton": order.get("cantonId"),
        "order_postal_code": order.get("postalCode"),
        "order_city": _first(order.get("city")),
        "contracting_authority": authority,
        "number_of_submissions": dec.get("numberOfSubmissions"),
        "vendors": vendors_raw,
    }
    filtered = _filter(record)
    rec = filtered.record or {}
    rec["private_person"] = any(v["name"] == PRIVATE_PLACEHOLDER for v in rec["vendors"])
    rec["provenance"] = {"source": SOURCE, "url": detail_url(project_id, publication_id),
                         "retrieved_at": retrieved_at.isoformat(timespec="seconds"), "license": LICENSE,
                         "fictif": False, "content_sha256": raw_sha256}
    rec["mention_obligatoire"] = MANDATORY_NOTICE
    return rec, filtered


def _filter(record: dict[str, Any]) -> FilterResult:
    """Personal-data filter on free text (all languages) and on vendor / authority names."""
    total = 0
    out = dict(record)
    for key in ("title", "description"):
        out[key] = {}
        for lang, text in record[key].items():
            res = _PII.apply({"text": text})
            assert res.record is not None
            out[key][lang] = res.record["text"]
            total += res.redactions
    vendors = []
    for v in record["vendors"]:
        # Audit B1: a vendor without a recognised legal form is usually a company; it is masked only when the
        # name really looks like a private person (« Firstname Lastname »).
        name = str(v["name"] or "")
        private = not v.get("uid") and looks_like_private_person(name)
        res = FilterResult({"builder": PRIVATE_PLACEHOLDER if private else redact_text(name)[0]},
                           redactions=int(private))
        note = {}
        for lang, text in v["note"].items():
            r2 = _PII.apply({"text": text})
            assert r2.record is not None
            note[lang] = r2.record["text"]
            total += r2.redactions
        assert res.record is not None
        vendors.append(v | {"name": res.record["builder"], "note": note,
                            # a private person's town is not kept either
                            "city": None if private else v["city"],
                            "postal_code": None if private else v["postal_code"]})
        total += res.redactions
    out["vendors"] = vendors
    if out["contracting_authority"]:
        # Audit of week 1 (m): details in parentheses (a contact person, a bureau) are dropped.
        out["contracting_authority"] = re.sub(r"\s*\([^)]*\)", "", str(out["contracting_authority"])).strip() or None
    if out["contracting_authority"]:
        # Audit B1 (2026-10-05): a contracting authority is normally a public body, so only text redaction applies;
        # audit of week 1 (2026-10-06, B1): simap sometimes shows a private person there → masked.
        if authority_looks_private(str(out["contracting_authority"])):
            out["contracting_authority"] = PRIVATE_PLACEHOLDER
            total += 1
        else:
            out["contracting_authority"], n = redact_text(str(out["contracting_authority"]))
            total += n
    return FilterResult(out, redactions=total)


class SimapIncomplete(RuntimeError):
    """Some details did not answer: what was read is kept (a new run completes it), but nothing may treat the result
    as complete (the live week is never published half-read)."""


def fetch_to_jsonl(client: PoliteClient, out: Path, *, lang: str, pub_types: tuple[str, ...],
                   sub_types: tuple[str, ...], date_from: str, date_to: str, cantons: tuple[str, ...] = (),
                   max_pages: int = 50, max_items: int | None = None, issued_by: tuple[str, ...] = ()) -> int:
    """Search, fetch each detail, normalise + filter, append filtered records only. A detail that does not answer
    200 raises ``SimapIncomplete`` at the end (after the others are written)."""
    params = search_params(lang, pub_types, sub_types, date_from, date_to, cantons, issued_by)
    out.parent.mkdir(parents=True, exist_ok=True)
    known = set()
    if out.exists():  # resumable: publications already written are not fetched again
        known = {json.loads(x)["publication_id"] for x in out.read_text("utf-8").splitlines() if x.strip()}
    n = 0
    missing: list[str] = []
    with out.open("a", encoding="utf-8") as fh:
        for summary in search(client, params, max_pages=max_pages):
            if summary["publicationId"] in known:
                continue
            res = client.get(detail_url(summary["id"], summary["publicationId"]), source=SOURCE, license=LICENSE,
                             store_raw=False)
            if res.status != 200:
                missing.append(f"{summary['publicationId']} ({res.status})")
                continue
            rec, _ = normalize(summary, res.json(), retrieved_at=datetime.now(UTC),
                               raw_sha256=res.provenance.content_sha256 or "")
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            known.add(summary["publicationId"])
            n += 1
            if max_items is not None and n >= max_items:
                break
    if missing:
        raise SimapIncomplete(f"{len(missing)} fiche(s) sans réponse : {', '.join(missing[:5])} ; {n} écrite(s), "
                              "relancer pour compléter")
    return n


def past_publications_url(publication_id: str) -> str:
    return f"{BASE}/publications/v1/publication/{publication_id}/past-publications"


def complete_past_awards(client: PoliteClient, out: Path) -> int:
    """Audit M7: the search only returns the newest publication of each project. For projects with more than two
    publications (number ``-03`` and above: lots awarded at different dates, corrections), the earlier award
    publications are fetched through ``past-publications`` and appended (filtered). Idempotent."""
    records = [json.loads(x) for x in out.read_text("utf-8").splitlines() if x.strip()]
    known = {r["publication_id"] for r in records}
    n = 0
    with out.open("a", encoding="utf-8") as fh:
        for r in records:
            try:
                seq = int(str(r.get("publication_number") or "").rsplit("-", 1)[-1])
            except ValueError:
                continue
            if seq < 3:
                continue
            res = client.get(past_publications_url(r["publication_id"]), source=SOURCE, license=LICENSE,
                             store_raw=False)
            if res.status != 200:
                continue
            for e in res.json().get("pastPublications") or []:
                kind = str(e.get("pubType") or e.get("type") or "")
                if not kind.startswith(("award", "direct")) or e["id"] in known:
                    continue
                det = client.get(detail_url(r["project_id"], e["id"]), source=SOURCE, license=LICENSE,
                                 store_raw=False)
                if det.status != 200:
                    continue
                summary = {"id": r["project_id"], "publicationId": e["id"], "publicationDate": e.get("publicationDate"),
                           "pubType": kind, "title": r.get("title"),
                           "orderAddress": {"cantonId": r.get("order_canton"), "postalCode": r.get("order_postal_code"),
                                            "city": {"fr": r["order_city"]} if r.get("order_city") else None}}
                rec, _ = normalize(summary, det.json(), retrieved_at=datetime.now(UTC),
                                   raw_sha256=det.provenance.content_sha256 or "")
                rec["publication_date"] = e.get("publicationDate") or rec["publication_date"]
                rec["completee_par"] = "past-publications"
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
                known.add(e["id"])
                n += 1
    return n


def refresh_records(client: PoliteClient, out: Path, select: Any) -> int:
    """Re-fetch the details of the selected records and rewrite them with the CURRENT normalisation and filter
    (e.g. after a filter fix). Other lines are kept as they are; the file is replaced atomically."""
    records = [json.loads(x) for x in out.read_text("utf-8").splitlines() if x.strip()]
    n = 0
    for i, r in enumerate(records):
        if not select(r):
            continue
        res = client.get(detail_url(r["project_id"], r["publication_id"]), source=SOURCE, license=LICENSE,
                         store_raw=False)
        if res.status != 200:
            continue
        summary = {"id": r["project_id"], "publicationId": r["publication_id"],
                   "publicationDate": r.get("publication_date"), "publicationNumber": r.get("publication_number"),
                   "title": r.get("title") or None,
                   "orderAddress": {"cantonId": r.get("order_canton"), "postalCode": r.get("order_postal_code"),
                                    "city": {"fr": r["order_city"]} if r.get("order_city") else None}}
        rec, _ = normalize(summary, res.json(), retrieved_at=datetime.now(UTC),
                           raw_sha256=res.provenance.content_sha256 or "")
        rec["publication_date"] = r.get("publication_date") or rec["publication_date"]
        if r.get("completee_par"):
            rec["completee_par"] = r["completee_par"]
        rec["rafraichi_le"] = datetime.now(UTC).date().isoformat()
        records[i] = rec
        n += 1
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), "utf-8")
    tmp.replace(out)
    return n


class SimapConnector(Connector):
    """Awards, through the common connector contract (one ``RawRecord`` per awarded vendor)."""

    name = SOURCE
    license = LICENSE
    base_url = BASE
    min_interval_s = 2.0

    def __init__(self, lang: str = "fr", cantons: tuple[str, ...] = ("VS",),
                 sub_types: tuple[str, ...] = ("construction",)) -> None:
        self.lang = lang
        self.cantons = cantons
        self.sub_types = sub_types

    def requests(self, since: date, until: date, **kw: Any) -> list[tuple[str, dict[str, Any]]]:
        params = search_params(self.lang, AWARD_TYPES, self.sub_types, since.isoformat(), until.isoformat(),
                               self.cantons)
        params = {k: ",".join(v) if isinstance(v, list) else v for k, v in params.items()}
        if kw.get("last_item"):
            params["lastItem"] = kw["last_item"]
        return [(SEARCH_URL, params)]

    def detail_request(self, project_id: str, publication_id: str) -> tuple[str, dict[str, Any]]:
        return detail_url(project_id, publication_id), {}

    def fetch(self, client: PoliteClient, since: date, until: date, **kw: Any) -> list[RawRecord]:
        """Search pages, then one detail per award; nothing raw is stored (``store_raw=False``)."""
        _, params = self.requests(since, until)[0]
        out: list[RawRecord] = []
        for summary in search(client, params, max_pages=int(kw.get("max_pages", 50))):
            res = client.get(detail_url(summary["id"], summary["publicationId"]), source=self.name,
                             license=self.license, store_raw=False)
            if res.status == 200:
                out.extend(self.parse(res, summary=summary))
        return out

    def parse(self, result: FetchResult, summary: dict[str, Any] | None = None) -> list[RawRecord]:
        d = result.json()
        if "projects" in d:  # search page: metadata only, details carry the winners
            return []
        rec, _ = normalize(summary or {}, d, retrieved_at=result.provenance.retrieved_at,
                           raw_sha256=result.provenance.content_sha256 or "")
        return records_from_normalized(rec)


def records_from_normalized(rec: dict[str, Any]) -> list[RawRecord]:
    """One ``RawRecord`` per awarded vendor of an already filtered record."""
    pub = _to_date(rec.get("publication_date"))
    if pub is None or not str(rec.get("pub_type", "")).startswith(("award", "direct")):
        return []
    lang = rec.get("creation_language") or "fr"
    title = rec["title"].get(lang) or next(iter(rec["title"].values()), "")
    out = []
    for i, v in enumerate(rec["vendors"]):
        if not v["name"]:
            continue
        out.append(RawRecord(
            source=SOURCE, record_id=f"{rec['publication_id']}:{i}", category="adjudication",
            event_date=_to_date(rec.get("decision_date")) or pub, available_at=pub,
            url=rec["provenance"]["url"], license=LICENSE, retrieved_at=rec["provenance"]["retrieved_at"],
            fields={"company_name": v["name"], "uid": normalize_uid(v.get("uid")), "value_chf": v["price_chf"],
                    "title": title, "canton": rec.get("order_canton"), "commune": rec.get("order_city"),
                    "npa": rec.get("order_postal_code"), "cpv": rec.get("cpv_code"), "bkp": rec.get("bkp_codes"),
                    "authority": rec.get("contracting_authority")},
        ))
    return out


def _to_date(v: Any) -> date | None:
    try:
        return date.fromisoformat(str(v)[:10]) if v else None
    except ValueError:
        return None
