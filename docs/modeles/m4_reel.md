# M4 sur les lauréats simap réels : variantes de noms et paires douteuses (tâche 8)

Données **RÉELLES** (simap.ch, API). *Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi.*

Commande : `proxsis m4-reel` → `docs/modeles/m4_reel_v1.json` et `docs/modeles/m4_paires_douteuses_v1.csv`. Mesuré le 2026-10-06. Module : `proxsis.real_entities` (testé).

## Mesures

| Mesure | Valeur |
|---|---|
| Lignes de lauréats lues (hors lauréats masqués) | 2 527 |
| Noms distincts après normalisation (forme juridique, casse, accents, ponctuation) | 903 |
| Noms normalisés regroupant au moins deux graphies | 8 |
| Lauréats avec numéro IDE publié par simap | **0** |
| Paires douteuses (similarité 80 à 93, zone « à revoir » de M4) | 50 (scores 81,2 à 92,3) |

## Ce qu'on en conclut

- simap ne publie **aucun IDE** de lauréat : le rapprochement d'entreprises repose sur les noms. La normalisation exacte fusionne les variantes évidentes (8 cas).
- Les 50 paires de la zone grise mêlent trois situations qu'un score de similarité ne sépare pas :
  1. **succursales d'une même société** (« …, succursale de Lancy » et « …, succursale de Martigny ») : même employeur au niveau du groupe, mais une agence valaisanne appelle la succursale valaisanne ;
  2. **sociétés sœurs régionales** (« … (GE) SA », « … (JU) SA ») : entités juridiques distinctes, à garder séparées ;
  3. **faux positifs** (« JPF Construction SA » et « PMB Construction SA » : noms proches, sigles différents) : à ne jamais fusionner.
- Décision appliquée en attendant la revue : **aucune fusion automatique dans la zone grise** ; la liste d'appels traite chaque nom normalisé comme une entreprise.

## À faire par Hiba

Remplir la colonne `decision_hiba` du CSV : `meme` (même entité juridique), `groupe` (même groupe, entités distinctes), `differente`. Les décisions serviront de jeu de test réel pour M4 (précision et rappel de la fusion). Le rapprochement par IDE (Zefix ou registre IDE de l'OFS) reste la vraie solution ; voir `docs/demandes/ofj_zefix.md`.
