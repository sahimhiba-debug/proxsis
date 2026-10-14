# Aperçu des adjudications simap collectées (tâche 2)

Données **RÉELLES** (simap.ch, API, CG du 30.09.2023). *Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi.*

Commande : `proxsis apercu-simap` → `docs/recherche/apercu_simap.json` (graine 0). Mesuré le 2026-10-06 sur les deux collectes :
`adjudications_romandie_construction_2024-07_2026-09.jsonl` (cantons romands) et
`adjudications_emetteur_vs_construction_2024-07_2026-09.jsonl` (adjudicateurs valaisans : institution racine « Valais » et ses enfants).

## Volume et période

- **2 508 adjudications de travaux de construction** distinctes (doublons entre les deux collectes retirés), publiées du 2024-07-19 au 2026-09-30.
- Par trimestre : 2024-T3 : 52 ; 2024-T4 : 127 ; 2025-T1 : 241 ; 2025-T2 : 389 ; 2025-T3 : 279 ; 2025-T4 : 271 ; 2026-T1 : 372 ; 2026-T2 : 432 ; 2026-T3 : 345. Le 3e trimestre 2024 est incomplet (début de la collecte au 1er juillet, et la recherche simap ne renvoie que la publication la plus récente de chaque projet, complétée ensuite par `past-publications`).

## Part du Valais (trois critères croisés)

28,4 % de ces 2 508 adjudications (713) n'indiquent pas le canton des travaux ; un seul critère sous-estimerait le Valais.

| Critère | Adjudications |
|---|---|
| Canton des travaux = VS | 474 |
| Adjudicateur valaisan (canton, communes, services) | 1 075 |
| Commune ou localité valaisanne citée (lieu, titre, description ; liste OpenPLZ) | 1 051 |
| **Au moins un critère** | **1 223 (48,8 %)** |

Limite : le critère « lieu cité » peut se tromper sur des homonymes (une localité valaisanne qui porte le nom d'un lieu d'un autre canton) ; il n'est pas vérifié à la main.

## Métiers (par code CFC du lot)

Un lot compte pour chaque métier de la taxonomie associé à sa phase CFC (un lot de gros œuvre compte pour maçon, coffreur, manœuvre et grutier). « sans_code_cfc » : lot sans code CFC (souvent un code NPK ou seulement un code CPV, classés par `proxsis.specialty`) ; « sans_metier_de_la_taxonomie » : phase sans métier de la taxonomie (enveloppe, CVC, ascenseurs).

| Métier | Lots |
|---|---|
| sans_code_cfc | 912 |
| sans_metier_de_la_taxonomie | 513 |
| manoeuvre_construction | 470 |
| macon | 241 |
| coffreur | 241 |
| grutier | 241 |
| machiniste | 229 |
| platrier | 215 |
| electricien | 178 |
| peintre | 128 |
| installateur_sanitaire | 92 |

### Métiers par trimestre

| Métier | 2024-T3 | 2024-T4 | 2025-T1 | 2025-T2 | 2025-T3 | 2025-T4 | 2026-T1 | 2026-T2 | 2026-T3 |
|---|---|---|---|---|---|---|---|---|---|
| sans_code_cfc | 34 | 40 | 90 | 122 | 116 | 83 | 122 | 164 | 141 |
| sans_metier_de_la_taxonomie | 4 | 33 | 52 | 80 | 45 | 62 | 72 | 94 | 71 |
| manoeuvre_construction | 8 | 25 | 41 | 83 | 50 | 51 | 70 | 88 | 54 |
| macon | 4 | 12 | 25 | 41 | 26 | 26 | 37 | 43 | 27 |
| coffreur | 4 | 12 | 25 | 41 | 26 | 26 | 37 | 43 | 27 |
| grutier | 4 | 12 | 25 | 41 | 26 | 26 | 37 | 43 | 27 |
| machiniste | 4 | 13 | 16 | 42 | 24 | 25 | 33 | 45 | 27 |
| platrier | 2 | 11 | 22 | 29 | 28 | 31 | 42 | 25 | 25 |
| electricien | 2 | 11 | 17 | 34 | 19 | 19 | 21 | 30 | 25 |
| peintre | 2 | 3 | 13 | 22 | 13 | 15 | 28 | 12 | 20 |
| installateur_sanitaire | 0 | 4 | 6 | 19 | 8 | 10 | 17 | 19 | 9 |

## Masquage (filtre des données personnelles)

- Lauréats : **9 masqués sur 2 536** (0,35 %). Règle : un lauréat n'est masqué que si son nom ressemble à une personne physique **et** qu'aucun numéro IDE n'est publié (simap ne publie l'IDE d'aucun lauréat dans nos données : 0 observé).
- Adjudicateurs : **0 masqués** (ce sont des autorités publiques ; seul le texte libre passe par le filtre).
- Moins de 20 cas masqués existent : **les 9 sont listés** ci-dessous pour vérification humaine (le nom masqué n'est pas stocké : ouvrir la fiche simap pour juger si le masquage était justifié).

| Date | Titre | Adjudicateur | Lien |
|---|---|---|---|
| 2026-07-11 | Commune d'Arbaz / Réaménagement de la route du village | (non renseigné par simap) | [fiche simap](https://www.simap.ch/fr/project-detail/eb554017-6110-4e2e-9ae9-a2f2feec2112) |
| 2026-04-21 | Renovierung des Daches der Turnhalle der Mittelschule, Brig | (non renseigné par simap) | [fiche simap](https://www.simap.ch/fr/project-detail/697ea3fd-7ad3-4458-bcdf-a9aec0ab8546) |
| 2025-04-08 | Correction et réfection de la chaussée à la sortie de Luc sur la RC no 79 Botyre - Icogne - Lens - Crans | DMTE, Service de la mobilité, arrondissement 2, Valais central | [fiche simap](https://www.simap.ch/fr/project-detail/408ecc99-de76-4fc4-92d1-94a3b3d7ad1a) |
| 2026-07-10 | Commune d'Arbaz / Réaménagement de la route du village | Commune d'Arbaz Service technique | [fiche simap](https://www.simap.ch/fr/project-detail/eb554017-6110-4e2e-9ae9-a2f2feec2112) |
| 2026-03-25 | Restauration du Château de Valère (5ème étape), Sion | Service immobilier et patrimoine | [fiche simap](https://www.simap.ch/fr/project-detail/735c9b35-df54-4419-a729-40d6528e2465) |
| 2025-11-06 | Réfection du Chemin des Marais Neufs | Commune de Saxon - Service Technique | [fiche simap](https://www.simap.ch/fr/project-detail/51cc141d-3708-4289-be12-b3b8975180fd) |
| 2025-10-30 | Correction de la chaussée et construction d'un trottoir à la route de Rougenan à Botyre, PR 0 à 3, sur la commune d'Ayent | Service de la mobilité, arrondissement 2, Valais central | [fiche simap](https://www.simap.ch/fr/project-detail/76a58b63-8cee-41ea-b60e-0ae2e79b2eea) |
| 2025-07-11 | Kollegium Spiritus Sanctus, Gebäude D, Brig | Service immobilier et patrimoine | [fiche simap](https://www.simap.ch/fr/project-detail/f6463527-8a06-488e-bde1-8f8f4dcf5173) |
| 2024-07-19 | Kollegium Spiritus Sanctus, Brig | Service immobilier et patrimoine | [fiche simap](https://www.simap.ch/fr/project-detail/495a6960-42e2-4a43-8b9b-ecd27492a6d0) |

À faire par Hiba : ouvrir chaque fiche et noter « justifié / à tort » ; un masquage à tort fait perdre une entreprise, un oubli ferait apparaître un particulier.
