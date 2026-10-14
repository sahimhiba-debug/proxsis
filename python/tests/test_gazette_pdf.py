"""Import of « Composition individuelle » PDFs of the Bulletin officiel (BA-VS05) — SYNTHETIC lines only."""

from proxsis.gazette_filter import classify_party, filter_publication
from proxsis.gazette_pdf import dedupe, link_to_index, parse_publication, split_publications


def L(texts, page=0, col=0):
    return [(page, col, float(i * 10), 40.0, t) for i, t in enumerate(texts)]


FR_PRIVATE = [
    "Demande d’autorisation de construire",
    "- Construction d'un chalet pour Jean Dupont",
    "Titre du projet de construction",
    "Construction d'un chalet",
    "Numéro pour consultation eConstruction",
    "1b23c456",
    "Requérant(e)",
    "Jean Dupont",
    "Auteur(e) de plans",
    "Marie Exemple",
    "Auteur(e) de plans - Entreprise",
    "Atelier Exemple Sàrl",
    "Parcelle",
    "Parcelle 123, No Folio 4, Section Sion",
    "Lieu-dit Les Prés",
    "Coordonnées",
    "2'595'000 1'120'000",
    "Propriétaire",
    "Jean Dupont",
    "Propriétaire",
    "Bourgeoisie de Sion",
    "Affectation(s) de la (des) zone(s)",
    "Zone à bâtir",
    "Point de contact",
    "Commune de Sion",
    "Délai de mise à disposition",
    "Expiration du délai : 07.11.2026",
]
FR_COMPANY = [
    "Demande d’autorisation de construire",
    "- Construction d'un immeuble de 12 logements",
    "Titre du projet de construction",
    "Immeuble de 12 logements",
    "Numéro pour consultation eConstruction",
    "9z88y777",
    "Requérant(e)",
    "Exemple Immobilier SA",
    "Propriétaire",
    "Commune de Fully",
    "Point de contact",
    "Commune de Fully",
    "Délai de mise à disposition",
    "Expiration du délai : 14.11.2026",
]
DE_TITLE_ONLY = [
    "Demande d’autorisation de construire",
    "- Neubau Lagerhalle",
    "Il n'existe pas de traduction pour cette publication.",
]


def test_split_and_parse_fields_in_reading_order():
    pubs = split_publications(L(FR_PRIVATE) + L(FR_COMPANY, col=1) + L(DE_TITLE_ONLY, col=2))
    assert len(pubs) == 3
    a = parse_publication(pubs[0])
    assert a["titre"] == "Construction d'un chalet pour Jean Dupont"
    assert a["numero_econstruction"] == "1b23c456" and a["expiration"] == "2026-11-07"
    assert a["roles"]["requerant"] == ["Jean Dupont"]
    assert a["roles"]["proprietaire"] == ["Jean Dupont", "Bourgeoisie de Sion"]
    assert a["roles"]["auteur_plans_entreprise"] == ["Atelier Exemple Sàrl"]
    assert a["langue"] == "fr" and a["contenu_complet"]
    de = parse_publication(pubs[2])
    assert de["langue"] == "de" and not de["contenu_complet"] and de["titre"] == "Neubau Lagerhalle"


def test_party_classification_keeps_companies_and_public_bodies_only():
    assert classify_party("Exemple Immobilier SA") == "entreprise"
    assert classify_party("Atelier Exemple Sàrl") == "entreprise"
    for name in ("Commune de Fully", "Bourgeoisie de Sion", "Fondation Les Pins", "Paroisse de Bagnes",
                 "Consortage de l'alpage de Tsijiore", "Etat du Valais", "Burgergemeinde Brig"):
        assert classify_party(name) == "public", name
    for name in ("Jean Dupont", "Dupont Jean et Marie", "Hoirie Dupont", "PPE Les Mélèzes", "Entreprise Jean Dupont"):
        assert classify_party(name) == "personne", name


def test_filter_masks_natural_persons_everywhere_before_saving():
    pub = parse_publication(split_publications(L(FR_PRIVATE))[0])
    f, masks = filter_publication(pub)
    assert f["roles"]["requerant"] == ["[masqué]"]
    assert f["roles"]["auteur_plans"] == ["[masqué]"]
    assert f["roles"]["proprietaire"] == ["[masqué]", "Bourgeoisie de Sion"]
    assert f["roles"]["auteur_plans_entreprise"] == ["Atelier Exemple Sàrl"]
    assert "Dupont" not in f["titre"] and "Dupont" not in f["texte"] and "Marie" not in f["texte"]
    assert "123" not in f["texte"] and "595" not in f["texte"]  # parcel and coordinates
    assert {m["champ"] for m in masks} >= {"requerant", "auteur_plans", "proprietaire", "titre"}
    assert all("Dupont" not in m["apercu"] for m in masks)  # previews are masked too
    assert f["entreprises_citees"] == ["Atelier Exemple Sàrl"]
    assert f["organismes_publics_cites"] == ["Bourgeoisie de Sion"]


def test_duplicates_between_files_are_detected():
    a = [parse_publication(p) | {"fichier": "a.pdf"} for p in split_publications(L(FR_PRIVATE) + L(FR_COMPANY))]
    b = [parse_publication(p) | {"fichier": "b.pdf"} for p in split_publications(L(FR_COMPANY))]
    unique, dups = dedupe(a + b)
    assert len(unique) == 2 and len(dups) == 1 and dups[0]["fichier"] == "b.pdf"
    assert unique[1]["fichiers"] == ["a.pdf", "b.pdf"]


def test_link_to_index_by_title_commune_and_expiration():
    pubs = [parse_publication(p) for p in split_publications(L(FR_PRIVATE) + L(FR_COMPANY) + L(DE_TITLE_ONLY))]
    index = [
        {"id": "11111111-1111-1111-1111-111111111111", "titres": {"fr": "Construction d'un chalet pour Jean Dupont"},
         "expiration": "2026-11-07", "date": "2026-08-14", "langue": "fr", "office": "Ville de Sion",
         "etat": "PUBLISHED"},
        {"id": "22222222-2222-2222-2222-222222222222", "titres": {"fr": "Construction d'un immeuble de 12 logements"},
         "expiration": "2026-11-14", "date": "2026-08-21", "langue": "fr", "office": "Commune de Fully - Constructions",
         "etat": "PUBLISHED"},
        {"id": "33333333-3333-3333-3333-333333333333", "titres": {"de": "Neubau Lagerhalle", "fr": "Neubau Lagerhalle"},
         "expiration": "2026-12-01", "date": "2026-09-01", "langue": "de", "office": "Gemeinde Naters",
         "etat": "PUBLISHED"},
    ]
    linked, unmatched = link_to_index(pubs, index)
    assert not unmatched
    assert [x["id"] for x in linked] == [i["id"] for i in index]
    assert linked[0]["date_publication"] == "2026-08-14" and linked[1]["commune"] == "Fully"
    assert linked[2]["contenu_allemand_a_importer"] is True


def test_titles_with_en_dash_or_lone_dash_and_hyphenation():
    raw = ["Demande d’autorisation de construire", "–", "Construc-", "tion d'un garage",
           "Titre du projet de construction", "Garage", "Expiration du délai : 07.11.2026"]
    p = parse_publication(raw)
    assert p["titre"] == "Construction d'un garage"


def test_index_titles_with_portal_prefix_and_spacing_differences_still_link():
    pubs = [parse_publication(p) for p in split_publications(L(FR_COMPANY))]
    index = [{"id": "22222222-2222-2222-2222-222222222222",
              "titres": {"fr": "Demande d'autorisation de construire - Construction d'un immeuble de 12 logements",
                         "de": "Gesuch für Baubewilligung Construction d'un immeuble de 12 logements"},
              "expiration": "2026-11-14", "date": "2026-08-21", "langue": "fr", "office": "Commune de Fully",
              "etat": "PUBLISHED"}]
    linked, unmatched = link_to_index(pubs, index)
    assert len(linked) == 1 and not unmatched


def test_identical_titles_are_resolved_by_the_date_window_of_the_file():
    pubs = [parse_publication(p) | {"fichier": "x.pdf"} for p in split_publications(L(DE_TITLE_ONLY))]
    index = [{"id": f"{i}" * 8 + "-1111-1111-1111-111111111111", "titres": {"de": "Neubau Lagerhalle"},
              "expiration": "2027-01-01", "date": d, "langue": "de", "office": "Gemeinde Naters", "etat": "PUBLISHED"}
             for i, d in ((4, "2026-08-10"), (5, "2026-09-20"))]
    linked, unmatched = link_to_index(pubs, index)
    assert not linked and unmatched[0]["motif_non_relie"] == "2 correspondances possibles"
    linked, unmatched = link_to_index(pubs, index, window=("2026-09-15", "2026-09-29"))
    assert len(linked) == 1 and linked[0]["date_publication"] == "2026-09-20"


def test_republished_identical_titles_are_resolved_by_the_expiration_date():
    raw = ["Gesuch für Baubewilligung - Neubau Lagerhalle", "Titel des Bauprojekts", "Lagerhalle",
           "Ablauf der Frist: 21.09.2026"]  # about 31 days after the publication date
    pubs = [parse_publication(raw) | {"fichier": "x.pdf"}]
    index = [{"id": f"{i}" * 8 + "-1111-1111-1111-111111111111", "titres": {"de": "Neubau Lagerhalle"},
              "expiration": "2029-01-01", "date": d, "langue": "de", "office": "Gemeinde Naters", "etat": "PUBLISHED"}
             for i, d in ((4, "2026-08-21"), (5, "2026-09-04"))]
    linked, _ = link_to_index(pubs, index, window=("2026-08-01", "2026-09-30"))
    assert len(linked) == 1 and linked[0]["date_publication"] == "2026-08-21"


def test_contact_point_commune_breaks_ties():
    pubs = [parse_publication(p) for p in split_publications(L(FR_COMPANY))]
    index = [{"id": f"{i}" * 8 + "-1111-1111-1111-111111111111",
              "titres": {"fr": "Construction d'un immeuble de 12 logements"}, "expiration": "x", "date": "2026-08-21",
              "langue": "fr", "office": office, "etat": "PUBLISHED"}
             for i, office in ((6, "Ville de Sion"), (7, "Commune de Fully - Constructions"))]
    linked, _ = link_to_index(pubs, index)
    assert len(linked) == 1 and linked[0]["commune"] == "Fully"


def test_kept_company_values_are_still_redacted_for_attached_persons():
    raw = ["Demande d’autorisation de construire", "- Neubau Halle", "Requérant(e)",
           "Exemple AG, vertreten durch Herr Hans Muster", "Expiration du délai : 07.11.2026"]
    f, _ = filter_publication(parse_publication(raw))
    assert "Muster" not in f["roles"]["requerant"][0] and f["roles"]["requerant"][0].startswith("Exemple AG")
    assert all("Muster" not in e for e in f["entreprises_citees"])


DE_FULL = [
    "Gesuch für Baubewilligung - Neubau",
    "Mehrfamilienhaus mit 6 Wohnungen",
    "Titel des Bauprojekts",
    "Neubau Mehrfamilienhaus",
    "Nummer für die Konsultation eConstructi-",
    "on",
    "1a23b456",
    "Gesuchsteller",
    "Hans Muster",
    "Gesuchstellende Partei",
    "Beispiel Immobilien AG",
    "Planverfasser - Firma",
    "Architektur Beispiel GmbH",
    "Parzelle",
    "Parzellen-Nr 123, Plan Nr 4, Im Orte genannt Matte",
    "Koordinaten",
    "2'640'000 1'130'000",
    "Grundeigentümer",
    "Burgergemeinde Naters",
    "Grundeigentümer",
    "Erbengemeinschaft Muster",
    "Nutzungszone",
    "Wohnzone W3",
    "Kontaktstelle",
    "Gemeinde Naters",
    "Auflagefrist",
    "Ablauf der Frist: 01.12.2026",
]
FR_IN_DE = ["Baugesuch - Construction d'un garage", "Es gibt keine Übersetzung für diese Publikation."]


def test_german_composition_is_read_and_filtered():
    pubs = split_publications(L(DE_FULL) + L(FR_IN_DE, col=1))
    assert len(pubs) == 2
    de = parse_publication(pubs[0])
    assert de["titre"] == "Neubau Mehrfamilienhaus mit 6 Wohnungen" and de["langue"] == "de"
    assert de["contenu_complet"] and de["expiration"] == "2026-12-01" and de["numero_econstruction"] == "1a23b456"
    assert de["roles"]["requerant"] == ["Hans Muster", "Beispiel Immobilien AG"]
    f, _ = filter_publication(de)
    assert f["roles"]["requerant"] == ["[masqué]", "Beispiel Immobilien AG"]
    assert f["roles"]["proprietaire"] == ["Burgergemeinde Naters", "[masqué]"]
    assert "Muster" not in f["texte"] and "123" not in f["texte"] and "640" not in f["texte"]
    fr = parse_publication(pubs[1])
    assert fr["titre"] == "Construction d'un garage" and fr["langue"] == "fr" and not fr["contenu_complet"]


def test_german_header_variants_and_empty_rubric_lines():
    lines = L(["Baugesuch", "Baugesuch – Umbau Stall", "Titel des Bauprojekts", "Umbau",
               "Ablauf der Frist: 01.12.2026", "Gesuch für Baubewilligungen - Neubau Halle",
               "Titel des Bauprojekts", "Halle", "Baugesuch vom 12.03.2026 ergänzt",
               "Ablauf der Frist: 02.12.2026", "Gesuch für Baubewilligungxyzabcdef", "Neubau Garage",
               "Titel des Bauprojekts", "Garage", "Ablauf der Frist: 03.12.2026"])
    pubs = [parse_publication(p) for p in split_publications(lines)]
    assert [p["titre"] for p in pubs] == ["Umbau Stall", "Neubau Halle", "Neubau Garage"]
    assert all(p["langue"] == "de" and p["contenu_complet"] for p in pubs)


def test_a_title_repeated_by_the_layout_is_read_once():
    raw = ["Baugesuch – Fenstersanierung und Umbau DG MFH, Visp", "Fenstersanierung und Umbau DG MFH, Visp",
           "Fenstersanierung und Umbau", "Titel des Bauprojekts", "Umbau", "Ablauf der Frist: 01.12.2026"]
    assert parse_publication(raw)["titre"] == "Fenstersanierung und Umbau DG MFH, Visp"
    raw2 = ["Gesuch für Baubewilligung - Neubau Halle und Halle", "Titel des Bauprojekts", "Halle",
            "Ablauf der Frist: 01.12.2026"]
    assert parse_publication(raw2)["titre"] == "Neubau Halle und Halle"
