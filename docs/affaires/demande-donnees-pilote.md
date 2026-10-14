# Demande de données à Flexsis — étude complémentaire et pilote

- **De** : équipe Proxsis (Hiba Sahim, AI Engineer)
- **À** : Flexsis — direction des opérations, responsable informatique, conseiller·ère à la protection des données
- **Date** : 2026-10-05, mise à jour le 2026-10-06 — **statut : projet à relire par Hiba, À VALIDER PAR UN
  JURISTE avant envoi**
- Documents liés : proposition de pilote d'une page (notes de travail, non publiées), modèle d'accord de
  confidentialité (`docs/affaires/modele_accord_confidentialite.md`, à valider par un juriste), protocole de pilote
  (`docs/affaires/pilote.md`), format des fichiers
  (`docs/guide-import.md`, `docs/recherche/donnees.md` § 6), mesure réelle (`docs/backtest/backtest_reel.md`)

## 1. Pourquoi nous demandons ces données

Proxsis classe chaque semaine les entreprises à appeler à partir de publications publiques (marchés
attribués sur simap.ch, etc.). Aujourd'hui :

- **nos chiffres réels portent sur l'activité publique** : sur 57 lundis passés, 66,8 % des dix premières
  entreprises de la liste Bâtiment en Valais ont remporté un nouveau marché public dans les 8 semaines, contre
  20,7 % au hasard (CLAIMS REEL-SPEC-BAT) ; les autres chiffres, mesurés sur un monde fictif, prouvent seulement
  que le calcul fonctionne (pas de fuite d'information du futur) ; **aucun** ne dit que Proxsis apporte des
  commandes ;
- les données publiques ne permettent de mesurer qu'un **indicateur indirect** (une entreprise gagne
  un nouveau marché public) ; une offre d'emploi publiée exigerait un accord avec le SECO (Job-Room)
  ou un fournisseur privé ;
- **la seule vérité qui compte — « l'entreprise a passé une commande à Flexsis » — n'existe que dans
  vos outils.**

Le pilote **démarre sans attendre** cet historique (brief du 07.10.2026). Avec lui, une **étude complémentaire**, sous
accord de confidentialité, pourra mesurer si les entreprises de la liste du lundi
ont effectivement commandé dans les 8 semaines, mesurer le délai réel entre un marché
attribué et une commande, par métier, et remplacer les hypothèses du monde fictif par vos chiffres.

## 2. Ce que nous demandons (minimum nécessaire)

| Fichier | Période | Contenu | Pourquoi |
|---|---|---|---|
| `commandes_missions.csv` | du **2024-07-01** à aujourd'hui (simap n'a pas d'historique avant) ; idéalement depuis 2023-01-01 | une ligne par demande : identifiant pseudonyme, identifiant client, agence, **date de réception de la demande**, date de début, métier (code interne + correspondance ISCO-08 si disponible), nombre de postes, temporaire ou fixe, statut (pourvue, annulée…), origine si connue | **cible de l'étude complémentaire** (« commande dans les 8 semaines »), délai entre le marché publié et la commande, taille des besoins |
| `clients.csv` | clients et prospects actifs sur la période | identifiant client, **IDE (CHE-…)** si connu, raison sociale, NPA ou commune, secteur (NOGA si disponible), agence, opposition au démarchage | rattacher vos clients aux entreprises des publications publiques |
| `resultats_appel.csv` | pendant le pilote seulement | suites des appels de la liste, notées dans le carnet (date fixée, besoin confirmé, prochaine étape acceptée, pas de besoin…), et leur équivalent pour le groupe pratique actuelle | mesure du pilote |

**Nous ne demandons pas** : de données sur les candidats ou collaborateurs temporaires (elles ne
servent pas à l'étude complémentaire ; une demande séparée suivra, après analyse d'impact, pour l'audit
d'équité des suggestions) ; aucun nom de personne, téléphone, e-mail, salaire, date de naissance,
nationalité ni note libre. Les contacts des entreprises, s'ils sont utiles plus tard, seront
transmis par **fonction** seulement.

## 3. Comment les données seront protégées

- **Finalité limitée** : étude complémentaire et pilote Proxsis uniquement ; aucune autre réutilisation.
- **Pseudonymes** générés par Flexsis ; la table de correspondance reste chez vous.
- **Transfert chiffré**, stockage en Suisse, accès nominatif (liste des personnes fournie) ; aucune
  copie sur un poste personnel ; **jamais versé dans le dépôt de code**.
- **Aucune donnée interne envoyée à un modèle de langue** (ni Apertus ni autre).
- **Suppression** à la fin du pilote + 3 mois (sauf accord écrit pour prolonger), avec attestation.
- Cadre contractuel : contrat de sous-traitance (art. 9 LPD) et, pour le pilote, mise à jour du
  registre des activités de traitement ; information des consultants (`docs/recherche/legal.md`).

### Ce que l'appli mesure déjà sans vos données (2026-10-06)

- Liste Bâtiment des entreprises valaisannes : 66,8 % des dix premières gagnent un nouveau marché public dans les
  8 semaines, contre 20,7 % au hasard (CLAIMS `REEL-SPEC-BAT`) — **activité**, pas commande.
- Une feuille « à valider par les consultants » (`data/terrain/`) donnera la première vérité terrain : entreprises
  connues de l'agence, qui recrutent en effet, ou hors sujet.

## 4. Ce que vous recevrez en retour

1. Un **rapport de l'étude complémentaire** : pour chaque semaine passée, la liste qu'aurait proposée la
   règle simple « vue à la date T » (sans information postérieure), comparée à vos commandes réelles ;
   part des 10 premières entreprises par agence qui ont commandé, jours d'avance, comparaison avec des méthodes
   simples (hasard, plus gros clients, activité récente). **Résultat publié tel quel, même nul.**
2. Le **délai médian marché attribué → commande**, par métier et par région.
3. Des éléments pour la décision du pilote (poursuivre, ajuster, arrêter : règle du protocole, § 8), sans le
   retarder : le pilote démarre sans attendre cet historique.

## 5. Questions pour Flexsis

1. Quel outil de gestion (ERP/CRM) contient les commandes, et qui peut faire l'extraction ?
2. Horizon métier : 8 semaines entre un appel et une commande est-il réaliste ? Varie-t-il selon le
   métier ?
3. Quelles deux agences pour le pilote (le protocole propose deux agences du Valais romand) ?
4. Les demandes non pourvues ou annulées sont-elles enregistrées ? (elles comptent comme besoin réel)
5. Une personne de contact pour les questions de format pendant l'import ?

## 6. Calendrier proposé

| Étape | Délai |
|---|---|
| Accord de principe et contrat de sous-traitance | S0 |
| Extraction et transfert chiffré des deux fichiers | S0 + 2 semaines |
| Contrôle de format, rapprochement IDE / nom (revue humaine des cas ambigus) | + 1 semaine |
| Rapport de l'étude complémentaire | + 1 semaine |
| Décision sur le pilote | réunion de restitution |
