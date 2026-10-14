# Audit de sécurité des dépendances, des secrets et des licences

Mesuré le 14.10.2026 sur la branche `design/nouvelle-version` (d'abord le 07.10.2026). Pour refaire tout l'audit, depuis la racine du dépôt
(lecture seule, environ 10 secondes ; réseau : registre npm et index PyPI seulement) :

```bash
scripts/securite/audit.sh
```

Le script échoue si une dépendance livrée a une faille connue ou si un secret apparaît dans un fichier suivi ou dans
l'historique ; il n'affiche jamais un secret, seulement le fichier ou le commit.

## Résultats

| Contrôle | Résultat |
|---|---|
| `npm audit --omit=dev` : ce que le site livre | **0 faille** |
| `npm audit` : outils de développement compris | 1 faille à la racine, `braces` 3.0.3 ([GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm), élevée : épuisement de la pile sur des motifs très imbriqués), qui atteint `micromatch`, `fast-glob`, `knip`, `eslint-config-next` et `@next/eslint-plugin-next` |
| `pip-audit` 2.10.1 sur l'environnement du moteur Python | **0 faille** |
| Secrets (clés d'API, jetons GitHub, Slack, AWS, clés privées, jetons JWT, clés Public AI ou Supabase renseignées) | **aucun**, ni dans les 1 536 fichiers suivis ni dans les 596 commits de l'historique |
| En-têtes de sécurité du site servi | testés par `apps/web/e2e/securite.spec.ts` (politique de contenu limitée au site, `nosniff`, `Referrer-Policy`, cadres seulement depuis le site, permissions coupées) |

**Faille `braces` : acceptée, avec sa raison.** Elle ne touche que deux outils lancés sur le poste de développement
ou en CI (`knip`, qui cherche le code mort, et la configuration ESLint de Next). Ils ne lisent que les motifs de
fichiers écrits dans le dépôt, jamais une entrée venue de l'extérieur, et rien de leur code ne part avec le site. La
correction proposée par npm (`npm audit fix --force`) change des versions majeures : elle attendra une mise à jour
volontaire de ces outils, pas une mise à jour automatique.

## Licences

**Application livrée** (`apps/web`, 45 paquets à l'exécution, `npm ls --omit=dev`) : 29 MIT, 9 Apache-2.0, 3 ISC,
1 BSD-3-Clause (`source-map-js`), 1 0BSD (`tslib`), et deux cas à connaître :

- `@img/sharp-libvips-*` (**LGPL-3.0-or-later**) : bibliothèque d'images que Next.js charge en option pour optimiser
  les images. L'application n'utilise pas `next/image` ; la bibliothèque reste un fichier séparé, chargé
  dynamiquement et non modifié, ce que la LGPL permet sans obliger à ouvrir le code de l'application.
- `caniuse-lite` (**CC-BY-4.0**) : tableau des navigateurs lu pendant la construction ; il n'est pas envoyé au
  navigateur. L'attribution est dans le paquet lui-même.

`@playwright/test` apparaît dans la liste parce que Next.js le déclare comme dépendance facultative ; c'est un outil de
test, absent du site servi.

**Polices** (`apps/web/public/fonts`, servies par le site) : Urbanist et Sora, **SIL Open Font
License 1.1** ; chaque famille est accompagnée de sa licence avec sa ligne de copyright (`OFL-*.txt`), comme l'OFL le
demande pour une redistribution.

**Moteur Python** (`python/`, dépendances à l'exécution de `pyproject.toml` et les leurs) : toutes permissives (MIT,
BSD, Apache-2.0, PSF), sauf `certifi` (**MPL-2.0**, copyleft limité à ses propres fichiers, utilisés sans
modification). Le moteur tourne sur le poste de Hiba et en CI ; il n'est pas distribué.

**Données** : les licences et conditions de chaque source (simap, Bulletin officiel, swisstopo) sont dans
`docs/recherche/` et sur chaque ligne de données (`provenance`), pas ici.
