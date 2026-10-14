# Tests

Six niveaux, tous lancés par la CI à chaque push (`.github/workflows/ci.yml`), sauf les captures au pixel, gardées
pour macOS. Règle du projet : un test rouge d'abord, puis le code qui le fait passer.

| Niveau | Où | Commande | Nombre (14.10.2026) |
|---|---|---|---|
| moteur Python | `python/tests/` | `make py-check` (ruff, mypy strict, pytest sans réseau) | 754 tests |
| application, tests unitaires | `apps/web/src/**/*.test.ts` | `npm test` (vitest) ; `npm run typecheck`, `npm run lint` | 211 tests |
| application, bout en bout | `apps/web/e2e/*.spec.ts` | `npm run e2e:prepare && npx playwright test` | 19 fichiers, trois passes (en ligne, hors ligne, allemand) |
| captures de référence | `apps/web/e2e/visuel/` | `npm run build:static && npm run visuel:temps` | 68 captures (17 écrans × 2 langues × 2 tailles) × J, J+2, J+30, J+90 |
| trois moteurs, trois tailles | `apps/web/e2e/moteurs/` | `npm run build:static && npm run moteurs` (`MOTEURS=chrome` si WebKit et Firefox ne sont pas installés) | premier écran, visite entière, application ; Chrome, Safari (WebKit), Firefox × téléphone, tablette, ordinateur |
| base des retours d'appel | `supabase/tests/` | `make db-test` (PostgreSQL jetable) | migrations et droits |
| contrôle de la production | `scripts/production/fraicheur.test.mjs` | `node --test scripts/production/fraicheur.test.mjs` | la règle de fraîcheur de « Chaque matin » |

Les tests qui demandent le réseau réel portent la marque `network` et ne tournent pas par défaut
(`pytest -m network` pour les lancer, à la main).

## Les règles du projet, et le test qui les protège

| Règle | Test |
|---|---|
| Aucune donnée de particulier dans ce que le dépôt publie | `python/tests/test_public_data_sweep.py`, `test_gazette_filter.py`, `test_pii*.py` |
| Mention simap obligatoire partout où il y a des données simap ; mention « Prototype · concept non officiel » sur chaque écran | `e2e/mentions.spec.ts`, `e2e/nom.spec.ts` |
| Aucun appel hors du site pendant la démonstration | `e2e/reseau.spec.ts` (aucune requête enregistrée), passe `hors-ligne` (toute requête externe bloquée) |
| Le portail du Bulletin officiel reste en consultation humaine ; robots.txt et débits respectés | `python/tests/test_http.py`, `test_netcheck.py`, `test_connectors.py` |
| Rien ne dépend de l'horloge : même affichage dans deux jours et dans trois semaines | `src/lib/clock.test.ts`, `npm run visuel:temps` |
| Les données lues par les écrans suivent leur schéma, et le schéma le type | `src/lib/schema.test.ts` |
| Chaque texte existe en français et en allemand ; vocabulaire interdit absent | `src/i18n/textes.test.ts`, `src/i18n/nom-et-vocabulaire.test.ts`, `src/presentation/vocabulary.test.ts` |
| Fictif toujours marqué ; besoins estimés jamais présentés comme réels | `src/visite/dossier.test.ts`, `src/lib/schema.test.ts` (`fictif: true` imposé) |
| Accessibilité : aucune violation axe, tous niveaux, toutes pages et étapes, FR et DE, téléphone et ordinateur ; focus jamais caché | `e2e/accessibilite.spec.ts`, `e2e/focus.spec.ts`, `e2e/telephone.spec.ts` |
| Au téléphone, rien ne défile de côté ni ne passe sous la navigation | `e2e/largeur.spec.ts` |
| La visite se fait jusqu'à la conclusion sur Chrome, Safari et Firefox, au téléphone, à la tablette et à l'ordinateur, et au clavier seul ; sans erreur, sans requête hors du site, sans défilement de côté | `e2e/moteurs/parcours.moteurs.ts` (CI : travail `moteurs`) |
| En-têtes de sécurité du site servi | `e2e/securite.spec.ts` |
| Un seul modèle de calcul pour le retour sur investissement | `src/lib/seuil.test.ts`, `e2e/roi.spec.ts` |
| Budget de performance au téléphone | `node scripts/budget.mjs` sur la version de production (Lighthouse, `perf-budget.json`) |

## Ajouter un test

- **Moteur** : un fichier `python/tests/test_<module>.py`, des données synthétiques (jamais de texte réel collecté à la
  main) ; le nom du test dit le comportement attendu.
- **Application** : à côté du fichier testé (`x.test.ts`) pour une règle de calcul ou de texte ; dans `e2e/` pour un
  parcours, en vérifiant le français et l'allemand.
- **Revue à l'œil** : `node scripts/captures/captures.mjs` prend les captures de la visite et de l'application à
  toutes les tailles, en Chrome et en WebKit, sur la version statique (sortie dans `captures/`, hors Git).
- **Écran modifié volontairement** : régénérer les captures concernées (`npm run visuel -- --update-snapshots`), les
  regarder, puis les commiter avec le changement ; les autres doivent rester identiques au pixel près.
