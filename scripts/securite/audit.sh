#!/usr/bin/env bash
# Audit de sécurité reproductible (docs/securite/AUDIT_DEPENDANCES.md) : vulnérabilités connues des dépendances
# (npm, pip-audit), recherche de secrets dans les fichiers suivis et dans tout l'historique, licences des dépendances
# livrées. N'affiche jamais un secret trouvé : seulement le fichier et la ligne (ou le commit). Lecture seule.
# Réseau : le registre npm et l'index PyPI (bases de vulnérabilités publiques), rien d'autre.
# Usage, depuis la racine du dépôt : scripts/securite/audit.sh
set -uo pipefail
# the secret search reads git: outside a repository (an archive, a copy) it would examine nothing and conclude « none »
root=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Pas un dépôt git : la recherche de secrets n'examinerait rien. Lancer depuis un clone." >&2; exit 2; }
cd "$root"
PIP_AUDIT_VERSION=2.10.1
status=0

echo "== npm : dépendances livrées (sans les outils de développement)"
(cd apps/web && npm audit --omit=dev) || status=1

echo "== npm : toutes les dépendances, outils de développement compris (pour information)"
(cd apps/web && npm audit --json) | node -e '
const r = JSON.parse(require("fs").readFileSync(0, "utf8"));
const v = Object.values(r.vulnerabilities || {});
const roots = v.filter((x) => x.via.some((a) => typeof a === "object"));
console.log(roots.length ? `faille à la racine : ${roots.map((x) => `${x.name} (${x.severity} ; ${x.via.filter((a) => typeof a === "object").map((a) => a.url).join(", ")})`).join(" ; ")}` : "aucune faille");
if (v.length > roots.length) console.log(`atteints par elle : ${v.filter((x) => !roots.includes(x)).map((x) => x.name).join(", ")}`);
'

echo "== Python : dépendances installées du moteur (pip-audit $PIP_AUDIT_VERSION)"
req=$(mktemp)
uv pip freeze --python python/.venv/bin/python | grep -v -E "^-e|proxsis|file://" > "$req"
uvx --quiet "pip-audit==$PIP_AUDIT_VERSION" -r "$req" --no-deps --disable-pip --progress-spinner off || status=1
rm -f "$req"

echo "== Secrets : fichiers suivis puis tout l'historique (emplacements seulement)"
PAT='(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[baprs]-[A-Za-z0-9-]{10,}|eyJhbGciOi[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}|PUBLICAI_API_KEY *= *[A-Za-z0-9]{8,}|SUPABASE_SERVICE_ROLE_KEY *= *[A-Za-z0-9])'
files=$(git grep -lIE "$PAT" -- . ':!*package-lock.json' ':!*.lock' || true)
commits=$(git log --all --format=%h | while read -r c; do
  git show --format= --no-color "$c" | grep -qE "$PAT" && echo "$c"; done || true)
nfiles=$(git ls-files | wc -l | tr -d ' '); ncommits=$(git rev-list --all | wc -l | tr -d ' ')
if [ -n "$files$commits" ]; then
  echo "secret possible : fichiers [${files//$'\n'/ }] commits [${commits//$'\n'/ }]"; status=1
elif [ "$nfiles" -eq 0 ] || [ "$ncommits" -eq 0 ]; then
  echo "rien n'a été examiné ($nfiles fichiers, $ncommits commits) : aucune conclusion possible"; status=1
else
  echo "aucun secret trouvé ($nfiles fichiers suivis, $ncommits commits)"
fi

echo "== Licences des dépendances livrées de l'application"
(cd apps/web && npm ls --omit=dev --all --parseable 2>/dev/null | tail -n +2 | sort -u | node -e '
const fs = require("fs"), path = require("path");
const by = {};
for (const p of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const j = JSON.parse(fs.readFileSync(path.join(p, "package.json")));
  const l = typeof j.license === "string" ? j.license : "?";
  (by[l] = by[l] || []).push(`${j.name}@${j.version}`);
}
for (const [l, v] of Object.entries(by).sort((a, b) => b[1].length - a[1].length))
  console.log(String(v.length).padStart(4), l, ["MIT", "Apache-2.0", "ISC"].includes(l) ? "" : v.join(", "));
')

echo "== Licences des dépendances du moteur Python (à l'exécution)"
python/.venv/bin/python - <<'EOF'
import importlib.metadata as md
import re
import tomllib

todo = [re.split(r"[<>=!~;\[ ]", d)[0] for d in tomllib.load(open("python/pyproject.toml", "rb"))["project"]["dependencies"]]
seen: dict[str, str] = {}
while todo:
    name = todo.pop()
    key = name.lower().replace("_", "-")
    if key in seen:
        continue
    try:
        dist = md.distribution(name)
    except md.PackageNotFoundError:
        seen[key] = "absent (dépendance conditionnelle)"
        continue
    lic = dist.metadata.get("License-Expression") or dist.metadata.get("License") or ""
    if not lic or len(lic) > 60:
        lic = "; ".join(c.split("::")[-1].strip() for c in dist.metadata.get_all("Classifier") or []
                        if c.startswith("License ::")) or "?"
    seen[key] = f"{dist.version}  {lic}"
    todo += [re.split(r"[<>=!~;\[ (]", r)[0] for r in dist.requires or [] if "extra ==" not in r]
for key, value in sorted(seen.items()):
    print(f"  {key}=={value}")
EOF

exit $status
