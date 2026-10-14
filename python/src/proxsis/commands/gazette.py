"""Commands of the Bulletin officiel (official gazette of Valais): PDF import with the personal-data filter before any
write, probing, reproducible draws, projects that matter.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from proxsis.commands.io import read_jsonl


def cmd_remask_authorities(args: argparse.Namespace) -> int:
    """[audit semaine 1, B1] Apply the private-authority rule to simap files already collected (in place)."""
    import re

    from proxsis.pii import PRIVATE_PLACEHOLDER, authority_looks_private

    for f in args.fichiers:
        path = Path(f)
        if not path.exists():
            continue
        rows, n = [], 0
        for line in path.read_text("utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            a = r.get("contracting_authority")
            if a and a != PRIVATE_PLACEHOLDER:
                stripped = re.sub(r"\s*\([^)]*\)", "", str(a)).strip() or None
                if stripped and authority_looks_private(stripped):
                    stripped = PRIVATE_PLACEHOLDER
                if stripped != a:
                    r["contracting_authority"] = stripped
                    n += 1
            rows.append(json.dumps(r, ensure_ascii=False))
        path.write_text("\n".join(rows) + "\n", "utf-8")
        print(f"{path.name} : {n} adjudicateur(s) modifié(s) (parenthèses retirées ou masqué)")
    return 0


def cmd_import_bo_pdf(args: argparse.Namespace) -> int:
    """Import of Bulletin officiel PDF compositions linked to the bulk XML index (filter before any write)."""
    import csv

    from proxsis.gazette_filter import PersonalDataFound
    from proxsis.gazette_import import run_import

    pdfs = sorted(Path(p) for p in args.pdfs)
    places: list[str] = []
    if Path(args.localites).exists():
        with Path(args.localites).open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                places += [row["localite"], row["commune"]]
    try:
        rep = run_import(pdfs, Path(args.index), Path(args.public), Path(args.prive), suffix=args.suffixe,
                         localities=places, context_pdfs=sorted(Path(p) for p in args.contexte or []))
    except PersonalDataFound as e:  # ids, fields and reasons only: never a value
        print(e)
        for f in e.findings[:50]:
            print(" ", f["publication"], f["champ"], f["motif"])
        return 1
    keys = ("lues", "doublons", "uniques", "acceptees", "rejetees", "rejetees_par_motif", "par_langue",
            "contenu_allemand_a_importer", "masquages", "fusion")
    print({k: rep[k] for k in keys})
    print("index :", rep["index"], "; semaines :", rep["par_semaine"])
    print("communes (10 premières) :", dict(list(rep["par_commune"].items())[:10]))
    return 0


def cmd_probe_pdf(args: argparse.Namespace) -> int:
    """Masked skeleton of a PDF (template words only) to adapt the parser without reading the content."""
    from proxsis.gazette_pdf import extract_lines, skeleton

    lines = []
    for f in args.pdfs:
        lines += extract_lines(Path(f))
    print(skeleton(lines, min_count=args.seuil, max_lines=args.lignes))
    return 0


def cmd_draw_bo(args: argparse.Namespace) -> int:
    """Reproducible draw of the Bulletin officiel test set + private annotation items."""

    from proxsis.gazette_import import annotation_items, draw_test_set, freeze_draw

    rows = read_jsonl(str(Path(args.public) / "publications.jsonl"))
    d = draw_test_set(rows, n=args.n, lang=args.langue, seed=args.seed)
    out = Path(args.annotations)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"TIRAGE_{args.langue}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", "utf-8")
    if d["ids"]:
        items = annotation_items(rows, d["ids"], Path(args.prive))
        target = Path(args.prive) / f"items_{args.langue}.jsonl"
        target.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items), "utf-8")
        print(f"{len(items)} items d'annotation → {target} (hors git)")
        frozen = out / f"tirage_{args.langue}_gele.jsonl"
        print(f"gel : {frozen} sha256 {freeze_draw(items, frozen)} (à reporter dans data/annotations/FROZEN.md)")
    print({k: d[k] for k in ("langue", "n_demande", "cadre", "graine", "note")}, "tirés :", len(d["ids"]))
    return 0


def cmd_radar_projects(args: argparse.Namespace) -> int:
    """Projects that matter for the radar (multi-dwelling, halls, public) from the imported permits."""
    from collections import Counter

    from proxsis.gazette_import import radar_projects

    rows = read_jsonl(str(Path(args.public) / "publications.jsonl"))
    projects = radar_projects(rows)
    Path(args.out).write_text(json.dumps(projects, ensure_ascii=False, indent=1) + "\n", "utf-8")
    cats = Counter(c for p in projects for c in p["categories"])
    with_company = sum(bool(p["requerants_entreprises"]) for p in projects)
    print(f"{len(projects)} projets ; catégories {dict(cats)} ; avec requérant entreprise : {with_company}")
    if args.md:
        from proxsis.gazette_import import radar_markdown

        Path(args.md).write_text(radar_markdown(projects, rows), "utf-8")
        print("note :", args.md)
    return 0
