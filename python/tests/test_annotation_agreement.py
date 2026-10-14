import json

import pytest

from proxsis.annotation_agreement import agreement, cohen_kappa, freeze, merge_gold


def _a(i, who, **g):
    base = {"doc_type": "adjudication", "company_name": "Bau AG", "uid": None, "commune": "Sion", "amount_chf": 1000.0,
            "rc_subtype": None, "trades": ["macon"], "private_person": False, "besoin_temporaire": "oui",
            "commentaire": None}
    return {"id": f"x{i}", "lang": "fr", "annotateur": who, "annotated_at": "t", "gold": base | g}


def test_cohen_kappa_perfect_and_chance():
    assert cohen_kappa(["a", "b", "a", "b"], ["a", "b", "a", "b"]) == pytest.approx(1.0)
    assert cohen_kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"]) == pytest.approx(0.0)


def test_agreement_normalises_names_and_amounts_and_lists_disagreements():
    A = [_a(1, "A"), _a(2, "A", company_name="Exemple SA"), _a(3, "A", trades=["macon", "electricien"])]
    B = [_a(1, "B", company_name="BAU  AG", amount_chf=1005.0), _a(2, "B", company_name="Autre SA"),
         _a(3, "B", trades=["macon"])]
    rep, dis = agreement(A, B)
    assert rep["n_commun"] == 3
    assert rep["accord_exact"]["company_name"] == pytest.approx(2 / 3)
    assert rep["accord_exact"]["amount_chf"] == pytest.approx(2 / 3)  # montants : accord EXACT (consigne du 2026-10-05)
    assert {d["id"] for d in dis} == {"x1", "x2", "x3"}
    assert "trades_jaccard_moyen" in rep and rep["kappa_par_metier"]["electricien"] is not None


def test_merge_uses_arbitration_for_disagreements_only():
    A = [_a(1, "A"), _a(2, "A", company_name="Exemple SA")]
    B = [_a(1, "B"), _a(2, "B", company_name="Autre SA")]
    agreement(A, B)
    arb = [_a(2, "C", company_name="Exemple SA")]
    gold = merge_gold(A, B, arb)
    assert [g["gold"]["company_name"] for g in gold] == ["Bau AG", "Exemple SA"]
    with pytest.raises(ValueError):
        merge_gold(A, B, [])  # unresolved disagreement


def test_freeze_writes_hash_line(tmp_path):
    items = [{"id": "x1", "lang": "fr", "text": "t"}]
    gold = [_a(1, "A")]
    frozen = tmp_path / "FROZEN.md"
    frozen.write_text("# Jeux de test gelés\n\n| Fichier | SHA-256 | Gelé le | Contenu |\n|---|---|---|---|\n")
    path, sha = freeze(items, gold, tmp_path / "reel_v2.jsonl", frozen, note="test")
    line = json.loads(path.read_text().splitlines()[0])
    assert line["text"] == "t" and line["gold"]["company_name"] == "Bau AG"
    assert sha in frozen.read_text()
    with pytest.raises(FileExistsError):
        freeze(items, gold, tmp_path / "reel_v2.jsonl", frozen, note="test")  # a frozen set never changes


def test_dates_and_rc_subtype_are_compared():
    A = [_a(1, "A", date_evenement="2026-09-15", rc_subtype="transfert_siege")]
    B = [_a(1, "B", date_evenement="2026-09-16", rc_subtype="transfert_siege")]
    rep, dis = agreement(A, B)
    assert rep["accord_exact"]["date_evenement"] == 0.0 and rep["accord_exact"]["rc_subtype"] == 1.0
    assert "date_evenement" in dis[0]["champs"]


def test_reliability_flags_fields_where_humans_disagree():
    from proxsis.annotation_agreement import reliability

    A = [_a(i, "A", besoin_temporaire=["oui", "non"][i % 2], commune="Sion") for i in range(20)]
    B = [_a(i, "B", besoin_temporaire=["oui", "non"][(i // 2) % 2], commune="Sion") for i in range(20)]
    rel = reliability(agreement(A, B)[0])
    assert rel["commune"]["fiable"] is True and rel["commune"]["mesure"] == "accord_exact"
    assert rel["besoin_temporaire"]["fiable"] is False and rel["besoin_temporaire"]["mesure"] == "kappa"
    assert rel["besoin_temporaire"]["n"] == 20


def test_assignment_double_annotates_twenty_blind_items():
    from proxsis.annotation_agreement import assign

    items = [{"id": f"i{k}", "strate": ["bo_vs/fr", "bo_vs/de", "fosc/fr", "fosc/de"][k % 4], "collecteur": "AA"}
             for k in range(150)]
    rep = assign(items, ["AA", "BB", "CC", "DD", "EE"], n_double=20, seed=1)
    doubles = [i for i, a in rep.items() if a["second"]]
    assert len(doubles) == 20
    assert all(rep[i]["second"] != rep[i]["primaire"] for i in doubles)
    assert all(a["primaire"] != "AA" for a in rep.values())  # pas son propre relevé quand c'est possible
    assert rep == assign(items, ["AA", "BB", "CC", "DD", "EE"], n_double=20, seed=1)


def test_partial_merge_uses_primary_and_arbitrates_disagreements_on_doubles():
    from proxsis.annotation_agreement import merge_gold_partial

    primary = [_a(1, "A"), _a(2, "A", company_name="Exemple SA"), _a(3, "A")]
    second = [_a(2, "B", company_name="Autre SA")]
    with pytest.raises(ValueError):
        merge_gold_partial(primary, second, [])
    gold = merge_gold_partial(primary, second, [_a(2, "C", company_name="Exemple SA")])
    assert [g["gold"]["company_name"] for g in gold] == ["Bau AG", "Exemple SA", "Bau AG"]
    assert gold[1]["double_annotation"] is True and gold[0]["double_annotation"] is False


def test_private_freeze_commits_no_text(tmp_path):
    from proxsis.annotation_agreement import freeze_private

    items = [{"id": "x1", "lang": "fr", "text": "texte privé", "source_url": "https://amtsblattportal.ch/#!/x"}]
    frozen = tmp_path / "FROZEN.md"
    frozen.write_text("| Fichier | SHA-256 | Gelé le | Contenu |\n|---|---|---|---|\n")
    priv, pub, sha_priv, sha_pub = freeze_private(items, [_a(1, "A")], tmp_path / "textes" / "reel_v3.jsonl",
                                                  tmp_path / "reel_v3_reference.jsonl", frozen, note="n")
    assert "texte privé" in priv.read_text() and "texte privé" not in pub.read_text()
    line = json.loads(pub.read_text().splitlines()[0])
    assert line["sha256_texte"] and line["gold"]["company_name"] == "Bau AG"
    assert sha_priv in frozen.read_text() and sha_pub in frozen.read_text()


def test_kappa_is_undefined_without_variation_and_reliability_uses_raw_agreement():
    from proxsis.annotation_agreement import reliability

    assert cohen_kappa(["a", "a", "a"], ["a", "a", "a"]) is None
    A = [_a(i, "A") for i in range(10)]
    B = [_a(i, "B") for i in range(10)]
    rel = reliability(agreement(A, B)[0])
    assert rel["doc_type"]["mesure"] == "accord_brut (kappa indéfini : aucune variation)"
    assert rel["doc_type"]["valeur"] == 1.0


def test_same_annotator_twice_is_refused():
    from proxsis.annotation_agreement import merge_gold_partial

    with pytest.raises(ValueError, match="même annotateur"):
        merge_gold_partial([_a(1, "A")], [_a(1, "A")], [])


# ---------------------------------------------------------------- profiles (Bulletin officiel, decision 2026-10-06)

BO_DE = ("company_name", "private_person", "commune", "date_evenement", "date_expiration", "parcelle_mentionnee",
         "coordonnees_mentionnees")


def _bo(i, who, lang="fr", **g):
    base = {"doc_type": "permis_construire", "company_name": "Bau AG", "private_person": False, "commune": "Visp",
            "date_evenement": "2026-09-04", "date_expiration": "2026-09-24", "parcelle_mentionnee": "oui",
            "coordonnees_mentionnees": "non", "commentaire": None}
    if lang == "fr":
        base |= {"amount_chf": None, "date_debut_travaux": None, "trades": ["macon"], "besoin_temporaire": "oui"}
    return {"id": f"x{i}", "lang": lang, "annotateur": who, "annotated_at": "t", "gold": base | g}


def test_bo_de_structure_measures_only_structured_fields_never_trades():
    from proxsis.annotation_agreement import reliability

    A = [_bo(i, "A", "de", parcelle_mentionnee=["oui", "non"][i % 2]) for i in range(10)]
    B = [_bo(i, "B", "de", parcelle_mentionnee=["oui", "non"][i % 2],
             date_expiration="2026-09-25" if i == 3 else "2026-09-24") for i in range(10)]
    rep, dis = agreement(A, B, profile="bo_de_structure")
    assert rep["profil"] == "bo_de_structure"
    assert tuple(rep["accord_exact"]) == BO_DE
    assert "kappa_par_metier" not in rep and "trades_jaccard_moyen" not in rep
    assert "trade" not in json.dumps(rep)
    assert rep["kappa"]["parcelle_mentionnee"] == pytest.approx(1.0)
    assert dis == [{"id": "x3", "champs": ["date_expiration"], "A": {"date_expiration": "2026-09-24"},
                    "B": {"date_expiration": "2026-09-25"}}]
    rel = reliability(rep)
    assert tuple(rel) == BO_DE
    assert rel["date_expiration"]["mesure"] == "accord_exact" and rel["date_expiration"]["valeur"] == 0.9
    assert rel["parcelle_mentionnee"]["mesure"] == "kappa"


def test_bo_de_structure_refuses_an_export_with_fields_outside_the_profile():
    A = [_bo(1, "A", "de")]
    B = [_bo(1, "B", "de", trades=["macon"])]
    with pytest.raises(ValueError, match="hors profil"):
        agreement(A, B, profile="bo_de_structure")
    from proxsis.annotation_agreement import merge_gold_partial

    with pytest.raises(ValueError, match="hors profil"):
        merge_gold_partial(B, [], [], profile="bo_de_structure")


def test_bo_fr_measures_presence_fields_and_trades_but_not_doc_type_uid_rc():
    A = [_bo(i, "A", coordonnees_mentionnees=["oui", "non"][i % 2]) for i in range(6)]
    B = [_bo(i, "B", coordonnees_mentionnees=["oui", "non"][(i // 2) % 2]) for i in range(6)]
    rep, dis = agreement(A, B, profile="bo_fr")
    assert set(rep["accord_exact"]) == {"company_name", "private_person", "commune", "date_evenement",
                                        "date_expiration", "parcelle_mentionnee", "coordonnees_mentionnees",
                                        "amount_chf", "date_debut_travaux", "trades", "besoin_temporaire"}
    assert "coordonnees_mentionnees" in rep["kappa"] and "doc_type" not in rep["kappa"]
    assert rep["kappa_par_metier"]["macon"] is None and rep["trades_jaccard_moyen"] == 1.0
    assert {f for d in dis for f in d["champs"]} == {"coordonnees_mentionnees"}


def test_bo_merge_arbitrates_only_profile_fields():
    from proxsis.annotation_agreement import merge_gold_partial

    primary = [_bo(1, "A", "de"), _bo(2, "A", "de", commentaire="note A")]
    second = [_bo(2, "B", "de", commentaire="note B", commune="Brig")]
    with pytest.raises(ValueError, match="commune"):
        merge_gold_partial(primary, second, [], profile="bo_de_structure")
    gold = merge_gold_partial(primary, second, [_bo(2, "C", "de", commune="Visp")], profile="bo_de_structure")
    assert gold[1]["gold"]["commune"] == "Visp" and gold[1]["gold"]["commentaire"] == "note A"


def test_unknown_profile_is_refused():
    with pytest.raises(ValueError, match="profil"):
        agreement([_a(1, "A")], [_a(1, "B")], profile="inconnu")


def test_default_profile_is_unchanged():
    rep, _ = agreement([_a(1, "A")], [_a(1, "B")])
    assert rep["profil"] == "simap"
    assert set(rep["accord_exact"]) == {"doc_type", "company_name", "uid", "commune", "amount_chf", "rc_subtype",
                                        "trades", "private_person", "besoin_temporaire", "date_evenement",
                                        "date_debut_travaux"}
