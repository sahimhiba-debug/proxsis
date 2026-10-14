# ADR-0014 — Versions exactes, un verrou par langage, aucune mise à jour automatique

- Statut : accepté
- Date : 2026-10-07
- Couloir : plateforme

## Contexte
La démonstration doit fonctionner à l'identique dans deux jours comme dans trois semaines. Avant cette décision, le
web déclarait seize dépendances par plage (`^`), la version de Node n'était fixée nulle part (CI en Node 22, poste en
Node 26), et le moteur Python s'installait par plages (`>=`) : la CI n'avait pas les mêmes paquets que le poste, et
mypy strict y a échoué (`365bf72`, paquets de types non déclarés).

## Décision
- **Web** : chaque dépendance à la version exacte du verrou (`package-lock.json`), `save-exact` pour les ajouts,
  `npm ci` partout ; **Node 22** déclaré dans `engines` (Vercel suit ce champ) et `apps/web/.nvmrc` (lu par la CI).
- **Python** : un seul verrou, `uv.lock`, résolu sous contrainte des versions exactes de l'environnement qui a passé
  tous les contrôles (`[tool.uv] constraint-dependencies`), **Python 3.12.13** (`.python-version`), installé tel quel
  (`uv sync --frozen`) par la CI, la tâche du lundi et `make install` ; uv épinglé dans la CI.
- Aucune mise à jour automatique (ni Dependabot, ni Renovate) : une version change par un commit, avec tous les
  contrôles.

## Alternatives considérées
`requirements.txt` à côté de `pyproject.toml` (deux sources de vérité) ; `uv lock` sans contrainte (il aurait pris
les versions les plus récentes, pandas 3 par exemple, jamais testées) ; Node 24 (mise à jour volontaire, à faire avec
ses tests).

## Conséquences
Les failles annoncées après le 07.10.2026 ne sont pas corrigées d'elles-mêmes : `scripts/securite/audit.sh` les
signale, et la mise à jour se fait à la main. ESLint 9 est annoncé en fin de support : à passer en version 10 lors
d'une mise à jour volontaire des outils. Raison de revenir dessus : un projet maintenu au long cours, où des mises à
jour automatiques sous tests seraient préférables.

## Mesures liées
Aucune.
