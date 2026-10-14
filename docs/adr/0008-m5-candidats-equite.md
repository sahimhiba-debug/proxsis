# ADR-0008 — M5 : suggestions de candidats et audit d'équité

- Statut : accepté — 2026-10-04 — couloir modèles / évaluation

## Décision
Critères stricts (métier ou métier proche, certification légale, disponibilité sous 14 jours, rayon de
déplacement ; 25 km sans permis de conduire), puis score souple (proximité de compétences, expérience,
distance, disponibilité). Raisons affichées en FR et DE ; le consultant choisit.
Les attributs protégés ne sont **jamais lus** par l'appariement (colonnes retirées à l'entrée, test). La langue
de travail est affichée mais n'entre pas dans le score (risque de proxy de nationalité).
Audit avant chaque version : taux de sélection par groupe, ratio min/max (règle des 4/5 comme signal
d'alerte), invariance contrefactuelle, mesure des proxys.

## Résultat mesuré (candidats FICTIFS)
Aucun ratio sous 0,8 ; invariance contrefactuelle vérifiée ; **l'expérience est un proxy de l'âge** et le
ratio par classe d'âge est proche du seuil (les 18–29 ans sont moins souvent proposés). Chiffres : CLAIMS.md.

## Conséquences
Le poids de l'expérience est un choix à discuter avec Flexsis (et le juriste) ; l'audit doit être relancé sur
les données réelles avant tout pilote, avec AIPD.
