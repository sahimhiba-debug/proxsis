"""Sheet « à valider par les consultants » and the integration of their answers (SYNTHETIC list)."""

import csv
import io

import pytest

from proxsis.validation_sheet import csv_template, freeze_list, integrate, render_html

MENTION = "Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi."


def _list(n=3):
    ents = [{"id": f"ent-{i:010d}", "rang": i, "nom": f"Entreprise {i} SA", "ville": "Sion", "canton": "VS",
             "confiance": "moyenne", "surprise": [], "raisons": [{"code": "marches_52s", "n": 5 - i}],
             "besoin": [{"semaine": "2026-10-12", "metier": "macon", "personnes_bas": 1.0, "personnes_milieu": 2.0,
                         "personnes_haut": 3.0}],
             "sources": [{"date": "2026-09-01", "titre": "Ecole <b>X</b>", "adjudicateur": "Commune",
                          "url_simap": f"https://www.simap.ch/fr/project-detail/p{i}", "montant_chf": 1e6}]}
            for i in range(1, n + 1)]
    return {"as_of": "2026-10-05", "specialite": "batiment", "region": ["VS"], "entreprises": ents, "surprises": [],
            "mention_obligatoire": MENTION, "ordre": "fréquence"}


def test_freeze_gives_a_stable_id_that_changes_with_the_list():
    a, b = freeze_list(_list()), freeze_list(_list())
    assert a["liste_id"] == b["liste_id"] and len(a["liste_id"]) == 12
    other = _list()
    other["entreprises"].reverse()
    assert freeze_list(other)["liste_id"] != a["liste_id"]


def test_html_has_three_boxes_per_company_sources_mention_and_escapes_text():
    lst = freeze_list(_list())
    html = render_html(lst, "fr")
    assert html.count('class="case"') == 3 * 3
    for label in ("Connue", "Recrute en effet", "Pas pertinente"):
        assert label in html
    assert MENTION in html and lst["liste_id"] in html
    assert "https://www.simap.ch/fr/project-detail/p1" in html
    assert "<b>X</b>" not in html  # source text is escaped
    de = render_html(lst, "de")
    assert "Bekannt" in de and MENTION in de


def test_csv_template_has_one_row_per_company():
    lst = freeze_list(_list())
    rows = list(csv.DictReader(io.StringIO(csv_template(lst))))
    assert [r["entreprise_id"] for r in rows] == [e["id"] for e in lst["entreprises"]]
    assert {"consultant", "connue", "recrute_en_effet", "pas_pertinente"} <= set(rows[0])


def _answers(lst, who, values):
    out = []
    for e, (k, r, p) in zip(lst["entreprises"], values, strict=True):
        out.append({"liste_id": lst["liste_id"], "entreprise_id": e["id"], "consultant": who, "agence": "Martigny",
                    "connue": str(k), "recrute_en_effet": str(r), "pas_pertinente": str(p), "remarque": ""})
    return out


def test_integration_measures_precision_novelty_and_agreement():
    lst = freeze_list(_list())
    rows = _answers(lst, "C1", [(1, 1, 0), (0, 1, 0), (0, 0, 1)]) + _answers(lst, "C2", [(1, 1, 0), (0, 0, 0),
                                                                                         (0, 0, 1)])
    rep = integrate(lst, rows)
    assert rep["consultants"] == 2 and rep["entreprises_evaluees"] == 3
    # an empty box means « je ne sais pas »: company 2 counts as hiring (one opinion, no opposite opinion)
    assert rep["recrute_en_effet"]["n"] == 2 and rep["pas_pertinente"]["n"] == 1
    assert rep["recrute_en_effet"]["part"] == pytest.approx(2 / 3)  # on the companies with an opinion
    assert rep["recrute_en_effet"]["borne_basse"] == pytest.approx(2 / 3)  # on the whole list
    assert rep["couverture"] == pytest.approx(1.0)
    assert rep["connue"]["n"] == 1
    # agreement only where both consultants gave an opinion: companies 1 and 3, both agree
    assert rep["accord"]["avis_exprimes"]["entreprises"] == 2
    assert rep["accord"]["avis_exprimes"]["accord_observe"] == pytest.approx(1.0)
    assert rep["type_de_donnee"] == "RÉEL-TERRAIN"


def test_unknown_answers_do_not_count_as_no_and_duplicates_are_flagged():
    lst = freeze_list(_list())
    rows = _answers(lst, "C1", [(0, 0, 0), (0, 0, 0), (0, 1, 0)])
    rows.append(dict(rows[2]))
    rep = integrate(lst, rows)
    assert rep["couverture"] == pytest.approx(1 / 3) and rep["recrute_en_effet"]["part"] == pytest.approx(1.0)
    assert any(i["motif"].startswith("doublon") for i in rep["incoherences"])


def test_integration_refuses_answers_for_another_list_or_bad_values():
    lst = freeze_list(_list())
    bad = _answers(lst, "C1", [(1, 1, 0), (0, 1, 0), (0, 0, 1)])
    bad[0]["liste_id"] = "autreliste00"
    with pytest.raises(ValueError, match="liste"):
        integrate(lst, bad)
    bad = _answers(lst, "C1", [(1, 1, 0), (0, 1, 0), (0, 0, 1)])
    bad[1]["recrute_en_effet"] = "oui"
    with pytest.raises(ValueError, match="0 ou 1"):
        integrate(lst, bad)
    bad = _answers(lst, "C1", [(1, 1, 1), (0, 1, 0), (0, 0, 1)])
    rep = integrate(lst, bad)
    assert rep["incoherences"] == [{"consultant": "C1", "entreprise_id": lst["entreprises"][0]["id"],
                                    "motif": "recrute en effet et pas pertinente"}]


def test_consultant_must_be_a_code_not_a_name():
    lst = freeze_list(_list())
    for who in ("Jean Dupont", "LEA"):
        rows = _answers(lst, who, [(1, 1, 0), (0, 1, 0), (0, 0, 1)])
        with pytest.raises(ValueError, match="code"):
            integrate(lst, rows)


def test_sheet_states_the_unit_of_the_need_and_formats_dates():
    html = render_html(freeze_list(_list()), "fr")
    assert "pers./semaine" in html and "01.09.2026" in html and ">2026-09-01<" not in html
    assert "Pers./Woche" in render_html(freeze_list(_list()), "de")


def _fake_chrome(pages):
    def run(cmd, **kw):
        if pages is None:
            import subprocess
            raise subprocess.CalledProcessError(1, cmd)
        from pypdf import PdfWriter
        out = next(a.split("=", 1)[1] for a in cmd if a.startswith("--print-to-pdf="))
        w = PdfWriter()
        for _ in range(pages):
            w.add_blank_page(width=842, height=595)
        with open(out, "wb") as fh:
            w.write(fh)
    return run


@pytest.mark.parametrize("pages, expected", [(1, 1), (2, 2), (None, None)])
def test_one_page_pdf_with_a_fake_chrome(tmp_path, monkeypatch, pages, expected):
    import proxsis.validation_sheet as vs

    monkeypatch.setattr(vs.subprocess, "run", _fake_chrome(pages))
    monkeypatch.setattr(vs, "CHROME", str(tmp_path / "chrome"))
    (tmp_path / "chrome").write_text("")
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"old")  # a stale file must never be counted
    n = vs.write_one_page_pdf(freeze_list(_list()), "fr", tmp_path / "x.html", pdf, chrome=str(tmp_path / "chrome"))
    assert n == expected


def test_surprises_get_their_own_section_boxes_and_csv_rows():
    lst = _list()
    s = dict(lst["entreprises"][0], id="ent-surprise01", nom="Bondit SA", surprise=["rythme_double"])
    s.pop("rang")
    lst["surprises"] = [s]
    frozen = freeze_list(lst)
    assert frozen["liste_id"] != freeze_list(_list())["liste_id"]
    html = render_html(frozen, "fr")
    assert html.count('class="case"') == 3 * 4 and "À surveiller" in html and "Bondit SA" in html
    assert "Auffällig" in render_html(frozen, "de")
    rows = list(csv.DictReader(io.StringIO(csv_template(frozen))))
    assert rows[-1]["entreprise_id"] == "ent-surprise01" and rows[-1]["rang"] == "S1"
    ans = [{"liste_id": frozen["liste_id"], "entreprise_id": "ent-surprise01", "consultant": "C1",
            "connue": "0", "recrute_en_effet": "1", "pas_pertinente": "0"}]
    assert integrate(frozen, ans)["entreprises_evaluees"] == 1
