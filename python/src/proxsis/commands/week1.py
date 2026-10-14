"""Commands of week 1: the frozen call list, the consultants' validation, the specialty backtests, places and commune
boundaries, fictional candidates and the week-1 engine.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from proxsis.commands.io import load_simap, permits, read_places


def cmd_call_list(args: argparse.Namespace) -> int:
    """[semaine 1] The k companies to call this week for a specialty, frozen, with the validation sheet."""
    from datetime import date

    from proxsis.call_list import CallListConfig, build_call_list
    from proxsis.demo_export import clean_json
    from proxsis.validation_sheet import csv_template, freeze_list, render_html, write_one_page_pdf

    if date.fromisoformat(args.date).weekday() != 0:
        print(f"--date {args.date} n'est pas un lundi : la liste est celle d'une semaine")
        return 2
    recs = load_simap(args.fichiers)
    cfg = CallListConfig(as_of=date.fromisoformat(args.date), specialty=args.specialite,
                         region_cantons=tuple(c for c in args.cantons.split(",") if c), k=args.k, ranker=args.ordre)
    lst = freeze_list(build_call_list(recs, cfg, permits=permits(args.permis)))
    lst["donnees"] = {"fichiers": [Path(f).name for f in args.fichiers], "adjudications": len(recs),
                      "type": "RÉEL (simap.ch)"}
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"liste_{args.date}_{args.specialite}"
    (out / f"{stem}.json").write_text(json.dumps(clean_json(lst), ensure_ascii=False, indent=1, default=str,
                                                 allow_nan=False) + "\n", "utf-8")
    too_long = False
    for lang in ("fr", "de"):
        page = out / f"{stem}_{lang}.html"
        page.write_text(render_html(lst, lang), "utf-8")
        if not args.sans_pdf:
            n = write_one_page_pdf(lst, lang, page, out / f"{stem}_{lang}.pdf")
            print(f"PDF {lang} : " + ("Chrome introuvable ou en échec, imprimer la page HTML" if n is None
                                      else f"{n} page(s)"))
            too_long |= bool(n and n > 1)
            page.write_text(render_html(lst, lang), "utf-8")
    (out / f"reponses_{args.date}_{args.specialite}.csv").write_text(csv_template(lst), "utf-8")
    print(f"liste {lst['liste_id']} : {len(lst['entreprises'])} entreprises, {len(lst['surprises'])} surprises "
          f"→ {out}")
    for e in lst["entreprises"]:
        print(f"{e['rang']:>2}. {e['nom']} ({e['ville']}) — {e['n_52s']} marchés/52 sem., confiance {e['confiance']}")
    if too_long:
        print("La feuille dépasse une page même réduite : à corriger avant l'envoi.")
        return 1
    return 0


def cmd_integrate_validation(args: argparse.Namespace) -> int:
    """[semaine 1] Consultants' answers on a frozen list → field ground truth (RÉEL-TERRAIN)."""
    import csv

    from proxsis.validation_sheet import integrate

    lst = json.loads(Path(args.liste).read_text("utf-8"))
    rows: list[dict[str, str]] = []
    for f in args.reponses:
        with open(f, encoding="utf-8") as fh:
            rows += [r for r in csv.DictReader(fh) if (r.get("consultant") or "").strip()]
    rep = integrate(lst, rows)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"validation_{lst['liste_id']}.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n",
                                                            "utf-8")
    print(json.dumps({k: rep[k] for k in ("consultants", "entreprises_evaluees", "recrute_en_effet", "connue",
                                          "pas_pertinente")}, ensure_ascii=False))
    return 0


def cmd_specialty_backtest(args: argparse.Namespace) -> int:
    """[semaine 1, 2.7] Real backtest per agency specialty, ranking restricted to firms of the region."""
    from datetime import date

    from proxsis.call_list import _events, lot_table
    from proxsis.real_backtest import evaluate_extended, region_at

    recs = load_simap(args.fichiers)
    lots = lot_table(recs)
    cantons = {c for c in args.cantons.split(",") if c}
    end = date.fromisoformat(args.fin_donnees) if args.fin_donnees else max(lots["available_at"])
    rep: dict[str, Any] = {"mesure_le": str(date.today()), "donnees": "RÉEL (simap.ch, adjudications de construction)",
                 "adjudications": len(recs), "region": sorted(cantons), "k": args.k, "fin_donnees": str(end),
                 "regle_ordre": "modèle combiné retenu seulement si la borne basse de l'IC 95 % de "
                                "(combiné − fréquence) sur T0 est > 0 ; sinon fréquence puis récence",
                 "specialites": {}}
    for spec in args.specialites:
        ev = _events(lots, spec)
        region = set(lots[(lots["specialty"] == spec) & lots["canton"].isin(cantons)]["company"])

        try:
            r = evaluate_extended(ev, first_week=date.fromisoformat(args.premiere_semaine),
                                  last_week=date.fromisoformat(args.derniere_semaine),
                                  train_from=date.fromisoformat(args.apprentissage_depuis), k=args.k,
                                  n_boot=args.n_boot, seed=0, data_end=end,
                                  eval_companies=lambda T, past: region_at(lots, cantons, T, past))
        except (ValueError, IndexError) as exc:
            rep["specialites"][spec] = {"erreur": str(exc), "entreprises_region": len(region)}
            continue
        low = r["cibles"]["t0"]["combine_moins_frequence"]["ic95"][0]
        r["ordre_retenu"] = "combine" if low > 0 else "frequence"
        r["entreprises_region"] = len(region)
        r["evenements"] = len(ev)
        rep["specialites"][spec] = r
        t0, pic = r["cibles"]["t0"], r["cibles"]["pic"]
        print(spec, f"T0 base {t0['taux_de_base']:.3f} fréq {t0['p_at_k']['frequence_52s']['moyenne']:.3f} "
                    f"comb {t0['p_at_k']['combine']['moyenne']:.3f} | pic base {pic['taux_de_base']:.3f} "
                    f"fréq {pic['p_at_k']['frequence_52s']['moyenne']:.3f} "
                    f"comb {pic['p_at_k']['combine']['moyenne']:.3f} → {r['ordre_retenu']}")
    Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n", "utf-8")
    return 0


def cmd_localities(args: argparse.Namespace) -> int:
    """[semaine 1] Official directory of Valais localities with coordinates (swisstopo, OGD)."""
    import csv

    from proxsis.connectors import swisstopo_localities as loc
    from proxsis.http import HttpCache, PoliteClient
    from proxsis.netcheck import USER_AGENT

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    client = PoliteClient(HttpCache(out.parent / ".nocache"), offline=False, user_agent=USER_AGENT, min_interval_s=2.0)
    rows = loc.fetch(client, tuple(args.cantons.split(",")))
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} localités → {out} (source : {loc.SOURCE})")
    return 0


def cmd_commune_boundaries(args: argparse.Namespace) -> int:
    """Commune boundaries of the Valais (swisstopo swissBOUNDARIES3D), simplified, for the map of the presentation."""

    from proxsis.connectors import swisstopo_boundaries as sb
    from proxsis.http import HttpCache, PoliteClient
    from proxsis.netcheck import USER_AGENT

    item = args.millesime or sb.ITEM
    tolerance = sb.DEFAULT_TOLERANCE if args.tolerance is None else args.tolerance
    folder = Path(args.brut) / item  # outside Git (python/.cache/ is ignored): a rebuild makes no request
    dl = None if args.rafraichir else sb.load_download(folder)
    if dl is None:
        client = PoliteClient(HttpCache(folder / ".nocache"), offline=False, user_agent=USER_AGENT, min_interval_s=4.0)
        try:
            dl = sb.fetch_commune_layer(client, item)
        finally:
            client.close()
        sb.save_download(dl, folder)
        print(f"téléchargé : {dl.requests} requêtes, {dl.bytes} octets ({dl.url})")
    else:
        print(f"couche communale déjà téléchargée le {dl.retrieved_at} ({folder}) : aucune requête")
    encoding = dl.files[".cpg"].decode("ascii").strip() or "utf-8"
    data = sb.build(sb.read_shapefile(dl.files[".shp"], dl.files[".dbf"], encoding), url=dl.url,
                    retrieved_at=dl.retrieved_at, vintage=sb.vintage(item), tolerance=tolerance)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(sb.dumps(data), "utf-8")
    print(f"{len(data['communes'])} communes, tolérance {tolerance}, {out.stat().st_size} octets → {out}")
    if Path(args.presentation).exists():
        pres = json.loads(Path(args.presentation).read_text("utf-8"))
        names = sorted({c["commune"] for key in ("territoire", "marches") for c in pres[key]["communes"]})
        found = sb.match_communes(names, data["communes"], read_places(args.localites))
        missing = [n for n, b in found.items() if b is None]
        print(f"présentation : {len(names) - len(missing)}/{len(names)} communes avec contour ; sans contour : "
              f"{', '.join(missing) or 'aucune'}")
    return 0


def cmd_candidates(args: argparse.Namespace) -> int:
    """[semaine 1, 2.4] The FICTIONAL pool of candidates, placed in real Valais localities."""

    from proxsis.synth.candidates import generate_candidates

    places = read_places(args.localites)
    for p in places:  # assumption (FICTIF): more candidates around the larger postcodes of the three agencies
        p["poids"] = 4.0 if p["commune"] in {"Sion", "Martigny", "Monthey", "Sierre", "Visp", "Brig-Glis"} else 1.0
    c = generate_candidates(places, today=date.fromisoformat(args.date), n=args.n, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    c.to_csv(out, index=False)
    print(f"{len(c)} candidats FICTIFS → {out} ; catégories CCT {c['categorie_cct'].value_counts().to_dict()} ; "
          f"en mission {int((c['statut'] == 'en_mission').sum())}")
    return 0


def cmd_week1_engine(args: argparse.Namespace) -> int:
    """[semaine 1, 2.4-2.6] Proposals for the real needs, redeployment, fairness audit, compliance."""
    from datetime import date

    import pandas as pd

    from proxsis.call_list import CallListConfig, build_call_list
    from proxsis.compliance import check
    from proxsis.fairness import permutation_test, run_audit
    from proxsis.honesty import mark
    from proxsis.proposals import need_sites, needs_from_call_list, propose
    from proxsis.redeploy import redeploy, slots_from_call_lists
    from proxsis.synth.candidates import generate_candidates

    today = date.fromisoformat(args.date)
    places = read_places(args.localites)
    cands = pd.read_csv(args.candidats, dtype={"fin_mission": "string"})
    cands["fin_mission"] = cands["fin_mission"].map(lambda v: v if isinstance(v, str) else None)
    recs = load_simap(args.fichiers)
    lists = [build_call_list(recs, CallListConfig(as_of=today, specialty=s)) for s in args.specialites]
    needs, skipped = [], []
    for cl in lists:
        n, sk = needs_from_call_list(cl, places)
        needs += n
        skipped += sk
    sites = need_sites(lists)
    props = [propose(cands, n, k=5, today=today, site=sites.get((n.company_id, n.trade), "batiment"))
             for n in needs]
    comp = [check(n.trade, site=sites.get((n.company_id, n.trade), "batiment"), on=today)
            | {"entreprise": n.company_id, "site": sites.get((n.company_id, n.trade), "batiment")} for n in needs]
    red = redeploy(cands, slots_from_call_lists(lists, places), today, weeks=3)
    import numpy as np

    from proxsis.models.m5_matching import DEFAULT_EXP_CAP_YEARS, CandidateMatcher

    class RandomTopK(CandidateMatcher):
        """Reference: the k proposals drawn at random among the eligible candidates (noise floor of the ratio)."""

        def score_frame(self, need: Any, e: Any) -> Any:
            key = sum(ord(ch) for ch in f"{need.company_id}{need.trade}")
            return np.random.default_rng(key).random(len(e))

    def audit_with(cap: float, factory: Any = None, permute: bool = True) -> dict[str, Any]:
        audits: list[dict[str, Any]] = []
        exp: list[float] = []
        for seed in range(args.graines):
            pool = generate_candidates(places, today=today, n=len(cands), seed=1000 + seed) if seed else cands
            make = factory or (lambda c, cap=cap: CandidateMatcher(c, exp_cap_years=cap))
            a = run_audit(pool, needs, k=5, seed=seed, matcher_factory=make)
            m = make(pool)
            ids = [x.candidate_id for n in needs for x in m.suggest(n, 5)]
            exp.append(float(pool.set_index("candidate_id").loc[ids, "experience_years"].mean()) if ids else 0.0)
            perms = {attr: permutation_test(pool, needs, attr, n_perm=args.permutations, seed=seed,
                                            matcher_factory=make)
                     for attr in ("audit_gender", "audit_age_band", "audit_nationality_group")} if permute else {}
            audits.append({"graine_vivier": 1000 + seed if seed else "vivier publié", "di_ratio": a.di_ratio,
                           "alertes": a.flags, "invariance_contrefactuelle": a.counterfactual_invariant,
                           "taux_selection": a.selection,
                           "permutation": {k: {"p_valeur": v["p_valeur"], "khi2": v["khi2_observe"],
                                               "taux_selection": v["taux_selection"]} for k, v in perms.items()}})
        di = {k: [x["di_ratio"].get(k) for x in audits if x["di_ratio"].get(k) is not None]
              for k in ("audit_gender", "audit_age_band", "audit_nationality_group")}
        perm_summary = {}
        for attr in ("audit_gender", "audit_age_band", "audit_nationality_group"):
            ps = [x["permutation"][attr]["p_valeur"] for x in audits if x.get("permutation", {}).get(attr)
                  and x["permutation"][attr]["p_valeur"] is not None]
            groups = sorted({g for x in audits for g in x.get("permutation", {}).get(attr, {}).get("taux_selection",
                                                                                                     {})})
            mean_rates = {g: float(np.mean(v)) for g in groups
                          if (v := [x["permutation"][attr]["taux_selection"][g] for x in audits
                                    if g in x.get("permutation", {}).get(attr, {}).get("taux_selection", {})])}
            perm_summary[attr] = {"viviers": len(ps), "part_p_inf_0_05": float(np.mean([p < 0.05 for p in ps]))
                                  if ps else None, "p_mediane": float(np.median(ps)) if ps else None,
                                  "taux_selection_moyens": mean_rates}
        return {"plafond_experience_ans": cap, "tirages": len(audits), "test_permutation": perm_summary,
                "di_ratio": {k: {"min": min(v), "max": max(v), "moyenne": sum(v) / len(v)} for k, v in di.items() if v},
                "tirages_avec_alerte": sum(bool(x["alertes"]) for x in audits),
                "invariance_contrefactuelle": all(x["invariance_contrefactuelle"] for x in audits),
                "experience_moyenne_proposes_ans": sum(exp) / len(exp), "details": audits}

    equity = {"plafond_15_ans_actuel": audit_with(DEFAULT_EXP_CAP_YEARS), "plafond_5_ans_adr_0012": audit_with(5.0),
              "reference_tirage_au_hasard": audit_with(DEFAULT_EXP_CAP_YEARS, factory=RandomTopK, permute=False)}
    rng = np.random.default_rng(0)
    ref = equity["reference_tirage_au_hasard"]["details"]
    for name in ("plafond_15_ans_actuel", "plafond_5_ans_adr_0012"):
        gaps = {}
        for attr in ("audit_gender", "audit_age_band", "audit_nationality_group"):
            d = np.array([m["di_ratio"][attr] - r["di_ratio"][attr] for m, r in zip(equity[name]["details"], ref,
                                                                                    strict=True)
                          if attr in m["di_ratio"] and attr in r["di_ratio"]])
            boots = [float(rng.choice(d, len(d)).mean()) for _ in range(2000)] if len(d) else [float("nan")]
            gaps[attr] = {"moyenne": float(d.mean()) if len(d) else None,
                          "ic95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}
        equity[name]["ecart_au_hasard_apparie"] = gaps
    rep = {"date": str(today), "type_de_donnee": "FICTIF (candidats) face à des besoins RÉELS (simap.ch)",
           "besoins": len(needs), "entreprises_sans_localite": skipped,
           "propositions": {"besoins_avec_au_moins_une": sum(bool(p["propositions"]) for p in props),
                            "besoins": len(props),
                            "entonnoir_moyen": {k: round(sum(p["entonnoir"][k] for p in props) / max(len(props), 1), 1)
                                                for k in ("tous", "metier", "certificat", "disponible", "distance")}},
           "redeploiement": {k: red[k] for k in ("fins_de_mission", "redeployes", "taux_redeploiement",
                                                  "motifs_non_redeploye", "besoins", "avertissement")},
           "equite": equity,
           "conformite": {"besoins_soumis": sum(bool(c["soumis"]) for c in comp), "besoins": len(comp),
                          "par_besoin": [{"entreprise": c["entreprise"], "metier": c["metier"], "site": c["site"],
                                          "genre": c["genre"], "soumis": c["soumis"]} for c in comp],
                          "contact_differe_propositions": sum(1 for p in props for x in p["propositions"]
                                                              if x.get("contact_des"))}}
    import hashlib

    rep["fictif"] = True
    rep["localites"] = {"fichier": args.localites,
                        "sha256": hashlib.sha256(Path(args.localites).read_bytes()).hexdigest()}
    rep = mark(rep, fictif=True)
    Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n", "utf-8")
    detail = mark({"propositions": props, "redeploiement": red, "conformite": comp}, fictif=True)
    Path(args.out_detail).write_text(json.dumps(detail, ensure_ascii=False, indent=1, default=str) + "\n", "utf-8")
    print(json.dumps({k: rep[k] for k in ("besoins", "propositions", "redeploiement")}, ensure_ascii=False,
                     default=str)[:900])
    for name, e in equity.items():
        print(name, "permutation", {k: (v["part_p_inf_0_05"], v["p_mediane"]) for k, v in
                                    e.get("test_permutation", {}).items()})
        print(name, {k: round(v["moyenne"], 3) for k, v in e["di_ratio"].items()}, "alertes", e["tirages_avec_alerte"],
              "expérience", round(e["experience_moyenne_proposes_ans"], 1),
              {k: (round(v["moyenne"], 3), [round(x, 3) for x in v["ic95"]])
               for k, v in e.get("ecart_au_hasard_apparie", {}).items()})
    conf: Any = rep["conformite"]
    print("conformité : besoins soumis", conf["besoins_soumis"], "sur", conf["besoins"])
    return 0


def cmd_docs_week1(args: argparse.Namespace) -> int:
    """Rewrite the week-1 reports from the JSON written by the commands (every figure from a command)."""
    from proxsis.docs_week1 import write_all

    for p in write_all(Path(args.racine)):
        print("écrit :", p)
    return 0
