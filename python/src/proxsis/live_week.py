"""« Chaque matin, en direct de simap » (Hiba, suite 10, § 2; first « Cette semaine, en direct de simap », 07.10.2026):
every working day from 6 a.m. (Swiss time) the public construction contracts awarded in Valais and published on simap.ch
are fetched through the simap API — on Monday the week that just ended, from Tuesday to Friday the day before — filtered
for personal data BEFORE anything is written (connectors.simap.normalize), turned into one small file for the web
section, and checked. The file is written only if every check passes; otherwise the previous valid file stays, with its
own date, and the automatic job reports the failure (.github/workflows/chaque-matin-en-direct.yml).

This section lives apart: the frozen demo data, the Monday list (it does not change during the week), the presentation
and the figures of CLAIMS.md never change with it. « Depuis hier » shows facts, never a score (suite 10, § 2).

Conditions of the simap API (AGB API ch. 5 al. 2, read on 07.10.2026, docs/DONNEES.md): the publications of a day may be
passed on to third parties only from 8 a.m. (Zurich) on that day: the reading never takes the day of the reading (at
most the day before), and the check refuses anything dated that day or later; the published content is shown apart
from our own sentences and unchanged; corrections are passed on: the corrections, revocations and abandonments
published during the period are listed with the awards, and those that concern a notice of the frozen data are kept in
a second small file (``corrections.json``), shown next to that notice, without changing the frozen data or CLAIMS.

The same section is replayed, frozen, for every Monday of « Choisissez une date » (``frozen_mornings``): only what was
published before that Monday.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from proxsis.call_list import company_id
from proxsis.connectors import simap
from proxsis.demo_export import pii_sweep
from proxsis.entities import is_legal_entity_name, normalize_name
from proxsis.pii import PRIVATE_PLACEHOLDER, looks_like_private_person
from proxsis.values import optional_text

SCHEMA = 2  # 2 (suite 10): every working day, « mode » and « periode », laureates with the identifier of the lists
MAX_SHOWN = 60  # a week of Valais construction awards is a few dozen; the section never grows without limit
# simap's search filter says « award_tender », its publication detail (what the records keep) says « award »: both are
# awards after a call for tenders (the section of 07.10.2026 kept only « award_tender » and lost them all)
AWARD_TYPES = ("award", "award_tender", "direct_award")
CORRECTION_TYPES = ("correction", "revocation", "abandonment")
CORRECTIONS_SCHEMA = 1
MODES = ("semaine", "veille")
_PROJECT_PAGE = re.compile(r"https://www\.simap\.ch/(?:fr|de|it|en)/project-detail/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
                           r"[0-9a-f]{4}-[0-9a-f]{12})")


def previous_week(monday: date) -> tuple[date, date]:
    """The full week (Monday to Sunday) that ends the day before ``monday``."""
    if monday.weekday() != 0:
        raise ValueError(f"{monday} n'est pas un lundi")
    start = monday - timedelta(days=7)
    return start, start + timedelta(days=6)


def last_monday(today: date) -> date:
    """The Monday of ``today``'s week (``today`` itself on a Monday)."""
    return today - timedelta(days=today.weekday())


def reading_period(day: date) -> tuple[str, date, date]:
    """What the morning reading of ``day`` shows (suite 10, § 2): on Monday the week that ended (« semaine », Monday to
    Sunday: Friday's, Saturday's and Sunday's publications are read then), from Tuesday to Friday the day before
    (« veille »); never ``day`` itself. No reading on Saturday or Sunday."""
    if day.weekday() == 0:
        start, end = previous_week(day)
        return "semaine", start, end
    if day.weekday() <= 4:
        before = day - timedelta(days=1)
        return "veille", before, before
    raise ValueError(f"{day} n'est pas un jour ouvrable")


def _title(rec: dict[str, Any]) -> str | None:
    """The title in the language it was written in (simap keeps the original), else the first one available."""
    titles = rec.get("title") or {}
    return optional_text(titles.get(rec.get("creation_language") or "")) or next(
        (optional_text(v) for v in titles.values() if optional_text(v)), None)


def laureate_id(name: str) -> str:
    """The identifier of a company in the application's lists (call_list.company_id of the normalised name)."""
    return company_id(normalize_name(name))


def build_live(records: list[dict[str, Any]], day: date) -> dict[str, Any]:
    """The section's file for the reading of ``day`` from filtered simap records (as written by
    ``simap.fetch_to_jsonl``)."""
    mode, start, end = reading_period(day)
    contracts = []
    for rec in records:
        published = str(rec.get("publication_date") or "")[:10]
        if rec.get("pub_type") not in AWARD_TYPES or not (start.isoformat() <= published <= end.isoformat()):
            continue
        if rec.get("corrected"):  # a correction of an award shown when first published: passed on as a correction
            continue
        title = _title(rec)
        # the human page of the project on simap (the provenance keeps the API address)
        url = simap.project_page(rec.get("project_id"))
        if not title or not url:
            continue
        authority = optional_text(rec.get("contracting_authority"))
        # published every day without anyone reading it: a laureate is named only when it is certainly a company
        # (an IDE, or a legal form in its name); otherwise the award is shown without its name (review 1, I2)
        winners = sorted({str(v["name"]) for v in rec.get("vendors") or [] if optional_text(v.get("name"))
                          and v["name"] != PRIVATE_PLACEHOLDER
                          and (v.get("uid") or is_legal_entity_name(str(v["name"])))})
        contracts.append({
            "date": published,
            "titre": title,
            "adjudicateur": None if authority in (None, PRIVATE_PLACEHOLDER) else authority,
            "commune": optional_text(rec.get("order_city")),
            "laureats": [{"nom": w, "id": laureate_id(w)} for w in winners],
            "url": url,
        })
    contracts.sort(key=lambda c: (c["date"], c["titre"]), reverse=True)
    rectifications = sorted(_period_corrections(records, start, end), key=lambda c: (c["date"], c["titre"]),
                            reverse=True)
    return {
        "schema": SCHEMA,
        "etat": "a_jour",
        "mode": mode,
        "periode": {"du": start.isoformat(), "au": end.isoformat()},
        "mis_a_jour_le": day.isoformat(),
        "source": simap.SOURCE,
        "mention": simap.MANDATORY_NOTICE,
        "total": len(contracts),
        "marches": contracts[:MAX_SHOWN],
        "rectifications": [{k: v for k, v in c.items() if k != "projet"} for c in rectifications[:MAX_SHOWN]],
    }


def _period_corrections(records: list[dict[str, Any]], start: date, end: date) -> list[dict[str, Any]]:
    """The corrections, revocations and abandonments published during the period: revocations and abandonments are
    publications of their own on simap; a correction is a new version of a publication, marked « corrected » (an award
    corrected during the period is read with the awards). Date, kind, title in its language, the project's page."""
    out = []
    for rec in records:
        published = str(rec.get("publication_date") or "")[:10]
        kind = "correction" if rec.get("corrected") else rec.get("pub_type")
        if kind not in CORRECTION_TYPES or not (start.isoformat() <= published <= end.isoformat()):
            continue
        title, url = _title(rec), simap.project_page(rec.get("project_id"))
        if title and url:
            out.append({"date": published, "type": kind, "titre": title, "url": url,
                        "projet": str(rec.get("project_id"))})
    return out


def frozen_projects(paths: Iterable[Path]) -> set[str]:
    """The simap projects cited by the frozen data (their pages, « project-detail/<id> »)."""
    found: set[str] = set()
    for path in paths:
        found |= set(_PROJECT_PAGE.findall(path.read_text("utf-8")))
    return found


def update_corrections(previous: dict[str, Any] | None, records: list[dict[str, Any]], day: date,
                       frozen: set[str]) -> dict[str, Any]:
    """The corrections that concern a notice of the frozen data: the earlier ones are kept, the period's are added."""
    _, start, end = reading_period(day)
    notices = {(n["projet"], n["date"], n["type"]): n for n in (previous or {}).get("avis") or []}
    for c in _period_corrections(records, start, end):
        if c["projet"] in frozen:
            notices[(c["projet"], c["date"], c["type"])] = {"projet": c["projet"], "date": c["date"],
                                                           "type": c["type"], "url": c["url"]}
    return {
        "schema": CORRECTIONS_SCHEMA,
        "mis_a_jour_le": day.isoformat(),
        "source": simap.SOURCE,
        "mention": simap.MANDATORY_NOTICE,
        "avis": sorted(notices.values(), key=lambda n: (n["date"], n["projet"], n["type"])),
    }


def check_corrections(data: dict[str, Any]) -> list[str]:
    """Everything that would make the corrections file unfit to publish."""
    problems: list[str] = []
    if data.get("schema") != CORRECTIONS_SCHEMA or data.get("mention") != simap.MANDATORY_NOTICE:
        problems.append("corrections : schéma ou mention inattendus")
    day = str(data.get("mis_a_jour_le") or "")
    for i, n in enumerate(data.get("avis") or []):
        where = f"corrections.avis[{i}]"
        if n.get("type") not in CORRECTION_TYPES:
            problems.append(f"{where} : type inconnu")
        if not str(n.get("date") or "") or str(n.get("date")) >= day:
            problems.append(f"{where} : date absente, ou pas avant le jour de la lecture (règle des 8 h)")
        url = str(n.get("url") or "")
        if _PROJECT_PAGE.fullmatch(url) is None or url.rsplit("/", 1)[-1] != n.get("projet"):
            problems.append(f"{where} : adresse qui n'est pas la page simap.ch du projet")
    return problems


def _expected_period(day_text: str) -> tuple[str, str, str] | None:
    """(mode, du, au) of the reading of that day, or None when it is not a working day (or not a date)."""
    try:
        mode, start, end = reading_period(date.fromisoformat(day_text))
    except ValueError:
        return None
    return mode, start.isoformat(), end.isoformat()


def check_live(data: dict[str, Any]) -> list[str]:
    """Everything that would make the file unfit to publish; an empty list means it can be written."""
    problems: list[str] = []
    if data.get("schema") != SCHEMA or data.get("etat") != "a_jour" or data.get("mode") not in MODES:
        problems.append("schéma, état ou mode inattendu")
    if data.get("mention") != simap.MANDATORY_NOTICE:
        problems.append("mention obligatoire de simap absente ou modifiée")
    period = data.get("periode") or {}
    day = str(data.get("mis_a_jour_le") or "")
    expected = _expected_period(day)
    if expected is None:
        problems.append("date de lecture absente, ou qui n'est pas un jour ouvrable")
    elif (data.get("mode"), period.get("du"), period.get("au")) != expected:
        problems.append(f"période qui n'est pas celle de la lecture du {day} : {expected}")
    items = [(f"marches[{i}]", c) for i, c in enumerate(data.get("marches") or [])] + [
        (f"rectifications[{i}]", c) for i, c in enumerate(data.get("rectifications") or [])]
    for where, c in items:
        if not (period.get("du", "") <= c.get("date", "") <= period.get("au", "")):
            problems.append(f"{where} : date hors de la période")
        # AGB API ch. 5 al. 2: a day's publications only from 8 a.m. that day; nothing of the reading day itself is read
        if not day or c.get("date", "") >= day:
            problems.append(f"{where} : publiée le jour de la lecture ou après (règle des 8 h)")
        if where.startswith("rectifications") and c.get("type") not in CORRECTION_TYPES:
            problems.append(f"{where} : type inconnu")
        host = urlparse(str(c.get("url") or "")).hostname or ""
        if host not in ("www.simap.ch", "simap.ch"):
            problems.append(f"{where} : adresse qui n'est pas une page simap.ch")
        if not c.get("titre"):
            problems.append(f"{where} : titre manquant")
        if PRIVATE_PLACEHOLDER in json.dumps(c, ensure_ascii=False):
            problems.append(f"{where} : un nom masqué ne doit pas apparaître")
        for w in c.get("laureats") or []:
            name = str(w.get("nom") or "") if isinstance(w, dict) else ""
            if not name or looks_like_private_person(name):
                problems.append(f"{where} : lauréat qui ressemble à une personne")
            elif w.get("id") != laureate_id(name):
                problems.append(f"{where} : identifiant de lauréat qui n'est pas celui des listes")
    problems += [f"donnée personnelle possible : {h['chemin']} ({h['motif']})"
                 for h in pii_sweep({"marches": data.get("marches"), "rectifications": data.get("rectifications")})]
    return problems


def write_if_valid(data: dict[str, Any], out: Path, corrections: dict[str, Any] | None = None,
                   corrections_out: Path | None = None) -> list[str]:
    """Write the section's file (and the corrections of the frozen notices, if given) only when everything passes every
    check; return the problems (the previous files are kept otherwise, both of them)."""
    problems = check_live(data) + (check_corrections(corrections) if corrections is not None else [])
    if not problems:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", "utf-8")
        if corrections is not None and corrections_out is not None:
            corrections_out.write_text(json.dumps(corrections, ensure_ascii=False, indent=1) + "\n", "utf-8")
    return problems


def frozen_mornings(records: list[dict[str, Any]], mondays: list[dict[str, Any]]) -> dict[str, Any]:
    """« Choisissez une date » (suite 10, § 2): for every Monday that can be chosen (``lundis.json``), the same section
    as that morning, from the frozen data and only from what was published before that Monday (the week that ended the
    day before). Each Monday is checked like a live reading; a single problem and nothing is returned."""
    shown: dict[str, Any] = {}
    for m in mondays:
        if not m.get("choisissable"):
            continue
        before = [r for r in records if str(r.get("publication_date") or "")[:10] < m["lundi"]]
        data = build_live(before, date.fromisoformat(m["lundi"]))
        problems = check_live(data)
        if problems:
            raise ValueError(f"lundi {m['lundi']} : " + " ; ".join(problems[:5]))
        shown[m["lundi"]] = {"periode": data["periode"], "total": data["total"], "marches": data["marches"]}
    return {"schema": 1, "source": simap.SOURCE, "mention": simap.MANDATORY_NOTICE, "lundis": shown}
