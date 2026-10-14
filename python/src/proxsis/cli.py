"""Command-line interface: ``proxsis <command>``. The parser lives here; the handlers in proxsis.commands."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from proxsis.commands.collection import (
    cmd_annotation_page,
    cmd_collect_simap,
    cmd_collection_plan,
    cmd_compare_extraction,
    cmd_m4_real,
    cmd_m6_real,
    cmd_manual_agreement,
    cmd_manual_collection,
    cmd_manual_freeze,
    cmd_manual_status,
    cmd_phasing,
    cmd_prepare_annotation,
    cmd_real_backtest,
    cmd_real_draw,
    cmd_simap_overview,
)
from proxsis.commands.demo import (
    cmd_backtest,
    cmd_export_demo,
    cmd_export_presentation,
    cmd_frozen_mornings,
    cmd_live_week,
    cmd_model_reports,
    cmd_presentation_moments,
    cmd_presentation_mondays,
    cmd_presentation_next_monday,
    cmd_presentation_stories,
    cmd_presentation_territory,
    cmd_source_map,
    cmd_update,
    cmd_world,
)
from proxsis.commands.gazette import (
    cmd_draw_bo,
    cmd_import_bo_pdf,
    cmd_probe_pdf,
    cmd_radar_projects,
    cmd_remask_authorities,
)
from proxsis.commands.week1 import (
    cmd_call_list,
    cmd_candidates,
    cmd_commune_boundaries,
    cmd_docs_week1,
    cmd_integrate_validation,
    cmd_localities,
    cmd_specialty_backtest,
    cmd_week1_engine,
)

# Default paths are anchored to the repository, so that a command gives the same result from any working directory
# (they used to be relative to python/; run from the root, a command wrote outside the repository; review 1, B2).
# A path typed on the command line stays relative to the current directory, as usual.
ROOT = Path(__file__).resolve().parents[3]


def repo(relative: str) -> str:
    """A default path, from the root of the repository."""
    return str(ROOT / relative)

SUPPLY_FILE = repo("data/reel/simap/adjudications_romandie_fournitures_2024-07_2026-09.jsonl")
SIMAP_FILES = [repo("data/reel/simap/adjudications_romandie_construction_2024-07_2026-09.jsonl"),
               repo("data/reel/simap/adjudications_emetteur_vs_construction_2024-07_2026-09.jsonl")]

# Versioned copy (swisstopo OGD, free reuse with the source): the fictional pool and the audit depend on it
# (audit of week 1, M10). Refresh with `proxsis localites --out ../data/referentiels/localites_vs.csv`.
LOCALITES_CSV = repo("data/referentiels/localites_vs.csv")
PERMITS_JSONL = repo("data/manuel/import_pdf/publications.jsonl")

STORY_TENDERS = repo("data/terrain/appels_offres_histoires.json")


def build_parser() -> argparse.ArgumentParser:
    """The 40 commands and their options (each handled by a function of proxsis.commands)."""
    from proxsis.annotation_agreement import DEFAULT_PROFILE, PROFILES

    p = argparse.ArgumentParser(prog="proxsis",
                                description="Proxsis — moteur proxsis : sources, données, modèles, exports")
    sub = p.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("world", help="génère le monde FICTIF et l'écrit sur disque")
    w.add_argument("--seed", type=int, default=42)
    w.add_argument("--companies", type=int, default=4000)
    w.add_argument("--out", default=repo("data/fictif"))
    w.set_defaults(func=cmd_world)

    b = sub.add_parser("backtest", help="suite de backtest reproductible")
    b.add_argument("--seed", type=int, default=42)
    b.add_argument("--quick", action="store_true", help="version rapide (1500 entreprises)")
    b.add_argument("--out-json", default=repo("docs/backtest/resultats.json"))
    b.add_argument("--out-md", default=repo("docs/backtest/RAPPORT_BACKTEST.md"))
    b.set_defaults(func=cmd_backtest)

    e = sub.add_parser("export-demo", help="données de démo de l'appli web (réel + FICTIF étiqueté, contrôles)")
    e.add_argument("--seed", type=int, default=42)
    e.add_argument("--out", default=repo("apps/web/src/data/demo"))
    e.add_argument("--date", default="2026-10-05")
    e.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    e.add_argument("--localites", default=LOCALITES_CSV)
    e.add_argument("--candidats", default=repo("data/fictif/candidats_300.csv"))
    e.add_argument("--claims", default=repo("CLAIMS.md"))
    e.add_argument("--backtest-json", default=repo("docs/backtest/specialites_v1.json"))
    e.add_argument("--permis", default=PERMITS_JSONL)
    e.add_argument("--liste-gelee", default=repo("data/terrain/liste_2026-10-05_batiment.json"),
                   help="liste gelée que montre la visite : la semaine de chaque agence en Bâtiment (B7)")
    e.set_defaults(func=cmd_export_demo)

    r = sub.add_parser("rapports-modeles", help="régénère docs/modeles/*.json (M3, M4, M5, M6) avec avertissements")
    r.add_argument("--seed", type=int, default=42)
    r.add_argument("--out", default=repo("docs/modeles"))
    r.set_defaults(func=cmd_model_reports)
    u = sub.add_parser("update", help="mise à jour quotidienne des sources publiques (ou rejeu hors ligne)")
    u.add_argument("--days", type=int, default=2)
    u.add_argument("--until", default=None,
                   help="dernier jour lu (AAAA-MM-JJ) ; par défaut, la veille à Zurich")
    u.add_argument("--cantons", default="VS")
    u.add_argument("--offline", action="store_true")
    u.add_argument("--cache", default=repo("python/.cache/http"))
    u.add_argument("--out", default=repo("data/reel"))
    u.set_defaults(func=cmd_update)

    t = sub.add_parser("tirage-reel", help="[session Mac] tire le jeu de test réel v2 (adjudications simap FR/DE)")
    t.add_argument("--date-from", default="2026-08-01")
    t.add_argument("--date-to", default="2026-09-30")
    t.add_argument("--sub-types", default="construction,service,supply")
    t.add_argument("--seed", type=int, default=20261005)
    t.add_argument("--n-fr", type=int, default=75)
    t.add_argument("--n-de", type=int, default=75)
    t.add_argument("--max-pages", type=int, default=250)
    t.add_argument("--cadre", default=None, help="réutiliser un cadre déjà enregistré (cadre.jsonl)")
    t.add_argument("--out", default=repo("data/annotations/reel_v2"))
    t.set_defaults(func=cmd_real_draw)

    pa = sub.add_parser("page-annotation", help="[session Mac] page HTML autonome d'annotation")
    pa.add_argument("--items", default=repo("data/annotations/reel_v2/a_annoter.jsonl"))
    pa.add_argument("--out", default=repo("apps/annotation/index.html"))
    pa.add_argument("--title", default="Annotation — jeu réel v2 (adjudications simap)")
    pa.add_argument("--profil", default=DEFAULT_PROFILE, choices=list(PROFILES), help="champs demandés")
    pa.set_defaults(func=cmd_annotation_page)


    cs = sub.add_parser("collecte-simap", help="[session Mac] collecte reprenable d'adjudications simap filtrées")
    cs.add_argument("--date-from", required=True)
    cs.add_argument("--date-to", required=True)
    cs.add_argument("--cantons", default="")
    cs.add_argument("--emetteurs", default="", help="identifiants simap d'organisations adjudicatrices (et enfants)")
    cs.add_argument("--sub-types", default="construction")
    cs.add_argument("--interval", type=float, default=2.0)
    cs.add_argument("--max-pages", type=int, default=2000)
    cs.add_argument("--out", required=True)
    cs.set_defaults(func=cmd_collect_simap)

    br = sub.add_parser("backtest-reel", help="[session Mac] backtest sur données publiques réelles (cible T0)")
    br.add_argument("records", nargs="+")
    br.add_argument("--first-week", required=True)
    br.add_argument("--last-week", required=True)
    br.add_argument("--data-end", required=True)
    br.add_argument("--k", type=int, default=20)
    br.add_argument("--seed", type=int, default=0)
    br.add_argument("--out", default=repo("docs/backtest/reel_t0.json"))
    br.add_argument("--etendu", action="store_true", help="cible « pic » et modèle combiné")
    br.add_argument("--train-from", default="2025-03-03")
    br.set_defaults(func=cmd_real_backtest)

    ce = sub.add_parser("comparer-extraction", help="[session Mac] règles vs Apertus sur le jeu réel GELÉ")
    ce.add_argument("--jeu", default=repo("data/annotations/reel_v2.jsonl"))
    ce.add_argument("--frozen-md", default=repo("data/annotations/FROZEN.md"))
    ce.add_argument("--apertus", action="store_true")
    ce.add_argument("--accord", default=None, help="accord.json : signale les champs où les humains divergent")
    ce.add_argument("--out", default=repo("docs/modeles/m3_comparaison_reel_v2.json"))
    ce.set_defaults(func=cmd_compare_extraction)

    cm = sub.add_parser("collecte-manuelle", help="[session Mac] page locale de collecte manuelle (BO VS, FOSC)")
    cm.add_argument("--dossier", default=repo("data/manuel"))
    cm.add_argument("--port", type=int, default=8766)
    cm.set_defaults(func=cmd_manual_collection)

    ec = sub.add_parser("etat-collecte", help="[session Mac] avancement de la collecte manuelle par strate")
    ec.add_argument("--dossier", default=repo("data/manuel"))
    ec.set_defaults(func=cmd_manual_status)

    pc = sub.add_parser("plan-collecte", help="[session Mac] jours à relever par personne (tirage reproductible)")
    pc.add_argument("--seed", type=int, default=20261005)
    pc.set_defaults(func=cmd_collection_plan)

    def _wf(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--dossier", default=repo("data/manuel"), help="collecte manuelle (textes privés dans textes/)")
        sp.add_argument("--items", default=None, help="ou un fichier d'items JSONL (ex. jeu simap)")
        sp.add_argument("--public", default=repo("data/manuel/annotation"))
        sp.add_argument("--prive", default=repo("data/manuel/textes"))

    ra = sub.add_parser("repartir-annotation", help="[session Mac] répartition + double annotation à l'aveugle")
    _wf(ra)
    ra.add_argument("--annotateurs", required=True, help="initiales séparées par des virgules")
    ra.add_argument("--double", type=int, default=20)
    ra.add_argument("--seed", type=int, default=20261005)
    ra.add_argument("--profil", default=DEFAULT_PROFILE, choices=list(PROFILES),
                    help="champs demandés et comparés (enregistré dans repartition.json, repris par accord-manuel et "
                         "geler-manuel) : simap ; bo_fr ; bo_de_structure (allemand, champs structurés, sans métiers)")
    ra.set_defaults(func=cmd_prepare_annotation)

    am = sub.add_parser("accord-manuel", help="[session Mac] accord champ par champ sur la double annotation")
    _wf(am)
    am.add_argument("exports", nargs="+")
    am.set_defaults(func=cmd_manual_agreement)

    gm = sub.add_parser("geler-manuel", help="[session Mac] référence + arbitrage, gel (textes hors git)")
    _wf(gm)
    gm.add_argument("exports", nargs="+")
    gm.add_argument("--arbitrage", default=None)
    gm.add_argument("--frozen-md", default=repo("data/annotations/FROZEN.md"))
    gm.add_argument("--nom", default="reel_v3")
    gm.set_defaults(func=cmd_manual_freeze)

    m6 = sub.add_parser("m6-reel", help="[session Mac] M6 sur séries publiques réelles")
    m6.add_argument("--simap", nargs="+", default=[
        repo("data/reel/simap/adjudications_romandie_construction_2024-07_2026-09.jsonl")])
    m6.add_argument("--series", default=repo("data/reel/series"))
    m6.add_argument("--out", default=repo("docs/modeles/m6_reel_v1.json"))
    m6.set_defaults(func=cmd_m6_real)

    ap = sub.add_parser("apercu-simap", help="[session Mac] aperçu des adjudications simap collectées")
    ap.add_argument("--romandie", default=SIMAP_FILES[0])
    ap.add_argument("--emetteur-vs", default=SIMAP_FILES[1])
    ap.add_argument("--lieux", default=repo("data/reel/referentiels/lieux_vs.csv"))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=repo("docs/recherche/apercu_simap.json"))
    ap.set_defaults(func=cmd_simap_overview)

    pz = sub.add_parser("phasage-reel", help="[session Mac] phasage appris sur les lots simap réels")
    pz.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    pz.add_argument("--coupures", nargs="+", default=["2025-10-01", "2026-01-01"])
    pz.add_argument("--out", default=repo("docs/modeles/phasage_reel_v1.json"))
    pz.set_defaults(func=cmd_phasing)

    m4 = sub.add_parser("m4-reel", help="[session Mac] variantes de noms et paires douteuses (lauréats simap)")
    m4.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    m4.add_argument("--out-csv", default=repo("docs/modeles/m4_paires_douteuses_v1.csv"))
    m4.add_argument("--out-json", default=repo("docs/modeles/m4_reel_v1.json"))
    m4.set_defaults(func=cmd_m4_real)

    dx = sub.add_parser("dix-entreprises", help="[semaine 1] liste d'appels gelée + feuille à valider (PDF) + CSV")
    dx.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    dx.add_argument("--date", required=True, help="lundi de la semaine (AAAA-MM-JJ)")
    dx.add_argument("--specialite", default="batiment", choices=["batiment", "electricite", "technique", "industrie"])
    dx.add_argument("--cantons", default="VS")
    dx.add_argument("--k", type=int, default=10)
    dx.add_argument("--ordre", default="frequence", choices=["frequence", "combine"])
    dx.add_argument("--out-dir", default=repo("data/terrain"))
    dx.add_argument("--sans-pdf", action="store_true")
    dx.add_argument("--permis", default=PERMITS_JSONL, help="permis importés du Bulletin officiel (contexte)")
    dx.set_defaults(func=cmd_call_list)

    iv = sub.add_parser("integrer-validation", help="[semaine 1] réponses des consultants → vérité terrain")
    iv.add_argument("--liste", required=True)
    iv.add_argument("--reponses", nargs="+", required=True)
    iv.add_argument("--out-dir", default=repo("data/terrain"))
    iv.set_defaults(func=cmd_integrate_validation)

    bs = sub.add_parser("backtest-specialites", help="[semaine 1] backtest réel par spécialité d'agence et région")
    bs.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    bs.add_argument("--specialites", nargs="+", default=["batiment", "electricite", "technique"])
    bs.add_argument("--cantons", default="VS")
    bs.add_argument("--premiere-semaine", default="2025-07-07")
    bs.add_argument("--derniere-semaine", default="2026-08-03")
    bs.add_argument("--apprentissage-depuis", default="2025-01-06")
    bs.add_argument("--fin-donnees", default="")
    bs.add_argument("--k", type=int, default=10)
    bs.add_argument("--n-boot", type=int, default=2000)
    bs.add_argument("--out", default=repo("docs/backtest/specialites_v1.json"))
    bs.set_defaults(func=cmd_specialty_backtest)

    lo = sub.add_parser("localites", help="[semaine 1] répertoire officiel des localités (swisstopo, OGD)")
    lo.add_argument("--cantons", default="VS")
    lo.add_argument("--out", default=LOCALITES_CSV)
    lo.set_defaults(func=cmd_localities)

    cc = sub.add_parser("contours-communes", help="contours des communes du Valais (swisstopo), simplifiés, hors ligne")
    cc.add_argument("--millesime", default=None, help="élément STAC swissBOUNDARIES3D (défaut : 2026-01)")
    cc.add_argument("--tolerance", type=float, default=None, help="Douglas–Peucker, unités de la carte (≈ 135 m)")
    cc.add_argument("--brut", default=repo("python/.cache/swissboundaries3d"), help="téléchargement brut, hors Git")
    cc.add_argument("--rafraichir", action="store_true", help="retélécharger même si la couche est déjà là")
    cc.add_argument("--presentation", default=repo("apps/web/src/data/presentation/presentation.json"))
    cc.add_argument("--localites", default=LOCALITES_CSV)
    cc.add_argument("--out", default=repo("apps/web/src/data/presentation/communes_vs.json"))
    cc.set_defaults(func=cmd_commune_boundaries)

    ca = sub.add_parser("candidats", help="[semaine 1] vivier de candidats FICTIFS (catégorie CCT par la règle)")
    ca.add_argument("--localites", default=LOCALITES_CSV)
    ca.add_argument("--date", default="2026-10-05")
    ca.add_argument("--n", type=int, default=300)
    ca.add_argument("--seed", type=int, default=42)
    ca.add_argument("--out", default=repo("data/fictif/candidats_300.csv"))
    ca.set_defaults(func=cmd_candidates)

    ms = sub.add_parser("moteur-semaine1", help="[semaine 1] propositions, redéploiement, équité, conformité")
    ms.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    ms.add_argument("--localites", default=LOCALITES_CSV)
    ms.add_argument("--candidats", default=repo("data/fictif/candidats_300.csv"))
    ms.add_argument("--date", default="2026-10-05")
    ms.add_argument("--specialites", nargs="+", default=["batiment", "electricite", "technique"])
    ms.add_argument("--graines", type=int, default=20, help="viviers tirés pour l'audit d'équité")
    ms.add_argument("--permutations", type=int, default=200)
    ms.add_argument("--out", default=repo("docs/modeles/semaine1_v1.json"))
    ms.add_argument("--out-detail", default=repo("docs/modeles/semaine1_detail_v1.json"))
    ms.set_defaults(func=cmd_week1_engine)

    dw = sub.add_parser("docs-semaine1", help="régénère les rapports de semaine 1 depuis les JSON des commandes")
    dw.add_argument("--racine", default="..")
    dw.set_defaults(func=cmd_docs_week1)

    rm = sub.add_parser("remasquer-adjudicateurs", help="[audit] masque les adjudicateurs ressemblant à des personnes")
    rm.add_argument("--fichiers", nargs="+",
                    default=[*SIMAP_FILES, SUPPLY_FILE])
    rm.set_defaults(func=cmd_remask_authorities)

    ib = sub.add_parser("import-bo-pdf", help="import des PDF du Bulletin officiel + index XML (filtre avant écriture)")
    ib.add_argument("--pdfs", nargs="+", required=True)
    ib.add_argument("--index", required=True)
    ib.add_argument("--public", default=repo("data/manuel/import_pdf"))
    ib.add_argument("--prive", default=repo("data/manuel/textes/bo_vs_pdf"))
    ib.add_argument("--suffixe", default="", help="suffixe du rapport (ex. _de) pour ne pas écraser le précédent")
    ib.add_argument("--contexte", nargs="*", help="autres PDF lus en mémoire seulement : une partie masquée là "
                    "l'est aussi ici")
    ib.add_argument("--localites", default=LOCALITES_CSV)
    ib.set_defaults(func=cmd_import_bo_pdf)

    sp = sub.add_parser("sonder-pdf", help="squelette masqué d'un PDF (mots du gabarit seulement)")
    sp.add_argument("pdfs", nargs="+")
    sp.add_argument("--seuil", type=int, default=150)
    sp.add_argument("--lignes", type=int, default=200)
    sp.set_defaults(func=cmd_probe_pdf)

    tb = sub.add_parser("tirage-bo", help="tirage reproductible du jeu de test Bulletin officiel")
    tb.add_argument("--langue", default="fr", choices=["fr", "de"])
    tb.add_argument("--n", type=int, default=100)
    tb.add_argument("--seed", type=int, default=20261006)
    tb.add_argument("--public", default=repo("data/manuel/import_pdf"))
    tb.add_argument("--prive", default=repo("data/manuel/textes/bo_vs_pdf"))
    tb.add_argument("--annotations", default=repo("data/annotations/bo_vs_v1"))
    tb.set_defaults(func=cmd_draw_bo)

    pr = sub.add_parser("projets-radar", help="projets qui comptent pour le radar (logements, halles, public)")
    pr.add_argument("--public", default=repo("data/manuel/import_pdf"))
    pr.add_argument("--out", default=repo("data/manuel/import_pdf/projets_radar.json"))
    pr.add_argument("--md", default=repo("docs/radar/projets_bo_vs_2026-08-09.md"))
    pr.set_defaults(func=cmd_radar_projects)

    xp = sub.add_parser("export-presentation", help="données de la présentation « Votre prochain lundi » (comptes)")
    xp.add_argument("--publications", default=PERMITS_JSONL)
    xp.add_argument("--localites", default=LOCALITES_CSV)
    xp.add_argument("--date", default="2026-10-06", help="date de préparation affichée")
    xp.add_argument("--marches",
                    default=repo("data/reel/simap/adjudications_emetteur_vs_construction_2024-07_2026-09.jsonl"))
    xp.add_argument("--out", default=repo("apps/web/src/data/presentation/presentation.json"))
    xp.add_argument("--dossiers", default=repo("apps/web/src/data/presentation/dossiers.json"))
    xp.set_defaults(func=cmd_export_presentation)

    hs = sub.add_parser("histoires-presentation", help="acte 4 : trois histoires datées (simap) et écran de mesure")
    hs.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    hs.add_argument("--appels-offres", default=STORY_TENDERS)
    hs.add_argument("--en-ligne", action="store_true", help="relire les appels d'offres par l'API simap")
    hs.add_argument("--interval", type=float, default=2.0)
    hs.add_argument("--publications", default=PERMITS_JSONL)
    hs.add_argument("--reel-t0", default=repo("docs/backtest/reel_t0.json"))
    hs.add_argument("--claims", default=repo("CLAIMS.md"))
    hs.add_argument("--date", default="2026-10-06", help="date de préparation affichée")
    hs.add_argument("--data-end", default="2026-09-30")
    hs.add_argument("--out", default=repo("apps/web/src/data/presentation/histoires.json"))
    hs.set_defaults(func=cmd_presentation_stories)

    ld = sub.add_parser("lundis-presentation",
                        help="acte 4 : « Choisissez une date », les dix entreprises de la règle simple à chaque lundi "
                             "de la mesure REEL-SPEC-BAT et ce qu'elles ont obtenu")
    ld.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    ld.add_argument("--mesure", default=repo("docs/backtest/specialites_v1.json"))
    ld.add_argument("--claims", default=repo("CLAIMS.md"))
    ld.add_argument("--data-end", default="2026-09-30")
    ld.add_argument("--out", default=repo("apps/web/src/data/presentation/lundis.json"))
    ld.set_defaults(func=cmd_presentation_mondays)

    te = sub.add_parser("territoire-presentation",
                        help="visite, temps 1 : par commune, les entreprises actives dans nos données (siège ici, "
                             "marché ici), seulement celles dont le dossier passe tous les contrôles")
    te.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    te.add_argument("--web", default=repo("apps/web/src/data"), help="données de l'application (export-demo)")
    te.add_argument("--localites", default=LOCALITES_CSV)
    te.add_argument("--exemple-commune", default="Saxon")
    te.add_argument("--out", default=repo("apps/web/src/data/presentation/territoire.json"))
    te.set_defaults(func=cmd_presentation_territory)

    nm = sub.add_parser("lundi-suivant-presentation",
                        help="visite, temps 2 : la liste du lundi suivant par la même règle, et les publications "
                             "parues "
                             "entre les deux lundis")
    nm.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    nm.add_argument("--dossiers", default=repo("apps/web/src/data/presentation/dossiers.json"))
    nm.add_argument("--data-end", default="2026-09-30")
    nm.add_argument("--out", default=repo("apps/web/src/data/presentation/lundi_suivant.json"))
    nm.set_defaults(func=cmd_presentation_next_monday)

    mo = sub.add_parser("moments-presentation",
                        help="visite (brief du 07.10.2026, § 3.2 à 3.4) : « Cette semaine », « Celles qui accélèrent » "
                             "et les faits publiés des dossiers guidés, chacun contrôlé contre sa ligne de CLAIMS.md")
    mo.add_argument("--fichiers", nargs="+", default=SIMAP_FILES)
    mo.add_argument("--permis", default=PERMITS_JSONL, help="import filtré du Bulletin officiel")
    mo.add_argument("--liste", default=repo("data/terrain/liste_2026-10-05_batiment.json"),
                    help="liste gelée du premier lundi de la visite")
    mo.add_argument("--mesure", default=repo("docs/backtest/specialites_v1.json"))
    mo.add_argument("--claims", default=repo("CLAIMS.md"))
    mo.add_argument("--data-end", default="2026-09-30")
    mo.add_argument("--date", default="2026-10-07", help="date de calcul inscrite dans les fichiers")
    mo.add_argument("--out-dir", default=repo("apps/web/src/data/presentation"))
    mo.set_defaults(func=cmd_presentation_moments)

    lw = sub.add_parser("matin-en-direct",
                        help="« Chaque matin, en direct de simap » (chaque jour ouvrable : le lundi la semaine "
                             "écoulée, du mardi au vendredi la veille ; filtré, contrôlé)")
    lw.add_argument("--jour", help="jour de lecture à rejouer (AAAA-MM-JJ, du lundi au vendredi) ; par défaut, "
                                   "aujourd'hui à Zurich")
    lw.add_argument("--rejeu", help="adjudications simap déjà filtrées (JSONL) au lieu de l'API")
    lw.add_argument("--interval", type=float, default=2.0)
    lw.add_argument("--out", default=repo("apps/web/src/data/direct/matin.json"))
    lw.add_argument("--corrections", default=repo("apps/web/src/data/direct/corrections.json"),
                    help="rectifications des avis des données figées (gardées d'une lecture à l'autre)")
    lw.add_argument("--figees", default=repo("apps/web/src/data"), help="données figées où chercher les avis cités")
    lw.set_defaults(func=cmd_live_week)

    lm = sub.add_parser("matins-presentation",
                        help="« Choisissez une date » : la section « Chaque matin » de chaque lundi au choix, figée, "
                             "avec seulement ce qui était publié avant ce lundi")
    lm.add_argument("--fichiers", nargs="+",
                    default=[repo("data/reel/simap/adjudications_emetteur_vs_construction_2024-07_2026-09.jsonl")])
    lm.add_argument("--lundis", default=repo("apps/web/src/data/presentation/lundis.json"))
    lm.add_argument("--out", default=repo("apps/web/src/data/presentation/matins.json"))
    lm.set_defaults(func=cmd_frozen_mornings)

    cs = sub.add_parser("carte-sources",
                        help="la carte des sources : les lignes du catalogue comptées par groupe (en service, demande "
                             "envoyée, écartées, autres), contrôlées contre la ligne SOURCES-1 de CLAIMS.md")
    cs.add_argument("--catalogue", default=repo("data/catalogue.csv"))
    cs.add_argument("--claims", default=repo("CLAIMS.md"))
    cs.add_argument("--out", default=repo("apps/web/src/data/sources/carte.json"))
    cs.set_defaults(func=cmd_source_map)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
