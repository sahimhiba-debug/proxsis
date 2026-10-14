"""End-to-end import of Bulletin officiel PDF compositions + bulk index (SYNTHETIC inputs, extraction faked)."""

import json

from proxsis.gazette_import import (
    annotation_items,
    draw_test_set,
    freeze_draw,
    radar_markdown,
    radar_projects,
    run_import,
)
from test_gazette_pdf import DE_TITLE_ONLY, FR_COMPANY, FR_PRIVATE, L

INDEX = """<?xml version="1.0" encoding="UTF-8"?><bulk-export>
<publication><meta><id>11111111-1111-1111-1111-111111111111</id><subRubric>BA-VS05</subRubric><language>fr</language>
<registrationOffice><displayName>Ville de Sion</displayName></registrationOffice>
<publicationState>PUBLISHED</publicationState>
<publicationDate>2026-08-14</publicationDate><expirationDate>2026-11-07</expirationDate>
<title><fr>Construction d'un chalet pour Jean Dupont</fr></title></meta></publication>
<publication><meta><id>22222222-2222-2222-2222-222222222222</id><subRubric>BA-VS05</subRubric><language>fr</language>
<registrationOffice><displayName>Commune de Fully - Constructions</displayName></registrationOffice>
<publicationState>PUBLISHED</publicationState><publicationDate>2026-08-21</publicationDate>
<expirationDate>2026-11-14</expirationDate><title><fr>Construction d'un immeuble de 12 logements</fr></title></meta>
</publication>
<publication><meta><id>33333333-3333-3333-3333-333333333333</id><subRubric>BA-VS05</subRubric><language>de</language>
<registrationOffice><displayName>Gemeinde Naters</displayName></registrationOffice>
<publicationState>PUBLISHED</publicationState>
<publicationDate>2026-09-01</publicationDate><expirationDate>2026-12-01</expirationDate>
<title><de>Neubau Lagerhalle</de></title></meta></publication>
</bulk-export>"""

ORPHAN = ["Demande d’autorisation de construire", "- Titre absent de l'index", "Titre du projet de construction",
          "Rien", "Expiration du délai : 01.12.2026"]


def _fake(files):
    return lambda p: files[p.name]


def _run(tmp_path):
    pdfs = {"a.pdf": L(FR_PRIVATE) + L(FR_COMPANY, col=1), "b.pdf": L(FR_COMPANY) + L(DE_TITLE_ONLY, col=1)
            + L(ORPHAN, col=2)}
    for n in pdfs:
        (tmp_path / n).write_bytes(b"%PDF fake")
    idx = tmp_path / "publications.xml"
    idx.write_text(INDEX, "utf-8")
    pub, priv = tmp_path / "public", tmp_path / "prive"
    rep = run_import([tmp_path / "a.pdf", tmp_path / "b.pdf"], idx, pub, priv, extract=_fake(pdfs))
    return rep, pub, priv


def test_report_counts_duplicates_acceptance_and_reasons(tmp_path):
    rep, _, _ = _run(tmp_path)
    assert rep["lues"] == 5 and rep["doublons"] == 1 and rep["uniques"] == 4
    assert rep["acceptees"] == 3
    assert rep["rejetees_par_motif"] == {"sans correspondance dans l'index XML": 1}
    assert rep["par_langue"] == {"fr": 2, "de": 1}
    assert rep["contenu_allemand_a_importer"] == 1
    assert rep["par_commune"]["Fully"] == 1 and rep["par_semaine"]
    assert rep["masquages_a_verifier"] and all("Dupont" not in m["apercu"] for m in rep["masquages_a_verifier"])


def test_public_files_never_contain_a_private_name_and_texts_stay_private(tmp_path):
    _, pub, priv = _run(tmp_path)
    for f in pub.rglob("*"):
        if f.is_file():
            content = f.read_text("utf-8")
            assert "Dupont" not in content and "Marie" not in content, f
    texts = list((priv / "textes").glob("*.txt"))
    assert len(texts) == 2  # the two French publications with full content
    assert all("Dupont" not in t.read_text("utf-8") for t in texts)
    rows = [json.loads(x) for x in (pub / "publications.jsonl").read_text("utf-8").splitlines()]
    assert {r["statut"] for r in rows} == {"acceptée", "rejetée"}


def test_draw_is_reproducible_and_by_language(tmp_path):
    _, pub, _ = _run(tmp_path)
    rows = [json.loads(x) for x in (pub / "publications.jsonl").read_text("utf-8").splitlines()]
    a = draw_test_set(rows, n=1, lang="fr", seed=7)
    b = draw_test_set(rows, n=1, lang="fr", seed=7)
    assert a == b and len(a["ids"]) == 1 and a["cadre"] == 2
    de = draw_test_set(rows, n=50, lang="de", seed=7)
    assert de["ids"] == [] and "contenu allemand" in de["note"]


def test_frozen_draw_holds_ids_and_text_hashes_only(tmp_path):
    _, pub, priv = _run(tmp_path)
    rows = [json.loads(x) for x in (pub / "publications.jsonl").read_text("utf-8").splitlines()]
    d = draw_test_set(rows, n=2, lang="fr", seed=7)
    items = annotation_items(rows, d["ids"], priv)
    target = tmp_path / "tirage_fr_gele.jsonl"
    sha = freeze_draw(items, target)
    lines = [json.loads(x) for x in target.read_text("utf-8").splitlines()]
    assert [x["id"] for x in lines] == [i["id"] for i in items]
    assert all(set(x) == {"id", "lang", "source_url", "sha256_texte"} for x in lines)
    assert sha == freeze_draw(items, tmp_path / "again.jsonl") and len(sha) == 64


def test_radar_projects_keep_company_applicants_only(tmp_path):
    _, pub, _ = _run(tmp_path)
    rows = [json.loads(x) for x in (pub / "publications.jsonl").read_text("utf-8").splitlines()]
    projects = radar_projects(rows)
    kinds = {p["id"]: p["categories"] for p in projects}
    assert "logements_collectifs" in kinds["22222222-2222-2222-2222-222222222222"]
    assert "halle" in kinds["33333333-3333-3333-3333-333333333333"]
    p = next(x for x in projects if x["id"].startswith("2222"))
    assert p["requerants_entreprises"] == ["Exemple Immobilier SA"]
    assert all("Dupont" not in json.dumps(x) for x in projects)


def test_second_homes_and_single_houses_are_not_collective_housing():
    from proxsis.gazette_import import _CATS

    rx = _CATS["logements_collectifs"]
    assert not rx.search("Construction d'un chalet (résidence secondaire)")
    assert not rx.search("Neubau Einfamilienwohnhaus")
    assert rx.search("Construction de deux immeubles de 8 logements") and rx.search("Neubau Mehrfamilienhaus")


def test_commune_name_with_elided_article():
    from proxsis.gazette_pdf import commune_of

    assert commune_of("Commune d'Ardon") == "Ardon" and commune_of("Commune d’Anniviers - Service") == "Anniviers"


def test_a_later_import_replaces_title_only_german_entries_and_keeps_the_rest(tmp_path):
    _, pub, priv = _run(tmp_path)
    full_de = ["Demande d’autorisation de construire", "- Neubau Lagerhalle", "Titre du projet de construction",
               "Neubau Lagerhalle", "Requérant(e)", "Beispiel Bau AG", "Expiration du délai : 01.12.2026"]
    (tmp_path / "de.pdf").write_bytes(b"%PDF fake")
    rep = run_import([tmp_path / "de.pdf"], tmp_path / "publications.xml", pub, priv,
                     extract=lambda p: L(full_de))
    rows = {json.loads(x)["id"]: json.loads(x) for x in (pub / "publications.jsonl").read_text("utf-8").splitlines()}
    de = rows["33333333-3333-3333-3333-333333333333"]
    assert de["contenu_complet"] and not de["contenu_allemand_a_importer"]
    assert "11111111-1111-1111-1111-111111111111" in rows and "22222222-2222-2222-2222-222222222222" in rows
    assert rep["fusion"]["remplacees"] == 1


def test_skeleton_shows_template_words_only():
    from proxsis.gazette_pdf import skeleton

    lines = L(["Requérant(e)", "Jean Dupont", "Requérant(e)", "Marie Exemple", "Requérant(e)", "Exemple SA"])
    sk = skeleton(lines, min_count=3)
    assert "Requérant(e)" in sk and "Dupont" not in sk and "Marie" not in sk and "Exemple" not in sk


def test_radar_note_is_generated_from_the_projects(tmp_path):
    _, pub, _ = _run(tmp_path)
    rows = [json.loads(x) for x in (pub / "publications.jsonl").read_text("utf-8").splitlines()]
    md = radar_markdown(radar_projects(rows), rows)
    assert "Exemple Immobilier SA" in md and "logements collectifs" in md and "Fully" in md
    assert "Dupont" not in md and "Seule la publication officielle fait foi" in md
