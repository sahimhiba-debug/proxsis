"""Commands of the demonstration: the fictional world, the backtest suite, the exports read by the web app and the
presentation, the daily update and « Cette semaine, en direct de simap ».
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

from proxsis.commands.io import load_simap, permits, read_jsonl, read_places


def cmd_world(args: argparse.Namespace) -> int:
    from proxsis.synth.store import save_world
    from proxsis.synth.world import WorldConfig, generate_world

    w = generate_world(WorldConfig(seed=args.seed, n_companies=args.companies))
    path = save_world(w, Path(args.out))
    print(f"Monde FICTIF écrit dans {path}")
    return 0


def cmd_backtest(args: argparse.Namespace) -> int:
    from proxsis.suite import run_suite, write_outputs

    res = run_suite(seed=args.seed, quick=args.quick)
    write_outputs(res, Path(args.out_json), Path(args.out_md))
    print(f"Résultats : {args.out_json} ; rapport : {args.out_md}")
    return 0


def cmd_export_demo(args: argparse.Namespace) -> int:
    """Demo data for apps/web: real companies and needs, FICTIONAL Flexsis side, both checks before writing."""
    from datetime import date

    import pandas as pd

    from proxsis.demo_export import export_demo
    from proxsis.llm.base import chosen_provider

    cands = pd.read_csv(args.candidats, dtype={"fin_mission": "string"})
    cands["fin_mission"] = cands["fin_mission"].map(lambda v: v if isinstance(v, str) else None)
    bt = json.loads(Path(args.backtest_json).read_text("utf-8")) if Path(args.backtest_json).exists() else None
    provider = chosen_provider()  # the deterministic text model unless PROXSIS_LLM_PROVIDER=apertus
    frozen_path = Path(args.liste_gelee) if args.liste_gelee else None
    frozen = json.loads(frozen_path.read_text("utf-8")) if frozen_path and frozen_path.exists() else None
    written = export_demo(Path(args.out), records=load_simap(args.fichiers), as_of=date.fromisoformat(args.date),
                          places=read_places(args.localites), candidates=cands, claims_md=Path(args.claims),
                          seed=args.seed, provider=provider, backtest=bt, permits=permits(args.permis), frozen=frozen)
    print(f"Export démo ({len(written)} fichiers) → {args.out} ; rédaction : "
          f"{'Apertus' if provider else 'modèle de texte (faux fournisseur)'}")
    return 0


def cmd_model_reports(args: argparse.Namespace) -> int:
    from proxsis.model_reports import write_all

    for path in write_all(Path(args.out), seed=args.seed):
        print(f"écrit : {path}")
    return 0


def update_window(until_arg: str | None, days: int, now: datetime) -> tuple[date, date]:
    """The days the daily update reads: up to ``--until``, or by default up to the day before in Zurich (suite 10, § 2:
    never a publication of the day itself), and ``days`` days before it."""
    from datetime import timedelta
    from zoneinfo import ZoneInfo

    yesterday = now.astimezone(ZoneInfo("Europe/Zurich")).date() - timedelta(days=1)
    until = date.fromisoformat(until_arg) if until_arg else yesterday
    return until - timedelta(days=days), until


def cmd_update(args: argparse.Namespace) -> int:
    """Daily update of the public sources (online), or replay from the cache (--offline)."""
    import os
    from datetime import UTC

    from proxsis.connectors.simap import SimapConnector
    from proxsis.http import HttpCache, OfflineCacheMiss, PoliteClient
    from proxsis.ingest import ingest

    since, until = update_window(args.until, args.days, datetime.now(UTC))
    offline = args.offline or os.environ.get("PROXSIS_OFFLINE") == "1"
    client = PoliteClient(
        HttpCache(Path(args.cache)),
        offline=offline,
        user_agent=os.environ.get("PROXSIS_USER_AGENT", "Proxsis/0.1"),
        min_interval_s=SimapConnector.min_interval_s,  # audit m5: the connector's pace, not the 1 s default
    )
    cantons = tuple(args.cantons.split(","))
    records = []
    failed: list[str] = []
    # FOSC / Bulletin officiel: consulted by a person only (Hiba, 05.10.2026); http.MANUAL_ONLY_HOSTS blocks them.
    for conn in (SimapConnector(cantons=cantons),):
        try:
            got = conn.fetch(client, since, until)
            print(f"{conn.name}: {len(got)} enregistrements")
            records.extend(got)
        except OfflineCacheMiss as e:
            print(f"{conn.name}: absent du cache hors ligne ({e})")
            failed.append(conn.name)
        except Exception as e:  # network denied, schema change...: reported, and the update fails
            print(f"{conn.name}: ÉCHEC — {type(e).__name__}: {e}")
            failed.append(conn.name)
    if failed:  # a day that was not read is not written as an empty day
        print(f"mise à jour non faite, source(s) en échec : {', '.join(failed)} ; rien n'est écrit")
        return 1
    signals, companies, log = ingest(records)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    signals.to_csv(out / f"signals_{until}.csv", index=False)
    companies.to_csv(out / f"companies_{until}.csv", index=False)
    (out / f"journal_{until}.txt").write_text("\n".join(log), "utf-8")
    print(f"{len(signals)} signaux, {len(companies)} entreprises nouvelles -> {out}")
    return 0


def cmd_export_presentation(args: argparse.Namespace) -> int:
    """Data of the « Votre prochain lundi » presentation: counts per commune and week, no text."""
    from datetime import date

    from proxsis.presentation_export import presentation_data

    rows = read_jsonl(args.publications)
    curated = json.loads(Path(args.dossiers).read_text("utf-8")) if Path(args.dossiers).exists() else {}
    urls = [d["annonce_url"] for d in curated.get("dossiers", {}).values()]
    data = presentation_data(rows, read_places(args.localites), date.fromisoformat(args.date),
                             awards=read_jsonl(args.marches) if args.marches else None, examples=urls)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1, allow_nan=False) + "\n", "utf-8")
    t = data["territoire"]
    m = data["marches"]
    print(f"{t['total_publications']} publications, {t['n_communes']} communes, hors carte {t['hors_carte']}, "
          f"période {t['periode']} ; marchés publics {m['total']} (hors carte {m['hors_carte']}) → {out}")
    return 0


def cmd_presentation_stories(args: argparse.Namespace) -> int:
    """Act 4: three dated stories replayed « at date T » + the measurement screen (CLAIMS REEL-T0). Tender dates come
    from the simap API only (``--en-ligne``: two calls per award, nothing raw stored), then from the saved file."""
    from datetime import UTC, date, datetime

    from proxsis.demo_export import parse_claims, pii_sweep
    from proxsis.presentation_stories import STORIES, presentation_stories

    records = load_simap(args.fichiers)
    tpath = Path(args.appels_offres)
    if args.en_ligne:
        from proxsis.connectors import simap
        from proxsis.http import HttpCache, PoliteClient
        from proxsis.netcheck import USER_AGENT
        from proxsis.presentation_stories import fetch_tenders

        wanted = {n for s in STORIES for n in (s.pivot, *s.open_tenders)}
        recs = sorted((r for r in records if r["publication_number"] in wanted and r.get("process_type") != "direct"),
                      key=lambda r: r["publication_number"])
        client = PoliteClient(HttpCache(Path(".cache/nocache")), offline=False, user_agent=USER_AGENT,
                              min_interval_s=args.interval)
        try:
            tenders = fetch_tenders(client, recs)
        finally:
            client.close()
        calls = [simap.past_publications_url(r["publication_id"]) for r in recs]
        calls += [t["url_api"] for t in tenders.values() if t]
        doc = {"source": "simap.ch (API, CG du 30.09.2023)", "mention_obligatoire": simap.MANDATORY_NOTICE,
               "consulte_le": datetime.now(UTC).date().isoformat(), "requetes_api": calls,
               "robots_txt": "https://www.simap.ch/robots.txt", "appels_offres": tenders}
        hits = pii_sweep(doc)
        if hits:
            raise SystemExit(f"balayage : {len(hits)} cas, rien n'est écrit")
        tpath.parent.mkdir(parents=True, exist_ok=True)
        tpath.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", "utf-8")
        print(f"{len(calls)} requêtes API simap (+ robots.txt) → {tpath}")
    tenders = json.loads(tpath.read_text("utf-8"))["appels_offres"]
    data = presentation_stories(records, tenders, read_jsonl(args.publications),
                                json.loads(Path(args.reel_t0).read_text("utf-8")), parse_claims(Path(args.claims)),
                                prepared=date.fromisoformat(args.date), data_end=date.fromisoformat(args.data_end))
    hits = pii_sweep(data)
    if hits:
        raise SystemExit(f"balayage : {len(hits)} cas, rien n'est écrit")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1, allow_nan=False) + "\n", "utf-8")
    for s in data["histoires"]:
        iv = " ; ".join(f"{i['code']} {i['debut']} → {i['fin']} = {i['jours']} j" for i in s["intervalles"])
        print(f"{s['id']} ({s['type']}, T = {s['date_T']}) : {iv}")
    return 0


def cmd_presentation_mondays(args: argparse.Namespace) -> int:
    """Act 4, « Choisissez une date »: the ten companies of the simple rule on every Monday of the measure REEL-SPEC-BAT
    and what they obtained in the 8 following weeks (offline file; refuses to differ from the measure)."""
    from datetime import date

    from proxsis.call_list import lot_table
    from proxsis.date_choice import CLAIMS_ID, build
    from proxsis.demo_export import parse_claims, pii_sweep

    measure = json.loads(Path(args.mesure).read_text("utf-8"))["specialites"]["batiment"]
    data = build(lot_table(load_simap(args.fichiers)), measure, parse_claims(Path(args.claims))[CLAIMS_ID],
                 data_end=date.fromisoformat(args.data_end))
    hits = pii_sweep(data)
    if hits:
        raise SystemExit(f"balayage : {len(hits)} cas, rien n'est écrit")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1, allow_nan=False) + "\n", "utf-8")
    low = min(data["lundis"], key=lambda m: (m["obtenu"], m["lundi"]))
    print(f"{len(data['lundis'])} lundis ({data['choix']['nombre']} au choix, {data['choix']['premier']} → "
          f"{data['choix']['dernier']}) ; moyenne {data['mesure']['affiche']['regle']['fr']}, hasard "
          f"{data['mesure']['affiche']['hasard']['fr']} ; le plus bas : {low['lundi']}, {low['obtenu']} sur 10 → {out}")
    offered = data["au_choix"]
    print(f"sur les {offered['semaines']} lundis au choix ({offered['premiere']} → {offered['derniere']}) : "
          f"{offered['affiche']['regle']['fr']} ({offered['obtenu']} sur {offered['sur']}), hasard "
          f"{offered['affiche']['hasard']['fr']}")
    return 0


def cmd_presentation_territory(args: argparse.Namespace) -> int:
    """Visit, time 1: the communes of the map and, in each, the companies active in our data (seat here / contract
    here), only those whose dossier passes every check; the others listed with their reasons."""
    from datetime import date

    from proxsis.call_list import lot_table
    from proxsis.demo_export import pii_sweep
    from proxsis.territory import Localities, build

    web = Path(args.web)
    curated = json.loads((web / "presentation" / "dossiers.json").read_text("utf-8"))
    contours = json.loads((web / "presentation" / "communes_vs.json").read_text("utf-8"))
    communes = {int(c["bfs"]): str(c["nom"]) for c in contours["communes"]}
    data = build(json.loads((web / "demo" / "entreprises.json").read_text("utf-8")),
                 json.loads((web / "demo" / "appels.json").read_text("utf-8")),
                 lot_table(load_simap(args.fichiers)), Localities.read(Path(args.localites), communes),
                 as_of=date.fromisoformat(curated["rejeu"]), guided=curated["guides"],
                 example=(args.exemple_commune, curated["guides"][0]),
                 mention=json.loads((web / "demo" / "meta.json").read_text("utf-8"))["mention_simap"])
    hits = pii_sweep(data)
    if hits:
        raise SystemExit(f"balayage : {len(hits)} cas, rien n'est écrit")
    out = Path(args.out)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1, allow_nan=False) + "\n", "utf-8")
    print(f"{len(data['entreprises'])} entreprises sur la carte, {len(data['exclues'])} écartées "
          f"({', '.join(e['nom'] + ' : ' + '/'.join(e['controles_echoues']) for e in data['exclues'])}) ; "
          f"{len(data['communes'])} communes → {out}")
    return 0


def cmd_presentation_next_monday(args: argparse.Namespace) -> int:
    """Visit, time 2: the list of the following Monday by the same rule, and the publications between the two
    Mondays."""
    from datetime import date

    from proxsis.demo_export import pii_sweep
    from proxsis.next_monday import next_monday

    curated = json.loads(Path(args.dossiers).read_text("utf-8"))
    data = next_monday(load_simap(args.fichiers), date.fromisoformat(curated["rejeu"]), curated["dix"],
                       data_end=date.fromisoformat(args.data_end))
    hits = pii_sweep(data)
    if hits:
        raise SystemExit(f"balayage : {len(hits)} cas, rien n'est écrit")
    out = Path(args.out)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1, allow_nan=False) + "\n", "utf-8")
    print(f"lundi {data['lundi']} : {len(data['classement'])} entreprises classées, "
          f"{len(data['nouvelles_publications'])} nouvelles publications depuis le {data['premier']} → {out}")
    return 0


def cmd_presentation_moments(args: argparse.Namespace) -> int:
    """Visit, the moments of the brief of 07.10.2026 (§ 3.2 to 3.4): three small files, each checked against its CLAIMS
    line and swept for personal data before anything is written (nothing is written when one check fails)."""
    from proxsis.demo_export import parse_claims, pii_sweep
    from proxsis.visit_moments import WEEK_CLAIMS, accelerating, guided_facts, week_counts

    claims = parse_claims(Path(args.claims))
    frozen = json.loads(Path(args.liste).read_text("utf-8"))
    bo_rows = read_jsonl(args.permis)
    files = {
        "cette_semaine.json": week_counts(load_simap(args.fichiers), bo_rows, frozen,
                                          data_end=date.fromisoformat(args.data_end), line=claims[WEEK_CLAIMS],
                                          prepared=args.date),
        "accelerent.json": accelerating(json.loads(Path(args.mesure).read_text("utf-8")), claims, prepared=args.date),
        "faits.json": guided_facts(frozen, bo_rows, claims, prepared=args.date),
    }
    hits = [h for data in files.values() for h in pii_sweep(data)]
    if hits:
        raise SystemExit(f"balayage : {len(hits)} cas, rien n'est écrit")
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=1, allow_nan=False) + "\n", "utf-8")
    week, surge = files["cette_semaine.json"], files["accelerent.json"]
    print(f"cette semaine ({week['semaine']['du']} → {week['semaine']['au']}) : {week['lues']['total']} publications "
          f"lues, {week['retenues']['total']} retenues, {week['appels']} appels")
    print(f"celles qui accélèrent : {surge['accelerent']['affiche']['fr']} ({surge['accelerent']['cas']} cas) contre "
          f"{surge['hors_des_dix']['affiche']['fr']} hors des dix")
    for cid, dossier in files["faits.json"]["dossiers"].items():
        print(f"{dossier['claims']} ({cid}) : {len(dossier['faits'])} faits datés")
    print(f"→ {out}")
    return 0


def cmd_live_week(args: argparse.Namespace) -> int:
    """« Chaque matin, en direct de simap » : the Valais construction awards published on the day before (on Monday,
    during the week that ended), filtered before any write, checked, then written for the web section (exit 1 and
    nothing written when a check fails; exit 2 when simap could not be read or the day is not a working day)."""
    import tempfile
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from proxsis.connectors import simap
    from proxsis.http import HttpCache, PoliteClient
    from proxsis.live_week import build_live, frozen_projects, reading_period, update_corrections, write_if_valid
    from proxsis.netcheck import USER_AGENT

    # the automatic job runs every working day from 6 a.m. in Zurich; by hand, --jour replays a given day
    day = date.fromisoformat(args.jour) if args.jour else datetime.now(ZoneInfo("Europe/Zurich")).date()
    try:
        mode, start, end = reading_period(day)
    except ValueError as e:
        print(f"Pas de lecture : {e}")
        return 2
    if args.rejeu:
        records = read_jsonl(args.rejeu)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "matin.jsonl"
            client = PoliteClient(HttpCache(Path(tmp) / ".nocache"), offline=False, user_agent=USER_AGENT,
                                  min_interval_s=args.interval)
            try:
                # the awards of the period (a corrected award among them is a correction), then its revocations and
                # abandonments (passed on too)
                for kinds in (("award_tender", "direct_award"), simap.WITHDRAWAL_TYPES):
                    simap.fetch_to_jsonl(client, out, lang="fr", pub_types=kinds, sub_types=("construction",),
                                         date_from=start.isoformat(), date_to=end.isoformat(),
                                         issued_by=(simap.VALAIS_ROOT,))
            except Exception as e:  # network, schema change: the previous file stays, the job reports it
                print(f"ÉCHEC de la lecture de simap : {type(e).__name__}: {e}")
                return 2
            records = read_jsonl(str(out)) if out.exists() else []
    data = build_live(records, day)
    corrections_out = Path(args.corrections)
    previous = json.loads(corrections_out.read_text("utf-8")) if corrections_out.exists() else None
    # the notices of the frozen data (application and presentation) that a correction of the period concerns
    figees = Path(args.figees)
    frozen = frozen_projects(sorted(figees.glob("demo/*.json")) + sorted(figees.glob("presentation/*.json")))
    corrections = update_corrections(previous, records, day, frozen)
    problems = write_if_valid(data, Path(args.out), corrections, corrections_out)
    if problems:
        print("Contrôles en échec, fichier NON écrit (la dernière version valide reste) :")
        print("\n".join(f"- {p}" for p in problems))
        return 1
    what = "semaine" if mode == "semaine" else "veille"
    print(f"Lecture du {day} ({what} : du {start} au {end}) : {data['total']} adjudications, "
          f"{len(data['rectifications'])} rectification(s) -> {args.out} ; avis figés rectifiés : "
          f"{len(corrections['avis'])} -> {args.corrections}")
    return 0


def cmd_frozen_mornings(args: argparse.Namespace) -> int:
    """« Choisissez une date » : the section « Chaque matin » of every Monday that can be chosen, frozen, with only what
    was published before that Monday (refused, nothing written, at the first failed check)."""
    from proxsis.demo_export import pii_sweep
    from proxsis.live_week import frozen_mornings

    mondays = json.loads(Path(args.lundis).read_text("utf-8"))["lundis"]
    records = [r for f in args.fichiers for r in read_jsonl(f)]
    data = frozen_mornings(records, mondays)
    hits = pii_sweep(data)
    if hits:
        raise SystemExit(f"balayage : {len(hits)} cas, rien n'est écrit")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1, allow_nan=False) + "\n", "utf-8")
    sizes = [m["total"] for m in data["lundis"].values()]
    print(f"{len(sizes)} lundis au choix ; adjudications de la semaine écoulée : de {min(sizes, default=0)} à "
          f"{max(sizes, default=0)} -> {out}")
    return 0


def cmd_source_map(args: argparse.Namespace) -> int:
    """La carte des sources (suite 10, § 3): the lines of data/catalogue.csv counted by group, for the page « Sources et
    mesures », the visit and the A4 page; refused, nothing written, when CLAIMS SOURCES-1 says other numbers."""
    import csv

    from proxsis.demo_export import parse_claims
    from proxsis.source_map import CLAIMS_ID, claim_matches, source_map

    with Path(args.catalogue).open(encoding="utf-8") as f:
        data = source_map(list(csv.DictReader(f)))
    claim = parse_claims(Path(args.claims)).get(CLAIMS_ID)
    if claim is None or not claim_matches(data, claim["valeur"]):
        raise SystemExit(f"la ligne {CLAIMS_ID} de CLAIMS.md ne dit pas les nombres du catalogue ; rien n'est écrit")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"{data['etudiees']} sources étudiées : {data['en_service']['nombre']} en service, "
          f"{data['demandes']['nombre']} couvertes par une demande d'accès envoyée, {data['ecartees']['nombre']} "
          f"écartées, {data['autres']['nombre']} autres ({data['autres']['conditions_a_verifier']} conditions à "
          f"vérifier, {data['autres']['sans_usage_pour_la_liste']} sans usage pour la liste) -> {out}")
    return 0
