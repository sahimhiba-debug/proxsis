"""Refait apps/web/src/data/demo/claims.json depuis CLAIMS.md, sans tout réexporter (la règle du moteur,
proxsis.demo_export.parse_claims : une ligne de tableau à 7 colonnes = une affirmation ; même écriture JSON).
  cd python && uv run python ../scripts/claims/vers-json.py [--verifier]   (--verifier : échoue si le fichier n'est pas à jour)"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "src"))
from proxsis.demo_export import parse_claims  # noqa: E402


text = json.dumps(parse_claims(ROOT / "CLAIMS.md"), ensure_ascii=False, indent=1, allow_nan=False) + "\n"
target = ROOT / "apps/web/src/data/demo/claims.json"
if "--verifier" in sys.argv:
    sys.exit(0 if target.read_text("utf-8") == text else 1)
target.write_text(text, "utf-8")
print(f"{len(json.loads(text))} affirmations → {target.relative_to(ROOT)}")
