# PROXSIS — Recherche de données (section 2b)

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

| | |
|---|---|
| Projet | PROXSIS : radar de la demande de main-d'œuvre pour Flexsis (Interiman Group) |
| Secteurs | industrie, construction, horlogerie, logistique, pharma |
| Zone | Suisse romande et alémanique (FR et DE) |
| Date de consultation de toutes les sources | **2026-10-04** |
| Livrables liés | [`data/catalogue.csv`](../../data/catalogue.csv) (68 lignes, 16 colonnes) |

## 1. Résumé

- **Aucune source cible n'a pu être interrogée depuis l'environnement.** Toutes les URL de données testées le 2026-10-04 ont échoué avec `curl: (56) CONNECT tunnel failed, response 403` (code HTTP `000`). La politique réseau de l'environnement bloque ces domaines. Les 3 URL de contrôle (api.github.com, pypi.org, raw.githubusercontent.com) ont répondu HTTP 200. Tout ce qui suit vient donc de documentation publique, et non de tests réels. Chaque fait porte sa source.
- **Catalogue :** 68 lignes. Après l'audit du 2026-10-05 (critère au § 3) : 10 « utilisable », 52 « sous_conditions » (dont 23 reclassées faute de CGU lues) et 6 « non ».
- **Sources les plus solides pour détecter un besoin de main-d'œuvre (selon la documentation) :**
  - simap.ch : API de lecture sans authentification, appels d'offres et adjudications avec entreprise lauréate ;
  - amtsblattportal.ch : FOSC rubrique HR (créations et mutations d'entreprises) et Bulletin officiel du Valais (BA-VS05, BA-VS10…) ;
  - OFS STAT-TAB : réserves de travail, BESTA, STATENT ;
  - RegBL : statuts « projeté / autorisé / en construction » ;
  - jeu OGD désidentifié des Baugesuche du canton de Zurich ;
  - KOF : indicateur de l'emploi ;
  - MétéoSuisse : CC BY 4.0, usage commercial autorisé ;
  - OpenHolidays : jours fériés et vacances scolaires.
- **Points bloquants juridiques :**
  - Plusieurs licences ne sont pas établies : conditions simap.ch, CGU amtsblattportal, extraits RegBL (informations contradictoires), jeux OFS en `terms_by_ask`.
  - Job-Room, jobs.ch/jobup.ch et les autres portails privés exigent un accord écrit.
  - Les rubriques FOSC et cantonales qui concernent des personnes physiques sont exclues : faillites, poursuites, successions, état civil, registre foncier. Les permis de construire déposés par des particuliers sont exclus aussi.
- **Écart par rapport à la consigne :** seulement 15 recherches WebSearch ont pu être faites (au lieu de ≥ 30). Le quota WebSearch de la session (200 appels, partagé) s'est épuisé pendant le travail. J'ai compensé par environ 40 recherches de code GitHub et par la lecture directe de documentation sur raw.githubusercontent.com et pypi.org (voir § 2.2).

## 2. Méthode

### 2.1 Tests réels depuis l'environnement (2026-10-04, entre 20:45 et 21:02 UTC)

Commande utilisée pour chaque URL :

```bash
curl -sS -o /dev/null --max-time 15 -w '%{http_code}|%{time_total}' "<URL>"
```

- **URL testées :** le détail par source du 2026-10-04 figure dans la colonne `test_reel_2026_10_04` du catalogue ; la liste numérotée annoncée n'a pas été conservée (agent interrompu). L'annexe A donne un nouveau test par hôte, daté du 2026-10-05.
  - **103 bloquées.** Message exact : `curl: (56) CONNECT tunnel failed, response 403`, code HTTP `000`. Le proxy d'egress refuse le tunnel avant tout contact avec le serveur cible. Ce n'est donc pas une réponse de l'API.
  - **3 contrôles OK (HTTP 200) :** `https://api.github.com/`, `https://pypi.org/pypi/pystatis/json` et `https://raw.githubusercontent.com/openpotato/openholidaysapi.data/main/README.md`.
- **WebFetch :** `EGRESS_BLOCKED` pour www.simap.ch, www.zefix.admin.ch, amtsblattportal.ch, developer.adzuna.com et api.geo.admin.ch. WebFetch fonctionne pour pypi.org.
- **Chemins non testés volontairement :** plateforme eConstruction VS (règle du projet), application SAD Consult de Genève (application de consultation nominative), Indeed et LinkedIn (exclus par principe).
- **Détail URL par URL :** annexe A.

Formulation retenue dans la colonne `test_reel_2026_10_04` du CSV : « GET <URL> -> curl: (56) CONNECT tunnel failed, response 403 ; code HTTP 000 (aucune réponse du serveur cible) ; bloqué par la politique réseau de l'environnement le 2026-10-04 ».

### 2.2 Recherche documentaire

1. **WebSearch (15 requêtes avant épuisement du quota de session).** Les requêtes portaient sur :
   - simap : API et doc OpenAPI, conditions de réutilisation ;
   - amtsblattportal : documentation API ;
   - Bulletin officiel VS ;
   - rubriques FOSC HR01/HR02/HR03 ;
   - Zefix PublicREST : identifiants ;
   - jeu Zefix sur opendata.swiss ;
   - webservice UID ;
   - codes GSTAT du RegBL ;
   - conditions housing-stat ;
   - conditions et fair use de geo.admin.ch ;
   - PxWeb de l'OFS.

   La 16e requête a renvoyé « this session has used its web search budget (200 of 200) ». Les requêtes suivantes n'ont pas été exécutées (conditions d'utilisation OFS, réserves de travail, BESTA…).
2. **Recherche de code GitHub (outil `search_code`, environ 40 requêtes)** pour trouver des clients et des documentations qui citent les endpoints exacts : KOF datenservice, TED, planning.data.gov.uk, Sitadel/DiDo, GENESIS, OJP, Adzuna, SITG, rubriques du BO Valais, jeux opendata.swiss.
3. **Lecture directe** de fichiers sur raw.githubusercontent.com, pypi.org (API JSON) et registry.npmjs.org :
   - documentation officielle hébergée sur GitHub : MeteoSwiss/opendata, schemaorg/schemaorg, openpotato/openholidaysapi.data, KOF-ch, careerjet, digital-land, MTES-MCT ;
   - clients open source sous licence permissive : portefeuille malkreide (MIT), swiss-procurement-mcp (MIT, copie locale lue), Dyumes/flexsis (MIT) ;

   **Aucun code ni instantané de données n'a été copié** depuis ces dépôts. Seules les URL d'endpoints et les règles d'accès sont reprises, reformulées et attribuées.
4. **Limites de ce que l'API GitHub permet ici :** `api.github.com` refuse les chemins non liés au dépôt de la session (« sessions are bound to their configured repositories »). L'exploration du portefeuille s'est donc faite par raw.githubusercontent.com.

### 2.3 Conventions

- « non vérifié » : l'information vient d'un tiers (client open source, catalogue tiers, extrait de moteur de recherche) et n'a pas pu être confirmée sur la source officielle.
- « inconnu » : aucune information trouvée.
- Les chiffres (volumes, quotas) cités viennent tous d'une source nommée et sont marqués « non vérifié par nous ». Aucun chiffre n'a été estimé.
- Licences : seuls les textes lus sont qualifiés de vérifiés. Exemples : conditions MétéoSuisse lues dans le dépôt officiel MeteoSwiss/opendata ; fichier LICENSE du dépôt OpenHolidays ; champ « Rights » des métadonnées opendata.swiss, tel que reproduit dans l'index tiers [32].

### 2.4 Contrôle qualité effectué sur un jeu accessible

Le fichier `holidays.public.csv` d'OpenHolidays (miroir GitHub) a été téléchargé : 429 jours fériés suisses de 2020 à 2030 [29].

**Anomalie détectée :** le Lundi du Jeûne vaudois 2026 y est daté du **2026-09-20**, qui est un dimanche (le jour du Jeûne fédéral). La bonne date est le **2026-09-21** : le Jeûne fédéral tombe le 3e dimanche de septembre, soit le 2026-09-20, et le lundi suit. Les années 2020 à 2025 et 2027 à 2030 sont correctes.

Conséquence : il faut un contrôle croisé systématique avec la source officielle (CDIP ou cantons) avant d'utiliser ce calendrier.

## 3. Tableau récapitulatif

Généré depuis `data/catalogue.csv` (état après l'audit du 2026-10-05). Critère de verdict : **utilisable** = accès documenté ET licence/CGU lues et compatibles ; **sous_conditions** = accès documenté mais CGU non lues ou non établies, compte/clé à demander, ou accord écrit requis ; **non** = interdit par nos règles ou par les CGU, ou données sur des personnes physiques.

| id | Source | Mode d'accès | Verdict |
|---|---|---|---|
| `simap_appels_offres` | simap.ch - API de lecture : recherche de projets (appels d'offres publ | API REST JSON publique | sous_conditions |
| `simap_adjudications` | simap.ch - adjudications (marchés attribués) et détail des publication | Même API | sous_conditions |
| `simap_referentiels` | simap.ch - référentiels (codes CPV, BKP, NPK, eBKP-H/T, OAG, CPC ; ins | API REST publique sans authentification : /codes/v1/{systeme | sous_conditions |
| `amtsblatt_fosc_hr` | amtsblattportal.ch - FOSC/SHAB rubrique HR registre du commerce (HR01  | API REST publique en lecture sans authentification | sous_conditions |
| `amtsblatt_rubriques_personnes_exclues` | amtsblattportal.ch - rubriques FOSC et cantonales concernant des perso | Ne pas interroger ces rubriques. Codes : KK faillites | non |
| `amtsblatt_fosc_up` | amtsblattportal.ch - FOSC rubrique UP (communications aux associés/act | API REST publique en lecture sans authentification | sous_conditions |
| `amtsblatt_vs_permis_construire` | Bulletin officiel du Valais (via amtsblattportal) - BA-VS05 demandes d | API REST publique en lecture sans authentification | sous_conditions |
| `amtsblatt_vs_grands_projets` | Bulletin officiel du Valais (via amtsblattportal) - BA-VS10 consultati | API REST publique en lecture sans authentification | sous_conditions |
| `amtsblatt_marches_hors_simap` | amtsblattportal.ch - marchés publics absents de simap (AR-VS40 Valais, | API REST publique en lecture sans authentification | sous_conditions |
| `amtsblatt_vs_emplois_publics` | Bulletin officiel du Valais (via amtsblattportal) - AL-VS20 offres d'e | API REST publique en lecture sans authentification | sous_conditions |
| `amtsblatt_permis_autres_cantons` | amtsblattportal.ch - Baugesuche/permis des autres cantons (BP-ZH, BP-B | API REST publique en lecture sans authentification | sous_conditions |
| `amtsblatt_amenagement` | amtsblattportal.ch - aménagement du territoire et avis institutionnels | API REST publique en lecture sans authentification | sous_conditions |
| `zefix_publicrest` | Zefix - API REST publique officielle du registre du commerce (ZefixPub | REST JSON | sous_conditions |
| `zefix_rest_site_web` | Zefix - API REST interne du site web (ZefixREST), utilisée sans compte | REST JSON sans authentification | non |
| `uid_register_ide` | Registre IDE de l'OFS (UID-Register) - webservice public | Webservice SOAP | sous_conditions |
| `regbl_geoadmin_api` | RegBL/GWR via api3.geo.admin.ch - couche ch.bfs.gebaeude_wohnungs_regi | REST JSON sans authentification | utilisable |
| `regbl_madd_dump` | RegBL/GWR - extraits publics cantonaux quotidiens (MADD, SQLite) : pip | Téléchargement ZIP par canton | sous_conditions |
| `ofs_pxweb_api` | OFS STAT-TAB - API PxWeb (générique) | REST : GET = métadonnées de la table, POST = requête JSON | sous_conditions |
| `ofs_construction` | OFS - statistique de la construction et des logements : investissement | PxWeb | sous_conditions |
| `ofs_besta` | OFS - statistique de l'emploi BESTA : places vacantes et emplois par d | PxWeb. Tables citées par le catalogue tiers Dyumes : _101 em | sous_conditions |
| `ofs_statent` | OFS - STATENT (statistique structurelle des entreprises : établissemen | PxWeb | sous_conditions |
| `ofs_hesta` | OFS - HESTA (hébergement touristique : arrivées et nuitées par commune | PxWeb | sous_conditions |
| `ofs_agvch_communes` | OFS - répertoire officiel des communes (AGVCH, service REST snapshot/c | REST sans authentification | sous_conditions |
| `seco_amstat` | SECO - AMSTAT (chômeurs et demandeurs d'emploi par profession, canton, | Application web JavaScript | sous_conditions |
| `seco_opendata_series` | SECO - séries chômage sur opendata.swiss (table T3.3.0.1) et rapport m | CKAN opendata.swiss | sous_conditions |
| `seco_obligation_annonce` | SECO - liste annuelle des genres de professions soumis à l'obligation  | Fichier annuel | sous_conditions |
| `jobroom_api` | Job-Room (SECO) - partie publique et API (API interne de recherche d'a | API interne non documentée | sous_conditions |
| `cantons_marche_travail_ogd` | Portails cantonaux - chômage et places vacantes (Fribourg opendata.fr. | API OpenDataSoft | sous_conditions |
| `swissstaffing_index` | Swiss Staffingindex (swissstaffing) - heures de travail temporaire et  | Communiques de presse | sous_conditions |
| `kof_datenservice` | KOF ETH - Datenservice API publique : baromètre conjoncturel et indica | REST sans authentification : /api/v1/public/collections/{ogd | utilisable |
| `kof_tsdb_job_tracker` | KOF - Time Séries DB API v2 (séries publiques, dont Swiss Job Tracker  | REST | sous_conditions |
| `kof_enquetes_construction` | KOF - enquêtes conjoncturelles (Konjunkturumfragen) construction et in | Séries détaillées par branche apparemment restreintes | sous_conditions |
| `sbv_baukonjunktur` | Société suisse des entrepreneurs (SSE/SBV) - enquête trimestrielle (ch | Pages web et communiqués | sous_conditions |
| `baublatt_docu` | Baublatt / Docu Media (Baublatt-Infodienst, Infomanager) - projets de  | Service commercial payant | sous_conditions |
| `opendata_swiss_ckan` | opendata.swiss - API CKAN (catalogue national des données ouvertes) | CKAN Action API | sous_conditions |
| `zh_baugesuche_ogd` | Canton de Zurich - Baugesuche im Kanton Zürich (OGD, désidentifié) | Fichier CSV unique mis à jour automatiquement | utilisable |
| `zh_zefix_neugruendungen` | Canton de Zurich - Tagesregistereinträge Zefix : créations d'entrepris | Fichiers CSV hebdomadaires | utilisable |
| `stadt_zh_ckan` | Ville de Zurich - Open Data (CKAN), catégorie bauen-und-wohnen | CKAN Action API sans authentification | utilisable |
| `bl_baubewilligungen` | Canton de Bâle-Campagne - Baubewilligungen par commune et trimestre (d | API OpenDataSoft | utilisable |
| `ge_sitg_autorisations` | Genève SITG - 'Autorisation de construire - Dossier' (couche ouverte) | Services WFS / ArcGIS REST / WMS du SITG, aussi référencé su | sous_conditions |
| `ge_sad_consult` | Genève - SAD Consult (application de consultation des autorisations de | Application web avec API interne | non |
| `vd_fao_camac` | Vaud - Feuille des avis officiels (FAO) : mises à l'enquête / permis d | Site web : liste résumée gratuite, contenu complet pour abon | sous_conditions |
| `fr_permis_construire` | Fribourg - permis de construire (Feuille officielle, plateforme canton | inconnu : mandant FR incomplet sur amtsblattportal | sous_conditions |
| `vs_econstruction` | Valais - plateforme eConstruction (dossiers mis à l'enquête) | Hors périmètre par règle du projet : les dossiers ne servent | non |
| `gebaeudeprogramm_stats` | Programme Bâtiments (Das Gebäudeprogramm, OFEN) - rapport et statistiq | Fichiers CSV OGD : ogd18_gebaeudeprogramm_auszahlungen.csv | utilisable |
| `meteosuisse_ogd` | MétéoSuisse - Open Data (stations SwissMetNet et autres) via STAC de l | API STAC | utilisable |
| `open_meteo_previsions` | Open-Meteo - prévisions (modèles MétéoSuisse ICON inclus) | REST sans clé | sous_conditions |
| `openholidays_feries_vacances` | OpenHolidays API - jours fériés (cantonaux, communaux) et vacances sco | REST sans authentification : /PublicHolidays, /SchoolHoliday | utilisable |
| `nager_date_feries` | Nager.Date - jours fériés et ponts (longs week-ends) | REST sans authentification | sous_conditions |
| `edk_vacances_scolaires` | CDIP/EDK (IDES) - listes officielles des vacances scolaires par canton | Documents PDF | sous_conditions |
| `conges_batiment_cn` | Congés du bâtiment : Convention nationale du secteur principal de la c | PDF | sous_conditions |
| `swisstopo_geocodage` | swisstopo / geo.admin.ch - SearchServer (géocodage d'adresses, adresse | REST JSON sans authentification | utilisable |
| `openplz_api` | OpenPLZ API - NPA -> commune (n° OFS) -> district -> canton | REST JSON sans authentification | sous_conditions |
| `transport_opendata_ch` | transport.opendata.ch - API horaires transports publics (connections) | REST JSON sans clé | sous_conditions |
| `ojp_opentransportdata` | opentransportdata.swiss - OJP 2.0 (calculateur d'itinéraires officiel) | POST XML avec en-tête Authorization: Bearer <clé> | sous_conditions |
| `osrm_routage` | OSRM sur données OpenStreetMap (routage routier ; serveur de démonstra | Serveur de démonstration FOSSGIS : usage raisonnable NON com | sous_conditions |
| `openrouteservice` | openrouteservice (HeiGIT) - API de routage sur OSM | REST avec clé API personnelle | sous_conditions |
| `pages_carrieres_jobposting` | Pages carrières des entreprises (balisage schema.org JobPosting en JSO | Lecture ponctuelle des pages carrières d'entreprises cliente | sous_conditions |
| `adzuna_api` | Adzuna - API officielle d'annonces (pays ch disponible) | REST JSON avec app_id/app_key | sous_conditions |
| `careerjet_api` | Careerjet - API publique de recherche (locales de_CH, fr_CH) | REST | sous_conditions |
| `jobcloud_jobs_ch_jobup` | jobs.ch / jobup.ch (JobCloud) - portails d'emploi privés | Aucune API publique documentée trouvée | non |
| `x28_donnees_emploi` | x28 AG - données du marché de l'emploi (Jobradar ; fournisseur du Swis | Rapport trimestriel de base gratuit, version Pro et données  | sous_conditions |
| `indeed_linkedin` | Indeed, LinkedIn Jobs et réseaux sociaux | Interdit par nos règles sans accord écrit | non |
| `fr_sitadel_dido` | France - Sitadel (permis de construire) via l'API DiDo du SDES | REST sans authentification | sous_conditions |
| `de_destatis_genesis` | Allemagne - Destatis GENESIS-Online : statistique des permis de constr | REST | sous_conditions |
| `uk_planning_data` | Royaume-Uni - planning.data.gov.uk (demandes de permis, Angleterre) | REST JSON sans authentification | sous_conditions |
| `eu_ted` | Union européenne - TED (Tenders Electronic Daily) Search API v3 | POST JSON sans authentification | sous_conditions |
| `i14y_catalogue` | I14Y (plateforme d'interopérabilité de la Confédération) - catalogue d | REST sans authentification en lecture | sous_conditions |

## 4. Fiches détaillées par source

Les numéros entre crochets renvoient à la liste « Sources » (§ 8). « Test réel » désigne toujours le résultat du § 2.1.

### 4.1 simap.ch (marchés publics) — `simap_appels_offres`, `simap_adjudications`, `simap_referentiels`

- **Endpoints**
  - Base : `https://www.simap.ch/api` [1]
  - Spécification OpenAPI : `https://www.simap.ch/api/specifications/simap.yaml` [1]
  - Recherche : `GET /publications/v2/project/project-search`
  - Détail : `GET /publications/v1/project/{projectId}/publication-details/{publicationId}`
  - Historique : `GET /publications/v1/publication/{publicationId}/past-publications`. Le paramètre `lotId` est obligatoire pour les marchés à lots.
  - Référentiels : `GET /codes/v1/{cpv|bkp|npk|ebkp-h|ebkp-t|oag|cpc}/search`, `/institutions/v1/institutions`, `/procoffices/v1/po/public`, `/cantons/v1` [1]
- **Paramètres** [1][53]
  - `lang` est **obligatoire** (de, fr, it ou en). Sans lui : HTTP 400, code d'erreur `E0025`.
  - Sans recherche textuelle, au moins un « quick-filter » est obligatoire, par exemple `projectSubTypes`. Les valeurs vont de construction, service et supply à project_competition, etc.
  - `newestPubTypes` : pour les adjudications, utiliser `award_tender`, `award_study_contract`, `award_competition` ou `direct_award`. La valeur `award` seule renvoie HTTP 400.
  - `orderAddressCantons` filtre sur le lieu d'exécution. Les codes canton sont nus (`VD`, pas `CH-VD`).
  - `issuedByOrganizations` filtre sur l'organisation adjudicatrice et ses sous-organisations : un identifiant racine par canton.
  - Les dates se filtrent avec `newestPublicationFrom` / `newestPublicationUntil` [53].
  - La pagination se fait par `lastItem` (vérifié par notre connecteur, `connectors/simap.py`).
  - La première requête pose un cookie de session [1].
- **Exemple de requête** (non testé : domaine bloqué) :
  `https://www.simap.ch/api/publications/v2/project/project-search?lang=fr&projectSubTypes=construction&orderAddressCantons=VS`
- **Champs utiles pour PROXSIS**
  - Objet, type de marché (`projectSubTypes`), codes CPV et BKP/NPK/eBKP, adjudicateur, lieu, délais.
  - Pour les adjudications : entreprise(s) lauréate(s) dans `decision.vendors` (y compris par lot) et montant quand il est publié [1].
  - Les codes BKP se traduisent en corps de métier (maçonnerie, électricité, sanitaire…). Une adjudication signale qu'une entreprise identifiée va devoir mobiliser du personnel. Le délai entre adjudication et besoin est **une hypothèse à valider** avec l'historique des commandes Flexsis.
- **Limites connues** [1]
  - L'index est fait par projet : un projet apparaît sous sa publication la plus récente.
  - D'après une mesure tierce (non vérifiée par nous), 60,6 % des projets n'ont pas de canton structuré. Il faut donc filtrer aussi par organisation.
  - Les adjudications sont publiées de façon inégale selon les cantons.
  - Seuls les marchés au-dessus des seuils légaux figureraient sur simap (non vérifié).
- **Licence et CGU**
  - simap.ch ne publie **aucune licence open data explicite**. La réutilisation est soumise aux conditions de https://www.simap.ch/de/about/legal [1], **non lues** car le domaine est bloqué.
  - La WebSearch n'a pas trouvé ces conditions [52].
  - Statut : **non vérifié**.
- **robots.txt :** inconnu (`https://www.simap.ch/robots.txt` bloqué).
- **Limites de débit :** inconnues. Un client tiers recommande un cache de 30 minutes [1].
- **Personnes physiques :** les organisations dominent. Les fiches peuvent contenir des noms et téléphones de personnes de contact : ne garder que l'organisation et la fonction. Un lauréat peut être une raison individuelle (le nom d'une personne) : ne le garder que s'il est inscrit au RC avec un UID, sans enrichissement sur la personne.
- **Verdict :** **utilisable** pour les trois lignes. C'est la source officielle nationale. Les endpoints de lecture sont documentés `security: None` [1]. **Réserve :** lire les conditions simap.ch avant la mise en production.
- **Test réel :** 5 URL bloquées (annexe A, test par hôte du 2026-10-05).

### 4.2 amtsblattportal.ch (FOSC/SHAB et feuilles officielles cantonales, dont le Bulletin officiel du Valais)

Lignes du catalogue concernées : `amtsblatt_fosc_hr`, `amtsblatt_rubriques_personnes_exclues`, `amtsblatt_fosc_up`, `amtsblatt_vs_permis_construire`, `amtsblatt_vs_grands_projets`, `amtsblatt_marches_hors_simap`, `amtsblatt_vs_emplois_publics`, `amtsblatt_permis_autres_cantons`, `amtsblatt_amenagement`.

- **Exploitant :** le SECO (plateforme eSHAB). Le portail regroupe la FOSC/SHAB et 27 feuilles officielles cantonales sur 29 « mandants » [7][54].
- **Bulletin officiel du Valais :** publié uniquement sous forme électronique sur cette plateforme depuis le 2023-03-01 (bulletin-officiel.vs.ch). Seule la version électronique fait foi. Mise à jour chaque jour ouvrable, consultation gratuite [46].
- **Endpoints** (base `https://amtsblattportal.ch/api/v1`) [7][3]
  - `GET /publications` : liste en JSON, **métadonnées seulement**.
  - `GET /publications/{id}/xml` : **texte complet** et `<uid>` de l'entreprise.
  - `GET /publications/xml` et `GET /publications/csv` : exports.
  - `GET /rubrics` : taxonomie complète (152 rubriques et 825 sous-rubriques au 2026-07-20 selon [4]).
  - `GET /tenants` : liste des mandants.
- **Paramètres** [7]
  - `publicationStates=PUBLISHED` est obligatoire. Sans lui, l'API renvoie HTTP 401, ce qui ne signifie pas qu'une authentification est requise.
  - Autres filtres : `rubrics`, `subRubrics`, `cantons`, `keyword`, `publicationDate.start`, `publicationDate.end`, `pageRequest.page`, `pageRequest.size`.
  - Taille de page : 200 résultats maximum (non vérifié) ; [3] limite volontairement à 100.
  - **Piège :** un nom de paramètre inconnu est ignoré sans erreur et renvoie tout le corpus. Il faut construire les requêtes à partir d'une liste blanche de paramètres. Un code de rubrique inconnu renvoie 0 résultat sans erreur [3][7].
  - Le tri n'est pas pilotable par l'API [3].
- **Exemples de requêtes** (non testés) :
  - Créations d'entreprises du jour en Valais :
    `https://amtsblattportal.ch/api/v1/publications?publicationStates=PUBLISHED&rubrics=HR&cantons=VS&publicationDate.start=2026-10-01&publicationDate.end=2026-10-04&pageRequest.size=100`
  - Mises à l'enquête valaisannes :
    `https://amtsblattportal.ch/api/v1/publications?publicationStates=PUBLISHED&cantons=VS&subRubrics=BA-VS05`
- **Rubriques : usage PROXSIS**

| Code | Contenu | Usage | Personnes physiques | Sources |
|---|---|---|---|---|
| `HR` (HR01 nouvelles inscriptions, HR02 mutations, HR03 radiations) | Registre du commerce | **Utiliser** : créations, nouveaux buts, transferts de siège, succursales, augmentations de capital | Les textes nomment des personnes (organes, signataires, titulaires de raisons individuelles) : **supprimer** ces données et ne garder que raison sociale, UID, forme, siège, but, capital | [7][4][47] |
| `BH` | Avis selon l'ordonnance sur le registre du commerce | Utiliser avec prudence | À filtrer | [5] |
| `UP` | Communications aux associés et actionnaires | Sous conditions (classée « jaune ») | Peut nommer des personnes | [5] |
| `BA-VS05` | Demandes d'autorisation de construire (VS) | **Sous conditions** | Requérants souvent particuliers : **exclure** les enregistrements des personnes physiques. Ne jamais suivre le lien eConstruction | non vérifié |
| `BA-VS10`, `BA-VS15`, `BA-VS20`, `BA-VS65` | Consultation publique des plans, approbations trafic et énergie, avis construction et territoire (VS) | Utiliser | Filtrer les noms d'opposants ou de propriétaires | non vérifié |
| `AR-VS40`, `AR-OW40`, `BA-SH40`, `OB-TI65`, `OB-*` | Marchés publics absents de simap | Utiliser, sans jamais interroger la rubrique parente | Faible | [3][4] |
| `AL-VS20` | Offres d'emploi publiques (VS) | Utiliser (signal secondaire) | Contact : garder la fonction | non vérifié |
| `BP-ZH`, `BP-BE`, `BP-BL`, `BP-BS`, `BP-TI`, `BP-ZG`, `BP-AR`, `AA-GR10` | Baugesuche des autres cantons | Sous conditions. Pour ZH, préférer le jeu OGD désidentifié (§ 4.10) | Classées « rouges » par [4] : particuliers | [4][5] |
| `RP-*`, `KA-*`, `KO-*`, `VE-*` | Aménagement, avis cantonaux et communaux, environnement-transport-énergie | Utiliser (contexte) | Faible | [3][4] |
| **`KK`, `SB`, `LS`, `SR`, `NA`, `ES`, `TE-*`, `VA-*`, `FZ-*`, `BV-*`, `BU-*`, `UV`, `GB-*`, `GE-*`, `SJ-BE`, `GR-*`, `AA-GR`** | Faillites, poursuites, appels aux créanciers, concordats, successions, testaments, décès, état civil, droit de cité, citations et justice, registre foncier, catalogue grison mixte | **EXCLURE (non)** | Données systématiques sur des particuliers | [3][4][5] |

- **Volumes cités par un tiers** (sonde du 2026-07-19 [7], non vérifiés par nous) : corpus de 2 789 951 publications, dont 2 262 954 en `HR` et 213 413 en `KK`, toutes années confondues.
- **Couverture :** seuls 16 mandants sur 29 exposent leur propre taxonomie. AG, FR, GE, GL, JU, LU, NE et UR sont incomplets [7]. Les publications sortent de l'API à l'échéance de leur délai légal de conservation [3].
- **Licence et CGU :** aucune licence CC formelle. D'après la documentation de l'API citée par [7] : accès libre (« freely accessible »), sans garantie d'exactitude, seul le PDF signé fait foi. Les CGU du portail n'ont **pas été lues** (domaine bloqué) : **non vérifié**.
- **robots.txt :** inconnu (bloqué).
- **Limites de débit :** non documentées dans les sources lues.
- **Données personnelles, règles d'implémentation** (reprises des principes de [3]) :
  - liste blanche de rubriques : tout ce qui n'est pas explicitement autorisé est fermé ;
  - aucune recherche par nom de personne ;
  - pas de conservation des publications au-delà du besoin, car elles ont des délais légaux de suppression ;
  - ne jamais injecter une rubrique parente bloquée à la place d'une sous-rubrique autorisée.
- **Verdicts :**
  - **utilisable** : HR, grands projets VS, marchés hors simap, emplois publics VS, aménagement ;
  - **sous_conditions** : UP, BA-VS05, BP des autres cantons ;
  - **non** : rubriques concernant des personnes physiques.
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.3 Zefix (registre du commerce) — `zefix_publicrest`, `zefix_rest_site_web`

- **API officielle : ZefixPublicREST**
  - Base : `https://www.zefix.admin.ch/ZefixPublicREST/api/v1` [48]
  - **Basic Auth obligatoire sur tous les endpoints**, y compris les référentiels. Les identifiants sont **gratuits** et s'obtiennent par e-mail à **zefix@bj.admin.ch** (Office fédéral du registre du commerce, OFRC/EHRA), en indiquant l'adresse e-mail qui servira de nom d'utilisateur [48].
  - Endpoints cités [48] : `GET /api/v1/company/uid/{uid}` (fiche, avec `sogcPub[]`), `POST /api/v1/company/search` et `GET /api/v1/sogc/bydate/{date}` (publications FOSC d'un jour).
- **Exemple de requête** (après obtention du compte) :
  `curl -u "<utilisateur>:<mot_de_passe>" https://www.zefix.admin.ch/ZefixPublicREST/api/v1/sogc/bydate/2026-10-02`
- **Champs utiles :** UID (clé de jointure avec simap, FOSC, IDE et les données Flexsis), raison sociale, forme juridique, siège, statut actif ou radié, but, succursales, publications FOSC. La version publique donne aussi signataires, capital et historique d'après [6] : **ne pas importer les champs de personnes**.
- **Licence :** le jeu opendata.swiss « zefix-zentraler-firmenindex » renvoie à `terms_by` (usage libre, citation de la source obligatoire) [48]. Le texte complet n'a pas été lu : **partiellement vérifié**.
- **API interne du site (ZefixREST)**, `https://www.zefix.admin.ch/ZefixREST/api/v1` : des clients tiers l'utilisent sans authentification [6]. Elle n'est pas publiée comme API de réutilisation. Verdict **non** : passer par la voie officielle.
- **robots.txt et limites de débit :** inconnus.
- **Verdict :** `zefix_publicrest` **sous_conditions** (compte à demander, simple et gratuit). `zefix_rest_site_web` **non**.
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.4 Registre IDE de l'OFS (UID-Register) — `uid_register_ide`

- **Endpoint :** `https://www.uid-wse.admin.ch/V5.0/PublicServices.svc` (SOAP, WSDL via `?wsdl`) [49].
- **Accès :** les PublicServices permettent des recherches « sous forme restreinte sans login » [49]. Les noms exacts des opérations sont dans la spécification OFS, disponible en FR et DE sur la page « UID-Schnittstellen », bloquée ici.
- **Limite :** 20 requêtes par minute selon [6] (non vérifié).
- **Champs utiles :** UID, raison sociale, adresse, forme juridique, statut TVA, **codes NOGA** [6]. Ils permettent de cibler les entreprises par secteur.
- **Licence :** non vérifiée. Contact OFS : uid@bfs.admin.ch [49].
- **Personnes physiques :** le registre contient aussi des raisons individuelles. Filtrer par forme juridique et ne pas stocker de noms de particuliers.
- **Verdict :** **utilisable**, sous réserve de lire la spécification et de respecter la limite.
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.5 RegBL / GWR (Registre fédéral des bâtiments et des logements) — `regbl_geoadmin_api`, `regbl_madd_dump`

- **Endpoints**
  - API geo.admin, couche `ch.bfs.gebaeude_wohnungs_register` [8][9] :
    - `https://api3.geo.admin.ch/rest/services/api/MapServer/find?layer=ch.bfs.gebaeude_wohnungs_register&searchField=egid&searchText={EGID}&returnGeometry=true&sr=2056` ;
    - `.../MapServer/identify` (par coordonnées) ;
    - `.../SearchServer` (adresse vers EGID).
    - Un EGID inconnu renvoie HTTP 200 avec une liste vide.
  - Extraits publics cantonaux : `https://public.madd.bfs.admin.ch/{canton}.zip`. Archive quotidienne contenant `data.sqlite` (tables `building`, `entrance`, `dwelling`, `code`) [8]. Selon [8], l'endpoint MADD `/api/buildings/{egid}` renvoyait 404 au 2026-07-24.
- **Champs utiles**
  - Statut du bâtiment GSTAT : 1001 projeté, 1002 autorisé, 1003 en construction, 1004 existant, 1005 inutilisable, 1007 démoli, 1008 non réalisé. Codes lus dans [9], à confirmer dans le catalogue officiel des caractères du RegBL [55].
  - Commune (numéro OFS), catégorie, année de construction, logements.
  - Le comptage des bâtiments par commune aux statuts 1001 à 1003 donne le **pipeline de chantiers**.
  - Les « données de projet » du RegBL au-delà du statut (coûts, maître d'ouvrage) ne figurent pas dans l'extrait public d'après [8] : **non vérifié**.
- **Licence et CGU**
  - API geo.admin : conditions générales de l'IFDG, gratuites, sans inscription. **Fair use : 20 requêtes par minute en moyenne 24h/24** sur les services REST ; au-delà, contacter info@geo.admin.ch. Pas d'interrogation intensive par robot : utiliser le téléchargement pour les volumes [50].
  - Extraits MADD : **informations contradictoires**. [8] indique « open government data with attribution ». Un extrait de résultat WebSearch mentionne « reproduction autorisée, sauf à des fins commerciales, si la source est mentionnée » ; son document source n'a pas pu être identifié [51]. **Confirmation écrite de l'OFS (housing-stat.ch) requise** avant tout usage commercial. Les autorisations d'accès aux services se demandent sur housing-stat.ch [51].
- **Personnes physiques :** l'extrait public omet les attributs personnels [8]. Ne jamais recouper avec d'autres sources pour retrouver des propriétaires privés.
- **Verdicts :** `regbl_geoadmin_api` **utilisable** (dans le fair use). `regbl_madd_dump` **sous_conditions** (licence à clarifier).
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.6 OFS : STAT-TAB (PxWeb) et statistiques — `ofs_pxweb_api`, `ofs_construction`, `ofs_besta`, `ofs_statent`, `ofs_hesta`, `ofs_agvch_communes`

- **API :** `https://www.pxweb.bfs.admin.ch/api/v1/{de|fr|it|en}/{table}/{table}.px`.
  - `GET` renvoie les métadonnées.
  - `POST` d'une requête JSON renvoie les données en JSON, CSV ou PX.
  - Pas d'authentification. 682 tables selon [10].
  - Limitation de débit (HTTP 429) : non vérifiée.
  - Les montants de construction seraient exprimés en milliers de CHF (non vérifié).
- **Tables citées** (identifiants tirés de sources tierces, non vérifiés par nous)

| Thème | Table(s) | Contenu | Source |
|---|---|---|---|
| Construction | `px-x-0904010000_205` | Investissements et réserves de travail par grande région, canton et commune (depuis 1994) | [10] |
| Construction | `px-x-0904010000_203`, `_201` | Investissements et réserves de travail de l'année suivante, maîtres d'ouvrage publics et privés | [19] |
| Construction | `px-x-0904010000_112`, `_111` | Projets de construction par canton et commune | [19] |
| Logements | `px-x-0904030000_105`, `_106` | Logements et bâtiments neufs par commune (depuis 2013) | [10] |
| Emploi | `px-x-0602000000_101`, `_102` | BESTA : emplois par division NOGA, dont la division 78 (activités liées à l'emploi, proxy du travail temporaire), et par grande région | [19] |
| Places vacantes | `px-x-0602000000_103`, `_104` | BESTA : places vacantes, indice et taux, par division NOGA et par grande région (la Région lémanique regroupe VD, VS et GE) | [19] |
| Entreprises | `px-x-0602010000_101` | STATENT : établissements, emplois et EPT par canton et division NOGA | [19] |
| Tourisme | HESTA (identifiant non vérifié) | Nuitées par commune et par mois, environ 2 mois de décalage | non vérifié |

- **Exemple de requête** (non testé) : `GET https://www.pxweb.bfs.admin.ch/api/v1/fr/px-x-0602000000_103/px-x-0602000000_103.px` (métadonnées), puis `POST` d'un corps `{"query":[…],"response":{"format":"csv"}}` sur la même URL.
- **Licence**
  - Conditions d'utilisation de l'OFS : https://www.bfs.admin.ch/bfs/en/home/grundlagen/nutzungsbedingungen.html [10], non lues.
  - **Attention :** sur opendata.swiss, des jeux de l'OFS portent `terms_by_ask` (usage commercial soumis à l'autorisation du fournisseur) et d'autres `terms_open` [32]. **Vérifier la licence de chaque table** avant usage commercial.
- **Répertoire des communes (AGVCH) :** service REST sans authentification (`snapshot`, `correspondances`, `mutations`, `levels`) [10]. C'est la clé de jointure par numéro OFS de commune, y compris pour suivre les fusions.
- **Personnes physiques :** aucune (statistiques agrégées).
- **Verdict :** **utilisable**, sous réserve de la licence de chaque table.
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.7 SECO : AMSTAT, séries publiées, obligation d'annonce, Job-Room

- **AMSTAT** (`seco_amstat`), `https://www.amstat.ch/v2/amstat_fr.html`
  - Application JavaScript, **sans API REST publique** [11].
  - Chômage par profession, canton et district selon [19] (non vérifié).
  - **Verdict : sous_conditions.** Exports manuels, ou demande de données au SECO. Ne pas automatiser l'extraction de l'application.
- **Séries publiées** (`seco_opendata_series`)
  - Table `T3.3.0.1` sur opendata.swiss, licence CC0 selon [11] (non vérifié).
  - Rapport mensuel PDF « La situation sur le marché du travail » sur arbeit.swiss, avec un motif d'URL structuré [11][19].
  - **Verdict : utilisable.**
- **Liste de l'obligation d'annonce** (`seco_obligation_annonce`)
  - Fichier annuel des genres de professions dont le taux de chômage atteint au moins 5 % (seuil en vigueur depuis 2020 selon [11]).
  - Page : https://www.arbeit.swiss/secoalv/de/home/menue/unternehmen/stellenmeldepflicht.html.
  - Une ancienne URL XLSX (DE/FR/IT) apparaît dans un index tiers [45]. [19] signale un 404 sur le PDF 2026. Le PDF annuel se trouverait sur arbeit.swiss (non vérifié).
  - Signal : un métier soumis à l'obligation signale de la main-d'œuvre disponible ; un métier absent, une tension relative (approximation).
  - **Verdict : utilisable** (téléchargement manuel annuel).
- **Job-Room** (`jobroom_api`)
  - Portail public du SECO.
  - L'API de recherche `POST https://api.job-room.ch/jobadservice/api/jobAdvertisements/_search?page=0&size=50&sort=date_desc` est **interne et non documentée**. Le total arrive dans l'en-tête `X-Total-Count` ; filtres `cantonCodes`, `keywords`, `onlineSince`, `radiusSearchRequest` [21].
  - Le **robots.txt interdit `/job-search/` aux robots** [21].
  - Les hôtes api et test-api.job-room.ch semblent servir à la publication d'annonces (catalogue tiers ; documentation bloquée par robots.txt) [19].
  - Le portail précise qu'il n'a pas d'influence sur le contenu des annonces externes [21].
  - Les annonces contiennent des agences concurrentes, Flexsis comprise [21], et des contacts de recruteurs.
  - **Verdict : sous_conditions (accord écrit du SECO requis).** Nos règles interdisent cette API interne sans autorisation.
  - Volume cité par [21], non vérifié par nous : environ 78 774 annonces en Suisse au 2026-08-28.
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.8 Marché du travail cantonal (OGD) — `cantons_marche_travail_ogd`

- **Fribourg** (OpenDataSoft) [32] :
  - `https://opendata.fr.ch/api/explore/v2.1/catalog/datasets/03_03_places_vacantes_annoncees_mensuelles/exports/csv?use_labels=true` ;
  - `…/03_03_chomage_mensuel/…` ;
  - séries mensuelles depuis 2004, licence **CC BY-SA**.
- **Vaud :** fichiers XLSX de Statistique Vaud [19] (non vérifié).
- **Zoug :** statistique du marché du travail [32].
- **Verdict : utilisable.**
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.9 Indices conjoncturels et sources sectorielles

- **Swiss Staffingindex** (`swissstaffing_index`) : selon [19], uniquement des communiqués de presse trimestriels, sans série téléchargeable ni API. Licence non indiquée. **sous_conditions** : saisie manuelle et citation.
- **KOF Datenservice** (`kof_datenservice`)
  - `https://datenservice.kof.ethz.ch/api/v1/public/collections/{ogd_ch.kof.barometer|ogd_ch.kof.ie}?mime=csv` ;
  - métadonnées : `…/api/v1/public/metadata/collections/{collection}?mime=csv&locale=de` [32].
  - Licence opendata.swiss `terms_by` [32].
  - L'indicateur de l'emploi KOF vient des enquêtes conjoncturelles trimestrielles. Il mesure le jugement des entreprises sur leurs effectifs et leurs intentions sur 3 mois [32].
  - Le paquet R `kofdata` est abandonné au profit de `tsdbapi` [30].
  - **utilisable.**
- **KOF Time Series DB v2** (`kof_tsdb_job_tracker`)
  - `https://tsdb-api.kof.ethz.ch/v2/` (documentation `/v2/docs`).
  - Séries publiques avec `access_type=public` ; clé API pour un accès programmatique non public [31].
  - Swiss Job Tracker (annonces en ligne hebdomadaires, données x28) : clé `ch.kof.jobtracker.total.total.clean.idx` selon [19].
  - Licence non vérifiée. **sous_conditions.**
- **Enquêtes conjoncturelles KOF de la construction** (`kof_enquetes_construction`) : séries détaillées apparemment restreintes [19]. **sous_conditions.**
- **SSE/SBV** (`sbv_baukonjunktur`) : enquête trimestrielle (chiffre d'affaires, entrées de commandes, réserves de travail) et Bauindex sur baumeister.swiss. Communiqués seulement, tableaux complets peut-être réservés aux membres [19]. **sous_conditions.**
- **Baublatt / Docu Media** (`baublatt_docu`) : service payant [19]. Exiger contractuellement l'exclusion des maîtres d'ouvrage privés. **sous_conditions** (contrat).
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.10 opendata.swiss et portails cantonaux ou communaux (permis de construire)

- **opendata.swiss** (`opendata_swiss_ckan`)
  - API CKAN : `https://ckan.opendata.swiss/api/3/action/package_search?q=…` (ou `https://opendata.swiss/api/3/action/…`) [10][11].
  - `ckan.opendata.swiss` renvoie HTTP 403 aux User-Agent par défaut : envoyer un UA explicite [10].
  - Licences par jeu : `terms_open`, `terms_by`, `terms_ask`, `terms_by_ask`.
  - Environ 14 551 jeux selon [2] (non vérifié).
  - **utilisable.**
- **Canton de Zurich : « Baugesuche im Kanton Zürich »** (`zh_baugesuche_ogd`)
  - Ressource `https://daten.statistik.zh.ch/ogd/daten/ressourcen/KTZH_00002982_00006183.csv`.
  - Licence **`terms_open`**. Le service OGD vérifie chaque jour les nouveaux Baugesuche (collecte depuis l'automne 2024).
  - **Noms et adresses des requérants et maîtres d'ouvrage supprimés volontairement** par le fournisseur. Localisation (numéro OFS, numéro cadastral) et description conservées [32].
  - Meilleur flux de permis alémanique trouvé. **utilisable.**
- **Canton de Zurich : créations d'entreprises par branche** (`zh_zefix_neugruendungen`)
  - `https://www.web.statistik.zh.ch/ogd/data/KANTON_ZUERICH_ZEFIX_Neugruendungen.csv`, hebdomadaire, `terms_by` [32].
  - La ressource « Konkurse » ne doit servir qu'en agrégé.
  - **utilisable.**
- **Ville de Zurich** (`stadt_zh_ckan`) : CKAN `https://data.stadt-zuerich.ch/api/3/`. Licence CC0 (« Open by Default » depuis 2021) selon [16]. Aucun jeu de permis spécifique vérifié. **utilisable.**
- **Bâle-Campagne** (`bl_baubewilligungen`) : `https://data.bl.ch/api/v2/catalog/datasets/12880/exports/csv?use_labels=true`. Permis par commune et par trimestre depuis 2005 ; jeu 12890 par type d'ouvrage ; `terms_by` [32]. **utilisable.**
- **Genève, SITG « Autorisation de construire – Dossier »** (`ge_sitg_autorisations`)
  - Page `https://sitg.ge.ch/donnees/sit-autor-dossier`.
  - Services WFS, ArcGIS REST et WMS ; mise à jour quotidienne ; « accès libre » ; champ `DATE_DEPOT` [19] (non vérifié).
  - **sous_conditions :** vérifier licence et champs nominatifs.
  - **L'application SAD Consult** (`https://app2.ge.ch/sadconsult`, `ge_sad_consult`) expose nom et adresse des requérants [44] : **non**.
- **Vaud, FAO** (`vd_fao_camac`) : `https://www.faovd.ch/permis-de-construire/…`. Liste résumée gratuite, contenu complet pour abonnés, CGU d'extraction non indiquées [19]. **sous_conditions** (accord écrit de l'éditeur ; requérants particuliers à filtrer).
- **Fribourg** (`fr_permis_construire`) : le mandant FR est incomplet sur amtsblattportal [7] et aucune API trouvée. **sous_conditions / inconnu.**
- **Valais, eConstruction** (`vs_econstruction`) : **non**, par règle du projet. Utiliser uniquement les publications officielles du BO (§ 4.2).
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.11 Programme Bâtiments (Das Gebäudeprogramm, OFEN) — `gebaeudeprogramm_stats`

- **Fichiers OGD** [32] :
  - `https://www.uvek-gis.admin.ch/BFE/ogd/18/ogd18_gebaeudeprogramm_auszahlungen.csv` (versements par domaine — technique du bâtiment, isolation, assainissement… — et par canton) ;
  - `…/ogd18_gebaeudeprogramm_anzahl_gesuche.csv` (demandes et bâtiments 2017-2022).
- **Licence :** `terms_by`.
- **Usage :** demande de second œuvre et d'installateurs (rénovation énergétique).
- **Verdict : utilisable.**
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.12 Météo — `meteosuisse_ogd`, `open_meteo_previsions`

- **MétéoSuisse Open Data**
  - API STAC de l'IFDG : `https://data.geo.admin.ch/api/stac/v1/collections`. Exemple de collection : `ch.meteoschweiz.ogd-smn` (stations automatiques) [25].
  - CSV séparés par `;` [25], encodage latin-1 (non vérifié).
  - Granularités `t` (10 min), `h`, `d`, `m`, `y`. Répertoires `historical` (mis à jour une fois par an), `recent` (chaque jour), `now` (toutes les 10 min) [25].
  - Recommandations [25] : en-têtes `If-None-Match` / ETag ; backoff exponentiel avec gigue.
- **Licence vérifiée** (texte officiel lu) [26] :
  - **CC BY 4.0**, réutilisation libre **y compris commerciale** ;
  - mention obligatoire « Source: MétéoSuisse » ;
  - interdiction d'un usage excessif de l'infrastructure (téléchargements à haute fréquence du même contenu) ;
  - conditions générales de l'IFDG applicables.
  - La date exacte d'ouverture des données (« depuis 2025 ? ») **n'a pas été vérifiée**. Les conditions renvoient à l'art. 10 LMét (RS cc/2023/682) et à l'art. 5 OMét [26].
- **Usage :** précipitations, gel et neige pour estimer les jours chômés sur les chantiers et la saisonnalité.
- **Verdict : utilisable.**
- **Open-Meteo** (prévisions à 16 jours, `https://api.open-meteo.com/v1/forecast`) [13] : conditions d'usage commercial non lues. **sous_conditions.**
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.13 Calendrier : jours fériés, vacances scolaires, congés du bâtiment

- **OpenHolidays API** (`openholidays_feries_vacances`)
  - Endpoints [12] : `https://openholidaysapi.org/PublicHolidays?countryIsoCode=CH&languageIsoCode=FR&validFrom=2026-01-01&validTo=2026-12-31&subdivisionCode=CH-VD`, puis `/SchoolHolidays` (plage de dates obligatoire, sinon HTTP 400), `/SchoolHolidaysByDate` et `/Subdivisions?countryIsoCode=CH` (26 cantons).
  - Six cantons différencient les vacances par type d'école : AI, AR, BE, GR, SO, ZH [12].
  - Données sources en CSV sur GitHub : `src/ch/holidays/holidays.public.csv`, jours fériés 2020-2030 [29].
  - **Licence divergente :** le fichier LICENSE du dépôt de données est l'**ODbL** [28], alors que [12] indique CC BY 4.0. Appliquer l'ODbL par prudence : attribution, et partage à l'identique d'une base dérivée publiée.
  - Anomalie qualité 2026 VD : voir § 2.4.
  - **utilisable.**
- **Nager.Date** (`https://date.nager.at/api/v3/PublicHolidays/2026/CH`, longs week-ends) : MIT selon [12]. **utilisable** (secondaire).
- **CDIP/EDK (IDES)** : listes officielles des vacances scolaires en PDF, archive `https://edudoc.ch/search?cc=idesferienliste&ln=de&c=idesferienliste` [32] et page EDK [19]. Référence pour contrôler OpenHolidays et pour l'historique avant 2020. **utilisable** (manuel).
- **Congés du bâtiment** (`conges_batiment_cn`)
  - Source nationale : la Convention nationale du secteur principal de la construction (CN/LMV). D'après [19], une CN 2026-2031 existe sur shop.baumeister.swiss, non ouverte par le tiers ni par nous.
  - Calendriers régionaux des commissions paritaires. Pour le Valais, une circulaire AVE-WBV 2026 indiquerait une fermeture estivale des chantiers du **3 au 10 août 2026** et 2 112 heures annuelles [19] (**non vérifié par nous**).
  - Pause de Noël : **inconnu**.
  - **sous_conditions** : saisie manuelle annuelle à partir des PDF officiels.
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.14 Géocodage et temps de trajet

- **swisstopo SearchServer** (`swisstopo_geocodage`)
  - `https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText={adresse}&type=locations&origins=address&limit=5&sr=2056` [9].
  - `featureId` = `{EGID}_{EDID}` ; axes inversés (`y` = est, `x` = nord) [8].
  - Fair use : 20 requêtes par minute [50].
  - **utilisable.** Ne pas géocoder d'adresses de candidats chez un tiers : travailler au NPA ou à la commune.
- **OpenPLZ API** (`https://openplzapi.org/ch/…`, NPA vers commune OFS, district et canton) [15] : licence non vérifiée. **utilisable.**
- **transport.opendata.ch** (`https://transport.opendata.ch/v1/connections?from=…&to=…`) [43]
  - Limites non documentées officiellement. Des utilisateurs rapportent environ 1 000 requêtes par 24 h et une limite par minute de timetable.search.ch [42] (non vérifié).
  - **sous_conditions.**
- **OJP 2.0** (`POST https://api.opentransportdata.swiss/ojp20`, en-tête `Authorization: Bearer <clé>`)
  - Clé gratuite sur api-manager.opentransportdata.swiss [14].
  - Offre gratuite : 50 requêtes par minute et 20 000 par jour et par clé, selon un audit tiers qui cite opentransportdata.swiss/en/limits-and-costs [42] (non vérifié).
  - **sous_conditions.**
- **OSRM**
  - Le serveur de démonstration `router.project-osrm.org` est limité à un **usage non commercial**, au maximum **1 requête par seconde**, sans garantie [33].
  - **sous_conditions** : auto-héberger OSRM avec un extrait OSM Suisse (données sous ODbL).
- **openrouteservice** : clé API personnelle requise [34], quotas non vérifiés. **sous_conditions.**
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.15 Offres d'emploi : pages carrières et agrégateurs

- **Pages carrières (schema.org `JobPosting`)** (`pages_carrieres_jobposting`)
  - 34 propriétés ont `JobPosting` pour domaine dans le vocabulaire officiel [41] : `title`, `datePosted`, `validThrough`, `hiringOrganization`, `jobLocation`, `employmentType`, `occupationalCategory`, `totalJobOpenings`, `jobStartDate`, `jobImmediateStart`, `workHours`, `baseSalary`, `skills`, `qualifications`, `industry`, `applicationContact`, etc.
  - **sous_conditions** :
    - seulement les sites d'entreprises clientes ou prospects ;
    - respect du robots.txt et des CGU de chaque site, débit faible ;
    - ne pas stocker `applicationContact` (personne) ;
    - pas d'ATS tiers ni de portails privés sans accord.
  - Le JSON-LD `JobPosting` se trouverait dans les pages de détail (non vérifié).
- **Adzuna** (`adzuna_api`)
  - API officielle **couvrant la Suisse** (`ch` fait partie des 19 pays) : `https://api.adzuna.com/v1/api/jobs/ch/search/{page}?app_id=…&app_key=…&what=…&where=…`.
  - Selon [20] (vérifié par le tiers le 2026-09-02, non par nous) :
    - au maximum 50 résultats par page ;
    - descriptions tronquées à 500 caractères ;
    - quotas de 25 appels par minute, 250 par jour, 1 000 par semaine, 2 500 par mois ;
    - obligation de renvoyer vers `redirect_url` ;
    - 81 882 annonces en Suisse sur une requête vide.
  - **sous_conditions** : clé requise, et confirmation écrite de l'usage analytique commercial.
- **Careerjet** (`careerjet_api`)
  - `http://public.api.careerjet.net/search`, locales `de_CH` et `fr_CH` [23][24].
  - Paramètres obligatoires : `affid` (compte partenaire), `user_ip`, `user_agent` et `url` de la page d'affichage. L'API est **conçue pour afficher des résultats à des utilisateurs finaux**.
  - **sous_conditions** (accord écrit pour un usage analytique) ; transmettre des IP d'utilisateurs est à éviter.
- **jobs.ch / jobup.ch (JobCloud)** (`jobcloud_jobs_ch_jobup`)
  - Pas d'API publique documentée trouvée.
  - Selon [19], le robots.txt interdit `/api/` et les pages de détail.
  - [22] extrait le DOM. Ces pratiques sont **interdites par nos règles** sans accord écrit.
  - **non.**
- **x28** (`x28_donnees_emploi`) : rapport trimestriel gratuit, version Pro et données brutes payantes [19]. **sous_conditions** (contrat).
- **Indeed, LinkedIn, réseaux sociaux** (`indeed_linkedin`) : **non**. Indeed répond HTTP 403 aux robots ; les CGU de LinkedIn interdiraient le scraping (non vérifié) ; Indeed Hiring Lab ne couvre pas la Suisse [19].
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.16 Données étrangères (comparaison et zones frontalières)

- **France, Sitadel** (`fr_sitadel_dido`) : API DiDo du SDES, base `https://data.statistiques.developpement-durable.gouv.fr/dido/api/v1`, jeu Sitadel `6513f0189d7d312c80ec5b5b` [38]. Utile pour l'Ain, la Haute-Savoie, le Doubs et le Haut-Rhin. Licence non vérifiée. **sous_conditions.**
- **Allemagne, Destatis GENESIS** (`de_destatis_genesis`)
  - `https://www-genesis.destatis.de/genesisWS/rest/2020/` (data/table, metadata, helloworld/logincheck).
  - **Compte requis** [35].
  - Statistique 31111 (Baugenehmigungen), table `31111-0002` [37], mensuelle, publiée environ 8 semaines après le mois [36].
  - Licence **Datenlizenz Deutschland – Namensnennung 2.0** [36].
  - Le nom du maître d'ouvrage n'est jamais publié [36].
  - **sous_conditions.**
- **Royaume-Uni, planning.data.gov.uk** (`uk_planning_data`) : `https://www.planning.data.gov.uk/entity.json?dataset=planning-application&limit=100&offset=0`. La documentation demande de limiter poliment la fréquence des requêtes et propose des téléchargements en masse [39]. Licence non vérifiée. Sert de référence méthodologique uniquement. **sous_conditions.**
- **UE, TED** (`eu_ted`) : `POST https://api.ted.europa.eu/v3/notices/search`, sans authentification, au maximum 250 avis par page [40]. Licence non vérifiée. **sous_conditions.**
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

### 4.17 Catalogues : I14Y — `i14y_catalogue`

- **Endpoint :** `https://api.i14y.admin.ch/api`. Le chemin exact est à confirmer ; lecture sans authentification [17].
- **Contenu :** registre des API officielles suisses et catalogue DCAT.
- **Usage :** découvrir de nouvelles sources.
- **Verdict : utilisable.**
- **Test réel :** bloqué le 2026-10-04 (colonne `test_reel_2026_10_04` du catalogue) et le 2026-10-05 (annexe A, test par hôte).

## 5. Ce qu'il faudrait pour tester pour de vrai

### 5.1 Domaines à autoriser dans la politique réseau

**Priorité 1 (cœur du radar)**

| Domaine | Usage |
|---|---|
| `www.simap.ch` | API simap, spécification, conditions légales |
| `amtsblattportal.ch`, `www.amtsblattportal.ch` | API FOSC et feuilles officielles cantonales (dont le BO VS) |
| `bulletin-officiel.vs.ch` | Contrôle visuel du BO VS (pas d'extraction) |
| `www.zefix.admin.ch`, `www.zefix.ch` | ZefixPublicREST (avec compte) |
| `www.uid-wse.admin.ch`, `www.uid.admin.ch` | Webservice IDE |
| `api3.geo.admin.ch`, `api.geo.admin.ch`, `data.geo.admin.ch`, `wmts.geo.admin.ch`, `www.geo.admin.ch`, `docs.geo.admin.ch` | RegBL, géocodage, STAC MétéoSuisse, CG et fair use |
| `public.madd.bfs.admin.ch`, `www.housing-stat.ch` | Extraits RegBL et conditions |
| `www.pxweb.bfs.admin.ch`, `www.bfs.admin.ch`, `dam-api.bfs.admin.ch`, `www.agvchapp.bfs.admin.ch` | STAT-TAB, conditions OFS, fichiers DAM, communes |
| `opendata.swiss`, `ckan.opendata.swiss` | CKAN et conditions d'utilisation |
| `www.arbeit.swiss`, `www.amstat.ch`, `www.seco.admin.ch` | Obligation d'annonce, rapports mensuels, AMSTAT |
| `datenservice.kof.ethz.ch`, `tsdb-api.kof.ethz.ch`, `kof.ethz.ch` | Indicateurs KOF |
| `openholidaysapi.org`, `www.openholidaysapi.org`, `date.nager.at`, `edudoc.ch`, `www.edk.ch` | Calendriers |
| `opendatadocs.meteoswiss.ch`, `www.meteoschweiz.admin.ch` | Documentation MétéoSuisse |

**Priorité 2 (cantons, indices, trajets)**

- **Statistique et open data cantonaux :** `daten.statistik.zh.ch`, `www.web.statistik.zh.ch`, `data.stadt-zuerich.ch`, `data.bl.ch`, `opendata.fr.ch`, `www.vd.ch`, `www.vs.ch`, `www.fr.ch`.
- **Genève :** `sitg.ge.ch` et `ge.ch`. L'hôte des services WFS/ArcGIS du SITG est à identifier.
- **Programme Bâtiments :** `www.uvek-gis.admin.ch`, `www.dasgebaeudeprogramm.ch`.
- **Indices et associations :** `www.swissstaffing.ch`, `baumeister.swiss`, `www.ave-wbv.ch`.
- **Catalogues et référentiels :** `api.i14y.admin.ch`, `openplzapi.org`.
- **Trajets :** `transport.opendata.ch`, `api.opentransportdata.swiss`, `api-manager.opentransportdata.swiss`, `opentransportdata.swiss`, `api.openrouteservice.org`.
- **Adzuna :** `api.adzuna.com`, `developer.adzuna.com`.
- **Météo :** `api.open-meteo.com`, `open-meteo.com` (conditions).
- **Vocabulaire :** `schema.org`.
- **FAO Vaud :** `www.faovd.ch`, seulement après accord de l'éditeur.
- **Job-Room :** `api.job-room.ch` et `www.job-room.ch`, **seulement après accord écrit du SECO**.

**Priorité 3 (étranger)**

`data.statistiques.developpement-durable.gouv.fr`, `www.data.gouv.fr`, `www-genesis.destatis.de`, `genesis.destatis.de`, `www.regionalstatistik.de`, `www.planning.data.gov.uk`, `api.ted.europa.eu`, `docs.ted.europa.eu`.

**À NE PAS autoriser (règles du projet)**

- plateforme eConstruction VS ;
- `app2.ge.ch` (SAD Consult) ;
- `www.jobs.ch`, `www.jobup.ch` ;
- Indeed, LinkedIn et réseaux sociaux ;
- `router.project-osrm.org` (usage non commercial : héberger OSRM soi-même).

### 5.2 Comptes et clés à demander

1. Identifiants ZefixPublicREST : e-mail à zefix@bj.admin.ch [48].
2. Clé OJP 2.0 sur api-manager.opentransportdata.swiss [14].
3. Clé Adzuna (developer.adzuna.com), avec confirmation écrite de l'usage commercial analytique.
4. Compte Destatis GENESIS [35] et, si besoin, clé API KOF [31].
5. Accords écrits :
   - SECO (Job-Room) ;
   - éditeur de la FAO Vaud ;
   - JobCloud, uniquement si la direction le souhaite ;
   - x28 et Docu Media (contrats commerciaux).
6. Confirmation de l'OFS (housing-stat.ch) sur l'usage commercial des extraits RegBL.

### 5.3 Protocole de test une fois le réseau ouvert

Pour chaque ligne du catalogue :

1. Rejouer la commande du § 2.1 et consigner le code HTTP.
2. Lire et archiver avec la date les conditions et le robots.txt du domaine.
3. Faire un appel « métier » minimal, par exemple `project-search` avec `lang=fr&projectSubTypes=construction&orderAddressCantons=VS`, ou `publications` avec `rubrics=HR&cantons=VS`.
4. Mesurer le volume réel sur 30 jours, sans le publier comme chiffre tant qu'il n'est pas reproductible.
5. Vérifier par échantillonnage l'absence de données de personnes physiques après filtrage.
6. Mettre à jour les colonnes `test_reel_2026_10_04` (en créant une colonne datée du nouveau test), `volume` et `verdict` du CSV.

## 5 bis. Tests réels du 2026-10-05 (session Mac, réseau ouvert)

Le protocole du § 5.3 a été appliqué depuis le Mac de Hiba, qui n'a pas de
liste blanche réseau.

- **Joignabilité** : 76 domaines sur 77 répondent (`docs/recherche/reseau.md`).
- **Conditions et robots.txt** lus et archivés
  (`docs/recherche/conditions_2026-10-05.md`, `data/conditions/2026-10-05/`).
  Le client applique robots.txt selon la RFC 9309 et n'appelle jamais un
  chemin interdit.
- **Chaque ligne du catalogue** a été rejouée (colonne `test_reel_2026_10_05`
  de `data/catalogue.csv`, détail `data/reseau/catalogue_tests_2026-10-05.csv`) :
  66 URL répondent, 40 sont interdites par robots.txt (non appelées), 3
  serveurs sont injoignables, 17 sources ne sont pas appelées parce qu'elles
  exigent une inscription, une clé ou un accord écrit, ou parce que leur
  verdict est « non ». **Aucun contournement.**
- **Changements de verdict** : simap (3 lignes) → `utilisable` (CG API lues :
  usage commercial autorisé, mention obligatoire) ; nager.date et créations
  Zefix ZH → `non` (robots.txt) ; KOF datenservice → `non` (serveur
  injoignable, remplacé par tsdb-api) ; KOF Job Tracker → `utilisable` pour la
  série nationale seulement.
- **Point bloquant** : amtsblattportal (FOSC, Bulletin officiel du Valais),
  data.bl.ch, opendata.fr.ch — les CG ou la vocation de portail ouvert
  autorisent la réutilisation, mais robots.txt interdit l'accès automatisé.
  Décision demandée à Hiba (§ « Question ouverte » des conditions).
- **Volumes réels** mesurés : voir `data/annotations/reel_v2/TIRAGE.json`
  (adjudications simap d'août–septembre 2026) ; backtest T0 : à venir
  (`docs/backtest/reel_t0.json`, après la collecte).

## 6. Données internes Flexsis/Interiman : format attendu

**Principes**

- **Format :** CSV UTF-8 (séparateur virgule) ou Parquet. Dates en ISO 8601 (`AAAA-MM-JJ`), horodatages en UTC (`AAAA-MM-JJThh:mm:ssZ`).
- **Codes de référence :** commune = numéro OFS ; métier = ISCO-08 à 4 chiffres (la nomenclature suisse CH-ISCO-19 peut être ajoutée si Flexsis l'utilise déjà) ; branche = NOGA 2008 ; canton = abréviation à 2 lettres.
- **Minimisation (nLPD) :** PROXSIS n'a besoin d'aucun nom de personne. Les identifiants de personnes (candidats, contacts, consultants) sont des **pseudonymes stables** générés par Flexsis. La table de correspondance reste dans le CRM et n'est jamais transmise.
- **Exclusions :** ne jamais transmettre de numéro AVS, date de naissance, nationalité, photo, donnée de santé, adresse exacte de candidat, appréciation personnelle libre ou donnée de salaire individuelle.
- **Jointures avec les sources publiques :** `uid` relie Zefix, FOSC, simap et IDE ; `commune_ofs` relie OFS, RegBL, MétéoSuisse et OpenHolidays ; `metier_isco` relie SECO, KOF et BESTA.

**Tous les exemples ci-dessous sont FICTIFS.** Les UID d'exemple ont un format volontairement invalide (`CHE-000.000.00x`) pour éviter toute collision avec une entreprise réelle.

### 6.1 `clients` (entreprises)

| Colonne | Type | Obligatoire | Description | Exemple fictif |
|---|---|---|---|---|
| `client_id` | texte | oui | Identifiant interne stable | `CLI-000123` |
| `raison_sociale` | texte | oui | Nom de l'entreprise | `Bâtisseurs Fictifs SA` |
| `uid` | texte (`CHE-\d{3}\.\d{3}\.\d{3}`) | si connu | UID IDE | `CHE-000.000.001` |
| `noga_code` | texte (6 chiffres) | si connu | Branche NOGA 2008 | `412000` |
| `secteur` | enum (`industrie`, `construction`, `horlogerie`, `logistique`, `pharma`, `autre`) | oui | Secteur Flexsis | `construction` |
| `commune_ofs` | entier | oui | Commune du site principal | `9999` |
| `npa` | texte (4) | oui | NPA du site | `1999` |
| `canton` | texte (2) | oui | Canton | `VS` |
| `agence_flexsis` | texte | oui | Agence responsable | `Agence Exemple-Ville` |
| `statut_relation` | enum (`client_actif`, `client_inactif`, `prospect`) | oui | Statut | `client_actif` |
| `date_premiere_commande` | date | non | Première commande | `2023-03-15` |
| `classe_taille` | enum (`1-9`, `10-49`, `50-249`, `250+`) | non | Effectif (classe) | `50-249` |
| `opposition_prospection` | booléen | oui | L'entreprise refuse d'être démarchée | `false` |

### 6.2 `contacts_entreprise` (fonction seulement)

| Colonne | Type | Obligatoire | Description | Exemple fictif |
|---|---|---|---|---|
| `contact_id` | texte (pseudonyme) | oui | Pseudonyme stable, sans nom | `CTC-7F3A9` |
| `client_id` | texte | oui | Lien vers le client | `CLI-000123` |
| `fonction` | texte normalisé | oui | Fonction (pas de nom) | `Chef de chantier` |
| `service` | enum (`direction`, `rh`, `production`, `chantier`, `logistique`, `achats`) | oui | Service | `chantier` |
| `langue` | enum (`fr`, `de`, `it`, `en`) | oui | Langue de contact | `fr` |
| `canal_prefere` | enum (`telephone`, `email`, `visite`) | non | Canal | `telephone` |
| `telephone_standard` | texte | non | Numéro **professionnel de standard** (pas de mobile privé) | `+41 00 000 00 00` |
| `email_generique` | texte | non | Adresse fonctionnelle (ex. rh@) plutôt que nominative | `rh@exemple-fictif.ch` |
| `date_maj` | date | oui | Dernière vérification | `2026-09-30` |

### 6.3 `commandes_missions`

| Colonne | Type | Obligatoire | Description | Exemple fictif |
|---|---|---|---|---|
| `commande_id` | texte | oui | Identifiant de la demande | `CMD-2026-004512` |
| `client_id` | texte | oui | Client | `CLI-000123` |
| `date_reception` | date | oui | Réception de la demande | `2026-09-01` |
| `origine` | enum (`appel_entrant`, `appel_sortant_radar`, `email`, `visite`, `portail_client`) | oui | Origine, pour mesurer l'effet du radar | `appel_sortant_radar` |
| `signal_id` | texte | non | Alerte PROXSIS à l'origine de l'appel | `SIG-2026-0815` |
| `metier_isco` | texte (4) | oui | Métier demandé | `7112` (maçon) |
| `metier_libelle` | texte | oui | Libellé Flexsis | `Maçon CFC` |
| `nb_postes` | entier | oui | Postes demandés | `3` |
| `taux_activite_pct` | entier | oui | Taux d'activité | `100` |
| `type_contrat` | enum (`temporaire`, `fixe`, `temp_to_fixe`) | oui | Type | `temporaire` |
| `date_debut_souhaitee` | date | oui | Début demandé | `2026-09-15` |
| `date_fin_prevue` | date | non | Fin prévue | `2026-12-18` |
| `commune_mission_ofs` | entier | oui | Lieu de mission | `9999` |
| `statut` | enum (`ouverte`, `pourvue`, `partielle`, `annulee`, `perdue`) | oui | Statut | `pourvue` |
| `nb_postes_pourvus` | entier | oui | Postes pourvus | `2` |
| `date_premier_placement` | date | non | Premier candidat en poste | `2026-09-12` |
| `motif_perte` | enum (`pas_de_candidat`, `concurrent`, `prix`, `annule_client`, `autre`) | non | Si perdue ou partielle | `pas_de_candidat` |
| `heures_facturees` | décimal | non | Total des heures (missions) | `1240.5` |

### 6.4 `candidats` (minimisés, pseudonymisés)

| Colonne | Type | Obligatoire | Description | Exemple fictif |
|---|---|---|---|---|
| `candidat_pid` | texte (pseudonyme) | oui | Pseudonyme stable, sans lien direct avec l'identité | `CAN-9B21E` |
| `metiers_isco` | liste de textes | oui | Métiers exerçables | `["7112","9313"]` |
| `niveau_experience` | enum (`debutant`, `confirme`, `expert`) | oui | Niveau | `confirme` |
| `certifications` | liste de codes internes | non | Certifications utiles à la mission | `["CARISTE","PERMIS_C1"]` |
| `npa_residence` | texte (4) | oui | NPA seulement (pas d'adresse) | `1999` |
| `rayon_mobilite_km` | entier | oui | Distance acceptée | `40` |
| `vehicule` | booléen | non | Dispose d'un véhicule | `true` |
| `langues` | liste ISO 639-1 | oui | Langues de travail | `["fr","de"]` |
| `autorisation_travail_ok` | booléen | oui | Autorisation de travail valable (sans le type de permis) | `true` |
| `statut_disponibilite` | enum (`disponible`, `en_mission`, `indisponible`) | oui | Statut | `en_mission` |
| `date_disponibilite` | date | non | Prochaine disponibilité | `2026-11-02` |
| `date_maj` | date | oui | Dernière mise à jour | `2026-10-01` |

Ne pas inclure : nom, date de naissance, numéro AVS, nationalité, type de permis de séjour, adresse, téléphone, photo, santé, notes libres.

### 6.5 `resultats_appel` (prospection déclenchée par le radar)

| Colonne | Type | Obligatoire | Description | Exemple fictif |
|---|---|---|---|---|
| `appel_id` | texte | oui | Identifiant | `APL-2026-10-0042` |
| `horodatage_utc` | horodatage | oui | Moment de l'appel | `2026-10-02T08:15:00Z` |
| `client_id` | texte | oui | Entreprise appelée | `CLI-000123` |
| `contact_id` | texte (pseudonyme) | non | Contact (fonction) | `CTC-7F3A9` |
| `consultant_pid` | texte (pseudonyme) | oui | Consultant Flexsis | `CONS-11` |
| `signal_id` | texte | non | Alerte PROXSIS appelée | `SIG-2026-0815` |
| `type_signal` | enum (`simap_adjudication`, `fosc_creation`, `permis_construire`, `regbl_pipeline`, `annonce_emploi`, `autre`) | non | Famille de signal | `simap_adjudication` |
| `canal` | enum (`telephone`, `email`, `visite`) | oui | Canal | `telephone` |
| `resultat` | enum (`besoin_confirme`, `besoin_futur`, `pas_de_besoin`, `rappel_demande`, `injoignable`, `refus_prospection`) | oui | Issue | `besoin_futur` |
| `horizon_besoin` | enum (`<2_semaines`, `2-8_semaines`, `>2_mois`, `inconnu`) | non | Horizon | `2-8_semaines` |
| `metiers_isco_mentionnes` | liste de textes | non | Métiers évoqués | `["7112"]` |
| `nb_postes_estimes` | entier | non | Volume évoqué | `4` |
| `commande_id` | texte | non | Commande générée | `CMD-2026-004512` |
| `commentaire` | texte ≤ 280 caractères | non | Contenu factuel, **sans donnée personnelle** | `Démarrage du gros œuvre prévu après les vacances d'automne` |

**Règles de conservation proposées (à valider par le DPO d'Interiman)**

- **Données d'appel détaillées :** 24 mois. Au-delà, ne conserver que des agrégats.
- **Opposition au démarchage :** une réponse `refus_prospection` met à jour `clients.opposition_prospection` et bloque toute nouvelle alerte pour ce client.

## 7. Points ouverts et risques

1. **Licences non établies :**
   - conditions simap.ch et CGU amtsblattportal (non lues) ;
   - extraits RegBL (contradiction) ;
   - jeux OFS en `terms_by_ask` ;
   - OpenHolidays (ODbL ou CC BY) ;
   - TED, Sitadel, planning.data.gov.uk, Open-Meteo, swissstaffing, SBV.
2. **Accès conditionnels :** Job-Room, FAO Vaud, Careerjet, Adzuna et JobCloud demandent un accord écrit ou une clé.
3. **Qualité des données :**
   - erreur de date dans OpenHolidays (§ 2.4) ;
   - 60,6 % des projets simap sans canton (mesure tierce) ;
   - couverture partielle des mandants amtsblattportal (AG, FR, GE, GL, JU, LU, NE, UR) ;
   - étiquette de langue peu fiable dans Job-Room [21].
4. **Délai entre signal et besoin de main-d'œuvre :** toutes les durées citées (adjudication → chantier, permis → chantier) sont des **hypothèses**. Elles se calibrent avec l'historique `commandes_missions` de Flexsis.
5. **Méthode :** 15 recherches WebSearch au lieu de ≥ 30 (quota épuisé). Plusieurs faits reposent sur des clients tiers ou un catalogue tiers, toujours signalés comme « non vérifié ».

## 8. Sources

Toutes consultées le **2026-10-04**. Les dépôts GitHub ont été lus via raw.githubusercontent.com ou l'outil de recherche de code GitHub.

1. swiss-procurement-mcp 0.19.0 (MIT), métadonnées et README, `constants.py` lu localement — https://pypi.org/project/swiss-procurement-mcp/ ; dépôt https://github.com/malkreide/swiss-procurement-mcp
2. Swiss Public Data MCP Portfolio, README — https://raw.githubusercontent.com/malkreide/swiss-public-data-mcp/main/README.md
3. amtsblatt-mcp, README — https://raw.githubusercontent.com/malkreide/amtsblatt-mcp/main/README.md
4. amtsblatt-mcp, classification des rubriques — https://raw.githubusercontent.com/malkreide/amtsblatt-mcp/main/docs/rubric-classification.md
5. amtsblatt-mcp, codes de rubriques (lecture des codes uniquement) — https://raw.githubusercontent.com/malkreide/amtsblatt-mcp/main/src/amtsblatt_mcp/rubrics.py
6. register-mcp, README — https://raw.githubusercontent.com/malkreide/register-mcp/main/README.md
7. register-mcp, sonde réelle amtsblattportal (2026-07-19) — https://raw.githubusercontent.com/malkreide/register-mcp/main/docs/probe-shab.md
8. swiss-housing-mcp, README — https://raw.githubusercontent.com/malkreide/swiss-housing-mcp/main/README.md
9. swiss-housing-mcp, URL d'endpoints et codes GSTAT — https://raw.githubusercontent.com/malkreide/swiss-housing-mcp/main/src/swiss_housing_mcp/gwr.py ; https://raw.githubusercontent.com/malkreide/swiss-housing-mcp/main/src/swiss_housing_mcp/server.py
10. swiss-statistics-mcp, README — https://raw.githubusercontent.com/malkreide/swiss-statistics-mcp/main/README.md
11. seco-labor-mcp, README — https://raw.githubusercontent.com/malkreide/seco-labor-mcp/main/README.md
12. swiss-holidays-mcp, README — https://raw.githubusercontent.com/malkreide/swiss-holidays-mcp/main/README.md
13. meteoswiss-mcp, README — https://raw.githubusercontent.com/malkreide/meteoswiss-mcp/main/README.md
14. swiss-transport-mcp, README — https://raw.githubusercontent.com/malkreide/swiss-transport-mcp/main/README.md
15. swisstopo-mcp, README — https://raw.githubusercontent.com/malkreide/swisstopo-mcp/master/README.md
16. zurich-opendata-mcp, README — https://raw.githubusercontent.com/malkreide/zurich-opendata-mcp/main/README.md
17. i14y-mcp, README — https://raw.githubusercontent.com/malkreide/i14y-mcp/main/README.md
18. (référence retirée)
19. Catalogue tiers « Data catalogue: early warning for staffing demand… » (Dyumes/flexsis, MIT, recherche du 2026-10-03) — https://raw.githubusercontent.com/Dyumes/flexsis/main/data_catalogue/flexsis_data_catalogue_construction_logistics_industry.md
20. claude-job-hunt, fiche Adzuna — https://raw.githubusercontent.com/dominiquevienne/claude-job-hunt/main/shared/boards/adzuna.md
21. claude-job-hunt, fiche Job-Room — https://raw.githubusercontent.com/dominiquevienne/claude-job-hunt/main/shared/boards/job-room.md
22. claude-job-hunt, fiche jobs.ch — https://raw.githubusercontent.com/dominiquevienne/claude-job-hunt/main/shared/boards/jobs-ch.md
23. Careerjet, client Python officiel (README et constantes) — https://raw.githubusercontent.com/careerjet/careerjet-api-client-python/master/README.md ; https://raw.githubusercontent.com/careerjet/careerjet-api-client-python/master/careerjet_api_client/constants.py
24. careerjet-api (PyPI, MIT) — https://pypi.org/project/careerjet-api/
25. MeteoSwiss Open Data, « Download data » — https://raw.githubusercontent.com/MeteoSwiss/opendata/main/docs/general/download.md
26. MeteoSwiss Open Data, « Terms of use » — https://raw.githubusercontent.com/MeteoSwiss/opendata/main/docs/general/terms-of-use.md
27. OpenHolidays API Data, README — https://raw.githubusercontent.com/openpotato/openholidaysapi.data/main/README.md
28. OpenHolidays API Data, LICENSE (ODbL) — https://raw.githubusercontent.com/openpotato/openholidaysapi.data/main/LICENSE
29. OpenHolidays API Data, jours fériés CH — https://raw.githubusercontent.com/openpotato/openholidaysapi.data/main/src/ch/holidays/holidays.public.csv
30. KOF, paquet kofdata (abandonné), README — https://raw.githubusercontent.com/KOF-ch/kofdata/master/README.md
31. KOF, tsdbapi-R, README — https://raw.githubusercontent.com/KOF-ch/tsdbapi-R/main/README.md
32. Index des jeux opendata.swiss (instantané du 2026-02-22) — https://github.com/rnckp/starter-code_opendataswiss. Fichiers `01_r-markdown/` : `c6f940e0-f97f-4aa3-8188-6306325d6ad9.Rmd` (KOF Beschäftigungsindikator), `ea0acb07-73a8-4b25-8247-ceed2586394a.Rmd` (KOF Konjunkturbarometer), `acb228e3-1a73-409b-902e-f0282c5a00e2.Rmd` (Baugesuche ZH), `55b1f3b4-6dff-4a28-812d-8190fe5ac4ec.Rmd` (Zefix ZH), `5bdd1fa6-2d27-4e04-bd97-82265e65494b.Rmd` (Gebäudeprogramm), `dcb9e0b2-3aa8-4739-b665-f4d88f1894ca.Rmd` et `86bd9e64-db3d-4e45-b7a6-8cb6c188ef5e.Rmd` (Baubewilligungen BL), `9c6fca81-548a-4c77-a497-afa8ae7c7da7.Rmd` et `2be419d8-0dc5-4881-8e93-963d5a5cc772.Rmd` (FR), `1d800180-5400-4232-9a11-88b184725472.Rmd` (Schulferien BS, archive IDES)
33. OSRM, wiki « Demo server » — https://raw.githubusercontent.com/wiki/Project-OSRM/osrm-backend/Demo-server.md
34. openrouteservice (PyPI, Apache-2.0) — https://pypi.org/project/openrouteservice/
35. pystatis (PyPI), client GENESIS — https://pypi.org/project/pystatis/
36. Métadonnées Destatis de la statistique 31111, exportées par un tiers — https://github.com/Bildad123/genesis-pipeline (fichier `GENESIS_Export/3_Wohnen, Umwelt/31111_Statistik der Baugenehmigungen/_statistik_31111.json`)
37. Code de table GENESIS 31111-0002 — https://github.com/SchoenTom/ConstructionSite (fichier `src/data_fetchers/destatis.py`, lu, non copié)
38. API DiDo et identifiant du jeu Sitadel — https://github.com/MTES-MCT/aigle-api (fichier `core/management/commands/import_sitadel.py`)
39. planning.data.gov.uk, page de documentation (source du site) — https://github.com/digital-land/digital-land.info (fichier `application/templates/pages/docs.html`)
40. TED Search API v3 — https://github.com/Italian-Builders-Org/DoveVannoINostriSoldi (fichier `docs/TED_NOTICES.md`, qui cite https://docs.ted.europa.eu/api/latest/search.html) ; https://github.com/worldwidelaw/legal-sources (fichier `sources/EU/TED/config.yaml`)
41. Vocabulaire schema.org — https://raw.githubusercontent.com/schemaorg/schemaorg/main/data/schema.ttl
42. Audit tiers des API transport.opendata.ch et opentransportdata.swiss — https://github.com/josh-freeman/hopp (fichier `docs/research/raw/api-audit.json`)
43. Transport API, README — https://raw.githubusercontent.com/OpendataCH/Transport/master/README.md
44. Pipeline tiers SAD Consult (lu pour identifier les champs nominatifs, non copié) — https://github.com/camelote-command-center/data-pipelines (fichier `pipelines/sad/import.py`)
45. Index tiers d'URL (liste SECO des professions soumises à l'obligation d'annonce) — https://github.com/gladiopeace/Files-Indexer (fichier `B/Boites/XLSX_files.csv`)
46. WebSearch, Bulletin officiel du Valais — https://www.vs.ch/en/web/communication/bo
47. WebSearch, exemple de publications HR01/HR02/HR03 — https://www.plattformj.ch/artikel/214984/
48. WebSearch, Zefix PublicREST (Basic Auth, zefix@bj.admin.ch, endpoints) — https://opendata.swiss/en/dataset/zefix-zentraler-firmenindex ; https://github.com/validitylabs/zefix ; https://glama.ai/mcp/servers/f5f5i4sng0
49. WebSearch, interfaces du registre IDE — https://www.bfs.admin.ch/bfs/en/home/register/unternehmensregister/unternehmens-identifikationsnummer/uid-register/uid-schnittstellen.html
50. WebSearch, conditions et fair use de geo.admin.ch — https://api.geo.admin.ch/api/faq/index.html ; https://www.geo.admin.ch/en/general-terms-of-use-fsdi ; https://geo.admin.ch/en/change-limits-fair-use
51. WebSearch, accès des tiers aux données RegBL — https://ech.ch/sites/default/files/dosvers/hauptdokument/STAN_f_REP_2019-08-15_eCH-0206_V1.0_Donne%20es%20du%20RegBL%20a%20tiers.pdf ; https://www.newsd.admin.ch/newsd/message/attachments/70511.pdf
52. WebSearch, simap.ch (mise en service le 2024-07-01) — https://en.wikipedia.org/wiki/Simap.ch
53. WebSearch, intégration de l'API simap (paramètres de date) — https://deepwiki.com/Digilac/simap-mcp/5-simap.ch-api-integration
54. WebSearch, plateforme Amtsblatt du SECO (guides cantonaux) — https://so.ch/services/amtsblatt-abrufen-fuer-die-leserschaft/ ; https://www.sz.ch/public/upload/assets/90253/Digitales_Amtsblatt_Benutzeranleitung_fuer_publizierende_Stellen.pdf
55. WebSearch, catalogue des caractères RegBL (référence pour les codes GSTAT) — https://www.rsta.dij.be.ch/content/dam/rsta_dij/dokumente/de/themen/geb%c3%a4ude--und-wohnungsregister-(gwr)/RSTA_GWR_Merkbatt%20Geometer_de.pdf

## Annexe A — Résultats bruts des tests curl du 2026-10-04

Code `000` : aucun échange HTTP avec le serveur cible. Le proxy de l'environnement a refusé le tunnel CONNECT (réponse 403 du proxy).

Re-test du 2026-10-05 (UTC) par `curl -s -o /dev/null -w '%{http_code}' --max-time 15 <url>` depuis l'environnement de développement, un appel par hôte :

| Hôte | URL testée | Code HTTP | Sources du catalogue |
|---|---|---|---|
| amtsblattportal.ch | https://amtsblattportal.ch/api/v1/publications?publicationStates=PUBLISHED&rubrics=HR | 000 | amtsblatt_fosc_hr, amtsblatt_rubriques_personnes_exclues, amtsblatt_fosc_up, amtsblatt_vs_permis_construire, amtsblatt_vs_grands_projets, amtsblatt_marches_hors_simap, amtsblatt_vs_emplois_publics, amtsblatt_permis_autres_cantons, amtsblatt_amenagement |
| api.adzuna.com | https://api.adzuna.com/v1/api/jobs/ch/search/1?app_id={id}&app_key={key}&what=&where= | 000 | adzuna_api |
| api.i14y.admin.ch | https://api.i14y.admin.ch/api/public/v1/catalog/datasets | 000 | i14y_catalogue |
| api.job-room.ch | https://api.job-room.ch/jobadservice/api/jobAdvertisements/_search | 000 | jobroom_api |
| api.open-meteo.com | https://api.open-meteo.com/v1/forecast | 000 | open_meteo_previsions |
| api.openrouteservice.org | https://api.openrouteservice.org/ | 000 | openrouteservice |
| api.opentransportdata.swiss | https://api.opentransportdata.swiss/ojp20 | 000 | ojp_opentransportdata |
| api.ted.europa.eu | https://api.ted.europa.eu/v3/notices/search | 000 | eu_ted |
| api3.geo.admin.ch | https://api3.geo.admin.ch/rest/services/api/MapServer/find?layer=ch.bfs.gebaeude_wohnungs_register&searchField=egid&searchText={EGID}&returnGeometry=true&sr=2056 | 000 | regbl_geoadmin_api, swisstopo_geocodage |
| app2.ge.ch | https://app2.ge.ch/sadconsult | 000 | ge_sad_consult |
| baumeister.swiss | https://baumeister.swiss/baumeister-5-0/konjunktur-statistiken/baukonjunktur/ | 000 | sbv_baukonjunktur |
| ckan.opendata.swiss | https://ckan.opendata.swiss/api/3/action/package_search?q=baugesuch | 000 | opendata_swiss_ckan |
| data.bl.ch | https://data.bl.ch/api/v2/catalog/datasets/12880/exports/csv?use_labels=true | 000 | bl_baubewilligungen |
| data.geo.admin.ch | https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn | 000 | meteosuisse_ogd |
| data.stadt-zuerich.ch | https://data.stadt-zuerich.ch/api/3/action/package_search?q=baugesuch | 000 | stadt_zh_ckan |
| data.statistiques.developpement-durable.gouv.fr | https://data.statistiques.developpement-durable.gouv.fr/dido/api/v1/datafiles | 000 | fr_sitadel_dido |
| date.nager.at | https://date.nager.at/api/v3/PublicHolidays/2026/CH | 000 | nager_date_feries |
| daten.statistik.zh.ch | https://daten.statistik.zh.ch/ogd/daten/ressourcen/KTZH_00002982_00006183.csv | 000 | zh_baugesuche_ogd |
| datenservice.kof.ethz.ch | https://datenservice.kof.ethz.ch/api/v1/public/collections/ogd_ch.kof.ie?mime=csv | 000 | kof_datenservice |
| edudoc.ch | https://edudoc.ch/search?cc=idesferienliste&ln=de&c=idesferienliste | 000 | edk_vacances_scolaires |
| kof.ethz.ch | https://kof.ethz.ch/ | 000 | kof_enquetes_construction |
| opendata.fr.ch | https://opendata.fr.ch/api/explore/v2.1/catalog/datasets/03_03_places_vacantes_annoncees_mensuelles/exports/csv?use_labels=true | 000 | cantons_marche_travail_ogd |
| opendata.swiss | https://opendata.swiss/api/3/action/package_search?q=T3.3.0.1 | 000 | seco_opendata_series |
| openholidaysapi.org | https://openholidaysapi.org/PublicHolidays?countryIsoCode=CH&languageIsoCode=FR&validFrom=2026-01-01&validTo=2026-12-31 | 000 | openholidays_feries_vacances |
| openplzapi.org | https://openplzapi.org/ch/Localities?name=Sion | 000 | openplz_api |
| public.api.careerjet.net | http://public.api.careerjet.net/search | 403 | careerjet_api |
| public.madd.bfs.admin.ch | https://public.madd.bfs.admin.ch/{canton}.zip | 000 | regbl_madd_dump |
| router.project-osrm.org | https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2} | 000 | osrm_routage |
| schema.org | https://schema.org/JobPosting | 000 | pages_carrieres_jobposting |
| sitg.ge.ch | https://sitg.ge.ch/donnees/sit-autor-dossier | 000 | ge_sitg_autorisations |
| transport.opendata.ch | https://transport.opendata.ch/v1/connections?from=Lausanne&to=Sion&limit=1 | 000 | transport_opendata_ch |
| tsdb-api.kof.ethz.ch | https://tsdb-api.kof.ethz.ch/v2/ts?keys=ch.kof.jobtracker.total.total.clean.idx&mime=csv&access_type=public | 000 | kof_tsdb_job_tracker |
| www-genesis.destatis.de | https://www-genesis.destatis.de/genesisWS/rest/2020/ | 000 | de_destatis_genesis |
| www.agvchapp.bfs.admin.ch | https://www.agvchapp.bfs.admin.ch/de/home | 000 | ofs_agvch_communes |
| www.amstat.ch | https://www.amstat.ch/v2/amstat_fr.html | 000 | seco_amstat |
| www.arbeit.swiss | https://www.arbeit.swiss/secoalv/de/home/menue/unternehmen/stellenmeldepflicht.html | 000 | seco_obligation_annonce |
| www.ave-wbv.ch | https://www.ave-wbv.ch/files/CIRCULAIRE2026-FR.pdf | 000 | conges_batiment_cn |
| www.baublatt.ch | https://www.baublatt.ch/ | 000 | baublatt_docu |
| www.faovd.ch | https://www.faovd.ch/permis-de-construire/district/lausanne/ | 000 | vd_fao_camac |
| www.fr.ch | https://www.fr.ch/ | 000 | fr_permis_construire |
| www.jobs.ch | https://www.jobs.ch/ | 000 | jobcloud_jobs_ch_jobup |
| www.planning.data.gov.uk | https://www.planning.data.gov.uk/entity.json?dataset=planning-application&limit=100&offset=0 | 000 | uk_planning_data |
| www.pxweb.bfs.admin.ch | https://www.pxweb.bfs.admin.ch/api/v1/{fr|de|it|en}/{table}/{table}.px | 000 | ofs_pxweb_api, ofs_construction, ofs_besta, ofs_statent, ofs_hesta |
| www.simap.ch | https://www.simap.ch/api/publications/v2/project/project-search | 000 | simap_appels_offres, simap_adjudications, simap_referentiels |
| www.swissstaffing.ch | https://www.swissstaffing.ch/ | 000 | swissstaffing_index |
| www.uid-wse.admin.ch | https://www.uid-wse.admin.ch/V5.0/PublicServices.svc | 000 | uid_register_ide |
| www.uvek-gis.admin.ch | https://www.uvek-gis.admin.ch/BFE/ogd/18/ogd18_gebaeudeprogramm_auszahlungen.csv | 000 | gebaeudeprogramm_stats |
| www.web.statistik.zh.ch | https://www.web.statistik.zh.ch/ogd/data/KANTON_ZUERICH_ZEFIX_Neugruendungen.csv | 000 | zh_zefix_neugruendungen |
| www.x28.ch | https://www.x28.ch/ | 000 | x28_donnees_emploi |
| www.zefix.admin.ch | https://www.zefix.admin.ch/ZefixPublicREST/api/v1 | 000 | zefix_publicrest, zefix_rest_site_web |

Les résultats détaillés du 2026-10-04 (heure, commande, code) sont repris par source dans la colonne `test_reel_2026_10_04` de `data/catalogue.csv`. Ajout de l'annexe par l'agent principal le 2026-10-05 (l'agent de recherche a été interrompu par une limite d'utilisation avant de la compléter).

