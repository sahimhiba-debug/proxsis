"""Commune boundaries of the canton of Valais (swissBOUNDARIES3D, swisstopo), simplified and projected for the map of
the presentation, embedded offline in ``apps/web/src/data/presentation/communes_vs.json``.

Source and licence
    Office fédéral de topographie swisstopo, swissBOUNDARIES3D, release ``swissboundaries3d_2026-01`` (state of the
    boundaries on 1 January 2026), STAC collection ``ch.swisstopo.swissboundaries3d`` on data.geo.admin.ch, shapefile
    in LV95 (EPSG:2056). Open government data of swisstopo: free use, the source must be cited (« © swisstopo »).

Why this route (fewest requests, smallest volume)
    The api3.geo.admin.ch layer ``ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill`` is historised (one feature
    per commune and year since 1850, fields ``gde_nr``, ``gemname``, ``kanton``, ``jahr``, ``is_current_jahr``), returns
    at most 200 features per request and does not accept ``layerDefs`` (not a « queryable » layer): its documentation
    sends whole datasets to the STAC files. The release ZIP weighs about 36 MB for all layers; only the commune layer
    (``TLM_HOHEITSGEBIET``, about 18 MB compressed) is transferred, with two HTTP ``Range`` requests through
    :class:`~proxsis.http.PoliteClient` (robots.txt, pace, provenance): (1) the last 16 kB of the ZIP (central
    directory), (2) the byte range holding the ``.cpg``, ``.dbf``, ``.prj`` and ``.shp`` of that layer. If the server
    ignores ``Range`` (HTTP 200), the whole ZIP of the first answer is used: one request. The extracted files are kept
    outside Git (``python/.cache/``, ignored) so that a rebuild makes no request.

Method
    1. Shapefile (PolygonZ) and dBASE read by hand (no GDAL, no shapely); the Z values are ignored.
    2. LV95 → WGS84 with the approximate formulas of swisstopo (« Formules approchées pour la transformation entre
       coordonnées WGS84 et coordonnées nationales suisses », precision about 1 m): y' = (E − 2 600 000) / 10⁶,
       x' = (N − 1 200 000) / 10⁶; λ' = 2.6779094 + 4.728982 y' + 0.791484 y'x' + 0.1306 y'x'² − 0.0436 y'³;
       φ' = 16.9023892 + 3.238272 x' − 0.270978 y'² − 0.002528 x'² − 0.0447 y'²x' − 0.0140 x'³;
       λ = λ' × 100 / 36, φ = φ' × 100 / 36 (degrees).
    3. Projection of the site's maps (read from the exported file by ``apps/web/src/futur/region.ts`` and the visit's
       map): x = (lon − 6.75) × cos(46.25°) × 820,
       y = (46.69 − lat) × 820 (1 unit ≈ 135 m in both directions).
    4. Topology-preserving simplification, in projected units: rings are cut into arcs at the points where the
       neighbours change (as TopoJSON does); each arc is simplified ONCE by Douglas–Peucker (both ends kept, and at
       least the farthest interior point, so that two arcs between the same nodes never collapse onto each other), so
       a border shared by two communes stays identical on both sides (no gap, no overlap). Coordinates rounded to
       0.1 unit; repeated points removed; rings with fewer than three distinct points or with an area under
       ``MIN_RING_AREA`` dropped (the largest ring of a commune is always kept).
    5. Canton outline: the arcs used by a single commune of the canton (borders with the other cantons, France and
       Italy, and the shore of the lake), chained into rings: no extra request, and it matches the communes exactly.
       Lake areas (``OBJEKTART`` other than a commune) are not communes and are not drawn.
"""

from __future__ import annotations

import io
import json
import math
import re
import struct
import unicodedata
import zipfile
import zlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

from proxsis.http import PoliteClient

ITEM = "swissboundaries3d_2026-01"
VINTAGE = "swissBOUNDARIES3D 2026-01 (limites communales au 1er janvier 2026)"
BASE_URL = "https://data.geo.admin.ch/ch.swisstopo.swissboundaries3d"
LAYER = "swissBOUNDARIES3D_1_5_TLM_HOHEITSGEBIET"
SOURCE = "Office fédéral de topographie swisstopo, swissBOUNDARIES3D (limites communales)"
ATTRIBUTION = "© swisstopo"
LICENSE = "données ouvertes swisstopo : utilisation libre, indication de la source obligatoire"
CANTON_VS = 23  # KANTONSNUM of the Valais

# Projection of the site's maps (written into communes_vs.json; read by futur/region.ts and visite/Carte.tsx)
LON0 = 6.75
LAT1 = 46.69
K = 820
COS_LAT_DEG = 46.25
_COS = math.cos(math.radians(COS_LAT_DEG))

TAIL_BYTES = 16_384
WANTED = (".cpg", ".dbf", ".prj", ".shp")
DEFAULT_TOLERANCE = 0.3  # projected units (1 unit ≈ 135 m): 0.3 px at the size of the map in 1920 × 1080
MIN_RING_AREA = 1.0  # square units (about 1.8 ha): smaller rings are invisible at 1 px per unit

Point = tuple[float, float]


# -- coordinates ------------------------------------------------------------------------------------------------------
def lv95_to_wgs84(e: float, n: float) -> tuple[float, float]:
    """(lon, lat) in degrees from LV95 easting/northing, approximate formulas of swisstopo (about 1 m)."""
    y = (e - 2_600_000.0) / 1e6
    x = (n - 1_200_000.0) / 1e6
    lam = 2.6779094 + 4.728982 * y + 0.791484 * y * x + 0.1306 * y * x * x - 0.0436 * y**3
    phi = 16.9023892 + 3.238272 * x - 0.270978 * y * y - 0.002528 * x * x - 0.0447 * y * y * x - 0.0140 * x**3
    return lam * 100.0 / 36.0, phi * 100.0 / 36.0


def project(lon: float, lat: float) -> Point:
    """Projection of the presentation map (Territory.tsx), in SVG units."""
    return (lon - LON0) * _COS * K, (LAT1 - lat) * K


# -- download ---------------------------------------------------------------------------------------------------------
def zip_url(item: str = ITEM) -> str:
    return f"{BASE_URL}/{item}/{item}_2056_5728.shp.zip"


def vintage(item: str = ITEM) -> str:
    return VINTAGE if item == ITEM else f"swissBOUNDARIES3D {item.rsplit('_', 1)[-1]}"


@dataclass
class Download:
    files: dict[str, bytes]  # extension → content (.cpg, .dbf, .prj, .shp)
    url: str
    retrieved_at: str
    requests: int
    bytes: int


@dataclass
class _Entry:
    name: str
    method: int
    crc: int
    csize: int
    offset: int


def _central_directory(tail: bytes) -> tuple[list[_Entry], int]:
    """Entries of the ZIP from its last bytes, and the absolute offset where the central directory starts."""
    i = tail.rfind(b"PK\x05\x06")
    if i < 0:
        raise ValueError("fin du répertoire ZIP introuvable dans les derniers octets")
    _sig, _d, _cd, _nd, n, cd_size, cd_off, _cl = struct.unpack("<IHHHHIIH", tail[i:i + 22])
    if 0xFFFFFFFF in (cd_size, cd_off) or n == 0xFFFF:
        raise ValueError("ZIP64 non pris en charge")
    if cd_size > i:
        raise ValueError("répertoire ZIP plus long que la fin lue : augmenter TAIL_BYTES")
    p, out = i - cd_size, []
    for _ in range(n):
        if tail[p:p + 4] != b"PK\x01\x02":
            raise ValueError("répertoire ZIP illisible")
        (_s, _vm, _vn, _fl, method, _t, _dt, crc, csize, _usize, fnl, exl, cml, _dk, _ia, _ea,
         lho) = struct.unpack("<IHHHHHHIIIHHHHHII", tail[p:p + 46])
        out.append(_Entry(tail[p + 46:p + 46 + fnl].decode("utf-8"), method, crc, csize, lho))
        p += 46 + fnl + exl + cml
    return out, cd_off


def _extract(blob: bytes, base: int, e: _Entry) -> bytes:
    """Content of one ZIP member from a byte range starting at absolute offset ``base``."""
    p = e.offset - base
    if blob[p:p + 4] != b"PK\x03\x04":
        raise ValueError(f"en-tête local absent pour {e.name}")
    fnl, exl = struct.unpack("<HH", blob[p + 26:p + 30])
    start = p + 30 + fnl + exl
    raw = blob[start:start + e.csize]
    if len(raw) != e.csize:
        raise ValueError(f"{e.name} : plage tronquée")
    data = zlib.decompressobj(-15).decompress(raw) if e.method == 8 else raw
    if e.method not in (0, 8) or zlib.crc32(data) != e.crc:
        raise ValueError(f"{e.name} : contenu invalide (méthode {e.method} ou CRC)")
    return data


def _from_whole_zip(blob: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        return {ext: z.read(LAYER + ext) for ext in WANTED}


def fetch_commune_layer(client: PoliteClient, item: str = ITEM) -> Download:
    """The commune layer of the release ZIP, by two Range requests (or one if the server ignores Range)."""
    url = zip_url(item)
    tail = client.get(url, source=SOURCE, license=LICENSE, headers={"Range": f"bytes=-{TAIL_BYTES}"})
    retrieved = tail.provenance.retrieved_at.isoformat(timespec="seconds")
    if tail.status == 200:
        return Download(_from_whole_zip(tail.body), url, retrieved, 1, len(tail.body))
    if tail.status != 206:
        raise RuntimeError(f"swisstopo : HTTP {tail.status} pour {url}")
    entries, cd_off = _central_directory(tail.body)
    names = {e.name: e for e in entries}
    wanted = [names[LAYER + ext] for ext in WANTED]
    first = min(e.offset for e in wanted)
    last = max(e.offset for e in wanted)
    end = min([e.offset for e in entries if e.offset > last] + [cd_off]) - 1
    part = client.get(url, source=SOURCE, license=LICENSE, headers={"Range": f"bytes={first}-{end}"})
    if part.status == 200:  # Range ignored on the second request: the whole ZIP came back
        return Download(_from_whole_zip(part.body), url, retrieved, 2, len(tail.body) + len(part.body))
    if part.status != 206:
        raise RuntimeError(f"swisstopo : HTTP {part.status} pour {url} (plage {first}-{end})")
    files = {ext: _extract(part.body, first, names[LAYER + ext]) for ext in WANTED}
    return Download(files, url, retrieved, 2, len(tail.body) + len(part.body))


def save_download(dl: Download, folder: Path) -> None:
    """Keep the extracted layer outside Git (python/.cache/ is ignored) so that a rebuild makes no request."""
    folder.mkdir(parents=True, exist_ok=True)
    for ext, data in dl.files.items():
        (folder / f"{LAYER}{ext}").write_bytes(data)
    meta = {"url": dl.url, "recupere_le": dl.retrieved_at, "requetes": dl.requests, "octets": dl.bytes,
            "source": SOURCE, "licence": LICENSE}
    (folder / "provenance.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", "utf-8")


def load_download(folder: Path) -> Download | None:
    meta_p = folder / "provenance.json"
    if not meta_p.exists() or not all((folder / f"{LAYER}{ext}").exists() for ext in WANTED):
        return None
    meta = json.loads(meta_p.read_text("utf-8"))
    files = {ext: (folder / f"{LAYER}{ext}").read_bytes() for ext in WANTED}
    return Download(files, meta["url"], meta["recupere_le"], 0, 0)


# -- shapefile ---------------------------------------------------------------------------------------------------------
def _read_dbf(dbf: bytes, encoding: str) -> list[dict[str, Any]]:
    n, header_len, _rec_len = struct.unpack("<IHH", dbf[4:12])
    fields: list[tuple[str, str, int, int]] = []
    p = 32
    while dbf[p] != 0x0D:
        name = dbf[p:p + 11].split(b"\0", 1)[0].decode("ascii")
        fields.append((name, chr(dbf[p + 11]), dbf[p + 16], dbf[p + 17]))
        p += 32
    rows: list[dict[str, Any]] = []
    p = header_len
    for _ in range(n):
        rec = dbf[p:p + 1 + sum(f[2] for f in fields)]
        p += len(rec)
        if rec[:1] == b"*":  # deleted record
            rows.append({})
            continue
        q, row = 1, {}
        for name, typ, length, dec in fields:
            raw = rec[q:q + length].decode(encoding, errors="replace").strip()
            q += length
            value: Any = raw
            if typ in "NF":
                value = None if not raw else (int(raw) if dec == 0 and typ == "N" else float(raw))
            row[name] = value
        rows.append(row)
    return rows


def _signed_area(ring: Sequence[Point]) -> float:
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in pairwise(ring))


def _inside(pt: Point, ring: Sequence[Point]) -> bool:
    x, y = pt
    hit = False
    for (x0, y0), (x1, y1) in pairwise(ring):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


def _group_rings(rings: list[list[Point]]) -> list[list[list[Point]]]:
    """Shapefile rings → polygons: outer rings are clockwise (negative area), holes counter-clockwise."""
    outers = [[r] for r in rings if _signed_area(r) < 0]
    for r in rings:
        if _signed_area(r) >= 0:
            host = next((o for o in outers if _inside(r[0], o[0])), None)
            if host is None:
                outers.append([r])  # orphan hole: kept as a polygon rather than lost
            else:
                host.append(r)
    return outers


def read_shapefile(shp: bytes, dbf: bytes, encoding: str = "utf-8") -> list[dict[str, Any]]:
    """GeoJSON features (WGS84 lon/lat) from a polygon shapefile in LV95; one feature per record."""
    rows = _read_dbf(dbf, encoding)
    feats: list[dict[str, Any]] = []
    p, i = 100, 0
    while p + 8 <= len(shp):
        _num, words = struct.unpack(">2i", shp[p:p + 8])
        content = shp[p + 8:p + 8 + 2 * words]
        p += 8 + 2 * words
        props = rows[i] if i < len(rows) else {}
        i += 1
        (stype,) = struct.unpack("<i", content[:4])
        if stype == 0 or not props:
            continue
        if stype not in (5, 15, 25):
            raise ValueError(f"type de forme {stype} inattendu (polygones attendus)")
        n_parts, n_points = struct.unpack("<2i", content[36:44])
        parts = list(struct.unpack(f"<{n_parts}i", content[44:44 + 4 * n_parts]))
        off = 44 + 4 * n_parts
        xy = struct.unpack(f"<{2 * n_points}d", content[off:off + 16 * n_points])
        pts = [(xy[2 * k], xy[2 * k + 1]) for k in range(n_points)]
        rings = [pts[a:b] for a, b in zip(parts, [*parts[1:], n_points], strict=True)]
        polys = _group_rings(rings)
        coords = [[[list(lv95_to_wgs84(e, n)) for e, n in r] for r in poly] for poly in polys]
        feats.append({"type": "Feature", "properties": props, "geometry": {"type": "MultiPolygon",
                                                                           "coordinates": coords}})
    return feats


# -- simplification ----------------------------------------------------------------------------------------------------
def _dist(p: Point, a: Point, b: Point) -> float:
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    return abs(dy * (px - ax) - dx * (py - ay)) / math.hypot(dx, dy)


def simplify(points: Sequence[Point], tolerance: float) -> list[Point]:
    """Douglas–Peucker: both ends kept, and at least the farthest interior point (an arc never becomes a chord that
    another arc between the same nodes could also become; a closed ring keeps a real polygon)."""
    n = len(points)
    if n <= 2:
        return list(points)
    keep = [False] * n
    keep[0] = keep[-1] = True
    stack = [(0, n - 1, True)]
    while stack:
        a, b, force = stack.pop()
        if b - a < 2:
            continue
        best, idx = -1.0, a + 1
        for k in range(a + 1, b):
            d = _dist(points[k], points[a], points[b])
            if d > best:
                best, idx = d, k
        if best > tolerance or force:
            keep[idx] = True
            closed = points[a] == points[b]  # a closed ring needs a third point after its farthest one
            stack.append((a, idx, closed))
            stack.append((idx, b, closed))
    return [p for p, k in zip(points, keep, strict=True) if k]


# -- topology, outline, output -----------------------------------------------------------------------------------------
def _open_ring(points: Iterable[Point]) -> list[Point]:
    """Ring without its closing point and without consecutive repeats."""
    out: list[Point] = []
    for p in points:
        if not out or p != out[-1]:
            out.append(p)
    while len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def _junctions(rings: Iterable[list[Point]]) -> set[Point]:
    """Points whose neighbours differ between two occurrences: the nodes where a border changes neighbour."""
    seen: dict[Point, tuple[Point, Point]] = {}
    nodes: set[Point] = set()
    for r in rings:
        n = len(r)
        for i, p in enumerate(r):
            a, b = r[i - 1], r[(i + 1) % n]
            pair = (a, b) if a <= b else (b, a)
            q = seen.setdefault(p, pair)
            if q != pair:
                nodes.add(p)
    return nodes


def _cut(ring: list[Point], nodes: set[Point]) -> list[list[Point]]:
    """Arcs of a ring (each from node to node, ends included); a ring without node is one closed arc that starts at
    its smallest point, so that the two sides of an enclave give the same arc."""
    idx = [i for i, p in enumerate(ring) if p in nodes]
    if not idx:
        k = ring.index(min(ring))
        return [ring[k:] + ring[:k] + [ring[k]]]
    r = ring[idx[0]:] + ring[:idx[0]]
    cuts = [i - idx[0] for i in idx] + [len(r)]
    r = [*r, r[0]]
    return [r[a:b + 1] for a, b in pairwise(cuts)]


def _clean(ring: list[Point]) -> list[Point] | None:
    """Rounded ring without repeats, or None when it is degenerate (fewer than three points, area too small)."""
    r = _open_ring(ring)
    if len(set(r)) < 3 or len(set(r)) != len(r) or abs(_signed_area([*r, r[0]])) < MIN_RING_AREA:
        return None
    return r


def _fmt(v: float) -> str:
    s = f"{v:.1f}".removesuffix(".0")
    return "0" if s == "-0" else s


def _path(rings: Iterable[list[Point]]) -> str:
    return "".join("M" + "L".join(f"{_fmt(x)} {_fmt(y)}" for x, y in r) + "Z" for r in rings)


def _chain(arcs: list[list[Point]]) -> list[list[Point]]:
    """Rings from undirected arcs (canton outline)."""
    at: dict[Point, list[int]] = {}
    for i, a in enumerate(arcs):
        at.setdefault(a[0], []).append(i)
        at.setdefault(a[-1], []).append(i)
    used = [False] * len(arcs)
    rings = []
    for i in range(len(arcs)):
        if used[i]:
            continue
        used[i] = True
        ring, start, end = list(arcs[i]), arcs[i][0], arcs[i][-1]
        while end != start:
            j = next((j for j in at.get(end, []) if not used[j]), None)
            if j is None:
                break  # open chain (should not happen with closed rings): drawn as it is
            used[j] = True
            nxt = arcs[j] if arcs[j][0] == end else arcs[j][::-1]
            ring += nxt[1:]
            end = ring[-1]
        rings.append(ring)
    return rings


def _polygons(geometry: dict[str, Any]) -> list[list[list[list[float]]]]:
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiPolygon":
        return list(geometry["coordinates"])
    raise ValueError(f"géométrie {geometry['type']} inattendue")


def build(features: Iterable[dict[str, Any]], *, url: str, retrieved_at: str, vintage: str = VINTAGE,
          tolerance: float = DEFAULT_TOLERANCE, canton: int = CANTON_VS) -> dict[str, Any]:
    """communes_vs.json: one simplified SVG path per commune of the canton, plus the canton outline."""
    names: dict[int, str] = {}
    rings: list[tuple[int, bool, list[Point]]] = []  # (bfs, outer?, open ring in projected units)
    for f in features:
        p = f["properties"]
        if p.get("KANTONSNUM") != canton or p.get("OBJEKTART") != "Gemeindegebiet":
            continue
        bfs = int(p["BFS_NUMMER"])
        names[bfs] = str(p["NAME"])
        for poly in _polygons(f["geometry"]):
            for j, ring in enumerate(poly):
                r = _open_ring(project(lon, lat) for lon, lat, *_z in ring)
                if len(r) >= 3:
                    rings.append((bfs, j == 0, r))

    nodes = _junctions(r for _b, _o, r in rings)
    arcs: list[list[Point]] = []
    index: dict[tuple[Point, ...], int] = {}
    uses: list[int] = []
    ring_arcs: list[list[tuple[int, bool]]] = []
    for _b, _o, r in rings:
        refs = []
        for arc in _cut(r, nodes):
            key, rkey = tuple(arc), tuple(reversed(arc))
            if key in index:
                refs.append((index[key], True))
            elif rkey in index:
                refs.append((index[rkey], False))
            else:
                index[key] = len(arcs)
                arcs.append(arc)
                uses.append(0)
                refs.append((index[key], True))
            uses[refs[-1][0]] += 1
        ring_arcs.append(refs)

    simple = [[(round(x, 1), round(y, 1)) for x, y in simplify(a, tolerance)] for a in arcs]

    def assemble(refs: list[tuple[int, bool]]) -> list[Point]:
        pts: list[Point] = []
        for i, forward in refs:
            seg = simple[i] if forward else simple[i][::-1]
            pts += seg if not pts else seg[1:]
        return pts

    per_commune: dict[int, list[list[Point]]] = {b: [] for b in names}
    largest: dict[int, tuple[float, list[Point]]] = {}
    for (bfs, outer, _r), refs in zip(rings, ring_arcs, strict=True):
        pts = assemble(refs)
        clean = _clean(pts)
        if clean is None:
            raw = _open_ring(pts)
            if outer and len(set(raw)) >= 3 and abs(_signed_area([*raw, raw[0]])) > largest.get(bfs, (0.0, []))[0]:
                largest[bfs] = (abs(_signed_area([*raw, raw[0]])), raw)
            continue
        area = _signed_area([*clean, clean[0]])
        if (area > 0) != outer:  # outer rings positive, holes negative (screen coordinates, y down)
            clean.reverse()
        per_commune[bfs].append(clean)
    for bfs, (_a, raw) in largest.items():
        if not any(_signed_area([*r, r[0]]) > 0 for r in per_commune[bfs]):  # never lose a commune entirely
            per_commune[bfs].append(raw if _signed_area([*raw, raw[0]]) > 0 else raw[::-1])

    outline = [r for r in (_clean(c) for c in _chain([simple[i] for i, n in enumerate(uses) if n == 1])) if r]
    pts_all = [p for rs in per_commune.values() for r in rs for p in r]
    bbox = [min(p[0] for p in pts_all), min(p[1] for p in pts_all), max(p[0] for p in pts_all),
            max(p[1] for p in pts_all)] if pts_all else []
    return {
        "meta": {"source": SOURCE, "attribution": ATTRIBUTION, "licence": LICENSE, "url": url,
                 "recupere_le": retrieved_at, "millesime": vintage,
                 "projection": {"lon0": LON0, "lat1": LAT1, "k": K, "cos_lat": COS_LAT_DEG},
                 "tolerance": tolerance, "bbox": bbox},
        "canton": _path(outline) or None,
        "communes": [{"bfs": b, "nom": names[b], "d": _path(per_commune[b])} for b in sorted(names)
                     if per_commune[b]],
    }


# -- correspondence with the names of the presentation -----------------------------------------------------------------
def _norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"\s*\((vs|valais|wallis)\)\s*$", "", s.strip())
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def match_communes(names: Iterable[str], communes: list[dict[str, Any]],
                   localities: list[dict[str, Any]]) -> dict[str, int | None]:
    """BFS number of the boundary drawn for each name (via the official directory of localities, then by
    normalised name); None when no boundary matches. Never guesses a boundary."""
    have = {int(c["bfs"]) for c in communes}
    by_name = {_norm(c["nom"]): int(c["bfs"]) for c in communes}
    directory = {_norm(str(r["commune"])): int(r["bfs"]) for r in localities}
    out: dict[str, int | None] = {}
    for n in names:
        k = _norm(n)
        bfs = directory.get(k)
        out[n] = bfs if bfs in have else by_name.get(k)
    return out


def dumps(data: dict[str, Any]) -> str:
    """JSON with one commune per line (readable diffs), identical to ``json.dumps`` once read back."""
    rows = [json.dumps(c, ensure_ascii=False, allow_nan=False) for c in data["communes"]]
    return "\n".join([
        "{",
        f' "meta": {json.dumps(data["meta"], ensure_ascii=False, allow_nan=False)},',
        f' "canton": {json.dumps(data["canton"], ensure_ascii=False)},',
        ' "communes": [',
        ",\n".join("  " + r for r in rows),
        " ]",
        "}",
    ]) + "\n"
