# ADR-0005 — M1 : LightGBM binaire, explications SHAP natives

- Statut : accepté — 2026-10-04 — couloir modèles

## Décision
LightGBM (objectif binaire, probabilité de la cible à 8 semaines), plutôt que `HistGradientBoosting` de
scikit-learn, parce que LightGBM fournit nativement les contributions SHAP (`pred_contrib`) : chaque
proposition affiche ses raisons regroupées par famille de signaux. Pas de learning-to-rank : avec peu de
listes, la propension calibrée est plus simple et la calibration est mesurable.
Trois réglages candidats (souple, régularisé, très régularisé) choisis sur une période de validation
antérieure à l'évaluation.

## Résultat mesuré (monde FICTIF)
Gain **faible mais significatif** sur la meilleure méthode naïve pour la cible principale ; gain nettement plus
grand sur les cibles « toute offre » et « offre dans le bâtiment » ; bien calibré (Brier inférieur à celui du
taux de base). Monde nul : aucun gain significatif. Chiffres exacts : CLAIMS.md.

## Conséquences
Modèle de classement par défaut. À réévaluer sur données réelles ; si le gain disparaît, on garde la méthode
naïve + les explications M0.
