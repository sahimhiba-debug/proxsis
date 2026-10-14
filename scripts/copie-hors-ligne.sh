#!/usr/bin/env bash
# Copie hors ligne versionnée de la démonstration (pour une clé USB) : l'export statique d'UN commit, construit depuis
# une extraction propre de ce commit (aucun fichier local ne s'y glisse), essayé avant d'être livré, avec son numéro de
# version, l'empreinte de chaque fichier et trois lignes pour l'ouvrir sans réseau.
#
# Usage, depuis la racine du dépôt :  scripts/copie-hors-ligne.sh [dossier de destination]   (défaut : copies-hors-ligne)
# Puis copier le dossier produit sur la clé ; sur la clé, « shasum -a 256 -c SHA256SUMS » vérifie la copie.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "Des modifications ne sont pas commitées : la copie doit correspondre exactement à un commit." >&2
  exit 1
fi
SHA=$(git rev-parse --short=7 HEAD)
DATE=$(git log -1 --format=%cs HEAD)
NAME="proxsis-hors-ligne-$DATE-$SHA"
DEST="${1:-copies-hors-ligne}/$NAME"
if [ -e "$DEST" ]; then echo "$DEST existe déjà." >&2; exit 1; fi

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
git archive HEAD | tar -x -C "$WORK"
echo "Construction de l'export statique du commit $SHA…"
( cd "$WORK/apps/web" && npm ci --no-audit --no-fund --loglevel=error && STATIC_EXPORT=1 npx next build > "$WORK/build.log" 2>&1 ) \
  || { tail -20 "$WORK/build.log" >&2; exit 1; }

# essai avant livraison : la copie s'ouvre sans réseau, en français et en allemand
PORT=$(python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
python3 -m http.server "$PORT" --bind 127.0.0.1 -d "$WORK/apps/web/out" > /dev/null 2>&1 &
SERVER=$!
sleep 1
for path in /fr/ /de/ /fr/presentation/ /de/presentation/ /fr/semaine/M1/; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT$path")
  if [ "$code" != "200" ]; then kill "$SERVER"; echo "Essai échoué : $path répond $code." >&2; exit 1; fi
done
kill "$SERVER"
wait "$SERVER" 2> /dev/null || true

mkdir -p "$DEST"
cp -R "$WORK/apps/web/out" "$DEST/site"
cat > "$DEST/LISEZMOI.txt" <<EOF
Proxsis, démonstration hors ligne — version $DATE ($SHA). Aucune connexion nécessaire.

1. Ouvrir le Terminal, taper « cd » suivi d'une espace, glisser ce dossier dans la fenêtre, puis Entrée.
2. Taper :  python3 -m http.server 8000 -d site
3. Ouvrir http://localhost:8000/fr/presentation/ dans le navigateur (en allemand : /de/presentation/) ; Ctrl+C pour arrêter.

Vérifier la copie (facultatif) :  shasum -a 256 -c SHA256SUMS
EOF
{ echo "commit: $(git rev-parse HEAD)"; echo "date du commit: $DATE"; echo "construite le: $(date -u +%Y-%m-%dT%H:%MZ)";
  echo "node: $(node --version)"; echo "next: $(node -p 'require("./apps/web/package.json").dependencies.next')"; } > "$DEST/VERSION.txt"
( cd "$DEST" && find site -type f | LC_ALL=C sort | while IFS= read -r f; do shasum -a 256 "$f"; done > SHA256SUMS )
( cd "$DEST" && shasum -a 256 -c SHA256SUMS > /dev/null ) && echo "Copie prête et vérifiée : $DEST ($(du -sh "$DEST" | cut -f1))"
