# M6 sur de vraies séries publiques — rapport (RÉEL, 2026-10-05)

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

Commande : `proxsis m6-reel` → `docs/modeles/m6_reel_v1.json` ; séries dans
`data/reel/series/` (sources et licences dans le JSON).

## Ce qui est mesuré

- **Cibles réelles** : l'indice **KOF Job Tracker** (offres d'emploi en ligne,
  Suisse, hebdomadaire depuis 2018) et les **places vacantes de l'OFS** par
  grande région (trimestriel depuis 2003).
- **Signaux** : le passé de la série, le calendrier, la **météo** retardée
  (MétéoSuisse OGD : Sion, Genève, Berne, Zurich) et les **volumes
  d'adjudications simap** (seulement depuis fin 2024).
- **Méthodes** : naïve saisonnière, dernière valeur, moyenne des 4 dernières
  périodes, puis **boosting d'arbres** (LightGBM, un modèle par horizon).
  **Pas d'apprentissage profond** : quelques centaines de points ne le
  justifient pas.
- **Backtest** : origines glissantes, horizons 1–8 semaines (1–4 trimestres),
  sans fuite (test `test_no_leakage_future_values_do_not_change_a_forecast`) ;
  erreur WAPE ; intervalle de confiance à 95 % de l'écart boosting − meilleure
  naïve par bootstrap par blocs d'origines.

## Résultats

| Série | Période évaluée | Origines | Saisonnière | Dernière valeur | Moyenne 4 | Boosting | Boosting − meilleure naïve (IC 95 %) |
|---|---|---|---|---|---|---|---|
| KOF Job Tracker (hebdo, Suisse), sans signal | 2022-01-03 → 2026-09-28 | 60 | 11,11 % | 1,59 % | 2,00 % | 1,85 % | +0,22 pt (-0,17 à +0,69) |
| KOF, avec météo (4 stations, retardée) | 2022-01-03 → 2026-09-28 | 60 | 11,11 % | 1,59 % | 2,00 % | 1,82 % | +0,20 pt (-0,14 à +0,63) |
| KOF, fenêtre simap, sans simap | 2025-06-02 → 2026-09-28 | 32 | 8,93 % | 1,55 % | 1,87 % | 1,23 % | -0,31 pt (-0,69 à +0,18) |
| KOF, fenêtre simap, avec volumes simap | 2025-06-02 → 2026-09-28 | 32 | 8,93 % | 1,55 % | 1,87 % | 1,25 % | -0,30 pt (-0,68 à +0,18) |
| Places vacantes OFS (trimestriel), Suisse | 2015Q1 → 2026Q2 | 43 | 15,69 % | 10,67 % | 14,66 % | 10,67 % | +0,01 pt (-2,62 à +1,77) |
| Places vacantes OFS (trimestriel), Région lémanique | 2015Q1 → 2026Q2 | 43 | 16,60 % | 11,81 % | 14,96 % | 12,72 % | +0,76 pt (-1,42 à +3,03) |
| Places vacantes OFS (trimestriel), Espace Mittelland | 2015Q1 → 2026Q2 | 43 | 17,58 % | 12,26 % | 16,84 % | 12,92 % | +0,95 pt (-1,99 à +3,58) |

## Lecture honnête (échecs compris)

1. **La dernière valeur est imbattable à court terme** sur ces séries très
   lisses : le boosting ne fait pas mieux, ni sur KOF ni sur les places
   vacantes (écarts non significatifs, parfois légèrement défavorables).
2. **La météo n'apporte rien** à la prévision nationale.
3. **Les volumes simap n'apportent rien** sur la courte fenêtre disponible
   (juin 2025 → septembre 2026) : trop peu d'historique, et un signal
   construction rapporté à une demande d'emploi tous secteurs.
4. La naïve saisonnière est mauvaise sur KOF : le niveau de l'indice change
   d'une année à l'autre ; elle ne doit pas servir de référence seule.

**Conséquence pour le produit** : M6 ne sert pas à prévoir « mieux que la
dernière valeur » ; il peut afficher la tendance régionale (dernière valeur
et sa variation) comme contexte. La valeur de Proxsis est au niveau des
entreprises (cible « pic » du backtest T0), pas de l'agrégat national.
**À refaire** avec des séries régionales par métier (offres Job-Room par
canton et par métier, si le SECO donne accès) et avec l'historique des
commandes de Flexsis.
