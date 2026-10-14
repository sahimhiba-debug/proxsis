# Vérité terrain : listes d'appels validées par les consultants

Données **RÉELLES** : entreprises et marchés publics de simap.ch. Aucune donnée de Flexsis ni de particulier.

## Fichiers d'une liste (exemple : semaine du 2026-10-05, Bâtiment)

| Fichier | Rôle |
|---|---|
| `liste_2026-10-05_batiment.json` | liste **gelée** (identifiant `liste_id`) : 10 entreprises + 3 surprises, raisons, sources, besoins, confiance, hypothèses |
| `liste_2026-10-05_batiment_fr.pdf` / `_de.pdf` | feuille d'une page à imprimer, en français ou en allemand |
| `liste_2026-10-05_batiment_fr.html` / `_de.html` | même feuille, liens cliquables |
| `reponses_2026-10-05_batiment.csv` | gabarit des réponses, une ligne par entreprise |

Produit par `proxsis dix-entreprises --date 2026-10-05` (depuis `python/`).

## Faire valider à Martigny ou à Sion

1. Imprimer la feuille, une par consultant.
2. Chaque consultant écrit un **code** (C1, C2… ou ses initiales en majuscules), jamais son nom.
3. Il coche, pour chaque entreprise, ce qu'il sait :
   - **Connue** : client ou contact déjà connu de l'agence ;
   - **Recrute en effet** : il sait que l'entreprise recrute ou cherche du personnel ;
   - **Pas pertinente** : elle n'a rien à faire sur une liste d'appels Bâtiment.

   Aucune case cochée veut dire « je ne sais pas ».

## Saisir et intégrer les réponses

1. Copier le gabarit CSV, une copie par consultant (ou plusieurs consultants dans un seul fichier).
2. Remplir `consultant`, `agence`, et les trois colonnes avec `1` (coché) ou `0`.
3. Lancer, depuis `python/` :

   ```bash
   .venv/bin/python -m proxsis.cli integrer-validation --liste ../data/terrain/liste_2026-10-05_batiment.json --reponses ../data/terrain/reponses_C1.csv ../data/terrain/reponses_C2.csv
   ```

4. Le résultat s'écrit dans `validation_<liste_id>.json`. Il donne :
   - la part de la liste qui **recrute en effet** (majorité stricte des consultants) ;
   - la part déjà **connue** de l'agence ;
   - la part **pas pertinente** ;
   - l'**accord** entre consultants.

   C'est la première mesure de la liste sur le terrain (CLAIMS, type `RÉEL-TERRAIN`).
