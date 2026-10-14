"""Candidate proposals for the estimated needs of real companies (FICTIONAL candidates)."""

from datetime import date

from proxsis.proposals import needs_from_call_list, propose
from proxsis.synth.candidates import generate_candidates

PLACES = [{"localite": "Martigny", "commune": "Martigny", "lat": 46.10, "lon": 7.07, "langue": "fr", "poids": 3},
          {"localite": "Sion", "commune": "Sion", "lat": 46.23, "lon": 7.36, "langue": "fr", "poids": 4},
          {"localite": "Visp", "commune": "Visp", "lat": 46.29, "lon": 7.88, "langue": "de", "poids": 2}]
TODAY = date(2026, 10, 5)


def _list():
    return {"as_of": "2026-10-05", "entreprises": [
        {"id": "ent-a", "nom": "Exemple SA", "ville": "Sion",
         "besoin": [{"semaine": "2026-10-19", "metier": "macon", "personnes_bas": 1, "personnes_milieu": 2,
                     "personnes_haut": 3},
                    {"semaine": "2026-10-26", "metier": "macon", "personnes_bas": 1, "personnes_milieu": 2,
                     "personnes_haut": 3},
                    {"semaine": "2026-10-26", "metier": "grutier", "personnes_bas": 0.2, "personnes_milieu": 0.4,
                     "personnes_haut": 0.6}]},
        {"id": "ent-b", "nom": "Ailleurs AG", "ville": "Inconnu", "besoin": [
            {"semaine": "2026-10-19", "metier": "macon", "personnes_bas": 1, "personnes_milieu": 1,
             "personnes_haut": 1}]}], "surprises": []}


def test_needs_are_one_per_company_and_trade_at_the_first_week_and_need_a_known_place():
    needs, skipped = needs_from_call_list(_list(), PLACES)
    assert {(n.company_id, n.trade) for n in needs} == {("ent-a", "macon"), ("ent-a", "grutier")}
    assert next(n for n in needs if n.trade == "macon").start == date(2026, 10, 19)
    assert skipped == [{"entreprise": "ent-b", "motif": "localité introuvable dans le répertoire swisstopo"}]


def test_proposals_explain_cct_category_mission_end_and_the_strict_criteria_funnel():
    cands = generate_candidates(PLACES, today=TODAY, n=300, seed=3)
    needs, _ = needs_from_call_list(_list(), PLACES)
    p = propose(cands, next(n for n in needs if n.trade == "macon"), k=5)
    assert 1 <= len(p["propositions"]) <= 5
    f = p["entonnoir"]
    assert f["tous"] == 300 and f["tous"] >= f["metier"] >= f["certificat"] >= f["disponible"] >= f["distance"]
    for s in p["propositions"]:
        assert s["libelle"].endswith("(FICTIF)")
        assert any("CCT" in r for r in s["raisons_fr"]) and any("GAV" in r for r in s["raisons_de"])
        assert s["categorie_cct"] in {"non_qualifie", "specialise", "qualifie"}
        assert s["salaire_minimum_cct_ls_heure"] is None or s["salaire_minimum_cct_ls_heure"] > 20
    assert p["fictif"] is True and "consultant" in p["note"]


def test_protected_attributes_never_change_a_proposal():
    cands = generate_candidates(PLACES, today=TODAY, n=300, seed=3)
    needs, _ = needs_from_call_list(_list(), PLACES)
    a = propose(cands, needs[0], k=5)
    shuffled = cands.copy()
    for col in ("audit_gender", "audit_age_band", "audit_nationality_group"):
        shuffled[col] = shuffled[col].sample(frac=1.0, random_state=0).to_numpy()
    b = propose(shuffled, needs[0], k=5)
    assert [s["candidate_id"] for s in a["propositions"]] == [s["candidate_id"] for s in b["propositions"]]


def test_wage_and_announcement_delay_on_proposals():
    cands = generate_candidates(PLACES, today=TODAY, n=300, seed=3)
    needs, _ = needs_from_call_list(_list(), PLACES)
    macon = next(n for n in needs if n.trade == "macon")
    p = propose(cands, macon, k=5, today=TODAY)
    for s in p["propositions"]:
        assert s["salaire_minimum_cct_ls_heure"] is None and s["cct_applicable"].startswith("CN")
    assert p["annonce"]["soumis"] is False  # mason: not on the 2026 list
    plat = propose(cands, macon.__class__("ent-a", "platrier", macon.lat, macon.lon, macon.start), k=5, today=TODAY)
    assert plat["annonce"]["soumis"] is True and plat["annonce"]["publication_libre"] == "2026-10-13"
    for s in plat["propositions"]:
        if not s["inscrit_orp"]:
            assert any("13.10.2026" in r for r in s["raisons_fr"])


def test_the_reporting_line_comes_last_exactly_when_the_contact_must_wait():
    # the web dossier (apps/web/src/presentation/dossier.ts) relies on it: it shows the reporting duty once, in its
    # checks, and drops this last line from the person's criteria when contact_des is set
    cands = generate_candidates(PLACES, today=TODAY, n=300, seed=3)
    needs, _ = needs_from_call_list(_list(), PLACES)
    macon = next(n for n in needs if n.trade == "macon")
    for trade in ("platrier", "macon"):
        p = propose(cands, macon.__class__("ent-a", trade, macon.lat, macon.lon, macon.start), k=5, today=TODAY)
        for s in p["propositions"]:
            waits = s["contact_des"] is not None
            assert s["raisons_fr"][-1].startswith("Poste soumis à l'obligation d'annonce") is waits
            assert s["raisons_de"][-1].startswith("Meldepflichtige Stelle") is waits
            assert sum(r.startswith("Poste soumis") for r in s["raisons_fr"]) == int(waits)
