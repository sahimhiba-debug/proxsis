"""Commune boundaries of the Valais (swissBOUNDARIES3D, swisstopo): download by byte ranges, shapefile reading,
LV95 → WGS84, projection of the presentation map, topology-preserving simplification. Everything is SYNTHETIC:
hand-written GeoJSON and tiny shapefiles built here, never a downloaded file."""

import io
import json
import math
import random
import re
import struct
import zipfile
from itertools import pairwise
from pathlib import Path

import httpx
import pytest

from proxsis.connectors import swisstopo_boundaries as sb
from proxsis.http import HttpCache, PoliteClient

REPO = Path(__file__).resolve().parents[2]


# -- projection --------------------------------------------------------------------------------------------------------
def test_projection_is_the_one_of_the_presentation_map():
    # the screens read the projection from the exported file (the visit's map, region.ts); it must be the module's own
    web = REPO / "apps/web/src"
    meta = json.loads((web / "data/presentation/communes_vs.json").read_text("utf-8"))["meta"]["projection"]
    assert meta == {"lon0": sb.LON0, "lat1": sb.LAT1, "k": sb.K, "cos_lat": sb.COS_LAT_DEG}, (
        "la projection de la carte a changé : régénérer communes_vs.json")
    for f in (web / "visite/Carte.tsx", web / "futur/region.ts"):
        text = f.read_text("utf-8")
        assert "communes_vs.json" in text and not re.search(r"\bconst (LON0|LAT1|K) = [0-9]", text), f.name
    assert sb.project(6.75, 46.69) == (0.0, 0.0)
    x, y = sb.project(7.35, 46.23)
    assert x == pytest.approx((7.35 - 6.75) * math.cos(math.radians(46.25)) * 820)
    assert y == pytest.approx((46.69 - 46.23) * 820)


def test_lv95_to_wgs84_reproduces_the_swisstopo_worked_example():
    # swisstopo, approximate formulas: E 2 700 000 / N 1 100 000 → 46° 02' 38.86" N, 8° 43' 49.80" E (about 1 m).
    lon, lat = sb.lv95_to_wgs84(2_700_000.0, 1_100_000.0)
    assert lat == pytest.approx(46 + 2 / 60 + 38.86 / 3600, abs=2e-5)
    assert lon == pytest.approx(8 + 43 / 60 + 49.80 / 3600, abs=2e-5)


# -- simplification ----------------------------------------------------------------------------------------------------
def test_simplify_keeps_both_ends_and_the_points_beyond_the_tolerance():
    line = [(0.0, 0.0), (1.0, 0.1), (2.0, -0.1), (3.0, 0.0), (3.0, 1.0), (3.1, 2.0), (3.0, 3.0)]
    assert sb.simplify(line, 0.5) == [(0.0, 0.0), (3.0, 0.0), (3.0, 3.0)]
    assert sb.simplify(line, 0.01) == line  # every point is farther than 0.01 from its chord


def test_simplify_keeps_one_interior_point_so_two_arcs_between_the_same_nodes_never_overlap():
    straight = [(0.0, 0.0), (1.0, 0.01), (2.0, 0.0), (3.0, 0.0)]
    assert sb.simplify(straight, 10.0) == [(0.0, 0.0), (1.0, 0.01), (3.0, 0.0)]
    assert sb.simplify([(0.0, 0.0), (1.0, 1.0)], 10.0) == [(0.0, 0.0), (1.0, 1.0)]


def test_simplify_a_closed_ring_without_node_keeps_a_real_polygon():
    ring = [(0.0, 0.0), (0.0, 1.0), (0.05, 2.0), (0.0, 3.0), (3.0, 3.0), (3.0, 0.0), (0.0, 0.0)]
    out = sb.simplify(ring, 0.5)
    assert out[0] == out[-1] == (0.0, 0.0)
    assert len(set(out)) >= 3


# -- reading the shapefile (synthetic bytes) -------------------------------------------------------------------------
def _dbf(fields: list[tuple[str, str, int, int]], rows: list[list[object]]) -> bytes:
    rec_len = 1 + sum(f[2] for f in fields)
    header_len = 32 + 32 * len(fields) + 1
    out = bytearray(struct.pack("<B3BIHH20x", 3, 126, 1, 1, len(rows), header_len, rec_len))
    for name, typ, length, dec in fields:
        out += struct.pack("<11sc4xBB14x", name.encode(), typ.encode(), length, dec)
    out += b"\r"
    for row in rows:
        out += b" "
        for (_name, typ, length, _dec), v in zip(fields, row, strict=True):
            s = "" if v is None else str(v)
            cell = s.encode("utf-8")
            out += cell.rjust(length) if typ in "NF" else cell.ljust(length)
    out += b"\x1a"
    return bytes(out)


def _shp(records: list[list[list[tuple[float, float]]]]) -> bytes:
    """PolygonZ (type 15) records, one list of rings per record."""
    body = bytearray()
    for i, rings in enumerate(records, start=1):
        pts = [p for r in rings for p in r]
        parts, n = [], 0
        for r in rings:
            parts.append(n)
            n += len(r)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        content = struct.pack("<i4d2i", 15, min(xs), min(ys), max(xs), max(ys), len(rings), len(pts))
        content += struct.pack(f"<{len(parts)}i", *parts)
        content += b"".join(struct.pack("<2d", *p) for p in pts)
        content += struct.pack("<2d", 400.0, 500.0) + struct.pack(f"<{len(pts)}d", *([450.0] * len(pts)))
        body += struct.pack(">2i", i, len(content) // 2) + content
    header = struct.pack(">7i", 9994, 0, 0, 0, 0, 0, (100 + len(body)) // 2)
    header += struct.pack("<2i8d", 1000, 15, 0, 0, 0, 0, 0, 0, 0, 0)
    return header + bytes(body)


FIELDS = [("BFS_NUMMER", "N", 6, 0), ("NAME", "C", 40, 0), ("KANTONSNUM", "N", 2, 0), ("OBJEKTART", "C", 20, 0)]
# LV95 squares around Sion; the second record has a hole (outer clockwise, hole counter-clockwise, as in a shapefile).
SQ_A = [(2_590_000.0, 1_120_000.0), (2_590_000.0, 1_122_000.0), (2_592_000.0, 1_122_000.0),
        (2_592_000.0, 1_120_000.0), (2_590_000.0, 1_120_000.0)]
SQ_B = [(2_592_000.0, 1_120_000.0), (2_592_000.0, 1_122_000.0), (2_596_000.0, 1_122_000.0),
        (2_596_000.0, 1_120_000.0), (2_592_000.0, 1_120_000.0)]
HOLE_B = [(2_593_000.0, 1_120_500.0), (2_594_000.0, 1_120_500.0), (2_594_000.0, 1_121_500.0),
          (2_593_000.0, 1_121_500.0), (2_593_000.0, 1_120_500.0)]


def test_read_shapefile_gives_geojson_features_in_wgs84_with_their_holes():
    shp = _shp([[SQ_A], [SQ_B, HOLE_B]])
    dbf = _dbf(FIELDS, [[6266, "Sion", 23, "Gemeindegebiet"], [6267, "Saint-Léonard", 23, "Gemeindegebiet"]])
    feats = sb.read_shapefile(shp, dbf, "utf-8")
    assert [f["properties"]["NAME"] for f in feats] == ["Sion", "Saint-Léonard"]
    assert feats[1]["properties"]["BFS_NUMMER"] == 6267 and feats[1]["properties"]["KANTONSNUM"] == 23
    geom = feats[1]["geometry"]
    assert geom["type"] == "MultiPolygon" and len(geom["coordinates"]) == 1 and len(geom["coordinates"][0]) == 2
    lon, lat = geom["coordinates"][0][0][0]
    assert (lon, lat) == pytest.approx(sb.lv95_to_wgs84(*SQ_B[0]))
    assert 7.0 < lon < 7.6 and 46.1 < lat < 46.3


# -- download by byte ranges (mock server) -----------------------------------------------------------------------------
def _release_zip() -> bytes:
    noise = random.Random(0)  # incompressible stand-ins for the other layers (bigger than the tail that is read)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("swissBOUNDARIES3D_1_5_TLM_BEZIRKSGEBIET.shp", noise.randbytes(20_000))
        for ext, data in ((".cpg", b"UTF-8"), (".dbf", b"D" * 3000), (".prj", b'PROJCS["CH1903+_LV95"]'),
                          (".shp", b"S" * 5000), (".shx", b"X" * 100)):
            z.writestr(sb.LAYER + ext, data)
        z.writestr("swissBOUNDARIES3D_1_5_TLM_LANDESGEBIET.shp", noise.randbytes(20_000))
    return buf.getvalue()


def _range_server(blob: bytes, calls: list[str], honour_range: bool = True) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        rng = request.headers.get("range", "")
        calls.append(rng)
        if not honour_range or not rng:
            return httpx.Response(200, content=blob)
        a, b = rng.removeprefix("bytes=").split("-")
        start, end = (max(0, len(blob) - int(b)), len(blob) - 1) if a == "" else (int(a), min(int(b), len(blob) - 1))
        return httpx.Response(206, content=blob[start:end + 1],
                              headers={"content-range": f"bytes {start}-{end}/{len(blob)}"})
    return httpx.MockTransport(handler)


def _client(tmp_path, transport) -> PoliteClient:
    return PoliteClient(HttpCache(tmp_path / "cache"), offline=False, user_agent="Proxsis-test",
                        min_interval_s=0.0, transport=transport, sleep=lambda s: None)


def test_fetch_reads_only_the_commune_layer_with_two_range_requests(tmp_path):
    blob, calls = _release_zip(), []
    dl = sb.fetch_commune_layer(_client(tmp_path, _range_server(blob, calls)))
    assert dl.files[".shp"] == b"S" * 5000 and dl.files[".dbf"] == b"D" * 3000 and dl.files[".cpg"] == b"UTF-8"
    assert len(calls) == 2 and calls[0].startswith("bytes=-") and dl.requests == 2
    assert dl.bytes < len(blob) / 2  # the other layers are never transferred
    assert dl.url == sb.zip_url() and dl.url.startswith("https://data.geo.admin.ch/ch.swisstopo.swissboundaries3d/")
    assert not list((tmp_path / "cache").rglob("*.body"))  # nothing stored by the HTTP cache


def test_fetch_falls_back_to_the_whole_zip_when_the_server_ignores_ranges(tmp_path):
    blob, calls = _release_zip(), []
    dl = sb.fetch_commune_layer(_client(tmp_path, _range_server(blob, calls, honour_range=False)))
    assert dl.files[".shp"] == b"S" * 5000 and len(calls) == 1 and dl.requests == 1


def test_downloaded_layer_round_trips_through_the_local_cache(tmp_path):
    blob, calls = _release_zip(), []
    dl = sb.fetch_commune_layer(_client(tmp_path, _range_server(blob, calls)))
    sb.save_download(dl, tmp_path / "brut")
    again = sb.load_download(tmp_path / "brut")
    assert again is not None and again.files == dl.files and again.url == dl.url
    assert again.retrieved_at == dl.retrieved_at
    assert sb.load_download(tmp_path / "absent") is None


# -- analysis of a hand-written GeoJSON (WGS84) ------------------------------------------------------------------------
def _feature(bfs, name, polygons, canton=23, kind="Gemeindegebiet"):
    return {"type": "Feature",
            "properties": {"BFS_NUMMER": bfs, "NAME": name, "KANTONSNUM": canton, "OBJEKTART": kind},
            "geometry": {"type": "MultiPolygon", "coordinates": polygons}}


# A | B side by side; their border wiggles by 0.0001° (well under the tolerance); C is an enclave filling B's hole;
# A has a tiny island (under MIN_RING_AREA); W is in another canton, L is a lake area of the Valais: neither is drawn.
BORDER = [[7.32, 46.205], [7.3201, 46.21], [7.32, 46.215]]
A = [[[7.30, 46.20], [7.32, 46.20], *BORDER, [7.32, 46.22], [7.30, 46.22], [7.30, 46.20]]]
ISLAND = [[[7.31, 46.23], [7.3101, 46.23], [7.31, 46.2301], [7.31, 46.23]]]
B_OUT = [[7.32, 46.20], [7.36, 46.20], [7.36, 46.22], [7.32, 46.22], *BORDER[::-1], [7.32, 46.20]]
C_RING = [[7.335, 46.205], [7.345, 46.205], [7.345, 46.215], [7.335, 46.215], [7.335, 46.205]]
GEOJSON = {"type": "FeatureCollection", "features": [
    _feature(6001, "Aval", [A, ISLAND]),
    _feature(6002, "Bourg", [[B_OUT, C_RING[::-1]]]),
    _feature(6003, "Clos", [[C_RING]]),
    _feature(5001, "Ouest", [[[[7.28, 46.20], [7.30, 46.20], [7.30, 46.22], [7.28, 46.22], [7.28, 46.20]]]], canton=22),
    _feature(9001, "Lac", [[[[7.37, 46.20], [7.38, 46.20], [7.38, 46.21], [7.37, 46.20]]]], kind="Kantonsgebiet"),
]}


def _rings(d: str) -> list[list[tuple[float, float]]]:
    assert re.fullmatch(r"(M[^MZ]+Z)+", d), d
    out = []
    for sub in re.findall(r"M([^MZ]+)Z", d):
        pts = [tuple(float(v) for v in pair.split()) for pair in sub.split("L")]
        out.append(pts)
    return out


def _area(r):
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1], strict=True))


def _built():
    return sb.build(GEOJSON["features"], url="https://example.test/x.zip", retrieved_at="2026-10-06T10:00:00+00:00",
                    vintage="essai", tolerance=0.5)


def test_build_keeps_the_communes_of_the_canton_only_with_the_contract_metadata():
    out = _built()
    assert [(c["bfs"], c["nom"]) for c in out["communes"]] == [(6001, "Aval"), (6002, "Bourg"), (6003, "Clos")]
    meta = out["meta"]
    assert set(meta) == {"source", "attribution", "licence", "url", "recupere_le", "millesime", "projection",
                         "tolerance", "bbox"}
    assert meta["attribution"] == "© swisstopo" and "swissBOUNDARIES3D" in meta["source"]
    assert meta["projection"] == {"lon0": 6.75, "lat1": 46.69, "k": 820, "cos_lat": 46.25}
    assert meta["tolerance"] == 0.5 and meta["url"] == "https://example.test/x.zip" and meta["millesime"] == "essai"
    pts = [p for c in out["communes"] for r in _rings(c["d"]) for p in r]
    x0, y0 = sb.project(7.30, 46.22)
    x1, y1 = sb.project(7.36, 46.20)
    assert meta["bbox"] == [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts),
                            max(p[1] for p in pts)]
    assert meta["bbox"] == pytest.approx([x0, y0, x1, y1], abs=0.051)


def test_rings_are_closed_rounded_and_never_degenerate():
    out = _built()
    for c in out["communes"]:
        assert re.fullmatch(r"[MLZ0-9. -]+", c["d"])
        assert all(re.fullmatch(r"-?\d+(\.\d)?", v) for v in re.findall(r"-?[\d.]+", c["d"]))
        for r in _rings(c["d"]):
            assert len(set(r)) == len(r) >= 3  # closed by Z, no repeated point
            assert all(a != b for a, b in pairwise(r))
            assert abs(_area(r)) >= sb.MIN_RING_AREA
    aval = next(c for c in out["communes"] if c["nom"] == "Aval")
    assert len(_rings(aval["d"])) == 1  # the tiny island is dropped, the main ring kept


def test_shared_borders_are_identical_on_both_sides_and_holes_wind_the_other_way():
    out = {c["nom"]: _rings(c["d"]) for c in _built()["communes"]}
    (a,), (b_out, b_hole), (c,) = out["Aval"], out["Bourg"], out["Clos"]
    xb = sb.project(7.32, 46.21)[0]
    border_a = {p for p in a if abs(p[0] - xb) < 1}
    border_b = {p for p in b_out if abs(p[0] - xb) < 1}
    assert border_a == border_b and len(border_a) >= 2
    assert set(b_hole) == set(c)
    assert _area(b_out) * _area(b_hole) < 0  # nonzero and evenodd fill rules both cut the hole


def test_canton_outline_follows_the_outer_border_only():
    out = _built()
    (ring,) = _rings(out["canton"])
    corners = {tuple(round(v, 1) for v in sb.project(lon, lat))
               for lon, lat in [(7.30, 46.20), (7.32, 46.20), (7.36, 46.20), (7.36, 46.22), (7.32, 46.22),
                                (7.30, 46.22)]}
    assert set(ring) == corners  # the corners only: no inner border, no wiggle point


def test_match_communes_by_bfs_number_then_by_name():
    communes = [{"bfs": 6266, "nom": "Sion", "d": ""}, {"bfs": 6077, "nom": "Goms", "d": ""}]
    localities = [{"commune": "Sion", "bfs": "6266"}, {"commune": "Goms", "bfs": "6077"},
                  {"commune": "Ancienne", "bfs": "6999"}]
    got = sb.match_communes(["Sion", "GOMS", "Ancienne", "Nulle part"], communes, localities)
    assert got == {"Sion": 6266, "GOMS": 6077, "Ancienne": None, "Nulle part": None}


def test_dumps_writes_one_commune_per_line_and_reads_back_identically():
    out = _built()
    text = sb.dumps(out)
    assert json.loads(text) == out
    assert sum(1 for line in text.splitlines() if line.lstrip().startswith('{"bfs"')) == len(out["communes"])
    assert sb.vintage("swissboundaries3d_2026-01") == sb.VINTAGE
    assert "2025-04" in sb.vintage("swissboundaries3d_2025-04")
