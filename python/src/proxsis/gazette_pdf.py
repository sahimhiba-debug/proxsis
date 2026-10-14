"""Import of « Composition individuelle » PDF exports of the Bulletin officiel du Valais (BA-VS05, building permit
applications), downloaded by a PERSON from the portal. No network.

The PDFs are laid out in three newspaper columns. ``pdftotext -bbox-layout`` gives every line with its position;
the reading order is rebuilt (page, column, height), full-width lines (page headers) are dropped, and the text is
cut into publications at each « Demande d'autorisation de construire » header.

Personal data: the raw text is only held in memory, and the filter (proxsis.gazette_filter) runs on each
publication before anything is written to disk.

German publications in a French composition carry only their title (« Il n'existe pas de traduction pour cette
publication »): they are kept as « contenu allemand à importer ».
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import unicodedata
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Any

Line = tuple[int, int, float, float, str]  # page, column (-1 = full width), y, x, text

HEADERS = ("Demande d’autorisation de construire", "Demande d'autorisation de construire")
# German composition (« Individuelle Zusammenstellung »): the header carries the start of the title.
DE_HEADER = re.compile(r"^(?:Gesuch für Baubewilligung(?:en)?|Baugesuch)\s*[-–—](?:\s+(?P<rest>.*))?$"
                       r"|^(?:Gesuch für Baubewilligung\w*|Baugesuch)$|^Gesuch für Bau\S*[-–—]$")
NO_TRANSLATION = "Il n'existe pas de traduction"
NO_TRANSLATION_DE = "Es gibt keine Übersetzung"
LABELS: list[tuple[str, str]] = [  # (prefix of the label line, field) — longest first where prefixes overlap
    ("Titre du projet de construction", "titre_projet"),
    ("Numéro pour consultation eConstruction", "numero_econstruction"),
    ("Requérant(e)", "requerant"),
    ("Requérant", "requerant"),
    ("Auteur du projet", "auteur_plans"),
    ("Auteur(e) de plans - Entreprise", "auteur_plans_entreprise"),
    ("Auteur(e) de plans", "auteur_plans"),
    ("Propriétaire", "proprietaire"),
    ("Maître d'ouvrage", "maitre_ouvrage"),
    ("Maître de l'ouvrage", "maitre_ouvrage"),
    ("Maître d’ouvrage", "maitre_ouvrage"),
    ("Coordonnées", "coordonnees"),
    ("Affectation(s) de la (des) zone(s)", "zone"),
    ("Dérogation(s)", "derogations"),
    ("Moyen de droit / Consultation", "moyen_de_droit"),
    ("Point de contact", "point_de_contact"),
    ("Délai de mise à disposition", "delai"),
    ("Expiration du délai", "expiration"),
    # German labels
    ("Titel des Bauprojekts", "titre_projet"),
    ("Nummer für die Konsultation", "numero_econstruction"),
    ("Gesuchstellende Partei", "requerant"),
    ("Gesuchsteller", "requerant"),
    ("Planverfasser - Firma", "auteur_plans_entreprise"),
    ("Planverfasser", "auteur_plans"),
    ("Projektverfasser", "auteur_plans"),
    ("Eigentümer", "proprietaire"),
    ("Grundeigentümer", "proprietaire"),
    ("Bauherrschaft", "maitre_ouvrage"),
    ("Bauherr", "maitre_ouvrage"),
    ("Koordinaten", "coordonnees"),
    ("Nutzungszone", "zone"),
    ("Ausnahmebewilligung", "derogations"),
    ("Rechtsmittel / Einsichtnahme", "moyen_de_droit"),
    ("Kontaktstelle", "point_de_contact"),
    ("Auflagefrist", "delai"),
    ("Ablauf der Frist", "expiration"),
]
ROLE_FIELDS = ("requerant", "proprietaire", "maitre_ouvrage", "auteur_plans", "auteur_plans_entreprise",
               "autres_parties")

# a role label at the start of a line: an unknown role never spills into the title
_ROLE_START = re.compile(
    r"^(?:Requérant|Gesuchsteller|Propriétaire|Grundeigentümer|Eigentümer|Auteur|Projektverfasser|Planverfasser|"
    r"Bauherr|Maître|Mandataire|Représentant|Vertreter|Architecte|Architekt|Domicile|Wohnsitz)\b", re.IGNORECASE)


# ---------------------------------------------------------------- extraction (memory only)

def extract_lines(pdf: Path) -> list[Line]:
    """Lines in reading order. The text stays in memory: nothing is written."""
    out = subprocess.run(["pdftotext", "-bbox-layout", "-enc", "UTF-8", str(pdf), "-"], capture_output=True,
                         check=True, timeout=300).stdout
    root = ET.fromstring(out)
    ns = {"h": "http://www.w3.org/1999/xhtml"}
    lines: list[Line] = []
    for pi, page in enumerate(root.findall(".//h:page", ns)):
        width = float(page.get("width") or 595.3)
        items = []
        for ln in page.findall(".//h:line", ns):
            x0, x1, y = float(ln.get("xMin") or 0), float(ln.get("xMax") or 0), float(ln.get("yMin") or 0)
            text = " ".join((w.text or "") for w in ln.findall("h:word", ns)).strip()
            if not text:
                continue
            # three columns starting near x = 40, 216 and 392 on an A4 page of 595 pt
            col = -1 if (x1 - x0) > 0.5 * width else (0 if x0 < 0.33 * width else (1 if x0 < 0.64 * width else 2))
            items.append((pi, col, y, x0, text))
        items.sort(key=lambda t: (t[1], t[2], t[3]))
        lines += items
    return lines


def split_publications(lines: list[Line]) -> list[list[str]]:
    pubs: list[list[str]] = []
    cur: list[str] | None = None
    for _, col, _, _, text in lines:
        if col == -1:
            continue  # page header / footer across the columns
        if text.strip() in HEADERS or DE_HEADER.match(text.strip()):
            if cur is not None and len(cur) == 1 and cur[0] == "Baugesuch":
                pubs.pop()  # rubric heading without content, not a publication
            cur = [text.strip()]
            pubs.append(cur)
        elif cur is not None:
            cur.append(text.strip())
    return pubs


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower().replace("’", "'")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _label(line: str) -> tuple[str, str] | None:
    if line in ("Parcelle", "Parzelle"):
        return line, "parcelle"
    if line == "Zone":
        return "Zone", "zone"
    for prefix, field in LABELS:
        if line.startswith(prefix):
            return prefix, field
    return None


def _once(title: str) -> str:
    """Some German compositions print the title two or three times in a row (the last copy may be cut): keep one."""
    toks = title.split()
    for k in range(3, len(toks) // 2 + 1):
        if all(toks[i] == toks[i + k] for i in range(len(toks) - k)):
            return " ".join(toks[:k])
    return title


def _join_hyphenated(lines: list[str]) -> list[str]:
    """« Jo- / hannes » → « Johannes »: a word cut at the end of a line (next line starting in lower case)."""
    out: list[str] = []
    for line in lines:
        if out and re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]-$", out[-1]) and line[:1].islower():
            out[-1] = out[-1][:-1] + line
        else:
            out.append(line)
    return out


def parse_publication(raw: list[str]) -> dict[str, Any]:
    title: list[str] = []
    i = 1
    german = bool(DE_HEADER.match(raw[0])) if raw else False
    if german:
        m = DE_HEADER.match(raw[0])
        rest = (m.group("rest") if m and m.groupdict().get("rest") else "") or ""
        if rest:
            title.append(rest)
    while (i < len(raw) and not _label(raw[i]) and not raw[i].startswith((NO_TRANSLATION, NO_TRANSLATION_DE))
           and not _ROLE_START.match(raw[i])):  # an unknown role label never spills into the title
        line = re.sub(r"^(?:bewilligung|gung)?\s*[-–—]\s*", "", raw[i]) if not title else raw[i]
        if line:
            if title and title[-1].endswith("-") and line[:1].islower():
                title[-1] = title[-1][:-1] + line  # word cut at the end of a line
            else:
                title.append(line)
        i += 1
    pub: dict[str, Any] = {"titre": _once(re.sub(r"\s+", " ", " ".join(title)).strip()),
                           "roles": {f: [] for f in ROLE_FIELDS},
                           "langue": "de" if german else "fr", "expiration": None, "champs": {}}
    field: str | None = None
    buf: list[str] = []

    def flush() -> None:
        if field is None:
            return
        lines = _join_hyphenated([re.sub(r"\s+", " ", x).strip() for x in buf if x.strip()])
        if field in ROLE_FIELDS:  # line breaks separate parties and addresses: kept for the filter
            value = "\n".join(lines)
            if value:
                pub["roles"][field].append(value)
        else:
            pub["champs"].setdefault(field, []).append(" ".join(lines))

    for line in raw[i:]:
        if line.startswith(NO_TRANSLATION):
            pub["langue"] = "de"  # German publication in a French composition: title only
            continue
        if line.startswith(NO_TRANSLATION_DE):
            pub["langue"] = "fr"  # French publication in a German composition: title only
            continue
        if field == "numero_econstruction" and line == "on" and not buf:
            continue  # « eConstructi- / on »: end of the hyphenated label
        lab = _label(line)
        if lab:
            flush()
            prefix, field = lab
            rest = line[len(prefix):].strip(" :")
            if field == "numero_econstruction" and rest.startswith("eConstruct"):
                rest = ""  # end of the label itself (« … eConstructi- / on »)
            buf = [rest] if rest else []
            if field == "expiration":
                m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", line)
                pub["expiration"] = f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None
        elif field not in ROLE_FIELDS and _ROLE_START.match(line):
            flush()  # unknown role label (« Domicile: », « Auteur du projet … ») in another field: treated as a party
            field, buf = "autres_parties", [line]
        else:
            buf.append(line)
    flush()
    num = (pub["champs"].get("numero_econstruction") or [""])[0]
    pub["numero_econstruction"] = num.replace(" ", "") or None
    pub["titre_projet"] = (pub["champs"].get("titre_projet") or [""])[0] or None
    pub["contenu_complet"] = pub["expiration"] is not None and not any(
        x.startswith((NO_TRANSLATION, NO_TRANSLATION_DE)) for x in raw)
    return pub


# ---------------------------------------------------------------- duplicates and index

def _key(p: dict[str, Any]) -> tuple[str, ...]:
    if p.get("contenu_complet"):
        return ("fr", p.get("numero_econstruction") or "", _norm(p["titre"]), p.get("expiration") or "")
    return ("titre", _norm(p["titre"]))


def dedupe(pubs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Same publication in several files: same index id once linked, otherwise same content key."""
    seen: dict[tuple[str, ...], dict[str, Any]] = {}
    unique, dups = [], []
    for p in pubs:
        k = ("id", p["id"]) if p.get("id") else _key(p)
        if k in seen:
            seen[k]["fichiers"] = sorted({*seen[k]["fichiers"], p.get("fichier", "")})
            dups.append(p)
            continue
        p = p | {"fichiers": [p.get("fichier", "")]}
        seen[k] = p
        unique.append(p)
    return unique, dups


def commune_of(office: str) -> str | None:
    s = re.split(r"\s+-\s+|,", office or "")[0].strip()
    if re.match(r"(?i)canton|kanton", s):
        return None
    s = re.sub(r"(?i)^(commune d['’]|ville d['’])", "", s)
    s = re.sub(r"(?i)^(commune de|ville de|einwohnergemeinde|munizipalgemeinde|gemeinde|stadtgemeinde|stadt|"
               r"municipalité de|administration communale de)\s+", "", s)
    return s or None


_PREFIXES = ("demande d autorisation de construire", "gesuch fur baubewilligung", "baugesuch")


def title_key(title: str) -> str:
    """Title without the portal prefix, ignoring case, accents, punctuation, spaces and line-end hyphenation."""
    n = _norm(title)
    for pre in _PREFIXES:
        if n.startswith(pre):
            n = n[len(pre):]
            break
    return n.replace(" ", "")


def _commune_hint(p: dict[str, Any]) -> str | None:
    contact = (p.get("champs", {}).get("point_de_contact") or [""])[0]
    m = re.match(r"(?i)((?:commune|ville|gemeinde|stadtgemeinde|municipalité)\b.*?)(?:\s+(?:service|bureau|case|"
                 r"rue|route|avenue|place|bauamt|\d)|$)", contact)
    return commune_of(m.group(1)) if m else None


def link_to_index(pubs: list[dict[str, Any]], index: list[dict[str, Any]],
                  window: tuple[str, str] | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Link by title (portal prefix removed); ties broken by the publication-date window of the file, by the
    expiration date, then by the commune of the contact point. The expiration date printed in the PDF is not the
    index's: it falls about 30 days after the publication date (31 days in 374 of 388 linked cases, 20 to 30 for
    the others), so a republished identical title is resolved by the publication date it implies."""
    by_title: dict[str, list[dict[str, Any]]] = {}
    for row in index:
        for t in set((row.get("titres") or {}).values()):
            if t and title_key(t):
                by_title.setdefault(title_key(t), []).append(row)
    linked, unmatched = [], []
    for p in pubs:
        cands = list({r["id"]: r for r in by_title.get(title_key(p["titre"]), [])}.values())
        if len(cands) > 1 and window:
            lo, hi = window
            cands = [r for r in cands if lo <= (r.get("date") or "") <= hi] or cands
        if len(cands) > 1 and p.get("expiration"):
            exp = date.fromisoformat(p["expiration"])
            fits = [r for r in cands if r.get("date") and 18 <= (exp - date.fromisoformat(r["date"][:10])).days <= 33]
            cands = fits if len(fits) == 1 else cands
        hint = _commune_hint(p)
        if len(cands) > 1 and hint:
            cands = [r for r in cands if commune_of(r.get("office", "")) == hint] or cands
        if len(cands) != 1:
            unmatched.append(p | {"motif_non_relie": "aucune correspondance" if not cands else
                                  f"{len(cands)} correspondances possibles"})
            continue
        r = cands[0]
        linked.append(p | {"id": r["id"], "date_publication": r.get("date"), "langue": r.get("langue") or p["langue"],
                           "commune": commune_of(r.get("office", "")), "office": r.get("office"),
                           "etat": r.get("etat"), "expiration_index": r.get("expiration"),
                           "url": f"https://bulletin-officiel.vs.ch/api/v1/publications/{r['id']}/pdf",
                           "contenu_allemand_a_importer": (r.get("langue") == "de" or p["langue"] == "de")
                           and not p.get("contenu_complet")})
    return linked, unmatched


def text_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def iso_week(d: str | None) -> str | None:
    if not d:
        return None
    y, w, _ = date.fromisoformat(d[:10]).isocalendar()
    return f"{y}-S{w:02d}"


def skeleton(lines: list[Line], min_count: int = 150, max_lines: int = 200) -> str:
    """Masked skeleton for adapting the parser to a new layout or language without reading the content: only
    tokens seen at least ``min_count`` times (template words) stay; others become Xx / x / 9."""
    from collections import Counter

    texts = [t for *_, t in lines]
    freq = Counter(w.lower() for t in texts for w in re.findall(r"[A-Za-zÀ-ÿ'’()\-]+", t))

    def shape(tok: str) -> str:
        if freq[tok.lower()] >= min_count:
            return tok
        if tok.isdigit():
            return "9" * min(len(tok), 4)
        return "Xx" if tok[:1].isupper() else "x"

    out = []
    for _, col, _, _, t in lines[:max_lines]:
        toks = re.findall(r"[A-Za-zÀ-ÿ'’()\-]+|\d+|[^\sA-Za-zÀ-ÿ\d]", t)
        out.append(("[large] " if col == -1 else "") + " ".join(shape(x) for x in toks))
    return "\n".join(out)
