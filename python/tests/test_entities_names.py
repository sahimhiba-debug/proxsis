import pytest

from proxsis.entities import (
    format_uid,
    is_legal_entity_name,
    legal_form,
    normalize_name,
    normalize_uid,
    uid_check_digit,
    uid_is_valid,
)


class TestUid:
    def test_check_digit_known_example(self):
        # Exemple courant de la documentation : CHE-123.456.788
        assert uid_check_digit("12345678") == 8

    @pytest.mark.parametrize(
        "raw",
        ["CHE-123.456.788", "che123456788", "CHE 123 456 788", "CHE-123456788 MWST", "123.456.788"],
    )
    def test_normalize_variants(self, raw):
        assert normalize_uid(raw) == "CHE123456788"

    def test_invalid_checksum_rejected(self):
        assert not uid_is_valid("CHE-123.456.789")
        assert normalize_uid("CHE-123.456.789") is None

    def test_garbage_returns_none(self):
        assert normalize_uid("") is None
        assert normalize_uid("CHE-12") is None
        assert normalize_uid(None) is None
        assert normalize_uid(float("nan")) is None

    def test_format(self):
        assert format_uid("CHE123456788") == "CHE-123.456.788"


class TestNames:
    @pytest.mark.parametrize(
        ("a", "b"),
        [
            ("Constructions Rhône SA", "CONSTRUCTIONS RHONE S.A."),
            ("Müller Bau AG", "Mueller Bau A.G."),
            ("Bâtiment & Génie civil Sàrl", "Batiment et Genie Civil SARL"),
            ("Logistik Zentrum GmbH", "Logistik-Zentrum G.m.b.H."),
        ],
    )
    def test_equivalent_names_normalize_equal(self, a, b):
        assert normalize_name(a) == normalize_name(b)

    def test_legal_form_detection(self):
        assert legal_form("Constructions Rhône SA") == "SA"
        assert legal_form("Müller Bau AG") == "AG"
        assert legal_form("Atelier Dupont Sàrl") == "SARL"
        assert legal_form("Holz GmbH") == "GMBH"
        assert legal_form("Genossenschaft Migros Wallis") == "GENOSSENSCHAFT"
        assert legal_form("Jean Dupont") is None

    @pytest.mark.parametrize(
        "name",
        [
            "Constructions Rhône SA",
            "Commune de Sion",
            "Einwohnergemeinde Visp",
            "Etat du Valais, Service de la mobilité",
            "Kanton Zürich, Hochbauamt",
            "Fondation Les Berges",
            "Bourgeoisie de Sion",
            "Coopérative d'habitation Les Pins",
            "Hôpital du Valais",
        ],
    )
    def test_legal_entities(self, name):
        assert is_legal_entity_name(name)

    @pytest.mark.parametrize(
        "name",
        ["Jean Dupont", "M. et Mme Pierre et Anne Rey", "Hans Muster", "Herr Peter Meier", "Famille Bonvin"],
    )
    def test_private_persons_not_legal_entities(self, name):
        assert not is_legal_entity_name(name)
