"""Les images d'Iris pour le site (apps/web/public/iris/), compressées en WebP et servies à la bonne taille.

  petite/   la petite Iris debout sur son manche (de face), sans les yeux, et ses deux yeux : 240 px de haut
  logo/     la tête et son manche avec ses yeux, pour le point du « i » : 512 px
  sons/     le toc (copié de docs/identite/mascotte/sons/)
  apps/web/src/iris/iris-meta.json : les positions des yeux de la petite Iris

Sources : docs/identite/mascotte/calques/ (calques.py) et petite/ (petite.py).
"""
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
M = ROOT / "docs/identite/mascotte"
OUT = ROOT / "apps/web/public/iris"
for d in ("petite", "logo", "sons"):
    (OUT / d).mkdir(parents=True, exist_ok=True)


def webp(src: Path, dst: Path, scale: float, q: int = 82):
    im = Image.open(src).convert("RGBA")
    if scale != 1:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    im.save(dst, "WEBP", quality=q, method=6, exact=False)
    return dst.stat().st_size


total = {}
# la petite Iris : 240 px de haut (affichée jusqu'à 96 px : deux fois et demie la taille, pour les écrans denses)
meta = json.loads((M / "petite/petite.json").read_text())
face = meta["face"]
k = 240 / face["h"]
total["petite/face.webp"] = webp(M / "petite/face.png", OUT / "petite/face.webp", k)
for side in ("g", "d"):
    total[f"petite/oeil-{side}.webp"] = webp(M / f"petite/face-oeil-{side}.png", OUT / f"petite/oeil-{side}.webp", k, 90)
petite = {
    "w": round(face["w"] * k), "h": round(face["h"] * k),
    "eyes": [{key: round(v * k, 2) for key, v in e.items()} for e in face["eyes"]],
}
# le logo : la tête et ses yeux, 512 px
for n in ("tete", "oeil-g", "oeil-d"):
    total[f"logo/{n}.webp"] = webp(M / f"calques/{n}.png", OUT / f"logo/{n}.webp", 0.5, 86)
for n in ("toc-court.mp3",):
    shutil.copy(M / "sons" / n, OUT / "sons" / n)
    total[f"sons/{n}"] = (OUT / "sons" / n).stat().st_size
(ROOT / "apps/web/src/iris/iris-meta.json").write_text(json.dumps({"petite": petite}, indent=2) + "\n")
for k_, v in total.items():
    print(f"{v / 1024:7.1f} Ko  {k_}")
print(f"{sum(v for k_, v in total.items() if k_.startswith('logo')) / 1024:.1f} Ko pour le logo (premier écran)")
