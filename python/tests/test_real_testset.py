"""Real test set v2: reproducible stratified draw of simap awards, rendered for annotation."""

import json
import re

from proxsis.real_testset import LANG_PROXY_FR, draw, render_text


def _rec(i, lang, vendor="Exemple Bau AG", price=250000.0, canton="VD"):
    return {
        "id": f"simap:p{i}", "publication_id": f"p{i}", "publication_number": f"{i}-02", "pub_type": "award",
        "order_type": "construction", "publication_date": "2026-09-01", "decision_date": "2026-08-25",
        "creation_language": lang, "title": {lang: "Travaux de maçonnerie" if lang == "fr" else "Baumeisterarbeiten"},
        "description": {lang: "Gros œuvre. Contact : [masqué]"}, "cpv_code": "45262500",
        "cpv_label": {lang: "Travaux de maçonnerie"}, "bkp_codes": ["211"], "bkp_labels_fr": ["Maçonnerie"],
        "order_canton": canton, "order_postal_code": "1000", "order_city": "Lausanne",
        "contracting_authority": "Ville de Lausanne", "number_of_submissions": 3,
        "vendors": [{"name": vendor, "canton": "VD", "city": "Renens", "postal_code": "1020", "country": "CH",
                     "price_chf": price, "note": {}}],
        "private_person": False, "provenance": {"url": f"https://www.simap.ch/api/x/{i}"},
    }


def test_render_in_creation_language_with_award_fields():
    fr = render_text(_rec(1, "fr"))
    assert "Adjudicataire" in fr and "Exemple Bau AG" in fr and "Lausanne" in fr and "250'000" in fr
    de = render_text(_rec(2, "de"))
    assert "Zuschlag" in de and "Baumeisterarbeiten" in de


def test_render_never_contains_contact_data():
    txt = render_text(_rec(1, "fr"))
    assert not re.search(r"[\w.+-]+@[\w-]+\.\w+", txt)
    assert "Renens" not in txt  # vendor address is not needed for annotation


def test_draw_is_reproducible_and_respects_language_quotas():
    frame = [{"project_id": f"x{i}", "publication_id": f"p{i}", "order_canton": "VD" if i % 3 else "ZH"}
             for i in range(60)]

    def fetch(item):
        i = int(item["publication_id"][1:])
        return _rec(i, "fr" if item["order_canton"] in LANG_PROXY_FR and i % 5 else "de")

    a, log_a = draw(frame, fetch, n_per_lang={"fr": 5, "de": 5}, seed=7)
    b, _ = draw(frame, fetch, n_per_lang={"fr": 5, "de": 5}, seed=7)
    assert [r["id"] for r in a] == [r["id"] for r in b]
    langs = [r["creation_language"] for r in a]
    assert langs.count("fr") == 5 and langs.count("de") == 5
    assert all(e["decision"] in ("retenu", "écarté : quota de langue atteint", "écarté : langue hors FR/DE",
                                 "écarté : pas d'adjudicataire") for e in log_a)
    c, _ = draw(frame, fetch, n_per_lang={"fr": 5, "de": 5}, seed=8)
    assert [r["id"] for r in c] != [r["id"] for r in a]


def test_items_have_no_gold_and_no_model_output():
    from proxsis.real_testset import to_annotation_item

    item = to_annotation_item(_rec(1, "fr"))
    assert set(item) >= {"id", "lang", "text", "source_url", "mention_obligatoire"}
    assert "gold" not in item and "pred" not in item
    json.dumps(item, ensure_ascii=False)


def test_draw_stops_reading_a_part_once_its_language_quota_is_full():
    frame = [{"project_id": f"x{i}", "publication_id": f"p{i}", "order_canton": "VD" if i < 50 else "ZH"}
             for i in range(100)]
    fetched = []

    def fetch(item):
        i = int(item["publication_id"][1:])
        fetched.append(i)
        return _rec(i, "fr" if i < 50 else "de")

    kept, _ = draw(frame, fetch, n_per_lang={"fr": 5, "de": 5}, seed=3)
    assert len(kept) == 10
    assert len(fetched) == 10  # no detail read once both quotas are reachable without waste


def test_frame_entry_keeps_only_the_summary_fields_needed():
    from proxsis.real_testset import frame_entry

    s = {"id": "proj", "publicationId": "pub", "publicationDate": "2026-09-01", "pubType": "award",
         "title": {"fr": "Objet"}, "procOfficeName": {"fr": "Bureau X"},
         "orderAddress": {"cantonId": "VS", "postalCode": "1950", "city": {"fr": "Sion"}}}
    e = frame_entry(s, "construction")
    assert e["order_canton"] == "VS" and e["order_city"] == {"fr": "Sion"} and e["title"] == {"fr": "Objet"}
    assert "procOfficeName" not in e and "_summary" not in e
    from proxsis.real_testset import summary_from_frame

    back = summary_from_frame(e)
    assert back["orderAddress"]["city"] == {"fr": "Sion"} and back["id"] == "proj"


def test_frame_titles_are_filtered_before_writing():
    from proxsis.real_testset import frame_entry

    s = {"id": "p", "publicationId": "q", "title": {"fr": "Villa de M. Jean Exemple, rue du Lac 3"},
         "orderAddress": {"cantonId": "VS"}}
    e = frame_entry(s, "construction")
    assert "Jean Exemple" not in e["title"]["fr"]
