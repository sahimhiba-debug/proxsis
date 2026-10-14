# ADR-0011 — Mise à jour quotidienne par GitHub Actions, rejeu hors ligne par le cache

- Statut : accepté — 2026-10-05 — couloir plateforme

## Décision
Workflow planifié (jours ouvrables, 05:17 UTC) qui exécute `proxsis update` : simap et amtsblattportal
(liste blanche de rubriques), filtre de données personnelles, rapprochement, validation par le schéma. Le
cache HTTP et les tables sont conservés en artefact ; ils permettent de rejouer la démo sans réseau
(`--offline`). En production, les tables vont dans Supabase (stockage en Suisse possible).

## Conséquences
Le réseau de GitHub Actions doit atteindre les sources (à vérifier au premier passage) ; chaque échec de
source est journalisé sans interrompre les autres ; les identifiants (Zefix) sont des secrets du dépôt.
