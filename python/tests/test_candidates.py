"""300 FICTIONAL candidates for the demo (tests on the generator itself)."""

from datetime import date

from proxsis.cct import cct_category
from proxsis.synth.candidates import generate_candidates

PLACES = [{"localite": "Martigny", "commune": "Martigny", "lat": 46.10, "lon": 7.07, "langue": "fr", "poids": 3},
          {"localite": "Sion", "commune": "Sion", "lat": 46.23, "lon": 7.36, "langue": "fr", "poids": 4},
          {"localite": "Visp", "commune": "Visp", "lat": 46.29, "lon": 7.88, "langue": "de", "poids": 2}]
TODAY = date(2026, 10, 5)


def test_300_fictional_profiles_without_names_and_deterministic():
    a = generate_candidates(PLACES, today=TODAY, n=300, seed=7)
    b = generate_candidates(PLACES, today=TODAY, n=300, seed=7)
    assert len(a) == 300 and a.equals(b)
    assert a["fictif"].all()
    assert not {"nom", "prenom", "name", "first_name"} & set(a.columns)
    assert a["libelle"].str.contains("FICTIF").all()
    assert a["candidate_id"].is_unique


def test_cct_category_follows_the_rule_not_chance():
    c = generate_candidates(PLACES, today=TODAY, n=300, seed=1)
    for r in c.itertuples():
        hours = [float(h) for h in r.heures_par_annee.split(";") if h]
        cat = cct_category(r.formation, r.annees_pratique, hours, r.formation_existe)
        assert cat.code == r.categorie_cct
    assert set(c["categorie_cct"]) == {"non_qualifie", "specialise", "qualifie"}


def test_mission_end_availability_permit_language_and_place():
    c = generate_candidates(PLACES, today=TODAY, n=300, seed=2)
    on = c[c["statut"] == "en_mission"]
    assert len(on) > 50
    assert all(date.fromisoformat(f) >= TODAY for f in on["fin_mission"])
    assert all(date.fromisoformat(a) > date.fromisoformat(f) for a, f in zip(on["available_from"], on["fin_mission"],
                                                                              strict=True))
    assert set(c["permis_travail"]) <= {"CH", "C", "B", "L"}
    assert c["langues"].str.len().min() >= 2
    assert set(c["localite"]) <= {p["localite"] for p in PLACES}
    # columns needed by the M5 matcher
    assert {"trades", "certifications", "available_from", "lat", "lon", "driving_licence", "max_travel_km",
            "experience_years", "audit_gender", "audit_age_band", "audit_nationality_group"} <= set(c.columns)
    # every crane operator holds the licence the trade legally requires, or is marked as not holding it
    grut = c[c["metier"] == "grutier"]
    assert grut["certifications"].str.contains("permis_grue").mean() > 0.5
