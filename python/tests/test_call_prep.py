"""« Préparer l'appel »: guide and e-mail where every claim is tied to its source (SYNTHETIC company)."""

from proxsis.call_prep import GUIDE_SECTIONS, HOUSE_ARGUMENTS, build_call_prep, facts_for, validate, validate_email
from proxsis.llm.base import FakeLLM

COMPANY = {
    "id": "ent-x", "nom": "Exemple Construction SA", "ville": "Sion", "n_52s": 6, "confiance": "moyenne",
    "specialite": "batiment",
    "sources": [{"date": "2026-09-20", "titre": "Ecole de Grône - CFC 211", "adjudicateur": "Commune de Grône",
                 "url_simap": "https://www.simap.ch/fr/project-detail/p1", "montant_chf": 1200000.0,
                 "phase": "gros_oeuvre"}],
    "besoin": [{"semaine": "2026-10-19", "metier": "macon", "personnes_bas": 2.0, "personnes_milieu": 3.0,
                "personnes_haut": 5.0}],
    "lots_attendus": [{"phase": "finitions", "date_p10": "2026-10-20", "date_p50": "2026-12-01",
                       "date_p90": "2027-03-01"}],
}
PROPOSALS = {"n_proposes": 4, "metier": "macon", "fictif": True}


def test_facts_are_numbered_with_url_kind_and_both_languages():
    facts = facts_for(COMPANY, PROPOSALS)
    ids = [f["id"] for f in facts]
    assert ids == list(range(1, len(facts) + 1))
    kinds = {f["type"] for f in facts}
    assert {"reel", "estimation", "maison", "fictif"} <= kinds
    for f in facts:
        assert f["fr"] and f["de"] and f["url"]
    award = facts[0]
    assert "Ecole de Grône" in award["fr"] and award["url"].startswith("https://www.simap.ch/")


def test_house_arguments_are_only_verified_ones_with_scope():
    texts = " ".join(a["fr"] for a in HOUSE_ARGUMENTS)
    assert "Try & Hire" in texts and "journée test" in texts
    test_day = next(a for a in HOUSE_ARGUMENTS if "journée test" in a["fr"])
    assert "Lausanne Bâtiment" in test_day["portee"]["fr"]  # published for one agency only
    assert "Lausanne Bâtiment" in test_day["portee"]["de"]
    assert all(a["sources"] and all(u.startswith("https://") for u in a["sources"]) for a in HOUSE_ARGUMENTS)


def test_template_guide_and_email_cite_sources_in_both_languages():
    out = build_call_prep(COMPANY, PROPOSALS, provider=None)
    for lang in ("fr", "de"):
        g = out[lang]["guide"]
        assert g and all("texte" in s and "sources" in s for sec in g for s in sec["phrases"])
        cited = {i for sec in g for s in sec["phrases"] for i in s["sources"]}
        assert cited <= {f["id"] for f in out["faits"]}
        assert out[lang]["email"]["objet"] and out[lang]["email"]["phrases"]
    assert out["redaction"]["fournisseur"] == "modèle de texte (faux fournisseur)"


def test_guide_sections_carry_the_same_stable_codes_in_both_languages():
    out = build_call_prep(COMPANY, PROPOSALS, provider=None)
    codes = {lang: [sec["code"] for sec in out[lang]["guide"]] for lang in ("fr", "de")}
    assert codes["fr"] == codes["de"]
    assert codes["fr"][0] == "ouverture" and "questions" in codes["fr"]
    assert codes["fr"] == [c for c in GUIDE_SECTIONS if c in codes["fr"]]  # known codes, in the order of the call


def test_validator_rejects_invented_numbers_and_unknown_sources():
    facts = facts_for(COMPANY, PROPOSALS)
    ok = [{"texte": "Vous avez remporté 6 marchés publics en un an.", "sources": [2]}]
    assert validate(ok, facts, "fr")[0]
    bad_num = [{"texte": "Vous avez remporté 9 marchés publics en un an.", "sources": [2]}]
    assert not validate(bad_num, facts, "fr")[0]
    bad_src = [{"texte": "Vous avez remporté 6 marchés.", "sources": [99]}]
    assert not validate(bad_src, facts, "fr")[0]
    unsourced_claim = [{"texte": "Nous plaçons des maçons en deux heures.", "sources": []}]
    assert not validate(unsourced_claim, facts, "fr")[0]
    question = [{"texte": "Quand démarrez-vous le chantier ?", "sources": []}]
    assert validate(question, facts, "fr")[0]


def test_a_provider_that_invents_falls_back_to_the_template_and_says_why():
    liar = FakeLLM(lambda system, user: {"phrases": [{"texte": "Nous avons 50 maçons libres demain.", "sources": []}]})
    liar.name = "apertus"
    out = build_call_prep(COMPANY, PROPOSALS, provider=liar)
    assert out["redaction"]["fournisseur"] == "modèle de texte (faux fournisseur)"
    assert "rejeté" in out["redaction"]["note"]


def test_a_faithful_provider_is_kept_and_named():
    # a short courtesy formula of the closed list (« Bonjour, ici l'agence. » is no longer one: audit M2)
    echo = FakeLLM(lambda system, user: {"phrases": [{"texte": "Madame, Monsieur,", "sources": []},
                                                     {"texte": "Vous avez remporté 6 marchés publics en un an.",
                                                      "sources": [2]}]})
    echo.name = "apertus"
    echo.model = "swiss-ai/apertus-v1.5-8b"
    out = build_call_prep(COMPANY, PROPOSALS, provider=echo)
    assert out["redaction"]["fournisseur"].startswith("Apertus")


# ---------------------------------------------------------------- audit semaine 2, M2 and M3
def test_audit_m2_invented_promises_are_rejected_even_as_courtesy_question_or_cited():
    facts = facts_for(COMPANY, PROPOSALS)
    try_hire = next(f["id"] for f in facts if f.get("code") == "try_hire")
    for phrase in (
        {"texte": "Merci de nous faire confiance : nous garantissons les meilleurs ouvriers du Valais.", "sources": []},
        {"texte": "Saviez-vous que Flexsis est le premier groupe RH de Suisse ?", "sources": []},
        {"texte": "Try & Hire : sans frais, et nous vous livrons une équipe complète dès demain.",
         "sources": [try_hire]},
    ):
        assert not validate([phrase], facts, "fr")[0], phrase["texte"]
    # the closed list of courtesy formulas still passes, and so does a plain question
    polite = [{"texte": "Meilleures salutations,", "sources": []},
              {"texte": "Seriez-vous disponible pour un court échange cette semaine ?", "sources": []}]
    assert validate(polite, facts, "fr")[0]


def test_audit_m2_subject_is_neutral_cut_at_a_word_and_has_a_fallback():
    long_title = "Construction d'un nouveau bâtiment scolaire avec salle de gymnastique double et abri PCi"
    company = {**COMPANY, "sources": [{**COMPANY["sources"][0], "titre": long_title}]}
    out = build_call_prep(company, PROPOSALS, provider=None)
    fr, de = out["fr"]["email"]["objet"], out["de"]["email"]["objet"]
    assert "disponible" not in fr and "verfügbar" not in de and "qualifié" not in fr
    assert fr.endswith("un échange sur vos besoins en personnel ?") and "…" in fr
    cut = fr.split("« ")[1].split(" »")[0].rstrip("…")
    assert long_title.startswith(cut) and long_title[len(cut)] == " "  # cut between two words
    assert validate_email(out["fr"]["email"], out["faits"], "fr")[0]
    empty = build_call_prep({**COMPANY, "sources": [{**COMPANY["sources"][0], "titre": ""}]}, PROPOSALS, provider=None)
    assert "«  »" not in empty["fr"]["email"]["objet"] and "«»" not in empty["de"]["email"]["objet"]
    promise = {**out["fr"]["email"], "objet": "Du personnel qualifié disponible dès demain"}
    assert not validate_email(promise, out["faits"], "fr")[0]


def test_audit_m2_lausanne_arguments_stay_out_of_the_valais_guide_and_facts():
    out = build_call_prep(COMPANY, PROPOSALS, provider=None)
    for lang in ("fr", "de"):
        texts = " ".join(s["texte"] for sec in out[lang]["guide"] for s in sec["phrases"])
        assert "Lausanne" not in texts
    assert not any("Lausanne" in str(f.get("portee", "")) for f in out["faits"])


def test_audit_m3_the_need_shows_trades_and_period_never_a_headcount():
    facts = facts_for(COMPANY, PROPOSALS)
    need = next(f for f in facts if f.get("code") == "besoin")
    assert "personnes" not in need["fr"].replace("nombre de personnes non estimé", "")
    assert "nombre de personnes non estimé" in need["fr"] and "à confirmer" in need["fr"]
    assert "Anzahl Personen nicht geschätzt" in need["de"]
    assert need["url"] == "app:/mesures#BESOIN-1"


# ---------------------------------------------------------------- design critique, round 1 (07.10.2026)
def test_the_email_carries_published_facts_and_questions_never_the_estimate_nor_the_tool():
    out = build_call_prep(COMPANY, PROPOSALS, provider=None)
    estimates = {f["id"] for f in out["faits"] if f["type"] == "estimation"}
    signatures = {"fr": ["[votre nom]", "Flexsis [votre agence]"], "de": ["[Ihr Name]", "Flexsis [Ihre Filiale]"]}
    for lang, slots in signatures.items():
        email = out[lang]["email"]
        texts = [p["texte"] for p in email["phrases"]]
        assert not estimates & {i for p in email["phrases"] for i in p["sources"]}
        assert not any("Proxsis" in t or "Estimation" in t or "Schätzung" in t for t in texts)
        assert texts[-2:] == slots  # the consultant signs
        assert "Ecole de Grône - CFC 211" in texts[1] and "20.09.2026" in texts[1]
        assert validate_email(email, out["faits"], lang)[0]


def test_each_fact_names_its_source_and_scope_in_both_languages():
    facts = facts_for(COMPANY, PROPOSALS)
    for f in facts:
        assert set(f["source"]) == {"fr", "de"} and f["source"]["fr"] and f["source"]["de"]
        if "portee" in f:
            assert set(f["portee"]) == {"fr", "de"}
    german = " ".join(f["source"]["de"] + " " + f.get("portee", {}).get("de", "") for f in facts)
    for french in ("lots publiés", "phasage", "candidats fictifs", "réseau", "hypothèses"):
        assert french not in german


def test_only_cited_sources_are_listed_and_a_total_leads_to_the_dossier():
    out = build_call_prep(COMPANY, PROPOSALS, provider=None)
    cited = {i for lang in ("fr", "de") for sec in out[lang]["guide"] for p in sec["phrases"] for i in p["sources"]}
    cited |= {i for lang in ("fr", "de") for p in out[lang]["email"]["phrases"] for i in p["sources"]}
    assert cited == {f["id"] for f in out["faits"]}
    total = next(f for f in out["faits"] if f.get("code") == "frequence")
    assert total["url"] == "app:/entreprise/ent-x#fx-timeline"
    award = next(f for f in out["faits"] if f.get("code") == "adjudication")
    assert "CHF 1'200'000" in award["fr"]  # Swiss separator, as in the dossier


def test_a_line_of_slots_is_not_a_claim_but_a_sentence_around_a_slot_is():
    facts = facts_for(COMPANY, PROPOSALS)
    signature = [{"texte": "[votre nom]", "sources": []}, {"texte": "Flexsis [votre agence]", "sources": []}]
    assert validate(signature, facts, "fr")[0]
    assert not validate([{"texte": "[votre nom], le meilleur placeur du Valais", "sources": []}], facts, "fr")[0]
