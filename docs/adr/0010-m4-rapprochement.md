# ADR-0010 — M4 : rapprochement des entreprises

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

- Statut : accepté — 2026-10-05 — couloir données / modèles

## Décision
1. IDE exact (clé de contrôle eCH-0097) ; 2. sinon blocage par canton, similarité de noms normalisés
(formes juridiques retirées) pondérée vers la **partie distinctive** du nom (mots génériques du métier
écartés), bonus de commune, malus de forme juridique différente ; 3. lien automatique au-dessus d'un seuil
**et** si le second candidat est assez loin, sinon **revue humaine**.
Méthode de base comparée : nom normalisé identique (l'approche la plus simple).

## Résultat mesuré (monde FICTIF, échantillon tenu à l'écart)
Précision comparable à la méthode exacte et rappel nettement supérieur ; une part des mentions part en revue
humaine. Chiffres : CLAIMS.md. Seuils choisis sur un premier échantillon, mesurés sur un second.

## Conséquences
Splink (Fellegi–Sunter) est la suite logique quand plusieurs champs fiables seront disponibles.
