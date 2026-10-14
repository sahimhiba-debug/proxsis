"""Import of an XML export downloaded BY A PERSON from the Bulletin officiel du Valais (BA-VS05).
Fixture: FICTITIOUS content in the real structure (natural / legal persons are typed in the XML)."""

from pathlib import Path

import pytest

from proxsis import gazette_xml as gx

FIX = Path(__file__).parent / "fixtures" / "manuel" / "ba_vs05_fictif.xml"


def test_natural_persons_are_masked_by_structure_and_companies_kept():
    r = gx.parse_export(FIX.read_bytes())
    t = r["text"]
    for name in ("Jean", "Exempleton", "Paula", "Fictivaz", "Luc Exemplaire"):
        assert name not in t
    assert "Exemple Immobilier SA" in t and "Commune de Fictiville" in t
    assert t.count("[masqué]") >= 3
    assert "99999" not in t and "2'600'000" not in t  # parcel and coordinates


def test_metadata_is_read_from_the_export():
    r = gx.parse_export(FIX.read_bytes())
    assert r["source"] == "bo_vs" and r["rubrique"] == "BA-VS05" and r["lang"] == "fr"
    assert r["date"] == "2026-09-25"
    assert r["url"] == "https://bulletin-officiel.vs.ch/api/v1/publications/00000000-0000-4000-8000-000000000001/pdf"
    assert r["numero"] == "BA-VS05-0000000001"
    assert "Délai de mise à disposition : 26.10.2026" in r["text"]
    assert "Construction d'un immeuble de 8 logements" in r["text"]


@pytest.mark.parametrize("bad", [b"<!DOCTYPE x [<!ENTITY a 'b'>]><x>&a;</x>", b"pas du xml", b"<x/>" * 10])
def test_unsafe_or_unknown_xml_is_refused(bad):
    with pytest.raises(gx.XmlRefused):
        gx.parse_export(bad)


def test_unsupported_rubric_is_refused():
    xml = FIX.read_bytes().replace(b"<subRubric>BA-VS05</subRubric>", b"<subRubric>KK01</subRubric>")
    with pytest.raises(gx.XmlRefused, match="rubrique"):
        gx.parse_export(xml)


def test_module_never_fetches_anything():
    src = Path(gx.__file__).read_text("utf-8")
    assert "httpx" not in src and "urllib.request" not in src and "PoliteClient" not in src


# --- Import d'une archive ZIP d'exports XML (demande de Hiba, 2026-10-05)
def _zip(entries):
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in entries:
            z.writestr(name, data)
    return buf.getvalue()


def test_zip_import_reads_every_xml_in_memory_and_reports_each_file():
    good = FIX.read_bytes()
    other = good.replace(b"000000000001</id>", b"000000000002</id>").replace(b"0000000001</publicationNumber>",
                                                                            b"0000000002</publicationNumber>")
    data = _zip([("lot/a.xml", good), ("lot/b.xml", other), ("__MACOSX/lot/._a.xml", b"junk"),
                 ("lot/notes.txt", b"x"), ("lot/casse.xml", b"<pas du xml")])
    out = gx.parse_zip(data)
    names = [o["fichier"] for o in out]
    assert names == ["lot/a.xml", "lot/b.xml", "lot/casse.xml"]
    assert out[0]["ok"] and out[1]["ok"] and not out[2]["ok"] and "illisible" in out[2]["erreur"]
    assert "Exempleton" not in out[0]["text"]


def test_zip_bomb_and_oversized_archives_are_refused():
    import zipfile

    with pytest.raises(gx.XmlRefused):
        gx.parse_zip(b"pas un zip")
    big = _zip([(f"f{i}.xml", b"<x/>") for i in range(gx.MAX_FILES + 1)])
    with pytest.raises(gx.XmlRefused, match="fichiers"):
        gx.parse_zip(big)
    huge = _zip([("h.xml", b" " * (gx.MAX_BYTES + 10))])
    out = gx.parse_zip(huge)
    assert not out[0]["ok"] and "volumineux" in out[0]["erreur"]
    assert zipfile  # (imported for clarity)


def test_plan_day_check():
    from proxsis.manual_collection import in_drawn_days

    assert in_drawn_days("bo_vs", "fr", "2026-08-04") is True
    assert in_drawn_days("bo_vs", "fr", "2026-08-09") is False  # dimanche, jamais tiré


BULK = b"""<?xml version="1.0" encoding="UTF-8"?>
<bulk-export><total>2</total>
<publication><meta><id>11111111-1111-1111-1111-111111111111</id><rubric>BA</rubric><subRubric>BA-VS05</subRubric>
<language>fr</language><registrationOffice><id>x</id><displayName>Commune de Fully - Constructions</displayName>
<street>Rue</street><streetNumber>1</streetNumber><swissZipCode>1926</swissZipCode><town>Fully</town>
<containsPostOfficeBox>false</containsPostOfficeBox></registrationOffice><publicationNumber>BA-VS05-0000000001</publicationNumber>
<publicationState>PUBLISHED</publicationState><publicationDate>2026-08-14T00:00:00</publicationDate>
<expirationDate>2026-11-07</expirationDate><primaryTenantCode>kabvs</primaryTenantCode><cantons>VS</cantons>
<title><de>Neubau</de><en>New</en><it>Nuovo</it><fr>Construction d'un immeuble</fr></title>
<invoiceAddress><name>Jean Dupont</name><street>Rue des Alpes</street></invoiceAddress></meta></publication>
<publication><meta><id>22222222-2222-2222-2222-222222222222</id><rubric>BA</rubric><subRubric>BA-VS05</subRubric>
<language>de</language><registrationOffice><displayName>Gemeinde Naters</displayName></registrationOffice>
<publicationNumber>BA-VS05-0000000002</publicationNumber><publicationState>CANCELLED</publicationState>
<publicationDate>2026-09-01</publicationDate><expirationDate>2026-12-01</expirationDate>
<title><de>Neubau Lagerhalle</de><fr></fr></title></meta></publication>
</bulk-export>"""


def test_bulk_index_reads_meta_only_and_never_the_invoice_address():
    from proxsis.gazette_xml import parse_bulk_index

    rows = parse_bulk_index(BULK)
    assert [r["id"] for r in rows] == ["11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222"]
    a, b = rows
    assert a["date"] == "2026-08-14" and a["expiration"] == "2026-11-07" and a["langue"] == "fr"
    assert a["office"] == "Commune de Fully - Constructions" and a["titres"]["fr"] == "Construction d'un immeuble"
    assert b["etat"] == "CANCELLED" and b["titres"] == {"de": "Neubau Lagerhalle"}
    assert "Dupont" not in repr(rows) and "Alpes" not in repr(rows)


def test_bulk_index_refuses_doctype():
    import pytest

    from proxsis.gazette_xml import XmlRefused, parse_bulk_index

    with pytest.raises(XmlRefused):
        parse_bulk_index(b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><bulk-export/>')
