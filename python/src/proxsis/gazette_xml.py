"""Import of an XML export that a PERSON downloaded from the Bulletin officiel du Valais (« Exporter au format
XML » on a publication). No network: the file is read from the person's disk.

The export types every person: ``<subject><selectType>naturalPerson</selectType>`` (private person) or
``legalPerson`` (company). Natural persons are replaced by ``[masqué]`` **from the structure** — their name
elements are never read into the output — and the rendered text then goes through the usual text filter
(parcel numbers, coordinates, civility + name in free text). The raw XML is parsed in memory only.

Supported: BA-VS05 (demandes d'autorisation de construire), structure observed on 2026-10-05. FOSC (HR)
exports: to add once an example is available; until then, paste the text.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date
from typing import Any

from proxsis.pii import REDACTED, redact_text

SUPPORTED = {"BA-VS05": ("bo_vs", "BA-VS05")}
MAX_BYTES = 2_000_000
MAX_FILES = 300  # one ZIP: the whole test set (150) with room for spares
MAX_ZIP_TOTAL = 150_000_000


class XmlRefused(ValueError):
    """The file is not a supported, safe export; nothing is kept."""


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].split(":")[-1]


def _child(el: ET.Element | None, name: str) -> ET.Element | None:
    if el is None:
        return None
    for c in el:
        if _local(c.tag) == name:
            return c
    return None


def _children(el: ET.Element | None, name: str) -> list[ET.Element]:
    return [c for c in el if _local(c.tag) == name] if el is not None else []


def _text(el: ET.Element | None) -> str:
    return (el.text or "").strip() if el is not None else ""


def _term(el: ET.Element | None, lang: str) -> str:
    """Multilingual ``<term><fr>…</fr><de>…</de></term>`` (or the element itself)."""
    if el is None:
        return ""
    by_lang = {_local(c.tag): _text(c) for c in el if _text(c)}
    return by_lang.get(lang) or by_lang.get("fr") or by_lang.get("de") or next(iter(by_lang.values()), _text(el))


def _fmt_date(s: str) -> str:
    try:
        return date.fromisoformat(s).strftime("%d.%m.%Y")
    except ValueError:
        return s


def _value(el: ET.Element, lang: str) -> tuple[str, int]:
    """Displayed value of a businessCase element; (text, structural masks)."""
    key = _text(_child(el, "key"))
    vtype = _text(_child(el, "valueType"))
    if vtype == "naturalLegalPerson":
        subject = _child(el, "subject")
        kind = _text(_child(subject, "selectType"))
        if kind == "legalPerson":
            company = _child(_child(subject, "legalPerson"), "company")
            name = _text(_child(company, "name"))
            return (name, 0) if name else (REDACTED, 1)
        return REDACTED, 1  # natural person (or unknown): never read the name
    if key == "coordinates":
        return REDACTED, 1
    if vtype == "textNeutral":
        return _text(_child(el, "valueTextNeutral")), 0
    if vtype == "text":
        return _term(_child(_child(el, "valueText"), "term"), lang), 0
    if vtype == "date":
        return _fmt_date(_text(_child(el, "valueDate")) or _text(_child(el, "date"))), 0
    return "", 0


def parse_export(xml: bytes) -> dict[str, Any]:
    if len(xml) > MAX_BYTES:
        raise XmlRefused("fichier trop volumineux pour un export de publication")
    head = xml[:4096].upper()
    if b"<!DOCTYPE" in head or b"<!ENTITY" in xml.upper():
        raise XmlRefused("fichier refusé : déclaration DOCTYPE/ENTITY (risque de sécurité)")
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise XmlRefused(f"fichier illisible : ce n'est pas un export XML du portail ({exc})") from exc
    meta, content = _child(root, "meta"), _child(root, "content")
    if meta is None or content is None:
        raise XmlRefused("ce n'est pas un export de publication du portail")
    sub = _text(_child(meta, "subRubric"))
    if sub not in SUPPORTED:
        raise XmlRefused(f"rubrique {sub or '?'} non prise en charge par l'import XML : collez le texte")
    lang = _text(_child(meta, "language")) or "fr"
    pub_id = _text(_child(meta, "id"))
    if not re.fullmatch(r"[0-9a-f-]{36}", pub_id):
        raise XmlRefused("identifiant de publication absent ou invalide")
    host = "bulletin-officiel.vs.ch" if _text(_child(meta, "primaryTenantCode")) == "kabvs" else "amtsblattportal.ch"
    masks = 0
    lines = [_term(_child(meta, "title"), lang)]
    case = _child(content, "businessCase")
    for block in [*_children(case, "primary"), *_children(case, "secondary")]:
        for el in _children(block, "element"):
            label = _term(_child(el, "term"), lang)
            value, n = _value(el, lang)
            masks += n
            if label and value:
                lines += ["", label, value]
    for el in _children(_child(content, "reaction"), "element"):
        remedy = _term(_child(el, "legalRemedy"), lang)
        contact = _term(_child(el, "contact"), lang)
        deadline = _child(el, "deadline")
        if remedy:
            lines += ["", "Moyen de droit / Consultation" if lang == "fr" else "Rechtsmittel", remedy]
        if contact:
            lines += ["", "Point de contact" if lang == "fr" else "Kontaktstelle", contact]
        if deadline is not None:
            lines += ["", f"{_term(_child(deadline, 'term'), lang)} : {_fmt_date(_text(_child(deadline, 'date')))}"]
    commune = _term(_child(_child(_child(content, "localization"), "municipalityId"), "term"), lang)
    if commune:
        lines += ["", f"Commune : {commune}" if lang == "fr" else f"Gemeinde: {commune}"]
    text, n = redact_text("\n".join(lines))
    source, rubric = SUPPORTED[sub]
    return {"source": source, "rubrique": rubric, "lang": lang, "date": _text(_child(meta, "publicationDate")),
            "url": f"https://{host}/api/v1/publications/{pub_id}/pdf",
            "numero": _text(_child(meta, "publicationNumber")),
            "text": text, "masquages": masks + n}


def parse_zip(data: bytes) -> list[dict[str, Any]]:
    """Every ``.xml`` of a ZIP of exports, read in memory (nothing is extracted to disk). One result per file:
    ``{"fichier", "ok", ...parse_export fields}`` or ``{"fichier", "ok": False, "erreur"}``."""
    import io
    import zipfile

    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise XmlRefused("ce n'est pas une archive ZIP lisible") from exc
    entries = [i for i in z.infolist() if not i.is_dir() and i.filename.lower().endswith(".xml")
               and not i.filename.startswith("__MACOSX/") and not i.filename.rsplit("/", 1)[-1].startswith("._")]
    if len(entries) > MAX_FILES:
        raise XmlRefused(f"{len(entries)} fichiers XML : {MAX_FILES} au maximum par archive")
    if sum(i.file_size for i in entries) > MAX_ZIP_TOTAL:
        raise XmlRefused("archive trop volumineuse une fois décompressée")
    out: list[dict[str, Any]] = []
    for info in sorted(entries, key=lambda i: i.filename):
        if info.file_size > MAX_BYTES:  # declared size checked before reading (zip bomb)
            out.append({"fichier": info.filename, "ok": False,
                        "erreur": "fichier trop volumineux pour un export de publication"})
            continue
        with z.open(info) as fh:
            raw = fh.read(MAX_BYTES + 1)
        try:
            out.append({"fichier": info.filename, "ok": True, **parse_export(raw)})
        except XmlRefused as exc:
            out.append({"fichier": info.filename, "ok": False, "erreur": str(exc)})
    return out


MAX_BULK_BYTES = 30_000_000


def parse_bulk_index(xml: bytes) -> list[dict[str, Any]]:
    """« bulk-export » list of publications (meta only). Read: id, number, language, office, dates, state, titles.
    Never read: invoice address, « on behalf of » (they may name a private person)."""
    if len(xml) > MAX_BULK_BYTES:
        raise XmlRefused("fichier trop volumineux pour un index de publications")
    if b"<!DOCTYPE" in xml[:4096].upper() or b"<!ENTITY" in xml.upper():
        raise XmlRefused("fichier refusé : déclaration DOCTYPE/ENTITY (risque de sécurité)")
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise XmlRefused(f"index illisible ({exc})") from exc
    if _local(root.tag) != "bulk-export":
        raise XmlRefused("ce n'est pas un export « bulk-export » du portail")
    rows = []
    for pub in _children(root, "publication"):
        meta = _child(pub, "meta")
        if meta is None:
            continue
        title_el = _child(meta, "title")
        titles = {_local(c.tag): _text(c) for c in (list(title_el) if title_el is not None else []) if _text(c)}
        rows.append({"id": _text(_child(meta, "id")), "numero": _text(_child(meta, "publicationNumber")),
                     "sous_rubrique": _text(_child(meta, "subRubric")), "langue": _text(_child(meta, "language")),
                     "office": _text(_child(_child(meta, "registrationOffice"), "displayName")),
                     "etat": _text(_child(meta, "publicationState")),
                     "date": _text(_child(meta, "publicationDate"))[:10],
                     "expiration": _text(_child(meta, "expirationDate"))[:10], "titres": titles})
    return rows
