# ADR-0004 — M0 : règles explicables par familles de signaux

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

- Statut : accepté — 2026-10-04 — couloir modèles

## Décision
Quatre familles (Projet, Entreprise, Recrutement, Région) ; niveau ROUGE ≥ 3 familles, ORANGE = 2, JAUNE = 1 ;
liquidation connue = exclusion. Fenêtres et seuils fixés par raisonnement métier, **sans réglage sur le
backtest**. Principe retenu : « compter les familles, pas les signaux ».

## Résultat mesuré (monde FICTIF, voir CLAIMS.md)
M0 fait **moins bien** que la méthode naïve « plus grosses entreprises » sur la cible principale, mais ses
niveaux d'alerte sont ordonnés (taux de réalisation rouge > orange > jaune > aucun). Dans le monde nul, l'ordre
disparaît, comme attendu.

## Conséquences
M0 reste dans le produit pour **expliquer** (raisons lisibles) ; le classement affiché vient du meilleur modèle
mesuré. Les fenêtres devront être recalibrées sur les commandes réelles de Flexsis.
