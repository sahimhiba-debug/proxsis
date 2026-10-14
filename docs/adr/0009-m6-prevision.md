# ADR-0009 — M6 : prévision par métier et région ; pas de deep learning

- Statut : accepté — 2026-10-05 — couloir modèles

## Décision
Méthodes naïves (saisonnière, moyenne des 4 dernières semaines), puis LightGBM global (modèles directs par
horizon, décalages ≥ horizon). **Pas de modèle profond** (N-BEATS, TFT, PatchTST…) : 8 séries
hebdomadaires d'environ 4 ans ne justifient pas leur coût, et l'état de l'art (leçons M4/M5) ne les favorise
pas dans ce régime. Ils ne seraient gardés que s'ils battaient LightGBM sur la même évaluation à origine
glissante.

## Résultat mesuré (monde FICTIF)
LightGBM bat les deux méthodes naïves (WAPE et MASE plus bas) ; chiffres : CLAIMS.md.

## Conséquences
Prévision affichée au niveau agence/groupe. Les modèles de fondation (TimesFM, Chronos) en « zéro
entraînement » sont la prochaine comparaison bon marché quand les données réelles seront là.
