# Phasage réel appris sur les lots simap (livrable 2.3)

Données **RÉELLES** : adjudications de travaux simap (Suisse romande et adjudicateurs valaisans, juillet 2024 à
septembre 2026). *Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi.*

Commandes : `proxsis phasage-reel` → `docs/modeles/phasage_reel_v1.json` (bootstrap 2 000 tirages, graine 0) ;
ce document : `proxsis docs-semaine1`. Module : `proxsis.phasing` (testé).

## Ce qui est mesuré

1. **Chantiers** : lots d'un même bâtiment regroupés (même adjudicateur et même lieu, titres proches : au moins deux
   mots communs, Jaccard ≥ 0,5, moins de trois ans d'écart). **542 chantiers**, dont
   **213 avec au moins deux lots** ; **145 ont un lot de gros
   œuvre (CFC 21)**, qui sert d'ancre.
2. Pour chaque phase, le **délai entre l'adjudication du gros œuvre et celle de la phase**, avec l'IC 95 % de la
   médiane (bootstrap) et l'étendue p10–p90.
3. Le **montant de la phase rapporté au montant du gros œuvre** (médiane).

| Phase (CFC) | Chantiers | Présence | Délai médian (jours) | IC 95 % de la médiane | p10 à p90 (jours) | Montant / gros œuvre |
|---|---|---|---|---|---|---|
| Travaux préparatoires (CFC 1) | 44 | 30 % | 0 | 0 à 0 | −113 à 16 | 0,78 |
| Terrassement (CFC 20) | 10 | 7 % | 0 | −36 à 20 | −80 à 55 | 1,12 |
| Enveloppe (CFC 22) | 79 | 54 % | 14 | 0 à 34 | −17 à 156 | 0,56 |
| Électricité (CFC 23) | 57 | 39 % | 0 | 0 à 9 | −3 à 174 | 0,72 |
| Chauffage, ventilation, climatisation (CFC 24) | 58 | 40 % | 0 | 0 à 0 | −74 à 77 | 0,33 |
| Sanitaire (CFC 25) | 47 | 32 % | 0 | 0 à 0 | −26 à 77 | 0,37 |
| Installations de transport (CFC 26) | 16 | 11 % | 10 | 0 à 49 | 0 à 176 | 0,11 |
| Aménagements intérieurs 1 (CFC 27) | 37 | 26 % | 74 | 28 à 112 | −114 à 327 | 0,33 |
| Aménagements intérieurs 2 (CFC 28) | 30 | 21 % | 71 | 15 à 160 | −59 à 317 | 0,18 |
| Équipements d'exploitation (CFC 3) | 10 | 7 % | 93 | 0 à 355 | −10 à 388 | 0,26 |
| Aménagements extérieurs (CFC 4) | 10 | 7 % | 4 | −12 à 396 | −31 à 488 | 0,27 |

Un délai négatif : la phase est adjugée **avant** le gros œuvre. « Présence » : part des chantiers avec gros œuvre
où la phase est adjugée séparément sur simap.

## Confrontation avec les références publiques du métier

- **SIA 112:2014** (sommaire gratuit ; `docs/recherche/conformite_cct_annonce.md` § e) : l'adjudication clôt la
  phase partielle **41** ; le besoin de main-d'œuvre arrive en **52** « Exécution de l'ouvrage ». La norme donne
  l'ordre des phases, pas leurs durées.
- **Données** : électricité, CVC et sanitaire sont adjugés en général **le même jour que le gros œuvre** (une vague
  41) ; les aménagements intérieurs et les finitions forment une **seconde vague**, deux à trois mois plus tard.
- **CFC (SN 506 500:2017, CRB)** : l'ordre des groupes 20 à 28 suit l'ordre d'exécution ; libellés livrés par simap ;
  norme détaillée payante, non lue.
- **Conséquence** : la date d'adjudication **ne révèle pas le calendrier des travaux** des installations. Le
  calendrier du besoin repose sur des **hypothèses déclarées** (début quatre semaines après l'adjudication, durées
  par phase, taille d'équipe plafonnée), à calibrer avec l'historique de Flexsis.

## Validation sur des chantiers plus récents

Apprentissage sur les chantiers dont le gros œuvre est adjugé avant la coupure, test sur les suivants. Référence :
un seul délai (médiane de toutes les phases).

| Coupure | Chantiers d'apprentissage | Chantiers de test | Lots de test | Couverture p10–p90 (attendu ≈ 80 %) | Erreur absolue moyenne du délai médian par phase | Erreur absolue moyenne d'un délai unique |
|---|---|---|---|---|---|---|
| 2025-10-01 | 85 | 60 | 160 | 85 % | 54 j | 44 j |
| 2026-01-01 | 96 | 49 | 138 | 83 % | 57 j | 43 j |

**Résultat honnête** : intervalles p10–p90 **bien calibrés** (83 à 85 % de couverture) ;
le délai **par phase ne bat pas un délai unique**. Le produit affiche donc des **fenêtres** (« lots attendus entre telle et telle date »), jamais une date
ponctuelle par phase : la médiane reste dans les données pour l'analyse, l'appli ne l'affiche pas.

## Ce que le phasage apporte au produit, et ce qu'il n'apporte pas

- **Apporte** : les lots encore attendus sur un chantier (fenêtre p10–p90) ; l'estimation d'un montant non publié par
  le rapport mesuré au gros œuvre du même chantier ; l'ordre des vagues d'adjudication.
- **N'apporte pas** : les durées de travaux, la part de main-d'œuvre, le coût hebdomadaire, la part confiée à des
  temporaires — hypothèses listées dans `PhasingModel.assumptions` et dans chaque liste d'appels.
