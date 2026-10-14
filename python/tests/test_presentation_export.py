"""Data of the « Votre prochain lundi » presentation: counts only, no title, no party (SYNTHETIC rows)."""

from proxsis.presentation_export import territory

PLACES = [{"localite": "Martigny", "commune": "Martigny", "lat": 46.10, "lon": 7.07},
          {"localite": "Martigny-Croix", "commune": "Martigny-Combe", "lat": 46.09, "lon": 7.05},
          {"localite": "Les Valettes", "commune": "Bovernier", "lat": 46.07, "lon": 7.08},
          {"localite": "Bovernier", "commune": "Bovernier", "lat": 46.08, "lon": 7.09}]


def _row(i, commune, d, statut="acceptée"):
    return {"id": f"p{i}", "statut": statut, "commune": commune, "date_publication": d, "semaine": None,
            "titre": "Nom Privé", "roles": {"requerant": ["X"]}}


def test_counts_by_commune_and_week_add_up_and_carry_no_text():
    rows = [_row(1, "Martigny", "2026-08-07"), _row(2, "Martigny", "2026-08-14"), _row(3, "Bovernier", "2026-08-14"),
            _row(4, None, "2026-08-14"), _row(5, "Atlantis", "2026-08-21"),
            _row(6, "Martigny", "2026-08-07", "rejetée"),
            _row(1, "Martigny", "2026-08-07")]  # same id twice: counted once
    t = territory(rows, PLACES)
    assert t["total_publications"] == 5 and t["n_communes"] == 2
    by = {c["commune"]: c for c in t["communes"]}
    assert by["Martigny"]["total"] == 2 and by["Martigny"]["semaines"] == {"2026-S32": 1, "2026-S33": 1}
    assert by["Bovernier"]["lat"] == 46.08  # its own locality (the commune bears its name)
    assert t["hors_carte"] == {"sans_commune": 1, "commune_non_localisee": 1}
    assert sum(c["total"] for c in t["communes"]) + sum(t["hors_carte"].values()) == t["total_publications"]
    assert "Nom Privé" not in str(t) and "requerant" not in str(t)
    assert t["periode"] == {"debut": "2026-08-07", "fin": "2026-08-21"}
    assert t["semaines"] == ["2026-S32", "2026-S33", "2026-S34"]


def test_commune_names_are_matched_without_prefix_or_canton_suffix_and_placed_on_their_own_locality():
    places = [*PLACES, {"localite": "St. Niklaus VS", "commune": "St. Niklaus", "lat": 46.18, "lon": 7.80},
              {"localite": "Raron", "commune": "Unterbäch", "lat": 46.31, "lon": 7.80},
              {"localite": "Unterbäch VS", "commune": "Unterbäch", "lat": 46.28, "lon": 7.79},
              {"localite": "Veyras", "commune": "Noble-Contrée", "lat": 46.30, "lon": 7.54}]
    rows = [_row(1, "St. Niklaus VS", "2026-08-07"), _row(2, "Unterbäch (VS)", "2026-08-07"),
            _row(3, "Commune Noble-Contrée", "2026-08-07")]
    t = territory(rows, places)
    by = {c["commune"]: c for c in t["communes"]}
    assert t["hors_carte"] == {"sans_commune": 0, "commune_non_localisee": 0}
    assert (by["Unterbäch"]["lat"], by["Unterbäch"]["lon"]) == (46.28, 7.79)  # its own locality, not Raron's
    assert set(by) == {"St. Niklaus", "Unterbäch", "Noble-Contrée"}


def test_public_award_layer_is_placed_by_postal_code_and_counted_off_map_otherwise():
    from proxsis.presentation_export import awards_layer

    places = [{"localite": "Le Châble VS", "commune": "Val de Bagnes", "npa": "1934", "lat": 46.08, "lon": 7.21},
              {"localite": "Bruson", "commune": "Val de Bagnes", "npa": "1934", "lat": 46.07, "lon": 7.23},
              {"localite": "Saxon", "commune": "Saxon", "npa": "1907", "lat": 46.15, "lon": 7.18}]
    base = {"order_canton": "VS", "pub_type": "award"}
    recs = [base | {"id": "a", "publication_date": "2026-08-12T00:00:00", "order_postal_code": "1934",
                    "project_id": "p1", "contracting_authority": "Service X", "vendors": [{"name": "Y SA"}]},
            {"id": "b", "publication_date": "2026-08-20", "order_postal_code": None, "order_canton": None},
            base | {"id": "c", "publication_date": "2026-07-01", "order_postal_code": "1907"},
            base | {"id": "a", "publication_date": "2026-08-12", "order_postal_code": "1934"}]
    layer = awards_layer(recs, places, ("2026-08-07", "2026-09-29"))
    assert layer["total"] == 2 and layer["hors_carte"] == {"sans_lieu": 1}
    assert layer["communes"] == [{"commune": "Val de Bagnes", "lat": 46.075, "lon": 7.22, "total": 1,
                                  "semaines": {"2026-S33": 1}}]
    assert "Y SA" not in str(layer) and "Service X" not in str(layer)


def test_guided_examples_are_placed_from_their_simap_record():
    from proxsis.presentation_export import example_points

    places = [{"localite": "Le Châble VS", "commune": "Val de Bagnes", "npa": "1934", "lat": 46.08, "lon": 7.21}]
    recs = [{"id": "x", "project_id": "7426f3df", "publication_date": "2026-08-12", "order_postal_code": "1934"}]
    pts = example_points(["https://www.simap.ch/fr/project-detail/7426f3df"], recs, places)
    assert pts == [{"url": "https://www.simap.ch/fr/project-detail/7426f3df", "commune": "Val de Bagnes",
                    "lat": 46.08, "lon": 7.21, "date": "2026-08-12"}]
    assert example_points(["https://www.simap.ch/fr/project-detail/inconnu"], recs, places) == []


def test_the_bulletin_mention_is_given_in_both_languages():
    t = territory([_row(1, "Martigny", "2026-08-07")], PLACES)
    assert set(t["source"]) == {"fr", "de"}
    assert "Bulletin officiel du Valais" in t["source"]["fr"] and "Amtsblatt des Kantons Wallis" in t["source"]["de"]
