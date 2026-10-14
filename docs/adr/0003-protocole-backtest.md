# ADR-0003 — Protocole : cible « nouveau besoin », listes opérationnelles, embargo

- Statut : accepté — 2026-10-04 — couloir évaluation

## Décision
- Cible principale `nouveau_besoin_8s` (offre dans les 8 semaines sans offre dans les 8 semaines
  précédentes) ; cibles A et C rapportées aussi (`docs/backtest/cibles.md`).
- Réentraînement toutes les 4 semaines sur des exemples dont la cible est connue avant T (embargo d'un horizon).
- Hyperparamètres de M1 choisis sur une période de validation **antérieure** à l'évaluation.
- Listes **opérationnelles** : 10 entreprises par agence et par semaine, pas de reproposition pendant
  6 semaines, pour que toutes les méthodes aient le même nombre d'appels distincts.
- IC par bootstrap par blocs de semaines ; écarts appariés contre la meilleure méthode naïve.

## Pourquoi
Une première version sans délai de relance favorisait les listes qui changent beaucoup (le hasard « détectait »
plus de besoins). La cible A récompense les entreprises qui publient en continu, que le consultant voit déjà.

## Conséquences
La cible B est la plus difficile : c'est elle qui sert de chiffre principal, pour ne pas surestimer le gain.
