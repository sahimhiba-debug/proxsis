"""Personal-data filter of the Bulletin officiel import: the 41 synthetic shapes of the week-2 audit (B2).

All names are INVENTED. A party value is cut into pieces; a piece is kept only if it is itself an organisation.
"""

import json
import re

import pytest

from proxsis.gazette_filter import PersonalDataFound, build_context, filter_publication, sweep_rows
from proxsis.gazette_pdf import parse_publication

NAMES = ("Exemple", "Modèle", "Muster", "Beispiel", "Fictif")


def _pub(role_lines, title="- Transformation d'un bâtiment", label="Requérant(e)", extra=()):
    raw = ["Demande d’autorisation de construire", title, label, *role_lines, *extra,
           "Expiration du délai : 07.11.2026"]
    return parse_publication(raw)


def _public_strings(f):
    out = [f["titre"], f.get("titre_projet") or "", *f["entreprises_citees"], *f["organismes_publics_cites"]]
    for values in f["roles"].values():
        out += values
    return out


def _leaks(f, private=True):
    strings = _public_strings(f) + ([f["texte"]] if private else [])
    return [n for n in NAMES if any(n in s for s in strings)]


ADDRESS_WITH_ORG_WORD = [
    ["Jean Exemple, Rue de l'Église 5, 1920 Martigny"],
    ["Jean Exemple", "Rue de l'Église 5, 1920 Martigny"],
    ["Jean Exemple, Route du Canton 12, 1950 Sion"],
    ["Jean Exemple, Chemin de la Paroisse 3"],
    ["Jean Exemple, Place de la Commune 1"],
    ["Jean Exemple, Rue du Service 1"],
    ["Hans Muster, bei der Kirche 3, 3900 Brig"],
]


@pytest.mark.parametrize("lines", ADDRESS_WITH_ORG_WORD)
def test_a_person_whose_address_contains_an_organisation_word_is_masked(lines):
    f, _ = filter_publication(_pub(lines))
    assert f["roles"]["requerant"] == ["[masqué]"]
    assert not _leaks(f) and not f["organismes_publics_cites"]


PERSON_WITH_COMPANY = [
    (["Jean Exemple p.a. Fiduciaire Modèle SA"], "Fiduciaire Modèle SA"),
    (["Jean Exemple c/o Atelier Beispiel SA"], "Atelier Beispiel SA"),
    (["Jean Exemple, Atelier Beispiel SA"], "Atelier Beispiel SA"),
    (["Atelier Beispiel SA, Jean Exemple"], "Atelier Beispiel SA"),
    (["Atelier Beispiel SA (Jean Exemple)"], "Atelier Beispiel SA"),
    (["Jean Exemple, Atelier Beispiel Sàrl en formation"], "Atelier Beispiel Sàrl en formation"),
    (["Hans Muster, AG Bahnhof 3"], None),
    (["Atelier Beispiel SA, vertreten durch Herr Hans Muster"], "Atelier Beispiel SA"),
]


@pytest.mark.parametrize("lines,company", PERSON_WITH_COMPANY)
def test_a_person_attached_to_a_company_is_cut_off(lines, company):
    f, _ = filter_publication(_pub(lines))
    names = [n for n in NAMES if n not in (company or "")]
    assert not [n for n in names if any(n in s for s in [*_public_strings(f), f["texte"]])]
    assert f["entreprises_citees"] == ([company] if company else [])
    assert "[masqué]" in f["roles"]["requerant"][0]


PERSON_WITH_PUBLIC_BODY = [
    (["Commune de Fully, représentée par Jean Exemple"], "Commune de Fully"),
    (["Bourgeoisie de Sion, p.a. Jean Exemple, président"], "Bourgeoisie de Sion"),
    (["Consortage de l'alpage de Tsijiore, Jean Exemple, président"], "Consortage de l'alpage de"),
    (["Jean Exemple p.a. Etat du Valais"], "Etat du Valais"),
    (["Gemeinde Ried-Brig z. Hd. Herr E. Muster"], "Gemeinde Ried-Brig"),
]


@pytest.mark.parametrize("lines,body", PERSON_WITH_PUBLIC_BODY)
def test_a_person_attached_to_a_public_body_is_cut_off(lines, body):
    f, _ = filter_publication(_pub(lines))
    assert not _leaks(f)
    assert len(f["organismes_publics_cites"]) == 1 and f["organismes_publics_cites"][0].startswith(body)


@pytest.mark.parametrize("value", ["Association Exemple-Modèle", "Fondation de famille Exemple",
                                   "Verein Hans Muster", "Hoirie Exemple", "Erbengemeinschaft Muster",
                                   "PPE Résidence Fictif", "Société simple Exemple et Modèle"])
def test_bodies_named_after_persons_do_not_leak_the_names(value):
    f, _ = filter_publication(_pub([value]))
    assert not _leaks(f), value


@pytest.mark.parametrize("title", ["- Transformation de la maison Exemple", "- Villa Exemple-Modèle",
                                   "- Chalet de Jean d’Exemple", "- Construction d'un chalet pour Mme Fictif",
                                   "- Umbau EFH Muster, Visp", "- Neubau Haus Muster Hans",
                                   "- Rénovation du chalet Xu"])
def test_titles_without_a_matching_role_are_masked_word_by_word(title):
    f, _ = filter_publication(_pub(["Atelier Beispiel SA"], title=title))
    assert not [n for n in NAMES if n != "Beispiel" and n in f["titre"]], f["titre"]
    assert "Xu" not in f["titre"] and "Hans" not in f["titre"] and "Jean" not in f["titre"]


def test_role_name_with_curly_apostrophe_is_masked_in_the_title():
    f, _ = filter_publication(_pub(["Jean d'Exemple"], title="- Chalet de Jean d’Exemple"))
    assert "Exemple" not in f["titre"]


def test_free_text_fields_are_masked_too():
    extra = ["Point de contact", "Commune de Fully, Jean Exemple, Rue de l'Église 5",
             "Dérogation(s)", "Distance à la route, accord de Hans Muster",
             "Moyen de droit / Consultation", "Opposition auprès de Marie Modèle, secrétaire"]
    f, _ = filter_publication(_pub(["Atelier Beispiel SA"], extra=extra))
    assert not [n for n in NAMES if n != "Beispiel" and n in f["texte"]]
    assert "Marie" not in f["texte"] and "Hans" not in f["texte"]


def test_unknown_role_labels_never_spill_into_the_title():
    raw = ["Demande d’autorisation de construire", "- Améliorations structurelles, chemin alpestre",
           "Requérant : Consortage de l'alpage de Tsijiore",
           "Propriétaire foncier : Jean Exemple, Domicile: 1920 Martigny",
           "Auteur du projet : Bureau Modèle SA", "Expiration du délai : 07.11.2026"]
    f, _ = filter_publication(parse_publication(raw))
    assert "Exemple" not in json.dumps(f, ensure_ascii=False)
    assert "Domicile" not in json.dumps(f, ensure_ascii=False)
    assert f["titre"].startswith("Améliorations structurelles")
    assert "Bureau Modèle SA" in f["entreprises_citees"]


def test_german_project_author_and_domicile_are_masked():
    raw = ["Gesuch für Baubewilligung - Umbau Wohnhaus", "Titel des Bauprojekts", "Umbau Wohnhaus",
           "Gesuchsteller", "Muster Hans, Wohnsitz: Brig", "Projektverfasser", "Muster Hans",
           "Beispiel Planung GmbH", "Ablauf der Frist: 01.12.2026"]
    f, _ = filter_publication(parse_publication(raw))
    assert "Muster" not in json.dumps(f, ensure_ascii=False) and "Wohnsitz" not in json.dumps(f, ensure_ascii=False)
    assert "Beispiel Planung GmbH" in f["entreprises_citees"]


def test_companies_stay_whole_and_usable():
    f, _ = filter_publication(_pub(["Exemple Immobilier SA"], title="- Construction d'un immeuble de 12 logements"))
    assert f["roles"]["requerant"] == ["Exemple Immobilier SA"]
    assert f["entreprises_citees"] == ["Exemple Immobilier SA"]
    assert f["titre"] == "Construction d'un immeuble de 12 logements"
    for name in ("Dupont & Fils SA", "Bonvin et Cie SA", "Muster und Söhne AG"):
        g, _ = filter_publication(_pub([name]))
        assert g["entreprises_citees"] == [name], name
    h, _ = filter_publication(_pub(["Atelier Exemple", "Sàrl"]))  # legal form wrapped on the next line
    assert h["entreprises_citees"] == ["Atelier Exemple Sàrl"]


def test_context_masks_a_role_name_in_every_publication():
    a = _pub(["Jean Exemple"], title="- Construction d'un garage")
    b = _pub(["Atelier Beispiel SA"], title="- Agrandissement du chalet Exemple")
    ctx = build_context([a, b], index_titles=[], localities=[])
    fb, _ = filter_publication(b, ctx)
    assert "Exemple" not in fb["titre"]


def test_frequent_title_words_and_localities_are_kept():
    a = _pub(["Atelier Beispiel SA"], title="- Neubau Mehrzweckhalle Rarnerchumma, Raron")
    titles = ["Neubau Mehrzweckhalle in Visp", "Mehrzweckhalle Rarnerchumma", "Rarnerchumma Umbau",
              "Rarnerchumma Erweiterung"]
    ctx = build_context([a], index_titles=titles, localities=["Raron"])
    f, _ = filter_publication(a, ctx)
    assert f["titre"] == "Neubau Mehrzweckhalle Rarnerchumma, Raron"


def test_sweep_blocks_leftover_person_markers():
    rows = [{"id": "x", "titre": "Chalet", "titre_projet": None, "roles": {"requerant": ["Domicile: Sion"]},
             "entreprises_citees": [], "organismes_publics_cites": []},
            {"id": "y", "titre": "Umbau Haus Hans", "titre_projet": None, "roles": {},
             "entreprises_citees": [], "organismes_publics_cites": []},
            {"id": "z", "titre": "Construction", "titre_projet": "Requérant : [masqué]", "roles": {},
             "entreprises_citees": [], "organismes_publics_cites": []}]
    with pytest.raises(PersonalDataFound) as e:
        sweep_rows(rows)
    found = {(x["publication"], x["motif"]) for x in e.value.findings}
    assert {p for p, _ in found} == {"x", "y", "z"}
    assert all("Sion" not in str(x) and "Hans" not in str(x) for x in e.value.findings)  # no value in the error
    sweep_rows([{"id": "ok", "titre": "Construction", "titre_projet": None,
                 "roles": {"requerant": ["Jean Exemple SA"]}, "entreprises_citees": ["Jean Exemple SA"],
                 "organismes_publics_cites": []}])
    place = {"id": "lieu", "titre": "Construction à Saint-Maurice", "titre_projet": None, "roles": {},
             "entreprises_citees": [], "organismes_publics_cites": []}
    with pytest.raises(PersonalDataFound):
        sweep_rows([place])
    sweep_rows([place], ctx=build_context([], [], ["Saint-Maurice"]))


def test_a_name_after_a_civility_is_masked_even_when_frequent():
    extra = ["Kontaktstelle", "Gemeinde Naters, Bauamt, z. Hd. Herr E. Muster, Tel. 027 000 00 00"]
    pubs = [_pub(["Beispiel Bau AG"], extra=extra) for _ in range(6)]  # the clerk is in every publication
    ctx = build_context(pubs, index_titles=[], localities=["Naters"])
    f, _ = filter_publication(pubs[0], ctx)
    assert "Muster" not in f["texte"] and "E. " not in f["texte"]
    sweep_rows([], {"x": f["texte"]}, ctx)
    g, _ = filter_publication(_pub(["Gemeinde Visp Frau Muster"]), ctx)
    assert "Muster" not in json.dumps(g, ensure_ascii=False)
    sweep_rows([g])


def test_a_rerun_does_not_keep_stale_rows_of_unlinked_publications(tmp_path):
    from test_gazette_import import _run

    _run(tmp_path)
    target = tmp_path / "public" / "publications.jsonl"
    # an earlier run with another filter gave the unlinked publication another text, hence another id
    target.write_text(target.read_text("utf-8").replace('"sans-id-', '"sans-id-ancien'), "utf-8")
    _run(tmp_path)  # same files again
    rows = [json.loads(x) for x in (tmp_path / "public" / "publications.jsonl").read_text("utf-8").splitlines()]
    assert sum(r["id"].startswith("sans-id-") for r in rows) == 1


# ---- counter-check of the week-2 audit: residual shapes (invented names) ----

def test_a_person_glued_before_a_company_cited_alone_elsewhere_is_cut():
    raw = ["Gesuch für Baubewilligung - Umbau Wohnhaus", "Titel des Bauprojekts", "Umbau", "Planverfasser",
           "Hans Muster bpm Planung AG", "Planverfasser - Firma", "bpm Planung AG", "Ablauf der Frist: 01.12.2026"]
    f, _ = filter_publication(parse_publication(raw))
    assert "Muster" not in json.dumps(f, ensure_ascii=False) and "Hans" not in json.dumps(f, ensure_ascii=False)
    assert f["entreprises_citees"] == ["bpm Planung AG"]


def test_a_person_glued_before_a_lowercase_brand_is_cut():
    f, _ = filter_publication(_pub(["Ottmar Beispiel mls architekten sia ag"], label="Planverfasser"))
    assert "Ottmar" not in json.dumps(f, ensure_ascii=False) and "Beispiel" not in json.dumps(f, ensure_ascii=False)
    assert f["entreprises_citees"] == ["mls architekten sia ag"]


def test_line_end_hyphenation_is_rejoined_in_every_field():
    raw = ["Gesuch für Baubewilligung - Umbau Wohnhaus", "Titel des Bauprojekts", "Umbau Haus Jo-", "hannes",
           "Gesuchsteller", "Muster-", "mann Ottmar", "Ablauf der Frist: 01.12.2026"]
    f, _ = filter_publication(parse_publication(raw))
    dump = json.dumps(f, ensure_ascii=False)
    assert "hannes" not in dump and "mann" not in dump and "Jo-" not in dump


def test_a_locality_right_after_a_house_word_is_masked_but_not_the_commune_after_a_comma():
    a = _pub(["Beispiel Bau AG"], title="- Umbau Haus Lens, Lens")
    f, _ = filter_publication(a, build_context([a], [], ["Lens"]))
    assert f["titre"] == "Umbau Haus [masqué], Lens"


def test_initials_are_masked():
    f, _ = filter_publication(_pub(["Beispiel Bau AG"], title="- Rénovation du Chalet J.-P. D."))
    assert not re.search(r"\b[JPD]\b", f["titre"]), f["titre"]


def test_a_street_address_in_a_title_is_masked_like_the_parcel():
    a = _pub(["Beispiel Bau AG"], title="- Construction d'une villa, Route de Exemple 12, 1950 Sion")
    f, _ = filter_publication(a, build_context([a], [], ["Sion"]))
    assert "12" not in f["titre"] and "Exemple" not in f["titre"] and f["titre"].endswith("Sion")


def test_a_family_consortage_does_not_leak_the_names():
    f, _ = filter_publication(_pub(["Consortage Exemple-Modèle"]))
    assert not _leaks(f)


def test_a_frequent_name_in_the_contact_point_without_civility_is_masked():
    extra = ["Kontaktstelle", "Gemeinde Naters, Bauamt, Muster Ottmar"]
    pubs = [_pub(["Beispiel Bau AG"], extra=extra) for _ in range(6)]
    ctx = build_context(pubs, index_titles=[], localities=["Naters"])
    f, _ = filter_publication(pubs[0], ctx)
    assert "Muster" not in f["texte"] and "Ottmar" not in f["texte"]


def test_a_domicile_glued_to_a_company_on_one_line_is_cut():
    f, _ = filter_publication(_pub(["Hans Muster 3930 Visp Beispiel AG"]))
    assert f["entreprises_citees"] == ["Beispiel AG"] and "Muster" not in json.dumps(f, ensure_ascii=False)
    g, _ = filter_publication(_pub(["Construction 2000 SA"]))
    assert g["entreprises_citees"] == ["Construction 2000 SA"]


def test_companies_whose_legal_form_is_followed_by_a_complement_are_kept():
    f, _ = filter_publication(_pub(["Exemple SA Immobilier"]))
    assert f["entreprises_citees"] == ["Exemple SA Immobilier"]
    g, _ = filter_publication(_pub(["Exemple S.A. - Rue du Rhône 12"]))
    assert g["entreprises_citees"] == ["Exemple S.A."]


def test_sweep_flags_a_word_fragment_left_after_a_mask():
    row = {"id": "f", "titre": "Umbau", "titre_projet": "Umbau Haus [masqué] hannes", "roles": {},
           "entreprises_citees": [], "organismes_publics_cites": []}
    ctx = build_context([], ["Umbau Haus und Stall", "Umbau Haus mit Garage", "Umbau Stall"], [])
    with pytest.raises(PersonalDataFound):
        sweep_rows([row], ctx=ctx)
    sweep_rows([row | {"titre_projet": "Umbau Haus [masqué] und Stall"}], ctx=ctx)


# ---- audit of the clean rebuild (working notes, not published): B-1 to B-3 (invented names)

@pytest.mark.parametrize("title", ["- Construction d'une villa, Les Fontanettes 12, Sion",
                                   "- Umbau Wohnhaus, Bodmen 3a, Visp", "- Agrandissement, [x] Champsec 7"])
def test_a_street_name_without_street_word_and_its_number_are_masked(title):
    a = _pub(["Beispiel Bau AG"], title=title)
    f, _ = filter_publication(a, build_context([a], ["Construction villa", "Construction villa", "Construction villa",
                                                     "Umbau Wohnhaus"] * 3, ["Sion", "Visp"]))
    assert not re.search(r"\b\d{1,3}[a-z]?\b", f["titre"]), f["titre"]
    assert "Fontanettes" not in f["titre"] and "Bodmen" not in f["titre"] and "Champsec" not in f["titre"]


def test_parcel_and_ppe_numbers_in_a_title_are_masked_but_useful_numbers_stay():
    f, _ = filter_publication(_pub(["Beispiel Bau AG"], title="- Réunion des PPE 4512 et 4513 en un logement"))
    assert "4512" not in f["titre"] and "4513" not in f["titre"]
    useful = "- Construction de 2 immeubles de 18 logements et 300 places en 2026"
    g, _ = filter_publication(_pub(["Beispiel Bau AG"], title=useful))
    assert g["titre"] == "Construction de 2 immeubles de 18 logements et 300 places en 2026"
    h, _ = filter_publication(_pub(["Beispiel Bau AG"], title="- Neubau MFH mit 12 Wohnungen, 450 m2 Gewerbe"))
    assert "12 Wohnungen" in h["titre"] and "450 m2" in h["titre"]


def test_company_names_are_not_cut_down_to_a_bare_legal_form():
    for name in ("Dupont construction sa", "Beispiel Bau ag", "Muster Hans Bau AG"):
        f, _ = filter_publication(_pub([name]))
        assert f["entreprises_citees"] == [name], (name, f["entreprises_citees"])
    raw = ["Gesuch für Baubewilligung - Umbau Wohnhaus", "Titel des Bauprojekts", "Umbau", "Gesuchsteller",
           "Beispiel Immobilien AG", "Grundeigentümer", "AG", "Ablauf der Frist: 01.12.2026"]
    g, _ = filter_publication(parse_publication(raw))
    assert "Beispiel Immobilien AG" in g["entreprises_citees"]


def test_the_expiration_field_keeps_its_date_but_not_spilled_text():
    extra = ["Expiration du délai : 07.11.2026 Parcelles 4512, 4513, Fontanettes Exemple"]
    raw = ["Demande d’autorisation de construire", "- Transformation d'un bâtiment", "Requérant(e)", "Beispiel Bau AG",
           *extra]
    f, _ = filter_publication(parse_publication(raw))
    assert "07.11.2026" in f["texte"] and "4512" not in f["texte"] and "Exemple" not in f["texte"]


# ---- audit v2 of the rebuild (« Contre-vérification v2 »), invented names ----

def _title(title, places=()):
    a = _pub(["Beispiel Bau AG"], title=title)
    ctx = build_context([a], ["Neubau Mehrfamilienhaus", "Neubau Mehrfamilienhaus", "Neubau Mehrfamilienhaus",
                              "Umbau Wohnhaus Garage", "Umbau Wohnhaus Garage", "Umbau Wohnhaus Garage"], list(places))
    return filter_publication(a, ctx)[0]


def test_a_house_number_anywhere_in_the_title_is_masked_with_its_street():
    f = _title("- Umbau Wohnhaus an der Sonnmatte 12 (EFH 13) in Visp und Garage", ["Visp"])
    assert not re.search(r"\b1[23]\b", f["titre"]) and "Sonnmatte" not in f["titre"], f["titre"]
    assert "Visp" in f["titre"] and "Garage" in f["titre"]
    g = _title("- Neubau Mehrfamilienhaus Sonnmatte 12 und 14 in Brig", ["Brig"])
    assert not re.search(r"\b1[24]\b", g["titre"]) and "Neubau Mehrfamilienhaus" in g["titre"], g["titre"]


def test_every_number_of_a_parcel_list_is_masked_but_units_laws_and_postcodes_stay():
    f = _title("- Vereinigung der Parzellen 4512, 4513, 4514 und 4515")
    assert not re.search(r"451\d", f["titre"]), f["titre"]
    g = _title("- Neubau Mehrfamilienhaus mit Photovoltaikanlage 30 kWh und Leitung 16 kV gemäss Art. 24 RPG")
    assert "30 kWh" in g["titre"] and "16 kV" in g["titre"] and "Art. 24" in g["titre"], g["titre"]
    h = _title("- Construction d'un garage, 1950 Sion", ["Sion"])
    assert h["titre"].endswith("1950 Sion"), h["titre"]


def test_trade_words_and_dashes_do_not_cut_company_names_and_bare_forms_are_not_companies():
    for name in ("Atelier Modèle architecte sàrl", "Exemple Planung - Architektur AG", "Beispiel ingénieur SA"):
        f, _ = filter_publication(_pub([name]))
        assert f["entreprises_citees"] == [name], (name, f["entreprises_citees"])
    g, _ = filter_publication(_pub(["Exemple Bau SA", "SA"]))
    assert g["entreprises_citees"] == ["Exemple Bau SA"]
