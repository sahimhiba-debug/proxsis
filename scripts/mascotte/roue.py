#!/usr/bin/env python3
"""La roue d'Iris, entière (bloquant B1 de l'audit du 13.10.2026, D12).

Runway a rendu la même roue que portrait.jpg, seule, vue exactement de face, sur fond gris uni
(images/roue-face-runway-b.png, tâche 1ce1fcf8-96b0-4112-af07-899bb526743e, à partir de roue-runway-a.png, tâche
c4ce0108-293e-4c9b-91f6-aa798ae77adc, elle-même tirée de portrait.jpg). Vue de face, le moyeu et la jante ont le même
centre : la roue tourne exactement dans son plan. On la détoure par sa couleur (le fond est gris, la roue orange), puis
on la met en perspective sur l'ellipse de la jante de la scène (WHEEL de la scène animée du film, historique Git : centre 655,9 ; 615,1 ; demi-axes
91,6 et 128,3 ; inclinaison 6,6°), le moyeu sur le centre. La scène l'épaissit en empilant des copies décalées le long
de l'axe, de plus en plus sombres (WHEEL_DEPTH, même scène) : les palettes vues par la tranche redeviennent des planches.

    python3 scripts/mascotte/roue.py [roue-face-runway-b.png]   → docs/identite/mascotte/calques/roue.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
MASCOTTE = ROOT / "docs/identite/mascotte"
SRC = MASCOTTE / "images" / (sys.argv[1] if len(sys.argv) > 1 else "roue-face-runway-b.png")
OUT = MASCOTTE / "calques" / "roue.png"
W = H = 1024
CX, CY, A_, B_, PHI = 655.9, 615.1, 91.6, 128.3, np.radians(6.6)


def detoure(img):
    """Alpha par la saturation (fond gris ≈ 0, orange ≈ 0,6) ; couleurs décontaminées du gris du fond."""
    mx, mn = img.max(2), img.min(2)
    sat = np.where(mx > 1e-3, (mx - mn) / np.maximum(mx, 1e-3), 0)
    a = np.clip((sat - 0.10) / (0.32 - 0.10), 0, 1)
    a = ndi.gaussian_filter(a, 0.6)
    lab, n = ndi.label(a > 0.5)
    if n > 1:  # seule la roue (la plus grande pièce)
        tailles = ndi.sum(a > 0.5, lab, range(1, n + 1))
        a = a * ndi.binary_dilation(lab == 1 + int(np.argmax(tailles)), iterations=3)
    bord = np.concatenate([img[:20].reshape(-1, 3), img[-20:].reshape(-1, 3), img[:, :20].reshape(-1, 3), img[:, -20:].reshape(-1, 3)])
    fond = np.median(bord, axis=0)
    rgb = np.clip(fond + (img - fond) / np.maximum(a[..., None], 0.05), 0, 1)
    rgb[a < 0.02] = 0
    return rgb, a


def centre_du_moyeu(alpha):
    """Le trou de l'axe (le fond vu à travers le moyeu) : le vide rond le plus proche du centre de la roue."""
    ys, xs = np.nonzero(alpha > 0.5)
    c0 = np.array([xs.mean(), ys.mean()])
    vides = ndi.binary_fill_holes(alpha > 0.5) & (alpha < 0.5)
    lab, n = ndi.label(vides)
    best, bd = c0, 1e9
    for i in range(1, n + 1):
        yy, xx = np.nonzero(lab == i)
        if len(xx) < 20: continue
        w, h = xx.max() - xx.min() + 1, yy.max() - yy.min() + 1
        c = np.array([xx.mean(), yy.mean()])
        if min(w, h) / max(w, h) > 0.75 and np.linalg.norm(c - c0) < bd: best, bd = c, np.linalg.norm(c - c0)
    return best


def rayon_exterieur(alpha, c):
    """Le bord extérieur de la jante : le plus grand rayon où la roue couvre encore presque tous les angles."""
    yy, xx = np.mgrid[0:alpha.shape[0], 0:alpha.shape[1]]
    r = np.hypot(xx - c[0], yy - c[1]).astype(int)
    on = (alpha > 0.5).astype(float)
    idx = np.arange(r.max() + 1)
    couvert = ndi.sum(on, r, index=idx) / np.maximum(1, ndi.sum(np.ones_like(on), r, index=idx))
    return float(np.nonzero(couvert > 0.9)[0].max())


def main():
    img = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float64) / 255
    rgb, a = detoure(img)
    c = centre_du_moyeu(a)
    R = rayon_exterieur(a, c)
    # de la roue de face (repère centré sur le moyeu, rayon R) vers la scène : R(φ) · diag(a, b) / R
    cp, sp = np.cos(PHI), np.sin(PHI)
    T = np.array([[cp, -sp], [sp, cp]]) @ np.diag([A_, B_]) / R
    Ti = np.linalg.inv(T)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    q = Ti @ np.stack([xx.ravel() - CX, yy.ravel() - CY])
    qx, qy = q[0] + c[0], q[1] + c[1]
    pre = np.dstack([rgb * a[..., None], a])
    out = np.dstack([ndi.map_coordinates(pre[..., i], [qy, qx], order=1, mode="constant", cval=0).reshape(H, W) for i in range(4)])
    al = np.clip(out[..., 3], 0, 1)
    col = np.where(al[..., None] > 1e-3, out[..., :3] / np.maximum(al[..., None], 1e-3), 0)
    Image.fromarray((np.clip(np.dstack([col, al]), 0, 1) * 255).astype(np.uint8), "RGBA").save(OUT)
    print(f"ok {OUT.relative_to(ROOT)} · moyeu {c.round(1)} · jante (rayon extérieur) {R:.0f} px → ellipse {A_} × {B_}")


if __name__ == "__main__":
    main()
