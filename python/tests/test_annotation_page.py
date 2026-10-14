import json
import re

from proxsis.annotation_page import build_page
from proxsis.taxonomy import TRADES

ITEMS = [
    {"id": "simap:a", "lang": "fr", "text": "Adjudication — objet </script><script>alert(1)</script>",
     "source_url": "https://www.simap.ch/fr/project-detail/x", "mention_obligatoire": "Ceci n'est pas…",
     "order_type": "construction", "publication_date": "2026-09-01"},
    {"id": "simap:b", "lang": "de", "text": "Zuschlag — Baumeisterarbeiten", "source_url": "https://www.simap.ch/de/p/y",
     "mention_obligatoire": "Ceci n'est pas…", "order_type": "service", "publication_date": "2026-09-02"},
]


def test_page_embeds_items_and_all_trades():
    html = build_page(ITEMS, title="Jeu réel v2")
    assert "simap:a" in html and "simap:b" in html
    for code in TRADES:
        assert code in html


def test_page_cannot_be_broken_by_item_text():
    html = build_page(ITEMS, title="t")
    assert "</script><script>alert(1)" not in html
    data = re.search(r'<script id="items" type="application/json">(.*?)</script>', html, re.S)
    assert data is not None
    assert json.loads(data.group(1))[0]["text"].endswith("</script><script>alert(1)</script>")


def test_page_contains_no_gold_or_model_output():
    html = build_page(ITEMS, title="t")
    assert '"gold"' not in html.split('<script id="items"')[1].split("</script>")[0]
    assert "pred" not in html.split('<script id="items"')[1].split("</script>")[0]


def test_page_is_self_contained():
    html = build_page(ITEMS, title="t")
    assert not re.search(r'<script[^>]+src=|<link[^>]+href="http', html)


def test_page_supports_all_document_types_rc_subtypes_and_dates():
    from proxsis.models.m3_extraction import DOC_TYPES, RC_SUBTYPES

    html = build_page(ITEMS, title="t")
    for code in (*DOC_TYPES, *RC_SUBTYPES):
        assert f'value="{code}"' in html
    assert 'id="date_evenement"' in html and 'id="date_debut_travaux"' in html
    assert "guide_annotation.md" in html


def test_items_default_doc_type_comes_from_metadata_not_a_model():
    html = build_page([ITEMS[0] | {"doc_type_indicatif": "registre_commerce"}], title="t")
    assert "doc_type_indicatif" in html


# ---------------------------------------------------------------- profiles (Bulletin officiel, decision 2026-10-06)

BO_ITEMS = [
    {"id": "bo_vs:fictif-fr", "lang": "fr", "text": "Texte FICTIF. requerant : Exemple SA\nparcelle : [masqué]",
     "source_url": "https://amtsblattportal.ch/#!/x", "mention_obligatoire": "Bulletin officiel du Valais",
     "order_type": "BA-VS05", "publication_date": "2026-09-04", "doc_type_indicatif": "permis_construire"},
]
BO_FR = ("company_name", "private_person", "commune", "date_evenement", "date_expiration", "parcelle_mentionnee",
         "coordonnees_mentionnees", "amount_chf", "date_debut_travaux", "trades", "besoin_temporaire", "commentaire")
BO_DE = ("company_name", "private_person", "commune", "date_evenement", "date_expiration", "parcelle_mentionnee",
         "coordonnees_mentionnees", "commentaire")


def _profile_config(html):
    data = re.search(r'<script id="profile" type="application/json">(.*?)</script>', html, re.S)
    assert data is not None
    return json.loads(data.group(1))


def test_default_profile_is_the_simap_page():
    import pytest

    assert build_page(ITEMS, title="t") == build_page(ITEMS, title="t", profile="simap")
    html = build_page(ITEMS, title="t")
    for field in ("doc_type", "rc_subtype", "uid", "company_name", "amount_chf", "date_debut_travaux"):
        assert f'id="{field}"' in html
    assert "voir sur simap.ch" in html and "Métiers" in html
    with pytest.raises(ValueError, match="profil"):
        build_page(ITEMS, title="t", profile="inconnu")


def test_bo_fr_profile_annotates_presence_of_parcel_and_coordinates_never_their_value():
    html = build_page(BO_ITEMS, title="t", profile="bo_fr")
    cfg = _profile_config(html)
    assert tuple(f["id"] for f in cfg["fields"]) == BO_FR
    assert cfg["fixed"] == {"doc_type": "permis_construire"}
    kinds = {f["id"]: f for f in cfg["fields"]}
    for f in ("parcelle_mentionnee", "coordonnees_mentionnees"):
        assert kinds[f]["kind"] == "choice" and [o["value"] for o in kinds[f]["options"]] == ["oui", "non"]
        assert kinds[f]["required"] is True
    assert kinds["date_expiration"]["kind"] == "date" and "Expiration du délai" in kinds["date_expiration"]["label"]
    assert kinds["besoin_temporaire"]["required"] is True
    assert {t["code"] for g in kinds["trades"]["groups"] for t in g["trades"]} == set(TRADES)
    for absent in ('id="doc_type"', 'id="uid"', 'id="rc_subtype"', "simap"):
        assert absent not in html
    assert "<html lang=\"fr\">" in html and "guide_annotation.md" in html


def test_bo_de_structure_profile_has_no_trade_field_and_a_visible_note():
    html = build_page([BO_ITEMS[0] | {"lang": "de"}], title="t", profile="bo_de_structure")
    cfg = _profile_config(html)
    assert tuple(f["id"] for f in cfg["fields"]) == BO_DE
    assert "Métiers" not in html and "trade" not in html
    for absent in ("amount_chf", "date_debut_travaux", "besoin", 'id="doc_type"', 'id="uid"', "rc_subtype"):
        assert absent not in html
    note = ("Lot allemand : seuls les champs structurés sont annotés ; métiers non mesurés. Ne pas utiliser de "
            "traduction automatique. Glossaire : docs/annotation/glossaire_bo_de_fr.md")
    assert note in html
    assert "<html lang=\"fr\">" in html


def test_bo_pages_cannot_be_broken_by_item_text_and_stay_self_contained():
    evil = BO_ITEMS[0] | {"text": "x </script><script>alert(1)</script>"}
    for profile in ("bo_fr", "bo_de_structure"):
        html = build_page([evil], title="t", profile=profile)
        assert "</script><script>alert(1)" not in html
        assert not re.search(r'<script[^>]+src=|<link[^>]+href="http', html)


def test_write_page_passes_the_profile(tmp_path):
    from proxsis.annotation_page import write_page

    src = tmp_path / "items.jsonl"
    src.write_text(json.dumps(BO_ITEMS[0]) + "\n", "utf-8")
    assert write_page(src, tmp_path / "p.html", title="t", profile="bo_de_structure") == 1
    assert "trade" not in (tmp_path / "p.html").read_text("utf-8")
