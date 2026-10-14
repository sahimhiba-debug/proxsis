"""Manual collection kit for the real test set (Bulletin officiel du Valais, FOSC).

People read the portals themselves (decision of 2026-10-05: no script browses
these sites; ``proxsis.http.MANUAL_ONLY_HOSTS``) and paste a publication
into a local page. This module:

* validates the submission (source, rubric, language, date, link) and refuses
  excluded categories (bankruptcy, debt enforcement, successions, civil
  status) — nothing is written in that case;
* applies the personal-data filter (:func:`proxsis.pii.redact_text`)
  **server-side, before anything is written**, even if the browser already
  showed a preview;
* writes the filtered text to ``<root>/textes/<collector>.jsonl`` (excluded
  from git) and only the link, metadata and SHA-256 of the filtered text to
  ``<root>/index/<collector>.jsonl`` (committed).

It makes no outbound request: the link is stored, never fetched.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import UTC, date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from proxsis.pii import redact_text

PERIOD = (date(2026, 8, 1), date(2026, 9, 30))
SOURCES: dict[str, str] = {"bo_vs": "Bulletin officiel du Valais", "fosc": "Feuille officielle suisse du commerce"}
RUBRICS: dict[str, dict[str, str]] = {
    "bo_vs": {"BA-VS05": "Demandes d'autorisation de construire / Baugesuche"},
    "fosc": {"HR01": "Nouvelles inscriptions / Neueintragungen", "HR02": "Mutations / Mutationen"},
}
DOC_TYPE = {"BA-VS05": "permis_construire", "HR01": "registre_commerce", "HR02": "registre_commerce"}
QUOTAS: dict[str, int] = {"bo_vs/fr": 50, "bo_vs/de": 25, "fosc/fr": 50, "fosc/de": 25}
LANG_QUOTAS = {"fr": 100, "de": 50}
URL_HOSTS = frozenset({"amtsblattportal.ch", "www.amtsblattportal.ch", "shab.ch", "www.shab.ch",
                       "bulletin-officiel.vs.ch"})
EXCLUDED = re.compile(
    r"faillite|Konkurs|office des poursuites|poursuite pour dettes|commandement de payer|Betreibung|"
    r"succession|Erbschaft|Erbgang|Nachlass|héritier|\bErben\b|état civil|Zivilstand|décès|Todesfall|"
    r"appel aux créanciers|Schuldenruf|sursis concordataire|concordat judiciaire|Nachlassstundung",
    re.IGNORECASE,
)
_COLLECTOR = re.compile(r"^[A-Za-z]{2,4}$")


PER_DAY = 2
ASSIGNMENT: dict[str, list[tuple[str, int]]] = {
    "Personne 1": [("bo_vs/fr", 30)],
    "Personne 2": [("bo_vs/fr", 20), ("bo_vs/de", 10)],
    "Personne 3": [("bo_vs/de", 15), ("fosc/de", 15)],
    "Personne 4": [("fosc/fr", 30)],
    "Personne 5": [("fosc/fr", 20), ("fosc/de", 10)],
}


def collection_plan(seed: int = 20261005) -> list[dict[str, Any]]:
    """Days to read per person and stratum: ``PER_DAY`` publications per day, in the portal's order, from the
    first one of the day. Days are drawn at random (working days of the period), disjoint between people of the
    same stratum, plus 3 spare days. This avoids each person choosing « interesting » publications."""
    import math
    from datetime import timedelta

    import numpy as np

    n_days = (PERIOD[1] - PERIOD[0]).days + 1
    days = [PERIOD[0] + timedelta(d) for d in range(n_days)]
    days = [d for d in days if d.weekday() < 5]
    rng = np.random.default_rng(seed)
    used: dict[str, set[date]] = {}
    plan = []
    for person, strata in ASSIGNMENT.items():
        for stratum, quota in strata:
            pool = [d for d in days if d not in used.get(stratum, set())]
            need = math.ceil(quota / PER_DAY)
            pick = [pool[i] for i in rng.choice(len(pool), size=need + 3, replace=False)]
            used.setdefault(stratum, set()).update(pick)
            plan.append({"personne": person, "strate": stratum, "quota": quota,
                         "jours": sorted(d.isoformat() for d in pick[:need]),
                         "reserve": sorted(d.isoformat() for d in pick[need:])})
    return plan


def in_drawn_days(source: str, lang: str, day: str, seed: int = 20261005) -> bool:
    """Is ``day`` one of the drawn days (or spares) of this stratum, all people together?"""
    stratum = f"{source}/{lang}"
    return any(day in r["jours"] or day in r["reserve"] for r in collection_plan(seed) if r["strate"] == stratum)


class Refused(ValueError):
    """The submission is refused; nothing has been written."""


def _check(sub: dict[str, Any]) -> dict[str, Any]:
    text = str(sub.get("text") or "").strip()
    src, rub, lang = sub.get("source"), sub.get("rubrique"), sub.get("lang")
    errors = []
    if src not in SOURCES:
        errors.append("source inconnue (BO VS ou FOSC seulement)")
    elif rub not in RUBRICS[src]:
        errors.append(f"rubrique non autorisée pour {src} : {rub}")
    if lang not in LANG_QUOTAS:
        errors.append("langue : fr ou de")
    try:
        d = date.fromisoformat(str(sub.get("date")))
        if not (PERIOD[0] <= d <= PERIOD[1]):
            errors.append(f"date hors période ({PERIOD[0]} → {PERIOD[1]})")
    except ValueError:
        errors.append("date au format AAAA-MM-JJ")
    url = str(sub.get("url") or "")
    if urlsplit(url).scheme != "https" or urlsplit(url).hostname not in URL_HOSTS:
        errors.append("lien : la page de la publication sur amtsblattportal.ch ou bulletin-officiel.vs.ch")
    if not _COLLECTOR.match(str(sub.get("collecteur") or "")):
        errors.append("collecteur : vos initiales (2 à 4 lettres)")
    if len(text) < 60:
        errors.append("texte trop court : collez la publication entière")
    m = EXCLUDED.search(text)
    if m:
        errors.append(f"catégorie exclue (« {m.group(0)} ») : passez à la publication suivante")
    if errors:
        raise Refused(" ; ".join(errors))
    return {"text": text, "url": url, "date": str(sub["date"]), "lang": lang, "source": src, "rubrique": rub,
            "collecteur": str(sub["collecteur"]).upper()}


def _int(v: Any) -> int:
    """Masks already applied by the XML import (structure), as reported by the page; 0 if absent or invalid."""
    try:
        return max(0, min(int(v), 1000))
    except (TypeError, ValueError):
        return 0


def preview(sub: dict[str, Any]) -> dict[str, Any]:
    """Filtered text, for the collector to check. Writes nothing."""
    s = _check(sub)
    filtered, n = redact_text(s["text"])
    return {"texte_filtre": filtered, "masquages": n}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def _publication_id(url: str) -> str | None:
    """The portal's publication UUID, whatever the link form (page, PDF, XML)."""
    m = _UUID.search(url.lower())
    return m.group(0) if m else None


def _index(root: Path) -> list[dict[str, Any]]:
    out = []
    for f in sorted((root / "index").glob("*.jsonl")):
        out += [json.loads(x) for x in f.read_text("utf-8").splitlines() if x.strip()]
    return out


def save(sub: dict[str, Any], root: Path) -> dict[str, Any]:
    s = _check(sub)
    filtered, n = redact_text(s["text"])  # always re-applied here, before writing
    sha = _sha(filtered)
    pub_id = _publication_id(s["url"])
    for e in _index(root):
        same_id = pub_id is not None and _publication_id(e["url"]) == pub_id
        if e["url"] == s["url"] or e["sha256_texte"] == sha or same_id:
            raise Refused("déjà collectée (même publication, même lien ou même texte)")
    entry = {"id": f"manuel:{s['source']}:{sha[:12]}", "source": s["source"], "rubrique": s["rubrique"],
             "doc_type_indicatif": DOC_TYPE[s["rubrique"]], "langue": s["lang"], "date_publication": s["date"],
             "url": s["url"], "collecteur": s["collecteur"], "sha256_texte": sha, "longueur": len(filtered),
             "masquages": n, "masquages_import": _int(sub.get("masquages_import")),
             "enregistre_le": datetime.now(UTC).isoformat(timespec="seconds")}
    for sub_dir in ("textes", "index"):
        (root / sub_dir).mkdir(parents=True, exist_ok=True)
    with (root / "textes" / f"{s['collecteur']}.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry | {"text": filtered}, ensure_ascii=False) + "\n")
    with (root / "index" / f"{s['collecteur']}.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def status(root: Path) -> dict[str, Any]:
    idx = _index(root)
    strata = {k: {"n": 0, "quota": q} for k, q in QUOTAS.items()}
    by_collector: dict[str, int] = {}
    for e in idx:
        strata[f"{e['source']}/{e['langue']}"]["n"] += 1
        by_collector[e["collecteur"]] = by_collector.get(e["collecteur"], 0) + 1
    langs = {lang: sum(v["n"] for k, v in strata.items() if k.endswith("/" + lang)) for lang in LANG_QUOTAS}
    return {"total": len(idx), "par_strate": strata, "par_langue": langs, "quotas_langue": LANG_QUOTAS,
            "par_collecteur": by_collector, "periode": [str(PERIOD[0]), str(PERIOD[1])]}


def load_items(root: Path) -> list[dict[str, Any]]:
    """Private texts (filtered) as annotation items."""
    items = []
    for f in sorted((root / "textes").glob("*.jsonl")):
        for line in f.read_text("utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                items.append({"id": r["id"], "lang": r["langue"], "doc_type_indicatif": r["doc_type_indicatif"],
                              "strate": f"{r['source']}/{r['langue']}", "collecteur": r["collecteur"],
                              "order_type": r["rubrique"], "publication_date": r["date_publication"],
                              "text": r["text"], "source_url": r["url"], "mention_obligatoire": SOURCES[r["source"]]
                              + " — seule la publication officielle fait foi."})
    return items


# ------------------------------------------------------------------ local page
class _Handler(BaseHTTPRequestHandler):
    root: Path
    token: str
    page: str

    def log_message(self, format: str, *args: Any) -> None:  # never log bodies
        return

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, data: Any) -> None:
        self._send(code, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._send(200, self.page.encode("utf-8"), "text/html; charset=utf-8")
        elif self.path == "/api/etat":
            self._json(200, status(self.root))
        else:
            self._send(404, b"", "text/plain")

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        limit = 60_000_000 if self.path == "/api/zip" else 3_000_000
        if length > limit:
            self.close_connection = True
            self._json(413, {"erreur": "requête trop volumineuse"})
            return
        body = self.rfile.read(length)  # always read before answering (else the client may see a reset)
        origin = self.headers.get("Origin", "")
        if self.headers.get("X-Jeton") != self.token or (origin and urlsplit(origin).hostname not in
                                                          ("127.0.0.1", "localhost")):
            self._json(403, {"erreur": "requête refusée"})
            return
        try:
            if self.path == "/api/zip":  # raw ZIP bytes, read in memory, nothing written
                from proxsis.gazette_xml import XmlRefused, parse_zip

                try:
                    items = parse_zip(body)
                except XmlRefused as exc:
                    self._json(422, {"erreur": str(exc)})
                    return
                for it in items:
                    if it["ok"]:
                        it["jour_tire"] = in_drawn_days(it["source"], it["lang"], it["date"])
                self._json(200, {"fichiers": items})
                return
            sub = json.loads(body or b"{}")
            if self.path == "/api/apercu":
                self._json(200, preview(sub))
            elif self.path == "/api/xml":
                from proxsis.gazette_xml import XmlRefused, parse_export

                try:  # raw XML parsed in memory only; natural persons masked from the structure
                    self._json(200, parse_export(str(sub.get("xml") or "").encode("utf-8")))
                except XmlRefused as exc:
                    self._json(422, {"erreur": str(exc)})
            elif self.path == "/api/enregistrer":
                self._json(200, {"enregistre": save(sub, self.root), "etat": status(self.root)})
            else:
                self._json(404, {"erreur": "inconnu"})
        except Refused as exc:
            self._json(422, {"erreur": str(exc)})
        except (ValueError, KeyError):
            self._json(400, {"erreur": "requête invalide"})


def make_server(root: Path, port: int = 8766) -> tuple[ThreadingHTTPServer, str]:
    """Local server bound to 127.0.0.1 only; a per-run token protects the write endpoints."""
    from proxsis.manual_collection_page import build_collection_page

    token = secrets.token_urlsafe(16)
    handler = type("H", (_Handler,), {"root": root, "token": token,
                                      "page": build_collection_page(token, SOURCES, RUBRICS, PERIOD, QUOTAS)})
    return ThreadingHTTPServer(("127.0.0.1", port), handler), token


def serve(root: Path, port: int = 8766) -> None:
    httpd, _ = make_server(root, port)
    print(f"Page de collecte : http://127.0.0.1:{httpd.server_address[1]}/  (Ctrl+C pour arrêter ; aucune donnée "
          "n'est envoyée ailleurs)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
