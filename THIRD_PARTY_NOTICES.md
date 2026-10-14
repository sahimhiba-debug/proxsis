# Contenus de tiers et attributions

Proxsis est publié sous « tous droits réservés » (voir le [README](README.md#licence-et-attributions)). Les contenus
ci-dessous appartiennent à des tiers : ils gardent leur licence, leurs conditions et leur mention. Le détail des
sources et de leurs règles de lecture est dans [docs/DONNEES.md](docs/DONNEES.md).

## Données publiques

| Source | Ce que le dépôt en contient | Conditions et mention |
|---|---|---|
| **simap.ch** (marchés publics) | champs dérivés des adjudications (entreprise lauréate, adjudicateur, date, titre, montant publié), lus par l'API officielle seulement | conditions générales de l'API, version du 30.09.2023, lues le 05.10.2026 ([docs/recherche/conditions_2026-10-05.md](docs/recherche/conditions_2026-10-05.md)) : usage commercial et transmission à des tiers autorisés (ch. 4), contenu non modifié et séparé de nos commentaires, mention obligatoire (ch. 5) : « Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi. » |
| **Bulletin officiel du Valais** (demandes d'autorisation de construire) | champs structurés tirés des exports PDF et XML téléchargés par une personne ; noms de particuliers, parcelles et adresses masqués avant tout enregistrement ; aucun texte brut | consultation humaine uniquement, aucun accès automatisé au portail ; chaque élément renvoie à la publication officielle ([docs/DONNEES.md](docs/DONNEES.md)) |
| **swisstopo** (données ouvertes) | localités et codes postaux du Valais ; contours des communes (swissBOUNDARIES3D, édition 2026-01), simplifiés | attribution « © swisstopo » |
| **geo.admin.ch** | géocodage | API publique, débit limité (≤ 20 requêtes par minute) |

## Polices

| Police | Fichiers | Licence |
|---|---|---|
| Sora, © 2019 The Sora Project Authors | `apps/web/public/fonts/sora-*.woff2` | SIL Open Font License 1.1 ([texte](apps/web/public/fonts/OFL-Sora.txt)) |
| Urbanist, © 2021 The Urbanist Project Authors | `apps/web/public/fonts/urbanist-*.woff2` | SIL Open Font License 1.1 ([texte](apps/web/public/fonts/OFL-Urbanist.txt)) |

## Code

| Composant | Où | Licence |
|---|---|---|
| Magic UI, maquette « iphone » (adaptée) | `apps/web/src/presentation/phone/` | MIT ; provenance, modifications et texte de la licence : [NOTICE.md](apps/web/src/presentation/phone/NOTICE.md) |
| Dépendances npm et Python | `apps/web/package-lock.json`, `python/uv.lock` | chacune sous sa licence ; `scripts/securite/audit.sh` les liste |

## Images et sons générés

La mascotte Iris (images et sons de `docs/identite/mascotte/` et de `apps/web/public/iris/`) a été générée avec
Runway, puis retouchée en code (`scripts/mascotte/`) ; les identifiants des tâches sont dans
[MASCOTTE.md](docs/identite/mascotte/MASCOTTE.md). Les deux présentations vidéo liées en tête du README (anglais,
français) sont hébergées par GitHub, hors des fichiers du dépôt : voix de synthèse ElevenLabs ; musique, images et
mascotte générées avec Runway.

## Marques

Flexsis, Interiman Group et simap sont des marques de leurs titulaires. Proxsis n'est ni affilié à Flexsis ni approuvé
par Flexsis. Aucun logo ni aucune photo de Flexsis n'est utilisé.
