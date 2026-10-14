# Guide d'import des données internes de Flexsis et d'Interiman

Statut : **format proposé, en attente des données réelles.** Toutes les données internes de ce
dépôt sont FICTIVES. Le format détaillé des colonnes (types, obligatoire, exemples fictifs) est
dans `docs/recherche/donnees.md` § 6 ; ce guide décrit la procédure.

## 1. Les cinq fichiers attendus

| Fichier | Contenu | Usage dans Proxsis |
|---|---|---|
| `clients.csv` | entreprises clientes et prospects (raison sociale, IDE, secteur, commune OFS, agence, statut, opposition au démarchage) | rattachement aux signaux publics (M4), territoire des agences, exclusion des entreprises qui refusent le démarchage |
| `contacts_entreprise.csv` | **fonction** du contact, service, langue, canal ; numéro de standard ou adresse générique | préparer l'appel ; aucun nom de personne |
| `commandes_missions.csv` | demandes et missions (date, métier ISCO, nombre de postes, type de contrat, statut, origine) | **vraie vérité terrain** : délai signal → commande, taille des besoins, calibration de M0–M2 |
| `candidats.csv` | profils **pseudonymisés et minimisés** (métiers, certifications, NPA, rayon, langues, disponibilité) | suggestions M5 ; jamais envoyés à un LLM |
| `resultats_appel.csv` | issue des appels déclenchés par le radar | étiquettes de retour, mesure du pilote |

## 2. Règles de protection des données (nLPD)

- Identifiants de personnes = **pseudonymes stables** générés par Flexsis ; la table de correspondance
  reste chez Flexsis.
- **Ne jamais transmettre** : nom, date de naissance, numéro AVS, nationalité, type de permis de séjour,
  adresse exacte, téléphone privé, photo, santé, notes libres, salaire individuel.
- Les attributs protégés (genre, classe d'âge, groupe de nationalité) ne servent **qu'à l'audit d'équité**,
  dans un fichier séparé à accès restreint, et ne sont jamais lus par les modèles
  (`proxsis.fairness`, test `test_matcher_never_sees_protected_attributes`).
- Transfert chiffré ; stockage en Suisse possible (un hébergeur suisse, à choisir avec Flexsis).

## 3. Procédure

1. **Extraction** par Flexsis depuis ses outils (CSV UTF-8, séparateur virgule, dates ISO 8601).
2. **Contrôle de format** : chaque fichier est validé contre le schéma avant import (colonnes obligatoires,
   types, codes ISCO-08 et OFS, cantons) ; les lignes refusées sont listées avec leur motif.
3. **Rapprochement** des clients avec les entreprises des sources publiques : IDE d'abord, puis nom et
   commune (M4) ; les cas ambigus passent en revue humaine.
4. **Calibration** : le délai entre signal et commande et la taille des besoins par métier remplacent les
   hypothèses du monde fictif ; le backtest est relancé sur les données réelles (`make backtest`).
5. **Phase suivante** : passage du fichier à une API (connecteur vers l'outil de gestion de Flexsis), à décrire avec
   Flexsis (voir la feuille de route, `docs/FEUILLE-DE-ROUTE.md`, étape 2).

## 4. Correspondance avec le schéma normalisé (`proxsis.schema`)

| Fichier interne | Modèle du schéma | Remarques |
|---|---|---|
| `clients` | `Company` | `uid` normalisé, `employees_est` depuis `classe_taille` (milieu de classe) |
| `commandes_missions` | cible du backtest + `NeedEstimate` (calibration) | `origine = appel_sortant_radar` identifie l'effet du radar |
| `candidats` | `Candidate` | le champ `fictif` passe à `false` pour des données réelles : le validateur actuel l'interdit volontairement tant que l'AIPD n'est pas faite |
| `resultats_appel` | `CallOutcome` | codes d'issue à aligner (`besoin_confirme` ↔ `rendez_vous` / `commande`, etc.) |
