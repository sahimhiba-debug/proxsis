"""Commands of the data collection and annotation sessions (run on Hiba's Mac): simap draws and collection, manual
collection of official gazettes, double annotation, agreement, freeze, real backtests.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from proxsis.commands.io import load_simap, read_jsonl, workflow_items


def cmd_real_draw(args: argparse.Namespace) -> int:
    """[session Mac] Real test set v2: reproducible draw of simap awards (filtered before writing)."""
    from datetime import UTC, datetime

    from proxsis.connectors import simap
    from proxsis.http import HttpCache, PoliteClient
    from proxsis.netcheck import USER_AGENT
    from proxsis.real_testset import build_frame, draw, summary_from_frame, write_set

    out = Path(args.out)
    client = PoliteClient(HttpCache(out / ".nocache"), offline=False, user_agent=USER_AGENT, min_interval_s=2.0)
    subs = tuple(args.sub_types.split(","))
    if args.cadre:  # reuse a saved frame: no new search requests
        frame = [json.loads(x) for x in Path(args.cadre).read_text("utf-8").splitlines() if x.strip()]
    else:
        frame = build_frame(client, args.date_from, args.date_to, subs, max_pages=args.max_pages)
    print(f"cadre : {len(frame)} adjudications")

    def fetch(item: dict[str, Any]) -> dict[str, Any] | None:
        res = client.get(simap.detail_url(item["project_id"], item["publication_id"]), source=simap.SOURCE,
                         license=simap.LICENSE, store_raw=False)
        if res.status != 200:
            return None
        rec, _ = simap.normalize(summary_from_frame(item), res.json(), retrieved_at=datetime.now(UTC),
                                 raw_sha256=res.provenance.content_sha256 or "")
        return rec

    kept, log = draw(frame, fetch, {"fr": args.n_fr, "de": args.n_de}, seed=args.seed)
    write_set(out, kept, log, frame, {"source": "simap.ch (API, CG du 30.09.2023)", "periode": [args.date_from,
              args.date_to], "types_marche": list(subs), "types_publication": ["award_tender", "direct_award"],
              "graine": args.seed, "quotas": {"fr": args.n_fr, "de": args.n_de},
              "methode": "cadre complet trié par (date, id) ; partition par canton d'exécution (proxy FR / DE) ; "
                         "permutation aléatoire de chaque partie (numpy default_rng(graine)) ; lecture des "
                         "détails dans cet ordre, chaque partie jusqu'à ce que le quota de sa langue soit "
                         "plein, puis second passage si un quota reste ouvert ; retenu si langue de création "
                         "fr/de, lauréat nommé et quota non atteint"})
    print(f"retenus : {len(kept)} (journal : {len(log)} détails lus) -> {out}")
    return 0


def cmd_annotation_page(args: argparse.Namespace) -> int:
    """[session Mac] Self-contained annotation page."""
    from proxsis.annotation_page import write_page

    n = write_page(Path(args.items), Path(args.out), title=args.title, profile=args.profil)
    print(f"page d'annotation ({n} publications) : {args.out}")
    return 0


def cmd_collect_simap(args: argparse.Namespace) -> int:
    """[session Mac] Resumable collection of filtered simap awards (nothing raw is stored)."""
    from proxsis.connectors import simap
    from proxsis.http import HttpCache, PoliteClient
    from proxsis.netcheck import USER_AGENT

    out = Path(args.out)
    client = PoliteClient(HttpCache(out.parent / ".nocache"), offline=False, user_agent=USER_AGENT,
                          min_interval_s=args.interval)
    cantons = tuple(c for c in args.cantons.split(",") if c)
    try:
        n = simap.fetch_to_jsonl(client, out, lang="fr", pub_types=("award_tender", "direct_award"),
                                 sub_types=tuple(args.sub_types.split(",")), date_from=args.date_from,
                                 date_to=args.date_to, cantons=cantons, max_pages=args.max_pages,
                                 issued_by=tuple(o for o in args.emetteurs.split(",") if o))
    except simap.SimapIncomplete as e:  # what was read is written; the collection is not complete
        print(f"collecte incomplète : {e} -> {out}")
        return 1
    print(f"{n} nouvelles adjudications filtrées -> {out}")
    return 0


def cmd_real_backtest(args: argparse.Namespace) -> int:
    """[session Mac] Backtest on public data only, target T0 (new public award within 8 weeks)."""

    from proxsis.real_backtest import evaluate_t0, events_from_records

    recs = [r for f in args.records for r in read_jsonl(f)]
    ev = events_from_records(recs)
    if args.etendu:  # « surprise » (pic) target + combined model, trained only on labels known at T
        from proxsis.real_backtest import evaluate_extended

        rep = evaluate_extended(ev, date.fromisoformat(args.first_week), date.fromisoformat(args.last_week),
                                train_from=date.fromisoformat(args.train_from), k=args.k,
                                data_end=date.fromisoformat(args.data_end), seed=args.seed)
    else:
        rep = evaluate_t0(ev, date.fromisoformat(args.first_week), date.fromisoformat(args.last_week), k=args.k,
                          data_end=date.fromisoformat(args.data_end), seed=args.seed)
    rep["donnees"] = {"fichiers": args.records, "adjudications": len(recs), "evenements_entreprise": len(ev),
                      "entreprises": int(ev["company"].nunique()), "fin_des_donnees": args.data_end}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(json.dumps(rep.get("p_at_k") or {t: r["p_at_k"] for t, r in rep["cibles"].items()}, ensure_ascii=False))
    return 0


def cmd_compare_extraction(args: argparse.Namespace) -> int:
    """[session Mac] Rules vs Apertus on the FROZEN real set (refuses an unfrozen set)."""
    from proxsis.compare_extractors import compare
    from proxsis.llm.base import apertus_provider
    from proxsis.models.m3_extraction import LLMExtractor, RulesExtractor

    extractors: list[Any] = [RulesExtractor()]
    if args.apertus:  # asked for on the command line: the provider is passed, the environment is not changed
        provider = apertus_provider()
        if provider is None:
            print("Clé Public AI absente (PUBLICAI_API_KEY ou trousseau proxsis-publicai) : Apertus non évalué.")
            return 2
        extractors.append(LLMExtractor(provider))
    donnees = "RÉEL"  # overridden by compare() when FROZEN.md registers the set as FICTIF
    rel = json.loads(Path(args.accord).read_text("utf-8"))["fiabilite"] if args.accord else None
    rep = compare(Path(args.jeu), Path(args.frozen_md), extractors, donnees=donnees, reliability=rel)
    Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", "utf-8")
    for name, r in rep["extracteurs"].items():
        print(name, {k: round(v, 3) for k, v in r["field_accuracy"].items()}, "fuites", r["pii_leaks"])
    return 0


def cmd_manual_collection(args: argparse.Namespace) -> int:
    """[session Mac] Local page to paste BO VS / FOSC publications read by a person (filter before saving)."""
    from proxsis.manual_collection import serve

    serve(Path(args.dossier), port=args.port)
    return 0


def cmd_manual_status(args: argparse.Namespace) -> int:

    from proxsis.manual_collection import status

    print(json.dumps(status(Path(args.dossier)), ensure_ascii=False, indent=1))
    return 0


def cmd_collection_plan(args: argparse.Namespace) -> int:
    from proxsis.manual_collection import collection_plan

    for r in collection_plan(seed=args.seed):
        print(f"{r['personne']} | {r['strate']} | {r['quota']} | jours : {', '.join(r['jours'])} | "
              f"réserve : {', '.join(r['reserve'])}")
    return 0


def cmd_prepare_annotation(args: argparse.Namespace) -> int:
    """[session Mac] Assignment (blind double annotation) + one private page per annotator."""
    from proxsis.annotation_workflow import prepare

    items = workflow_items(args)
    rep = prepare(items, args.annotateurs.split(","), Path(args.public), Path(args.prive), n_double=args.double,
                  seed=args.seed, profile=args.profil)
    print(f"{len(rep)} publications réparties ; {sum(bool(a['second']) for a in rep.values())} en double annotation ;"
          f" profil {args.profil} ; pages dans {Path(args.prive) / 'pages'} (hors git)")
    return 0


def cmd_manual_agreement(args: argparse.Namespace) -> int:
    from proxsis.annotation_workflow import agreement_step

    rep = agreement_step([Path(x) for x in args.exports], Path(args.public) / "repartition.json",
                         workflow_items(args), Path(args.public), Path(args.prive))
    print(f"{rep['n_commun']} publications en double annotation ; {rep['n_desaccords']} désaccords ; "
          f"accord : {Path(args.public) / 'accord.json'}")
    return 0


def cmd_manual_freeze(args: argparse.Namespace) -> int:
    from proxsis.annotation_workflow import freeze_step

    out = freeze_step([Path(x) for x in args.exports], Path(args.public) / "repartition.json", workflow_items(args),
                      Path(args.arbitrage) if args.arbitrage else None, Path(args.public), Path(args.prive),
                      Path(args.frozen_md), args.nom)
    print(f"gelé : {out['n']} publications ; public {out['public']} ; privé {out['prive']} (sha256 {out['sha_prive']})")
    return 0


def cmd_m6_real(args: argparse.Namespace) -> int:
    """[session Mac] M6 on real public series (KOF, FSO vacancies, MeteoSwiss, simap volumes)."""

    from proxsis.http import HttpCache, PoliteClient
    from proxsis.m6_real import run_all
    from proxsis.netcheck import USER_AGENT

    client = PoliteClient(HttpCache("/tmp/proxsis-nocache"), offline=False, user_agent=USER_AGENT, min_interval_s=2.0)
    rep = run_all(client, args.simap, args.series)
    Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", "utf-8")
    for k, v in rep.items():
        if isinstance(v, dict) and "wape" in v:
            print(k, {m: round(x, 4) for m, x in v["wape"].items()}, v["boosting_moins_meilleure_naive"])
    return 0


def cmd_simap_overview(args: argparse.Namespace) -> int:
    """[session Mac] Task 2: overview of the collected simap awards."""
    import csv

    from proxsis.simap_overview import overview

    with open(args.lieux, encoding="utf-8") as fh:
        places = {row["nom"] for row in csv.DictReader(fh)}
    rep = overview(read_jsonl(args.romandie), read_jsonl(args.emetteur_vs), places, sample=20, seed=args.seed)
    rep["sources"] = {"romandie": args.romandie, "emetteur_vs": args.emetteur_vs, "lieux": args.lieux}
    Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(json.dumps({k: rep[k] for k in ("n_adjudications", "periode", "valais")}, ensure_ascii=False))
    return 0


def cmd_phasing(args: argparse.Namespace) -> int:
    """[session Mac] Task 3: real lags between phases, validation on recent chantiers, example of needs."""

    from proxsis import phasing as ph

    ch = ph.group_chantiers(load_simap(args.fichiers))
    rep = {"donnees": "RÉEL (simap, adjudications de construction)", "chantiers": len(ch),
           "chantiers_2_lots_ou_plus": sum(len(c["lots"]) >= 2 for c in ch),
           "delais": ph.measure_lags(ch, n_boot=2000, seed=0),
           "validation": [ph.validate(ch, date.fromisoformat(c)) for c in args.coupures]}
    model = ph.PhasingModel.fit(ch)
    rep["hypotheses"] = model.assumptions
    ex = model.needs(anchor=date(2026, 10, 5), amount_chf=None)
    rep["exemple_besoins_sans_montant"] = ex.assign(semaine=ex["semaine"].astype(str)).round(2).to_dict("records")
    Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n", "utf-8")
    print(json.dumps(rep["validation"], ensure_ascii=False)[:600])
    return 0


def cmd_m4_real(args: argparse.Namespace) -> int:
    """[session Mac] Task 8: name variants of real laureates and 50 doubtful pairs for a human check."""
    import csv

    from proxsis.real_entities import doubtful_pairs, vendor_table

    t = vendor_table(load_simap(args.fichiers))
    pairs = doubtful_pairs(t, low=80, high=93, n=50)
    with open(args.out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[*pairs[0].keys(), "decision_hiba"] if pairs else ["vide"])
        w.writeheader()
        for p in pairs:
            w.writerow(p | {"decision_hiba": ""})
    rep = {"noms_normalises": len(t), "cles_a_plusieurs_variantes": int((t["variantes"] >= 2).sum()),
           "avec_ide": int((t["ide"] != "").sum()), "paires_douteuses": len(pairs),
           "lignes_laureats": int(t["adjudications"].sum())}
    Path(args.out_json).write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(json.dumps(rep, ensure_ascii=False))
    return 0
