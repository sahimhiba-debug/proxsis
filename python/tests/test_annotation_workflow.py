"""End to end on SYNTHETIC items: assignment → per-annotator pages → agreement → arbitration → private freeze."""

import json

from proxsis import annotation_workflow as aw


def _items(n=30):
    return [{"id": f"manuel:bo_vs:{k:03d}", "lang": "fr" if k % 3 else "de",
             "strate": "bo_vs/fr" if k % 3 else "bo_vs/de",
             "collecteur": ["AA", "BB"][k % 2], "text": f"Texte FICTIF {k}. Requérant : Exemple {k} SA.",
             "source_url": f"https://amtsblattportal.ch/#!/x/{k}", "doc_type_indicatif": "permis_construire"}
            for k in range(n)]


def _gold(company):
    return {"doc_type": "permis_construire", "company_name": company, "uid": None, "commune": "Sion",
            "amount_chf": None, "rc_subtype": None, "trades": ["macon"], "private_person": False,
            "besoin_temporaire": "oui", "date_evenement": None, "date_debut_travaux": None, "commentaire": None}


def test_full_workflow_keeps_texts_private(tmp_path):
    items = _items()
    pub, priv = tmp_path / "public", tmp_path / "prive"
    rep = aw.prepare(items, ["AA", "BB", "CC"], public_dir=pub, private_dir=priv, n_double=6, seed=2)
    assert (pub / "repartition.json").exists() and not list(pub.glob("*.html"))
    pages = sorted(priv.glob("pages/annotation_*.html"))
    assert len(pages) == 3
    assert "Texte FICTIF" not in (pub / "repartition.json").read_text()
    # each annotator annotates what the page gave them; CC disagrees on one double item
    exports = []
    for who in ("AA", "BB", "CC"):
        rows = []
        for iid, a in rep.items():
            if who in (a["primaire"], a["second"]):
                company = "Autre SA" if (who == a["second"] and iid == sorted(rep)[0]) else "Exemple SA"
                rows.append({"id": iid, "lang": "fr", "annotateur": who, "annotated_at": "t", "gold": _gold(company)})
        f = tmp_path / f"annotations_{who}.jsonl"
        f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        exports.append(f)
    acc = aw.agreement_step(exports, pub / "repartition.json", items, public_dir=pub, private_dir=priv)
    assert acc["n_commun"] == 6
    assert (pub / "accord.json").exists() and (priv / "pages" / "arbitrage.html").exists()
    rel = json.loads((pub / "accord.json").read_text())["fiabilite"]
    assert "company_name" in rel
    first = sorted(rep)[0]
    if rep[first]["second"]:
        arb = tmp_path / "arbitrage.jsonl"
        arb.write_text(json.dumps({"id": first, "annotateur": "DD", "gold": _gold("Exemple SA")}) + "\n")
    else:
        arb = None
    frozen = tmp_path / "FROZEN.md"
    frozen.write_text("| Fichier | SHA-256 | Gelé le | Contenu |\n|---|---|---|---|\n")
    out = aw.freeze_step(exports, pub / "repartition.json", items, arb, public_dir=pub, private_dir=priv,
                         frozen_md=frozen, name="reel_v3")
    assert "Texte FICTIF" not in out["public"].read_text() and "Texte FICTIF" in out["prive"].read_text()
    assert out["sha_prive"] in frozen.read_text()


def _bo_gold(commune, lang):
    g = {"doc_type": "permis_construire", "company_name": "Exemple AG", "private_person": False, "commune": commune,
         "date_evenement": "2026-09-04", "date_expiration": "2026-09-24", "parcelle_mentionnee": "oui",
         "coordonnees_mentionnees": "oui", "commentaire": None}
    if lang == "fr":
        g |= {"amount_chf": None, "date_debut_travaux": None, "trades": ["macon"], "besoin_temporaire": "oui"}
    return g


def test_profile_is_recorded_in_the_assignment_and_reused_for_agreement_and_freeze(tmp_path):
    items = [it | {"lang": "de", "strate": "bo_vs/de"} for it in _items(12)]
    pub, priv = tmp_path / "public", tmp_path / "prive"
    rep = aw.prepare(items, ["A1", "A2"], public_dir=pub, private_dir=priv, n_double=4, seed=3,
                     profile="bo_de_structure")
    assert rep == aw.prepare(items, ["A1", "A2"], public_dir=tmp_path / "p2", private_dir=tmp_path / "q2", n_double=4,
                             seed=3)  # who annotates what does not depend on the profile
    assert json.loads((pub / "repartition.json").read_text())["profil"] == "bo_de_structure"
    for page in priv.glob("pages/annotation_*.html"):
        html = page.read_text()
        assert "Métiers" not in html and "trade" not in html and "Lot allemand" in html
    exports = []
    for who in ("A1", "A2"):
        rows = [{"id": i, "lang": "de", "annotateur": who, "annotated_at": "t",
                 "gold": _bo_gold("Brig" if (who == a["second"] and i == min(k for k, v in rep.items() if v["second"]))
                                  else "Visp", "de")}
                for i, a in rep.items() if who in (a["primaire"], a["second"])]
        f = tmp_path / f"annotations_{who}.jsonl"
        f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        exports.append(f)
    acc = aw.agreement_step(exports, pub / "repartition.json", items, public_dir=pub, private_dir=priv)
    assert acc["n_commun"] == 4 and acc["profil"] == "bo_de_structure"
    saved = json.loads((pub / "accord.json").read_text())
    assert "trade" not in json.dumps(saved) and "commune" in saved["fiabilite"]
    arb_html = (priv / "pages" / "arbitrage.html").read_text()
    assert "trade" not in arb_html and "Lot allemand" in arb_html
    first = min(k for k, v in rep.items() if v["second"])
    arb = tmp_path / "arbitrage.jsonl"
    arb.write_text(json.dumps({"id": first, "annotateur": "A3", "gold": _bo_gold("Visp", "de")}) + "\n")
    frozen = tmp_path / "FROZEN.md"
    frozen.write_text("| Fichier | SHA-256 | Gelé le | Contenu |\n|---|---|---|---|\n")
    out = aw.freeze_step(exports, pub / "repartition.json", items, arb, public_dir=pub, private_dir=priv,
                         frozen_md=frozen, name="bo_de_v1")
    assert out["profil"] == "bo_de_structure" and "bo_de_structure" in frozen.read_text()
    assert "trade" not in out["public"].read_text()


def test_assignment_without_profile_is_read_as_the_default(tmp_path):
    items = _items(6)
    pub, priv = tmp_path / "public", tmp_path / "prive"
    aw.prepare(items, ["AA", "BB"], public_dir=pub, private_dir=priv, n_double=2, seed=2)
    data = json.loads((pub / "repartition.json").read_text())
    assert data["profil"] == "simap"
    del data["profil"]
    (pub / "repartition.json").write_text(json.dumps(data))
    assert aw.profile_of(pub / "repartition.json") == "simap"


def test_cli_repartir_annotation_takes_a_profile(tmp_path):
    from proxsis.cli import main

    src = tmp_path / "items_de.jsonl"
    src.write_text("\n".join(json.dumps(it | {"lang": "de"}) for it in _items(8)) + "\n", "utf-8")
    pub, priv = tmp_path / "public", tmp_path / "prive"
    assert main(["repartir-annotation", "--items", str(src), "--annotateurs", "A1,A2", "--double", "2", "--seed", "5",
                 "--public", str(pub), "--prive", str(priv), "--profil", "bo_de_structure"]) == 0
    assert json.loads((pub / "repartition.json").read_text())["profil"] == "bo_de_structure"
    assert "trade" not in (priv / "pages" / "annotation_A1.html").read_text()
