"""Official directory of localities (swisstopo, OGD): parsing and geocoding of a locality name (SYNTHETIC zip)."""

import io
import zipfile

from proxsis.connectors.swisstopo_localities import geocode, parse

HEAD = "Ortschaftsname;PLZ4;Zusatzziffer;ZIP_ID;Gemeindename;BFS-Nr;Kantonskürzel;Adressenanteil;E;N;Sprache;Validity"
ROWS = ["Sion;1950;00;1;Sion;6266;VS;100 %;7.35;46.23;fr;2008-07-01",
        "Reckingen VS;3998;00;2;Goms;6077;VS;100 %;8.24;46.47;de;2008-07-01",
        "Lausanne;1003;00;3;Lausanne;5586;VD;100 %;6.63;46.52;fr;2008-07-01",
        "Châteauneuf-Conthey;1964;00;4;Conthey;6023;VS;100 %;7.30;46.22;fr;2008-07-01"]


def _zip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("AMTOVZ_CSV_WGS84/AMTOVZ_CSV_WGS84.csv", "﻿" + "\n".join([HEAD, *ROWS]))
    return buf.getvalue()


def test_parse_keeps_the_canton_with_coordinates_language_and_source():
    rows = parse(_zip(), cantons=("VS",))
    assert {r["localite"] for r in rows} == {"Sion", "Reckingen VS", "Châteauneuf-Conthey"}
    sion = next(r for r in rows if r["localite"] == "Sion")
    assert sion["lat"] == 46.23 and sion["lon"] == 7.35 and sion["langue"] == "fr" and sion["npa"] == "1950"
    assert "swisstopo" in sion["source"]


def test_geocode_matches_locality_or_commune_ignoring_accents_case_and_canton_suffix():
    rows = parse(_zip(), cantons=("VS",))
    assert geocode("SION", rows)["localite"] == "Sion"
    assert geocode("Sion 4", rows)["localite"] == "Sion"  # postal office number
    assert geocode("Reckingen", rows)["commune"] == "Goms"
    assert geocode("Reckingen VS", rows)["localite"] == "Reckingen VS"
    assert geocode("Chateauneuf-Conthey", rows)["commune"] == "Conthey"
    assert geocode("Conthey", rows)["commune"] == "Conthey"
    assert geocode("Lausanne", rows) is None
