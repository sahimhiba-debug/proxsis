import pytest

from proxsis.pii import EXCLUDED_CATEGORIES, PiiFilter, redact_text


@pytest.fixture
def f():
    return PiiFilter()


class TestRubrics:
    @pytest.mark.parametrize("cat", ["faillite", "poursuite", "succession", "etat_civil"])
    def test_excluded_categories_are_dropped(self, f, cat):
        assert cat in EXCLUDED_CATEGORIES
        res = f.apply({"category": cat, "text": "Avis de ..."})
        assert res.record is None
        assert res.dropped_reason and cat in res.dropped_reason

    def test_company_mutation_kept(self, f):
        res = f.apply({"category": "registre_commerce", "text": "Nouvelle succursale à Sion."})
        assert res.record is not None


class TestFields:
    def test_private_owner_field_removed(self, f):
        rec = {
            "category": "permis_construire",
            "applicant": "Jean Dupont",
            "owner": "Jean Dupont",
            "architect": "Atelier Archi SA",
            "text": "Construction d'une villa",
        }
        out = f.apply(rec).record
        assert out is not None
        assert "owner" not in out
        assert out["applicant"] == "[particulier]"
        assert out["architect"] == "Atelier Archi SA"

    def test_company_applicant_kept(self, f):
        rec = {"category": "permis_construire", "applicant": "Lonzi Pharma AG", "text": "Neubau Halle"}
        out = f.apply(rec).record
        assert out is not None and out["applicant"] == "Lonzi Pharma AG"

    def test_owner_field_always_removed_even_if_company(self, f):
        # Minimisation : le propriétaire foncier n'est pas utile au métier
        rec = {"category": "permis_construire", "owner": "Immo SA", "text": "x"}
        out = f.apply(rec).record
        assert out is not None and "owner" not in out


class TestTextRedaction:
    @pytest.mark.parametrize(
        ("text", "forbidden"),
        [
            ("Requérant : M. Pierre Rey, rue du Rhône 1, Sion", "Pierre Rey"),
            ("Propriétaire: Madame Anne Bonvin", "Anne Bonvin"),
            ("Bauherrschaft: Herr Hans Muster, Visp", "Hans Muster"),
            ("Grundeigentümerin: Frau Erika Meier", "Erika Meier"),
            ("Personnes inscrites: Dupont, Jean, de Sion, à Sion, président, signature individuelle.", "Dupont"),
            ("Eingetragene Personen: Muster, Hans, von Bern, in Visp, Mitglied, mit Einzelunterschrift.", "Muster"),
            ("Contact: jean.dupont@exemple.ch, 079 123 45 67", "jean.dupont@exemple.ch"),
            ("Contact: 079 123 45 67", "079 123 45 67"),
            ("No AVS 756.1234.5678.97", "756.1234.5678.97"),
        ],
    )
    def test_person_data_removed(self, text, forbidden):
        out, n = redact_text(text)
        assert forbidden not in out
        assert n >= 1

    def test_company_text_untouched(self):
        text = "Adjudicataire: Constructions Rhône SA, Sion. Prix: CHF 1'250'000."
        out, n = redact_text(text)
        assert out == text
        assert n == 0

    def test_filter_redacts_text_field(self, f):
        rec = {"category": "registre_commerce", "text": "Personnes inscrites: Rey, Paul, de Sion, à Sion, gérant."}
        out = f.apply(rec).record
        assert out is not None
        assert "Rey" not in out["text"]


class TestManualCollectionFormats:
    """Formats rencontrés dans les demandes d'autorisation de construire (BO VS) et la FOSC (exemples FICTIFS)."""

    @pytest.mark.parametrize(
        "text, forbidden",
        [
            ("Requérant : Jean Exemple, Sion. Objet : construction d'une villa.", "Jean Exemple"),
            ("Auteur du projet : Paul Modèle, architecte, Sierre.", "Paul Modèle"),
            ("Auteurs des plans : Atelier Fictif, Anne Exemple", "Anne Exemple"),
            ("Gesuchsteller: Hans Muster, Visp. Projektverfasser: Peter Beispiel, Brig.", "Peter Beispiel"),
            ("Planverfasserin: Anna Muster, Naters", "Anna Muster"),
            ("Mandataire : Luc Exemple, Martigny", "Luc Exemple"),
            ("Vertreter: Hans Beispiel, Visp", "Hans Beispiel"),
            ("Exemple, Jean, ressortissant français, à Genève, associé gérant, avec signature individuelle.",
             "Exemple, Jean"),
            ("Muster, Hans, deutscher Staatsangehöriger, in Zürich, Mitglied, mit Kollektivunterschrift zu zweien.",
             "Muster, Hans"),
        ],
    )
    def test_person_names_masked(self, text, forbidden):
        out, n = redact_text(text)
        assert forbidden not in out and n >= 1

    @pytest.mark.parametrize(
        "text, kept",
        [
            ("Requérant : Exemple Construction SA, Sion. Auteur du projet : Bureau Fictif Sàrl.",
             "Exemple Construction SA"),
            ("Projektverfasser: Muster Architekten AG, Brig.", "Muster Architekten AG"),
            ("Exemple Holding SA, à Lausanne, CHE-123.456.789. Nouvelle inscription.", "Exemple Holding SA"),
        ],
    )
    def test_company_names_kept(self, text, kept):
        out, _ = redact_text(text)
        assert kept in out


def test_private_street_address_after_role_is_masked_but_commune_kept():
    out, _ = redact_text("Requérant : M. Pierre Exemple, rue du Rhône 1, Sion. Objet : villa.")
    assert "Pierre Exemple" not in out and "rue du Rhône 1" not in out
    assert "Sion" in out and "Objet : villa" in out


def test_legal_abbreviation_is_not_a_civility():
    for t in ("gemäss Art. 47 Absatz 1 IVöB 2019 i.v.M. Art. XI Abs. 2 GPA.", "Art. 21 i.V.m. Art. XI GPA."):
        out, n = redact_text(t)
        assert out == t and n == 0


# --- Format réel du BO VS (2026-10-05) : étiquette sur une ligne, valeur sur la suivante, sans « : ».
#     Texte FICTIF reproduisant la structure d'une vraie publication.
BO_VS_FICTIF = "\n".join([
    "Demande d'autorisation de construire - Création de places de parc, Val de Bagnes", "",
    "Titre du projet de construction", "Création de places de parc (dossier de régularisation)", "",
    "Numéro pour consultation eConstruction", "ab12cd34", "",
    "Requérant(e)", "Atelier Fictif S.A. ", "",  # espaces de fin de ligne comme dans le vrai texte
    "Auteur(e) de plans", "Jean Exemple ", "  ", "",
    "Auteur(e) de plans - Entreprise", "Atelier Fictif S.A. ", "",
    "Parcelle", "Parcelle 12345, No Folio 205, Lieu-dit Les Exemples", "",
    "Coordonnées", "2'579'000 1'104'000", "",
    "Propriétaire", "Paul Modèle ", "  ", "",
    "Propriétaire", "Anne-Marie Fictive ", "",
    "Point de contact", "Commune de Val de Bagnes", "Service des constructions", "",
])


def test_bo_vs_line_format_masks_persons_keeps_companies_and_commune():
    out, n = redact_text(BO_VS_FICTIF)
    for name in ("Jean Exemple", "Paul Modèle", "Anne-Marie Fictive"):
        assert name not in out
    assert out.count("Atelier Fictif S.A.") == 2
    assert "Commune de Val de Bagnes" in out and "Lieu-dit Les Exemples" in out
    assert n >= 3


def test_bo_vs_parcel_and_coordinates_are_masked_quasi_identifiers():
    out, _ = redact_text(BO_VS_FICTIF)
    assert "12345" not in out and "2'579'000" not in out


def test_bo_vs_private_applicant_on_next_line_is_masked():
    out, _ = redact_text("Requérant(e)\nPierre Fictif\n\nObjet\nVilla")
    assert "Pierre Fictif" not in out and "Villa" in out


def test_german_line_format():
    t = ("Gesuchsteller/in\nHans Beispiel\n\nGrundeigentümer/in\nAnna Muster\n\n"
         "Projektverfasser/in - Unternehmen\nMuster Bau AG\n")
    out, _ = redact_text(t)
    assert "Hans Beispiel" not in out and "Anna Muster" not in out and "Muster Bau AG" in out


def test_a_contracting_authority_that_looks_like_a_person_is_detected():
    from proxsis.pii import authority_looks_private

    assert authority_looks_private("Gaston exemplaire")  # first name not in any list, lowercase surname
    assert authority_looks_private("Exemple Rodolphe (pour la PPE)")
    for body in ("Commune de Sion", "Service de la mobilité", "Viteos SA Direction générale", "Swissgrid",
                 "Association du Foyer St-Joseph", "Ville de Sierre", "Etat du Valais", "Canton du Valais",
                 "Bourgeoisie de Sion", "Gemeinde Naters", "Fondation Les Pins"):
        assert not authority_looks_private(body), body


# Review 1 of the mission (07.10.2026, I2): common Swiss names slipped through — a business word found inside a
# surname (« Baumann », « Zimmermann », « Bussien »), a first name missing from the list, a name in capitals.
@pytest.mark.parametrize("name", ["Hans Baumann", "Peter Zimmermann", "Jean Bussien", "Kevin Rossier", "DUPONT Jean",
                                  "Jean-Pierre Dupont", "Maler Anna"])
def test_common_private_names_are_recognised(name):
    from proxsis.pii import looks_like_private_person

    assert looks_like_private_person(name), name


@pytest.mark.parametrize("name", [
    "Marti Bauunternehmung", "Garage Martin", "Holzbau Schmid", "Elektro Bitz", "Transports Rossier", "Bus Alpin",
    "Stadler Rail", "Exemple Peinture", "Implenia Schweiz", "Martin & Fils", "Rossier Frères",
    "Thermo Fisher Scientific Inc.", "Peter Metallbau", "Anna Gartenbau",
])
def test_companies_with_a_business_word_stay_companies(name):
    from proxsis.pii import looks_like_private_person

    assert not looks_like_private_person(name), name


@pytest.mark.parametrize("text, hidden, kept", [
    ("Contact: Jean Dupont, Sion", "Dupont", "Sion"),
    ("Le bureau de Monsieur DUPONT répondra.", "DUPONT", "bureau"),
    ("Adresse : c/o Jean Exemple, 1950 Sion", "Exemple", "Sion"),
    ("Livraison c/o Gérance Exemple SA, Sion", None, "Gérance Exemple SA"),
    ("Ville de Sion, p.a. Direction générale de l'enseignement", None, "Direction générale"),
    ("Etat du Valais, p.a. Service de la mobilité", None, "Service de la mobilité"),
])
def test_contacts_capitals_and_care_of_are_masked(text, hidden, kept):
    red, _ = redact_text(text)
    if hidden:
        assert hidden not in red, red
    assert kept in red, red
