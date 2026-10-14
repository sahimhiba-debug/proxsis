# ADR-0006 — M2 : modèle de survie (Cox) pour le « quand »

- Statut : accepté pour la fenêtre de besoin, **non retenu pour le classement** — 2026-10-05 — couloir modèles

## Décision
Cox à risques proportionnels (lifelines), censure administrative à la date d'entraînement (les exemples
récents sont utilisables), sous-échantillon de 40 000 lignes, pénalisation 0,1.
Sortie : P(besoin dans 8 semaines) et semaine la plus probable du premier besoin.

## Résultat mesuré (monde FICTIF)
Sur la cible principale, M2 ne bat **pas** significativement la meilleure méthode naïve et fait moins bien que
M1 ; calibration correcte. Il n'est donc pas gardé pour classer (règle « simple d'abord »).

## Conséquences
M2 sert uniquement à afficher la **fenêtre de besoin** probable dans la fiche entreprise, avec la mention
« estimation ». Une survie à temps discret (logistique, puis LightGBM) est la prochaine étape si le « quand »
doit être mesuré plus finement (`docs/recherche/etat-de-l-art.md` § 3).
