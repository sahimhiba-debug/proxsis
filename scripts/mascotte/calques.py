"""Découpe portrait.jpg en calques pour l'essai d'Iris qui frappe (sans crédits).

Calques (tous à la taille de l'image, 1024 × 1024, superposés à l'origine) :
  decor.png         le fond, la tête, le manche et la roue retirés et le vide retouché (remplissage harmonique)
  roue.png          la roue orange seule (masque par couleur)
  devant-bisse.png  le bord avant du bisse et le palier, qui passent devant la roue
  tete.png          la tête et son manche, sans les yeux
  oeil-g.png, oeil-d.png   les deux yeux lumineux, découpés
  devant-chevalet.png      les pieds avant du chevalet, qui passent devant le manche
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import splu

S = Path(__file__).resolve().parent
ROOT = S.parents[1]
SRC = ROOT / "docs/identite/mascotte/images/portrait.jpg"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/identite/mascotte/calques"
OUT.mkdir(parents=True, exist_ok=True)

img = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float64) / 255
H, W, _ = img.shape
# détourage de macOS (Vision) : `swiftc -O mask.swift -o /tmp/mask && /tmp/mask portrait.jpg .` écrit mask_all.png
vis = np.asarray(Image.open(S / "mask_all.png").convert("L")).astype(np.float64) / 255
vis = np.maximum(vis, ndi.binary_fill_holes(vis > 0.5).astype(np.float64))  # pas de trou dans les yeux ni la visière


def poly(points):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(points, fill=255)
    return np.asarray(m) > 0


def soft(mask, r=1.0):
    return ndi.gaussian_filter(mask.astype(np.float64), r)


def orange_mask():
    """La roue par sa couleur : teinte orange franche, dans le cadre de la roue, sans les éclats au-dessus."""
    from skimage.color import rgb2hsv
    hsv = rgb2hsv(img)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    m = ((h < 32) | (h > 350)) & (s > 0.55) & (v > 0.25)
    box = np.zeros_like(m)
    box[420:720, 470:790] = True
    m &= box
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    m = np.isin(lab, 1 + np.where(sizes > 40)[0])
    m = ndi.binary_closing(m, iterations=2)
    m[:444, :] = False
    return m


def harmonic_fill(image, hole):
    """Remplit les pixels de `hole` par la solution de Laplace (bord = pixels connus)."""
    idx = -np.ones(hole.shape, dtype=np.int64)
    ys, xs = np.nonzero(hole)
    idx[ys, xs] = np.arange(len(ys))
    n = len(ys)
    A = lil_matrix((n, n))
    b = np.zeros((n, image.shape[2]))
    for k, (y, x) in enumerate(zip(ys, xs)):
        nb = 0
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W:
                nb += 1
                j = idx[yy, xx]
                if j >= 0:
                    A[k, j] = -1
                else:
                    b[k] += image[yy, xx]
        A[k, k] = nb
    lu = splu(csr_matrix(A).tocsc())
    out = image.copy()
    for c in range(image.shape[2]):
        out[ys, xs, c] = lu.solve(b[:, c])
    return out


orange = orange_mask()
# l'intérieur sombre de la roue (ombres orangées entre les rayons), seulement dans l'ellipse de la jante
_yy, _xx = np.mgrid[0:H, 0:W]
_c, _s = np.cos(np.radians(6.6)), np.sin(np.radians(6.6))
_u = ((_xx - 655.9) * _c + (_yy - 615.1) * _s) / 96.0
_v = (-(_xx - 655.9) * _s + (_yy - 615.1) * _c) / 133.0
inside_rim = _u ** 2 + _v ** 2 <= 1.0
from skimage.color import rgb2hsv as _hsv
_h = _hsv(img)
colorful = (_h[..., 1] > 0.45) & ((_h[..., 0] * 360 < 38) | (_h[..., 0] * 360 > 345))  # orange franc, même à l'ombre ; pas le bois
reddish = (img[..., 0] - img[..., 1] > 0.10) & (img[..., 0] - img[..., 2] > 0.16) & colorful
above_trough = _yy < 685 - (_xx - 565) * 0.2326  # au-dessus du bord avant du bisse
orange = ndi.binary_closing(orange | (reddish & inside_rim & above_trough), iterations=1)
orange &= colorful | ndi.binary_erosion(orange, iterations=2)  # les bords bruns tombent, l'intérieur reste

# --- régions dessinées à la main (coordonnées relevées sur des grilles agrandies) ---
PIVOT = (907.0, 432.0)  # le boulon du chevalet
head_handle_poly = poly([
    (138, 192), (562, 192), (562, 350), (750, 378), (860, 396), (917, 401), (962, 413),
    (962, 478), (850, 464), (750, 454), (600, 442), (562, 440), (562, 512), (138, 512),
])
frame_poly = poly([(861, 385), (917, 385), (936, 520), (846, 520)])
# tout ce qui est devant la roue : la face avant du bisse jusqu'au sol, et la planche
trough_poly = poly([(470, 707), (565, 685), (830, 623), (862, 623), (862, 1024), (470, 1024)])
board_poly = poly([(118, 639), (567, 694), (568, 738), (440, 777), (118, 680)])
axle_poly = poly([(663, 610), (704, 606), (709, 663), (667, 666)])

orange &= ~(poly([(558, 688), (565, 685), (830, 623), (848, 623), (848, 770), (558, 770)])
             | poly([(663, 610), (704, 606), (709, 663), (667, 666)]))  # le bord du bisse et le palier restent devant
orange_soft = soft(orange, 0.7)
head_mask = (head_handle_poly & ~frame_poly & ~ndi.binary_dilation(orange, iterations=1))
head_alpha = np.clip(vis * soft(head_mask, 0.6), 0, 1)
_hl, _hn = ndi.label(head_alpha > 0.04)
if _hn > 1:  # la tête et son manche seulement, sans éclat détaché
    _hs = ndi.sum(head_alpha > 0.04, _hl, range(1, _hn + 1))
    head_alpha = head_alpha * ndi.binary_dilation(np.isin(_hl, 1 + np.where(_hs >= 0.004 * _hs.max())[0]), iterations=1)
frame_alpha = np.clip(vis * soft(frame_poly, 0.6), 0, 1)
front_alpha = soft((trough_poly | axle_poly | board_poly) & ~orange, 0.6)

# --- les yeux : taches claires et chaudes dans la visière ---
lum = img @ np.array([0.299, 0.587, 0.114])
visor_box = poly([(275, 250), (545, 250), (545, 470), (275, 470)])
bright = (lum > 0.80) & visor_box & (img[..., 0] > img[..., 2] + 0.03)
lab, n = ndi.label(bright)
sizes = ndi.sum(bright, lab, range(1, n + 1))
eyes = sorted([i + 1 for i in np.argsort(sizes)[-2:]], key=lambda i: ndi.center_of_mass(bright, lab, i)[1])
eye_boxes = []
eye_hole = np.zeros_like(bright)
for i in eyes:
    ys, xs = np.nonzero(lab == i)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    eye_boxes.append((int(x0), int(y0), int(x1), int(y1)))
    blob = ndi.binary_dilation(lab == i, iterations=16)
    eye_hole |= blob
print("yeux :", eye_boxes)

# visière sans les yeux
visor_filled = harmonic_fill(img, eye_hole)

# --- la tête sans les yeux ---
head_rgb = img.copy()
head_rgb[eye_hole] = visor_filled[eye_hole]

# --- les sprites des yeux : alpha = ce qui dépasse la visière retouchée ---
eye_meta = []
for name, (x0, y0, x1, y1) in zip(("oeil-g", "oeil-d"), eye_boxes):
    pad = 18
    X0, Y0, X1, Y1 = x0 - pad, y0 - pad, x1 + pad + 1, y1 + pad + 1
    crop = img[Y0:Y1, X0:X1]
    bg = visor_filled[Y0:Y1, X0:X1]
    d = np.clip((crop - bg).max(axis=2), 0, None)
    peak = np.percentile(d[d > 0], 99) if (d > 0).any() else 1
    a = np.clip(d / max(peak, 1e-3), 0, 1)
    col = np.clip(bg + (crop - bg) / np.maximum(a[..., None], 1e-3), 0, 1)
    col[a < 0.02] = crop[a < 0.02]
    rgba = np.dstack([col, a])
    Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(OUT / f"{name}.png")
    eye_meta.append({"name": name, "x": X0, "y": Y0, "w": X1 - X0, "h": Y1 - Y0,
                     "cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2, "ew": x1 - x0 + 1, "eh": y1 - y0 + 1})

# --- le décor : tête, manche et roue retirés ---
# Le vide est rempli par le décor que Runway a rendu sans le marteau ni la roue (images/decor-runway.png, tâche
# c8f327c5-dffd-4bfc-b7bf-d389b0d36f4b, à partir de portrait.jpg) : aligné au pixel près (décalage mesuré : 0 px).
# On garde l'original partout ailleurs ; le raccord est fondu sur quelques pixels.
wheel_box = poly([(470, 430), (800, 430), (800, 720), (470, 720)])
orange_wide = (img[..., 0] - img[..., 1] > 0.12) & (img[..., 0] - img[..., 2] > 0.20) & wheel_box
orange_wide = ndi.binary_closing(orange_wide | orange, iterations=2)
hole = ndi.binary_dilation(head_alpha > 0.03, iterations=4) | ndi.binary_dilation(orange_wide, iterations=5)
hole &= ~frame_poly  # les pieds avant du chevalet restent ceux de l'original
hole &= ~(trough_poly | axle_poly)
clean = np.asarray(Image.open(ROOT / "docs/identite/mascotte/images/decor-runway.png").convert("RGB")).astype(np.float64) / 255
m = ndi.gaussian_filter(ndi.binary_dilation(hole, iterations=2).astype(np.float64), 2.0)[..., None]
decor = img * (1 - m) + clean * m


# --- la roue entière : la partie cachée par le bisse et le palier est reconstituée par symétrie ---
# 15 palettes régulières (espacement mesuré : 24°) ; on tourne la partie visible de multiples de 24° dans le plan de la
# roue (la même transformation que la scène, wheelMatrix) et on remplit seulement ce qui manque.
def wheel_T(theta):
    a_, b_, phi_ = 91.6, 128.3, np.radians(6.6)
    r = b_ / a_
    cp, sp = np.cos(phi_), np.sin(phi_)
    ct, st = np.cos(np.radians(theta)), np.sin(np.radians(theta))
    R = lambda c, s: np.array([[c, -s], [s, c]])
    return R(cp, sp) @ np.diag([1, r]) @ R(ct, st) @ np.diag([1, 1 / r]) @ R(cp, -sp)


def rotate_layer(rgba, theta, cx=655.9, cy=615.1):
    Ti = wheel_T(-theta)  # pour chaque pixel d'arrivée, d'où vient-il
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    qx = Ti[0, 0] * (xx - cx) + Ti[0, 1] * (yy - cy) + cx
    qy = Ti[1, 0] * (xx - cx) + Ti[1, 1] * (yy - cy) + cy
    return np.dstack([ndi.map_coordinates(rgba[..., k], [qy, qx], order=1, mode="constant", cval=0) for k in range(4)])


# la roue est coupée à son plan (le bout des palettes, rayon 1,38 de la jante) : à gauche, l'épaisseur des palettes vue
# de biais tournerait avec la roue ; la scène la recrée avec une seconde roue plus sombre, décalée (la scène animée du film, retirée de l'application : historique Git)
_r = np.sqrt(_u ** 2 * (96.0 / 91.6) ** 2 + _v ** 2 * (133.0 / 128.3) ** 2)
in_plane = np.clip((1.44 - _r) / 0.04, 0, 1)
orange_soft = orange_soft * in_plane
wheel0 = np.dstack([img * orange_soft[..., None], orange_soft])  # prémultiplié
# ce qui était caché dans l'original : sous le bord avant du bisse et derrière le palier, dans le plan de la roue
hidden = ((~above_trough) | axle_poly) & (_r <= 1.42)
hidden_s = ndi.gaussian_filter(ndi.binary_dilation(hidden, iterations=2).astype(np.float64), 1.2)[..., None]
full = wheel0 * (1 - hidden_s)
remaining = hidden_s.copy()
for k in (7, -8, 8, -7):  # 168°, -192°, 192°, -168° : la partie haute, entièrement visible, vient prendre la place du bas
    rk = rotate_layer(wheel0, 24 * k)
    src_ok = rotate_layer(np.dstack([np.zeros((H, W, 3)), (~hidden).astype(np.float64)]), 24 * k)[..., 3:4]
    take = remaining * src_ok
    full = full + rk * take
    remaining = remaining - take
fa = np.clip(full[..., 3], 0, 1)
# aucun fragment détaché : seule la roue (la plus grande pièce) et ce qui la touche
_lab, _n = ndi.label(fa > 0.04)
if _n > 1:
    _sizes = ndi.sum(fa > 0.04, _lab, range(1, _n + 1))
    _keep = np.isin(_lab, 1 + np.where(_sizes >= 0.02 * _sizes.max())[0])
    fa = fa * ndi.binary_dilation(_keep, iterations=1)
wheel_rgb = np.where(fa[..., None] > 1e-3, full[..., :3] / np.maximum(fa[..., None], 1e-3), 0)


def save_rgba(rgb, alpha, name):
    rgb = rgb.copy()
    rgb[alpha <= 0.001] = 0
    rgba = np.dstack([rgb, alpha])
    Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA").save(OUT / name)


Image.fromarray((decor * 255).astype(np.uint8)).save(OUT / "decor.png")
# la roue : scripts/mascotte/roue.py (roue neuve vue de face, D12) ; l'ancienne roue reconstituée ci-dessus n'est plus écrite
# (working notes, not published)
save_rgba(img, front_alpha, "devant-bisse.png")
save_rgba(head_rgb, head_alpha, "tete.png")
save_rgba(img, frame_alpha, "devant-chevalet.png")

meta = {
    "source": "docs/identite/mascotte/images/portrait.jpg (tâche Runway 5f4ca776-d1a9-4708-bb31-1352d802d844)",
    "taille": [W, H],
    "pivot": PIVOT,
    "roue": {"cx": 655.9, "cy": 615.1, "a": 91.6, "b": 128.3, "angle": 6.6},
    "yeux": eye_meta,
}
(OUT / "calques.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
print("ok", OUT)
