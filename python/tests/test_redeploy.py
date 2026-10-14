"""« Fin de mission, prochaine mission »: FICTIONAL workers ending a mission vs real estimated needs."""

from datetime import date

import pandas as pd

from proxsis.redeploy import ending_missions, redeploy

TODAY = date(2026, 10, 5)


def _cands():
    base = {"certifications": "", "driving_licence": True, "max_travel_km": 40.0, "experience_years": 5,
            "audit_gender": "m", "audit_age_band": "26-35", "audit_nationality_group": "CH",
            "categorie_cct": "qualifie",
            "regle_cct": "al. 4", "permis_travail": "CH", "langues": "fr", "localite": "Sion", "lat": 46.23,
            "lon": 7.36, "fictif": True}
    rows = [
        base | {"candidate_id": "c1", "libelle": "Candidat·e 001 (FICTIF)", "trades": "macon", "statut": "en_mission",
                "fin_mission": "2026-10-14", "available_from": "2026-10-15"},
        base | {"candidate_id": "c2", "libelle": "Candidat·e 002 (FICTIF)", "trades": "macon", "statut": "en_mission",
                "fin_mission": "2026-10-20", "available_from": "2026-10-21"},
        base | {"candidate_id": "c3", "libelle": "Candidat·e 003 (FICTIF)", "trades": "electricien",
                "statut": "en_mission", "fin_mission": "2026-10-16", "available_from": "2026-10-17"},
        base | {"candidate_id": "c4", "libelle": "Candidat·e 004 (FICTIF)", "trades": "macon", "statut": "en_mission",
                "fin_mission": "2026-12-20", "available_from": "2026-12-21"},  # ends in more than 3 weeks
        base | {"candidate_id": "c5", "libelle": "Candidat·e 005 (FICTIF)", "trades": "macon", "statut": "disponible",
                "fin_mission": None, "available_from": "2026-10-05"},
    ]
    return pd.DataFrame(rows)


SLOTS = [{"entreprise": "ent-a", "nom": "Exemple SA", "metier": "macon", "lat": 46.23, "lon": 7.36,
          "semaines": {"2026-10-12": 1.2, "2026-10-19": 1.4, "2026-10-26": 1.0}, "source": "simap.ch"}]


def test_only_missions_ending_within_three_weeks():
    e = ending_missions(_cands(), TODAY, weeks=3)
    assert set(e["candidate_id"]) == {"c1", "c2", "c3"}


def test_redeployment_respects_capacity_trade_and_timing_and_is_labelled_fictional():
    rep = redeploy(_cands(), SLOTS, TODAY, weeks=3)
    assert rep["fictif"] is True and "FICTIF" in rep["avertissement"]
    assert rep["fins_de_mission"] == 3
    placed = {r["candidate_id"]: r for r in rep["travailleurs"] if r.get("proposition")}
    # capacity: peak mid need 1.4 → at most 2 people on ent-a / maçon; the electrician has no matching need
    assert set(placed) == {"c1", "c2"}
    assert placed["c1"]["proposition"]["entreprise"] == "ent-a"
    not_placed = next(r for r in rep["travailleurs"] if r["candidate_id"] == "c3")
    assert not_placed["motif"] == "aucun besoin prévu compatible (métier)"
    assert rep["taux_redeploiement"] == 2 / 3


def test_a_crane_operator_without_the_licence_is_not_redeployed():
    c = _cands()
    c.loc[0, "trades"] = "grutier"
    slots = [SLOTS[0] | {"metier": "grutier"}]
    rep = redeploy(c, slots, TODAY, weeks=3)
    row = next(r for r in rep["travailleurs"] if r["candidate_id"] == "c1")
    assert "proposition" not in row and row["motif_code"] == "permis"


def test_subject_posts_wait_for_the_end_of_the_restriction_unless_registered_at_the_orp():
    c = _cands()
    slots = [SLOTS[0] | {"metier": "platrier"}]
    c["trades"] = "platrier"
    c["inscrit_orp"] = False
    rep = redeploy(c, slots, TODAY, weeks=3)
    placed = [r for r in rep["travailleurs"] if r.get("proposition")]
    assert placed and all(r["proposition"]["contact_des"] == "2026-10-13" for r in placed)
