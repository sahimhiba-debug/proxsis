# ADR-0002 — Backtest sur un monde FICTIF tant que les données réelles sont inaccessibles

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

- Statut : accepté — 2026-10-04 — couloir évaluation

## Contexte
La politique réseau de l'environnement de développement bloque les sources suisses (simap, amtsblattportal,
Zefix, geo.admin, OFS…) et les données internes de Flexsis sont absentes. Le cahier des charges demande
pourtant une preuve mesurée et un backtest reproductible.

## Décision
Construire le banc d'essai complet (panel « vu à la date T », cibles, méthodes naïves, métriques avec IC) et le
faire tourner sur un **monde FICTIF simulé** (`proxsis.synth.world`) aux paramètres écrits à l'avance :
processus latents non observables (cycle, projets privés), signaux publics avec délai de publication,
taille d'entreprise observée avec bruit, offres publiées comme cible.
Contrôles d'honnêteté : **monde nul** (`signal_effect=0`) — aucun modèle ne doit y battre significativement
les méthodes naïves (test automatique) ; analyses de sensibilité ; plusieurs graines.

## Alternatives
Attendre les données (rien à montrer, mécanique non testée) ; données réelles d'un tiers sans licence
(interdit).

## Conséquences
Les chiffres valident la **mécanique**, pas la valeur commerciale ; ils sont marqués FICTIF partout
(`CLAIMS.md`). Le même code tournera sur les données réelles dès l'ouverture du réseau.
Risque connu : l'auteur du générateur a aussi écrit les modèles (biais de conception).
