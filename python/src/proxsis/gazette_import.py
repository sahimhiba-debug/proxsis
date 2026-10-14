"""Import of Bulletin officiel PDF compositions (BA-VS05) linked to the portal's « bulk-export » index.

Order of operations (personal data never reaches the disk unfiltered):
1. read every PDF in memory (``gazette_pdf.extract_lines``), cut and parse the publications;
2. detect duplicates between files;
3. link each publication to the XML index (title, then expiration, then commune) to get its id and date;
4. FILTER each publication (``gazette_filter``: natural persons masked in roles, title and text; parcels and
   coordinates masked);
5. only then write: public index (no full text) and report in ``public_dir``; filtered texts in ``private_dir``
   (git-ignored).

The test set is drawn at random with a recorded seed from the accepted publications with full content, per
language. German publications only have their title in a French composition: they wait for the German export.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from proxsis.gazette_filter import build_context, filter_publication, sweep_rows
from proxsis.gazette_pdf import (
    commune_of,
    dedupe,
    extract_lines,
    iso_week,
    link_to_index,
    parse_publication,
    split_publications,
    text_sha,
)
from proxsis.gazette_xml import parse_bulk_index
from proxsis.pii import REDACTED

SOURCE = "Bulletin officiel du Valais (bulletin-officiel.vs.ch), exports PDF « Composition individuelle »"
MENTION = "Bulletin officiel du Valais — seule la publication officielle fait foi."
PUBLIC_FIELDS = ("id", "date_publication", "semaine", "commune", "langue", "titre", "titre_projet",
                 "numero_econstruction", "expiration", "url", "fichiers", "statut", "motif", "contenu_complet",
                 "contenu_allemand_a_importer", "masquages", "entreprises_citees", "organismes_publics_cites",
                 "roles", "sha256_texte")


REJECTED_FIELDS = ("id", "langue", "fichiers", "statut", "motif", "contenu_complet")


def run_import(pdfs: list[Path], index_xml: Path, public_dir: Path, private_dir: Path,
               extract: Callable[[Path], list[Any]] = extract_lines, suffix: str = "",
               localities: list[str] | None = None, context_pdfs: list[Path] | None = None) -> dict[str, Any]:
    """``context_pdfs``: other compositions read IN MEMORY only, so that a party masked there (e.g. in the French
    export) is also masked here (e.g. in a German title). Nothing is written if the final sweep finds anything."""
    index = parse_bulk_index(index_xml.read_bytes())
    per_file: dict[str, dict[str, Any]] = {}
    parsed: list[dict[str, Any]] = []
    n_read = 0
    for pdf in pdfs:
        pubs = [parse_publication(raw) | {"fichier": pdf.name} for raw in split_publications(extract(pdf))]
        n_read += len(pubs)
        first, _ = link_to_index(pubs, index)  # unambiguous links give the file's publication-date window
        dates = sorted(x["date_publication"] for x in first if x.get("date_publication"))
        window = (dates[0], dates[-1]) if dates else None
        lk, um = link_to_index(pubs, index, window=window)
        per_file[pdf.name] = {"publications": len(pubs), "contenu_complet": sum(p["contenu_complet"] for p in pubs),
                              "en_allemand": sum(p["langue"] == "de" for p in pubs),
                              "periode": list(window) if window else None}
        parsed += lk + um
    others = [parse_publication(raw) for pdf in (context_pdfs or []) if pdf not in pdfs
              for raw in split_publications(extract(pdf))]
    places = list(localities or []) + [c for c in (commune_of(r.get("office") or "") for r in index) if c]
    ctx = build_context(parsed + others, [" ".join((r.get("titres") or {}).values()) for r in index], places)
    unique, dups = dedupe(parsed)
    linked = [p for p in unique if p.get("id")]
    unmatched = [p for p in unique if not p.get("id")]
    rows: list[dict[str, Any]] = []
    masks_to_check: list[dict[str, str]] = []
    private_texts: dict[str, str] = {}
    unlinked: list[dict[str, Any]] = []
    for p, status, reason in ([(x, "acceptée", None) for x in linked] +
                              [(x, "rejetée", "sans correspondance dans l'index XML") for x in unmatched]):
        f, masks = filter_publication(p, ctx)  # BEFORE anything is written
        if status == "acceptée" and p.get("etat") == "CANCELLED":
            status, reason = "rejetée", "publication annulée (index)"
        if status == "acceptée" and p["langue"] == "fr" and not p["contenu_complet"]:
            status, reason = "rejetée", "lecture incomplète (ni date d'expiration ni mention allemande)"
        key = f.get("id") or "sans-id-" + text_sha(f["texte"])[:12]
        row = f | {"id": key, "statut": status, "motif": reason, "semaine": iso_week(f.get("date_publication")),
                   "sha256_texte": text_sha(f["texte"]),
                   "contenu_allemand_a_importer": bool(f.get("contenu_allemand_a_importer"))}
        rows.append({k: row.get(k) for k in (PUBLIC_FIELDS if status == "acceptée" else REJECTED_FIELDS)})
        if status != "acceptée":
            if reason == "sans correspondance dans l'index XML":
                unlinked.append({"titre_masque": f["titre"], "fichiers": f.get("fichiers") or [],
                                 "motif": p.get("motif_non_relie") or ""})
            continue  # a rejected publication is only counted: no title, no party in the public file
        for m in masks:
            masks_to_check.append({"publication": key, "date": f.get("date_publication") or "", "champ": m["champ"],
                                   "motif": m["motif"], "apercu": m["apercu"], "lien": f.get("url") or ""})
        if status == "acceptée" and p["contenu_complet"]:
            private_texts[key] = f["texte"]
    acc = [r for r in rows if r["statut"] == "acceptée"]
    rep = {
        "source": SOURCE, "fichiers": per_file, "lues": n_read, "doublons": len(dups), "uniques": len(unique),
        "acceptees": len(acc), "rejetees": len(rows) - len(acc),
        "rejetees_par_motif": dict(Counter(r["motif"] for r in rows if r["statut"] == "rejetée")),
        "par_langue": dict(Counter(r["langue"] for r in acc)),
        "contenu_allemand_a_importer": sum(r["contenu_allemand_a_importer"] for r in acc),
        "par_commune": dict(Counter(r["commune"] or "(commission cantonale)" for r in acc).most_common()),
        "par_semaine": dict(sorted(Counter(r["semaine"] for r in acc if r["semaine"]).items())),
        "index": {"publications": len(index), "relies": len({r["id"] for r in acc}),
                  "non_trouvees_dans_les_pdf": len({i["id"] for i in index} - {r["id"] for r in rows})},
        "masquages": len(masks_to_check), "masquages_a_verifier": masks_to_check,
        "non_relies": unlinked,
    }
    public_dir.mkdir(parents=True, exist_ok=True)
    target = public_dir / "publications.jsonl"
    replaced = 0
    if target.exists():  # a later import (e.g. the German export) completes the earlier one
        names = {pdf.name for pdf in pdfs}
        old = {r["id"]: r for r in (json.loads(x) for x in target.read_text("utf-8").splitlines() if x.strip())
               # an unlinked publication of the same files is re-derived (its id depends on the filtered text)
               if not (str(r["id"]).startswith("sans-id-") and set(r.get("fichiers") or []) & names)}
        before = len(old)
        for r in rows:
            prev = old.get(r["id"])
            if prev is not None and prev.get("contenu_complet") and not r.get("contenu_complet"):
                continue  # never replace full content by a title-only entry
            if prev is not None and r.get("contenu_complet") and not prev.get("contenu_complet"):
                replaced += 1
            old[r["id"]] = r
        rows = list(old.values())
        rep["fusion"] = {"avant": before, "apres": len(rows), "remplacees": replaced}
    else:
        rep["fusion"] = {"avant": 0, "apres": len(rows), "remplacees": 0}
    # last check, on everything about to be written (merged rows too): stops the import, nothing is written
    report_strings = [{"id": m["publication"], "titre": m["apercu"]} for m in masks_to_check] + [
        {"id": "non-relie", "titre": u["titre_masque"]} for u in unlinked]
    sweep_rows(rows + report_strings, private_texts, ctx)
    merged_acc = [r for r in rows if r["statut"] == "acceptée"]
    rep["fusion"] |= {"acceptees": len(merged_acc),
                      "allemandes_completes": sum(r["langue"] == "de" and bool(r.get("contenu_complet"))
                                                  for r in merged_acc),
                      "allemandes_titre_seul": sum(r["langue"] == "de" and not r.get("contenu_complet")
                                                   for r in merged_acc)}
    target.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
    report_json = json.dumps(rep, ensure_ascii=False, indent=1) + "\n"
    (public_dir / f"rapport_import{suffix.lower()}.json").write_text(report_json, "utf-8")
    (public_dir / f"RAPPORT_IMPORT{suffix.upper()}.md").write_text(report_md(rep), "utf-8")
    tdir = private_dir / "textes"
    tdir.mkdir(parents=True, exist_ok=True)
    for key, text in private_texts.items():
        (tdir / f"{key}.txt").write_text(text + "\n", "utf-8")
    return rep


def report_md(rep: dict[str, Any]) -> str:
    files = "\n".join(f"| {k} | {' → '.join(v['periode'] or ['?'])} | {v['publications']} | {v['contenu_complet']} | "
                      f"{v['en_allemand']} |" for k, v in rep["fichiers"].items())
    reasons = "\n".join(f"- {k} : {v}" for k, v in rep["rejetees_par_motif"].items()) or "- aucune"
    communes = "\n".join(f"| {k} | {v} |" for k, v in list(rep["par_commune"].items())[:40])
    weeks = "\n".join(f"| {k} | {v} |" for k, v in rep["par_semaine"].items())
    masks = "\n".join(f"| {m['date']} | {m['champ']} | {m['apercu']} | {m['lien']} |"
                      for m in rep["masquages_a_verifier"][:400])
    unlinked = "\n".join(f"- « {u['titre_masque'][:100]} » ({', '.join(u['fichiers'])}) — {u.get('motif', '')}"
                         for u in rep["non_relies"])
    fusion = rep.get("fusion") or {}
    return f"""# Rapport d'import — Bulletin officiel du Valais, demandes d'autorisation de construire (PDF)

Source : {rep['source']}. Données **RÉELLES**, filtrées avant tout enregistrement : toute personne physique est
masquée (requérant, propriétaire, maître d'ouvrage, auteur des plans, titre, texte) ; entreprises, communes,
bourgeoisies, fondations, paroisses, consortages, autorités et associations sont conservés. Parcelles et
coordonnées masquées. Textes filtrés hors git ; ce rapport ne contient que des statistiques et des aperçus masqués.

## Lecture

| Fichier | Période (dates de publication reliées) | Publications lues | Contenu complet | En allemand |
|---|---|---|---|---|
{files}

- Publications lues : **{rep['lues']}** ; doublons entre fichiers : **{rep['doublons']}** ;
  uniques : **{rep['uniques']}**.
- Acceptées : **{rep['acceptees']}** ; rejetées : **{rep['rejetees']}**.
{reasons}
- Par langue (acceptées) : {rep['par_langue']} ; contenu allemand à importer : **{rep['contenu_allemand_a_importer']}**.
- Index XML : {rep['index']['publications']} publications ; reliées : {rep['index']['relies']} ; absentes des PDF :
  {rep['index']['non_trouvees_dans_les_pdf']}.
- Fusion avec l'index public déjà importé : {fusion.get('avant', 0)} entrées avant, {fusion.get('apres', 0)} après ;
  **{fusion.get('remplacees', 0)} entrées « titre seul » complétées par leur contenu** lors de cette exécution.
- État après fusion : {fusion.get('acceptees', 0)} publications acceptées, dont
  **{fusion.get('allemandes_completes', 0)} allemandes au contenu complet** et
  {fusion.get('allemandes_titre_seul', 0)} allemandes encore « titre seul ».

## Publications sans correspondance dans l'index

{unlinked or "Aucune."}

## Par commune (acceptées)

| Commune | Publications |
|---|---|
{communes}

## Par semaine de publication (acceptées)

| Semaine | Publications |
|---|---|
{weeks}

## Masquages à vérifier à la main ({rep['masquages']})

Ouvrir le lien officiel et vérifier que le masquage était justifié (une entreprise masquée à tort est une perte ;
un particulier non masqué serait une faute).

| Date | Champ | Aperçu masqué | Lien |
|---|---|---|---|
{masks}
"""


def draw_test_set(rows: list[dict[str, Any]], n: int, lang: str, seed: int) -> dict[str, Any]:
    """Random, reproducible draw among accepted publications of ``lang`` with full content."""
    frame = sorted(r["id"] for r in rows if r["statut"] == "acceptée" and r["langue"] == lang
                   and r.get("contenu_complet"))
    note = ""
    if lang == "de" and not frame:
        waiting = sum(1 for r in rows if r.get("contenu_allemand_a_importer"))
        note = f"{waiting} publications au contenu allemand à importer : tirage après l'import de l'export allemand"
    rng = np.random.default_rng(seed)
    ids = sorted(rng.choice(frame, size=min(n, len(frame)), replace=False).tolist()) if frame else []
    return {"langue": lang, "n_demande": n, "cadre": len(frame), "graine": seed, "ids": ids, "note": note,
            "empreinte_cadre": text_sha(json.dumps(frame))}


_CATS: dict[str, re.Pattern[str]] = {
    "logements_collectifs": re.compile(
        r"immeubles?\b|logements|appartements|habitat collectif|mehrfamilienh|\bmfh\b|wohnungen|"
        r"wohn(?:ü|ue)berbauung|appartementhaus", re.IGNORECASE),
    "halle": re.compile(r"\bhalles?\b|hangar|entrep[ôo]t|d[ée]p[ôo]t|atelier|usine|industriel|artisanal|"
                        r"lagerhalle|werkhalle|gewerbe|industrie|lager\b|werkstatt", re.IGNORECASE),
    "public": re.compile(r"[ée]cole|salle (?:de gym|polyvalente)|\bems\b|cr[èe]che|h[ôo]pital|centre scolaire|"
                         r"administration communale|schule|turnhalle|spital|altersheim|kindergarten", re.IGNORECASE),
}


def radar_projects(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Projects that matter for the radar: multi-dwelling buildings, halls, public projects; with the applicant
    when it is a company (natural persons are already masked in ``rows``)."""
    out = []
    for r in rows:
        if r["statut"] != "acceptée":
            continue
        text = " ".join(filter(None, [r.get("titre"), r.get("titre_projet")]))
        cats = [c for c, rx in _CATS.items() if rx.search(text)]
        roles = r.get("roles") or {}
        publics = r.get("organismes_publics_cites") or []
        def pieces(*fields: str, roles: dict[str, list[str]] = roles) -> list[str]:
            return [x for f in fields for v in roles.get(f) or [] for x in v.split(" ; ") if x != REDACTED]

        if any(p in publics for p in pieces("requerant", "maitre_ouvrage")):
            cats.append("public")
        cats = sorted(set(cats))
        if not cats:
            continue
        companies = [x for x in pieces("requerant", "maitre_ouvrage") if x in (r.get("entreprises_citees") or [])]
        out.append({"id": r["id"], "date_publication": r.get("date_publication"), "commune": r.get("commune"),
                    "langue": r.get("langue"), "titre": r.get("titre"), "categories": cats,
                    "requerants_entreprises": companies, "organismes_publics": publics,
                    "auteurs_plans_entreprises": [x for x in pieces("auteur_plans_entreprise", "auteur_plans")
                                                  if x in (r.get("entreprises_citees") or [])],
                    "url": r.get("url"), "contenu_allemand_a_importer": r.get("contenu_allemand_a_importer")})
    return sorted(out, key=lambda x: (x["date_publication"] or "", x["id"]))


# communes of the Martigny agency's catchment (Bas-Valais central), for the demo section of the radar note
MARTIGNY_REGION = frozenset({
    "Martigny", "Martigny-Combe", "Bovernier", "Trient", "Fully", "Saxon", "Saillon", "Leytron", "Riddes", "Isérables",
    "Chamoson", "Ardon", "Vétroz", "Conthey", "Charrat", "Val de Bagnes", "Sembrancher", "Orsières", "Liddes",
    "Bourg-Saint-Pierre", "Salvan", "Finhaut", "Vernayaz", "Evionnaz", "Dorénaz", "Collonges", "Saint-Maurice",
    "Mex", "Vérossaz", "Massongex"})
_TYPES = {"logements_collectifs": "logements collectifs", "halle": "halle / atelier", "public": "projet public"}


def radar_markdown(projects: list[dict[str, Any]], rows: list[dict[str, Any]]) -> str:
    """The radar note (docs/radar/…), generated from ``projects`` — no hand-written number."""
    acc = [r for r in rows if r["statut"] == "acceptée"]
    dates = sorted(r["date_publication"][:10] for r in acc if r.get("date_publication"))
    period = f"{_fr_date(dates[0])} au {_fr_date(dates[-1])}" if dates else "?"
    cats = Counter(c for p in projects for c in p["categories"])
    langs = Counter(r["langue"] for r in acc)
    complete_de = sum(r["langue"] == "de" and bool(r.get("contenu_complet")) for r in acc)
    with_company = sum(bool(p["requerants_entreprises"]) for p in projects)

    def table(ps: list[dict[str, Any]]) -> str:
        head = ("| Date | Commune | Type | Titre (masqué) | Requérant entreprise ou organisme public | Lien |\n"
                "|---|---|---|---|---|---|\n")
        def row(p: dict[str, Any]) -> str:
            who = p["requerants_entreprises"] + [x for x in p["organismes_publics"]
                                                 if x not in p["requerants_entreprises"]]
            cells = [_fr_date((p["date_publication"] or "")[:10]), p["commune"] or "commission cantonale",
                     " + ".join(_TYPES[c] for c in p["categories"]), (p["titre"] or "")[:90], ", ".join(who),
                     f"[BO]({p['url']})"]
            return "| " + " | ".join(c.replace("|", "/") for c in cells) + " |"

        return head + "\n".join(row(p) for p in ps)

    named = [p for p in projects if p["requerants_entreprises"] or p["organismes_publics"]]
    region = [p for p in named if p["commune"] in MARTIGNY_REGION]
    return f"""# Projets du Bulletin officiel qui comptent pour le radar (août–septembre 2026)

Données **RÉELLES** : {len(acc)} demandes d'autorisation de construire du Bulletin officiel du Valais
({langs['fr']} en français, {langs['de']} en allemand dont {complete_de} au contenu complet), publiées du {period},
importées depuis les PDF exportés par Hiba et reliées à l'index du portail (`proxsis import-bo-pdf`, rapports :
`data/manuel/import_pdf/RAPPORT_IMPORT.md` et `RAPPORT_IMPORT_DE.md`). *Seule la publication officielle fait foi.*

Toute personne physique est masquée (requérant, propriétaire, maître d'ouvrage, auteur des plans, titre), selon une
règle prudente : un mot de titre qui pourrait être un nom est masqué. Les entreprises et les organismes publics
restent nommés.

Commande : `proxsis projets-radar` → `data/manuel/import_pdf/projets_radar.json` et cette page.

## Ce qui est retenu

Projets qui annoncent un besoin de main-d'œuvre de chantier au-delà d'une maison individuelle :

- **logements collectifs** (immeubles, logements, appartements, Mehrfamilienhaus, Wohnungen) :
  {cats['logements_collectifs']} ;
- **halles, ateliers, entrepôts** (Halle, Lager, Werkstatt, industriel, artisanal) : {cats['halle']} ;
- **projets publics** (école, EMS, crèche, ou requérant public) : {cats['public']}.

Total : **{len(projects)} projets**, dont **{with_company}** avec un requérant entreprise.

Le tri se fait sur des mots du titre : c'est un repérage, pas une classification vérifiée.

## Pour la démo « Lundi 8 h à Martigny » : région de Martigny et Bas-Valais central

{table(region)}

## Tous les projets avec un requérant entreprise ou public

{table(named)}

## Limites

- Fenêtre courte (8 semaines) : ces permis ne peuvent pas encore entrer dans le classement backtesté. Il faudrait au
  moins 8 semaines de marchés simap après la fenêtre, ou des exports plus anciens. Ils s'affichent comme **signaux de
  contexte** dans la fiche entreprise et la liste d'appels (demandes publiées dans la commune de l'entreprise,
  entreprise citée comme requérante ou auteure des plans).
- Un requérant entreprise n'est pas forcément l'entreprise de construction : promoteur, gérance ou bureau
  d'architectes. C'est au consultant de le qualifier.
- Le masquage prudent des titres peut cacher un nom de lieu-dit ou un mot rare : le lien vers la publication
  officielle donne le titre complet.
"""


def _fr_date(d: str) -> str:
    return f"{d[8:10]}.{d[5:7]}.{d[0:4]}" if len(d) >= 10 else d


def freeze_draw(items: list[dict[str, Any]], target: Path) -> str:
    """Public record of a draw BEFORE any annotation: ids, links and hashes of the filtered texts (no text).
    Returns the sha256 of the file, to be written in data/annotations/FROZEN.md."""
    lines = [{"id": it["id"], "lang": it["lang"], "source_url": it["source_url"], "sha256_texte": text_sha(it["text"])}
             for it in items]
    content = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lines)
    target.write_text(content, "utf-8")
    return text_sha(content)


def annotation_items(rows: list[dict[str, Any]], ids: list[str], private_dir: Path) -> list[dict[str, Any]]:
    """Items for the annotation page (texts read from the private, already filtered files)."""
    by_id = {r["id"]: r for r in rows}
    items = []
    for i in ids:
        r = by_id[i]
        text = (private_dir / "textes" / f"{i}.txt").read_text("utf-8")
        items.append({"id": f"bo_vs:{i}", "lang": r["langue"], "doc_type_indicatif": "permis_construire",
                      "strate": f"bo_vs/{r['langue']}", "collecteur": "import_pdf", "order_type": "BA-VS05",
                      "publication_date": r["date_publication"], "text": text, "source_url": r["url"],
                      "mention_obligatoire": MENTION})
    return items
