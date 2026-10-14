"""La petite Iris (debout sur son manche) et l'icône (la tête de face), tirées de vues.jpg.

Sorties dans docs/identite/mascotte/petite/ :
  face.png, face-oeil-g.png, face-oeil-d.png   de face, sans les yeux, et ses deux yeux (pour les animer)
  trois-quarts.png, trois-quarts-oeil-*.png   de trois quarts, tournée vers la droite
  tete.png                                     la tête de face seule (pour l'icône)
  petite.json                                  positions des yeux
Puis les icônes de l'application dans apps/web (onglet, écran d'accueil, manifeste).

Détourage : macOS (Vision), `build/mask docs/.../vues.jpg build/vues` (voir mask.swift) ; yeux retirés par remplissage
harmonique de la visière (comme calques.py).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import splu

S = Path(__file__).resolve().parent
ROOT = S.parents[1]
OUT = ROOT / "docs/identite/mascotte/petite"
OUT.mkdir(parents=True, exist_ok=True)
WEB = ROOT / "apps/web"

src = np.asarray(Image.open(ROOT / "docs/identite/mascotte/images/vues.jpg").convert("RGB")).astype(np.float64) / 255
H, W, _ = src.shape


def harmonic_fill(image, hole):
    idx = -np.ones(hole.shape, dtype=np.int64)
    ys, xs = np.nonzero(hole)
    idx[ys, xs] = np.arange(len(ys))
    n = len(ys)
    A = lil_matrix((n, n))
    b = np.zeros((n, image.shape[2]))
    h, w = hole.shape
    for k, (y, x) in enumerate(zip(ys, xs)):
        nb = 0
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w:
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


masks = []
for i in range(1, 5):
    m = np.asarray(Image.open(S / f"build/vues/mask_{i}.png").convert("L")).astype(np.float64) / 255
    ys, xs = np.nonzero(m > 0.5)
    masks.append((xs.min(), m))
masks.sort(key=lambda t: t[0])  # de gauche à droite : face, trois-quarts, profil, dos


def cut(view, mask, name):
    ys, xs = np.nonzero(mask > 0.5)
    pad = 6
    x0, x1, y0, y1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, W), max(ys.min() - pad, 0), min(ys.max() + pad + 1, H)
    rgb = view[y0:y1, x0:x1].copy()
    a = mask[y0:y1, x0:x1].copy()
    a = np.maximum(a, ndi.binary_fill_holes(a > 0.5).astype(np.float64))  # le détourage laisse des trous dans les yeux, trop clairs
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    hh, ww = a.shape
    # les yeux : les deux taches claires et chaudes à l'intérieur de la visière (zone grise, peu saturée)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    grey = (sat < 0.09) & (lum > 0.45) & (a > 0.5)
    glab, gn = ndi.label(grey)
    gsz = ndi.sum(grey, glab, range(1, gn + 1))
    from skimage.morphology import convex_hull_image
    visor = convex_hull_image(glab == (1 + int(np.argmax(gsz))))  # la visière est un rectangle arrondi : convexe
    warm = rgb[..., 0] > rgb[..., 2] + 0.035
    bright = (lum > 0.80) & warm & ndi.binary_erosion(visor, iterations=2)
    lab, n = ndi.label(bright)
    sizes = ndi.sum(bright, lab, range(1, n + 1))
    eyes = sorted([i + 1 for i in np.argsort(sizes)[-2:]], key=lambda i: ndi.center_of_mass(bright, lab, i)[1])
    hole = np.zeros_like(bright)
    boxes = []
    for i in eyes:
        yy, xx = np.nonzero(lab == i)
        boxes.append((int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())))
        hole |= ndi.binary_dilation(lab == i, iterations=13)
    hole &= ndi.binary_erosion(visor, iterations=1)  # la retouche reste dans la visière
    filled = harmonic_fill(rgb, hole)
    meta = {"w": ww, "h": hh, "eyes": []}
    for side, (ex0, ey0, ex1, ey1) in zip(("g", "d"), boxes):
        p = 10
        X0, Y0, X1, Y1 = max(ex0 - p, 0), max(ey0 - p, 0), min(ex1 + p + 1, ww), min(ey1 + p + 1, hh)
        crop, bg = rgb[Y0:Y1, X0:X1], filled[Y0:Y1, X0:X1]
        d = np.clip((crop - bg).max(axis=2), 0, None)
        peak = np.percentile(d[d > 0], 99) if (d > 0).any() else 1
        ea = np.clip(d / max(peak, 1e-3), 0, 1)
        col = np.clip(bg + (crop - bg) / np.maximum(ea[..., None], 1e-3), 0, 1)
        Image.fromarray((np.dstack([col, ea]) * 255).astype(np.uint8), "RGBA").save(OUT / f"{name}-oeil-{side}.png")
        meta["eyes"].append({"x": X0, "y": Y0, "w": X1 - X0, "h": Y1 - Y0, "cx": (ex0 + ex1) / 2, "cy": (ey0 + ey1) / 2,
                             "ew": ex1 - ex0 + 1, "eh": ey1 - ey0 + 1})
    rgba = np.dstack([filled, a])
    rgba[a < 0.002, :3] = 0
    Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(OUT / f"{name}.png")
    # avec les yeux d'origine, pour l'image fixe et l'icône
    full = np.dstack([rgb, a]); full[a < 0.002, :3] = 0
    Image.fromarray((full * 255).astype(np.uint8), "RGBA").save(OUT / f"{name}-yeux.png")
    return meta


meta = {"face": cut(src, masks[0][1], "face"), "trois-quarts": cut(src, masks[1][1], "trois-quarts")}

# la tête seule (sans le manche), de face, avec ses yeux d'origine
face = Image.open(OUT / "face-yeux.png")
fa = np.asarray(face)[..., 3] > 128
rows = fa.sum(axis=1)
# le manche est bien plus étroit que la tête : la tête finit là où la largeur chute
widths = rows / max(rows.max(), 1)
neck = next(y for y in range(int(len(widths) * 0.3), len(widths)) if widths[y] < 0.45)
head = face.crop((0, 0, face.width, neck + 2))
head.save(OUT / "tete.png")
meta["tete"] = {"w": head.width, "h": head.height}
(OUT / "petite.json").write_text(json.dumps(meta, indent=2))


# --- les icônes de l'application ---
def icon(size, bg=(255, 255, 255, 255), pad=0.12, radius=0.22, sharpen=True):
    """La tête de face, centrée sur un carré blanc arrondi ; à petite taille, la visière est assombrie et les yeux
    éclaircis pour rester lisibles."""
    k = 4  # dessin à 4× puis réduction
    S4 = size * k
    canvas = Image.new("RGBA", (S4, S4), (0, 0, 0, 0))
    mask = Image.new("L", (S4, S4), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, S4 - 1, S4 - 1), radius=int(S4 * radius), fill=255)
    canvas.paste(Image.new("RGBA", (S4, S4), bg), (0, 0), mask)
    h = head.copy()
    if size <= 48:
        arr = np.asarray(h).astype(np.float64) / 255
        lum = arr[..., :3] @ np.array([0.299, 0.587, 0.114])
        sat = arr[..., :3].max(axis=2) - arr[..., :3].min(axis=2)
        visor = (lum > 0.55) & (lum < 0.84) & (sat < 0.08)
        eyes = lum >= 0.84
        arr[visor, :3] *= 0.62
        arr[eyes, :3] = np.clip(arr[eyes, :3] * 1.15 + 0.05, 0, 1)
        h = Image.fromarray((arr * 255).astype(np.uint8), "RGBA")
    inner = int(S4 * (1 - 2 * pad))
    hw, hh = h.size
    scale = inner / max(hw, hh)
    h = h.resize((max(1, int(hw * scale)), max(1, int(hh * scale))), Image.LANCZOS)
    canvas.alpha_composite(h, ((S4 - h.width) // 2, (S4 - h.height) // 2))
    out = canvas.resize((size, size), Image.LANCZOS)
    if sharpen and size <= 64:
        out = out.filter(ImageFilter.UnsharpMask(radius=0.6, percent=80, threshold=1))
    return out


icons = OUT / "icones"
icons.mkdir(exist_ok=True)
def small_or_big(s, **kw):
    # à 16, 32 et 48 px, la tête occupe presque tout le carré pour que les yeux restent visibles
    return icon(s, pad=0.04, radius=0.18, **kw) if s <= 48 else icon(s, **kw)


for s in (16, 32, 48, 64, 180, 192, 512):
    small_or_big(s).save(icons / f"iris-{s}.png")
# en grand : un peu plus d'air, pour les icônes masquées des téléphones
icon(512, pad=0.16).save(icons / "iris-512-masquable.png")

# dans l'application (sur la branche) : onglet, écran d'accueil, manifeste
icon(180, radius=0).convert("RGB").save(WEB / "src/app/apple-icon.png")
icon(192).save(WEB / "public/icon-192.png")
icon(512).save(WEB / "public/icon-512.png")
icon(512, pad=0.16, radius=0).save(WEB / "public/icon-512-maskable.png")
small_or_big(32).save(icons / "favicon-32.png")
small_or_big(32).save(WEB / "src/app/icon.png")
ico = [small_or_big(s) for s in (16, 32, 48)]
ico[0].save(WEB / "src/app/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[1:])
print("ok", json.dumps(meta)[:200])
