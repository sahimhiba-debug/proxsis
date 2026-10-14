# Fournisseurs étrangers de données chantiers et de demande de travail

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

- **Date de consultation de toutes les sources : 2026-10-04.**
- Auteur : agent de recherche (Claude Code), pour l'équipe Proxsis.
- But : voir comment d'autres pays vendent ou ouvrent les données de chantiers,
  de marchés publics et de demande de travail, et en tirer des **idées
  réutilisables** pour Proxsis (Suisse romande et alémanique).

## Méthode, limites et légende

Mêmes contraintes que `docs/recherche/marche.md` : les sites des éditeurs et
des administrations étaient bloqués depuis l'environnement (`EGRESS_BLOCKED`,
testé le 2026-10-04 sur construction.com, glenigan.com, planit.org.uk,
boamp.fr, data.gouv.fr, bls.gov, cedefop.europa.eu, oecd.org, ibau.de,
dtad.com, byggfakta.se, doffin.no, hankintailmoitukset.fi, destatis.de…).
Les faits viennent donc surtout des **extraits du moteur de recherche**. Le
quota de recherche web de la session s'est épuisé en cours de travail : pour
l'Allemagne, les pays nordiques et les organismes publics de mesure, nous
avons complété avec des **README de projets open source lus directement**
sur GitHub, PyPI et npm (seuls domaines accessibles). Ce qui n'a pas pu être
vérifié est écrit « inconnu » ou « non vérifié ».

| Code | Signification |
|---|---|
| **V** | Affirmé par le vendeur / l'éditeur. |
| **T** | Source tierce (presse, comparatif, agrégateur, concurrent). |
| **E** | Extrait de recherche, page non consultée. |
| **M** | Mesuré / vérifié indépendamment par nous le 2026-10-04 (fichier lu directement). |
| **OS** | Attesté par un projet open source tiers (README lu directement) ; pas une confirmation officielle. |

---

## 1. États-Unis

| Fournisseur | Ce qu'il fait, couverture | Modèle économique et prix | API | Résultats / études publiés | Idée réutilisable pour Proxsis | Source |
|---|---|---|---|---|---|---|
| **Dodge Construction Network** | Données de projets de construction commerciale en Amérique du Nord, suivis « du pré-projet et de la conception jusqu'au permis et au début des travaux », « 700 000+ projets par an » ; produits Dodge One, The Blue Book, Dodge Reports ; base mensuelle des **mises en chantier depuis 1967** (national, État, aire métropolitaine) (E·V). | Abonnement ; **prix non public** (E). | Oui : API REST (projets, contacts d'entreprises, documents de conception), synchronisation en temps réel au lieu de fichiers XML quotidiens (E·V). | Prévisions et statistiques de mises en chantier (E·V) ; pas de mesure indépendante trouvée. | **Suivre le stade du projet** (pré-projet → permis → début des travaux) : chaque stade donne une fenêtre de besoin en personnel différente. | [I1](https://www.construction.com/what-is-dodge-construction-network-the-dodge-report-explained/), [I1b](https://www.construction.com/apis/) |
| **ConstructConnect** (+ **BidClerk**) | Base de projets commerciaux issue de la fusion de **BidClerk, CMD Group, Reed Construction Data, Construction Journal et iSqFt** (E·V). BidClerk subsiste comme plateforme de recherche de projets (E·T). | Abonnement ; prix non confirmé publiquement (E·T). Une page « pricing » existe (contenu non consulté). | Inconnu. | Inconnu. | **Fusionner plusieurs sources en une fiche projet unique** (dédoublonnage) : même problème que simap + feuilles officielles + presse. | [I2](https://www.constructconnect.com/industry-trusted-preconstruction-software), [I2b](https://constructionbids.ai/blog/bidclerk-vs-constructconnect-comparison-2026) |
| **Construction Monitor** | Permis de construire (résidentiel, commercial, solaire) dans « 70+ aires métropolitaines », « ~17 millions de permis » ; publication **hebdomadaire** ; moteur de recherche, carte par permis (E·V/T). Distribué aussi sur la place de marché de données de Dun & Bradstreet (E). | Abonnement 1, 6 ou 12 mois, **prix selon la population et le nombre de permis** ; exemple Los Angeles : 96 $/mois, 540 $/6 mois, 960 $/an (E·T, article JLC, date de l'article inconnue). | Inconnu. | Inconnu. | **Prix par zone géographique** et cadence hebdomadaire : modèle simple pour vendre par agence ou par canton. | [I3](https://www.jlconline.com/business/sales-marketing/pulled-permits-as-a-source-of-leads/), [I3b](https://www.constructionmonitor.com/assets/pdf/construction-monitor-brochure.pdf), [I3c](https://www.dnb.com/marketplace/data/construction-monitor.html) |
| **BuildZoom** | Place de marché qui relie propriétaires et entrepreneurs (fondée en 2013) ; agrège licences, permis et registres publics : « 400 autorités de licence, 1 500 services des permis, 160 M de permis, 5,5 M de licences rapprochées de 3,5 M d'entités et 55 M de parcelles » (E·V, chiffres d'une interview YC, date inconnue). Division données : « 350 M+ permis sur 25+ ans » (E·V). | Gratuit pour le propriétaire ; **commission de 2,5 %** sur les chantiers gagnés par l'entrepreneur (E·T) ; offre de données séparée, prix non public. Financement total 23,7 M$ (E·T). | Inconnu (offre « data » sans détail). | Inconnu. | **Le cœur de la valeur est le rapprochement permis ↔ entreprise** (résolution d'entités). Pour nous : rattacher chaque permis et chaque adjudication à un IDE/UID. | [I4](https://www.ycombinator.com/blog/qa-with-jiyan-wei-and-david-petersen-cofounders-of-buildzoom/), [I4b](https://www.buildzoomdata.com), [I4c](https://cherre.com/vendors/buildzoom/) |
| **Shovels.ai** | Données publiques nettoyées et enrichies : permis, entrepreneurs, propriétés, décisions locales (E·T). Mi-2026 : « 178 M+ permis, 2 770+ juridictions, ~85 % de la population US, ~3,65 M de profils d'entrepreneurs » (E·T). L'API v2 couvre « 1 800+ juridictions » (E ; même chiffre dans la description d'un paquet npm tiers, OS). | Abonnements Online et API, crédits à l'usage, licences de données entreprise livrées via Snowflake, Databricks ou BigQuery ; **prix non publics** (E·T). | Oui (API v2) (E, OS). | Inconnu. | **Mesurer et afficher la couverture en % de population** ; interface en langage naturel (« Charlie AI ») ; segments d'audience. Pour nous : couverture par canton et par langue. | [I5](https://sacra.com/c/shovels/), [I5b](https://thegtmdirectory.com/tools/shovels), [I5c](https://www.npmjs.com/package/n8n-nodes-shovels) |

---

## 2. Royaume-Uni

| Fournisseur | Ce qu'il fait, couverture | Modèle et prix | API | Résultats / études | Idée réutilisable | Source |
|---|---|---|---|---|---|---|
| **Glenigan** | Leads de projets, données, analyses, **prévisions** et informations d'entreprises pour la construction au Royaume-Uni et en Irlande ; projets « y compris hors du processus de planification » grâce à des partenariats exclusifs ; « la plus grande équipe de recherche du secteur, plus d'un million d'appels téléphoniques par an » (E·V). | Abonnement sur mesure ; **prix non public** (E). | Inconnu (rien trouvé). | Prévisions sectorielles (E·V). | **Vérification humaine** des projets par téléphone : chez nous, le « retour d'appel en un clic » des consultants joue ce rôle et doit alimenter la qualité des signaux. | [I6](https://www.glenigan.com/about-us/), [I6b](https://www.theconstructionindex.co.uk/news/view/why-use-glenigan) |
| **Builder's Conference** | Existe : **partenariat exclusif avec Glenigan** (titre d'une page Glenigan) (E·V). Activité exacte : inconnue. | Inconnu. | Inconnu. | Inconnu. | Les partenariats donnent accès à des projets **avant** la demande de permis. | [I6c](https://www.glenigan.com/exclusive-builders-conference-partnership-delivers-significant-value-to-glenigan-customers/) |
| **Barbour ABI** | Leads de construction pour tout le Royaume-Uni, avec coordonnées de décideurs « conformes au RGPD » ; modèle d'abonnement ; 140 employés (Cheshire Oaks) ; **racheté par Infopro Digital** (E·V). Vendu aussi sur la place de marché Datarade (E). | Abonnement ; **prix non public** (E). | Inconnu. | Inconnu. | Les contacts de décideurs sont la partie la plus sensible juridiquement : Proxsis s'en tient aux **entreprises** et aux fonctions, jamais aux particuliers (nLPD). | [I7](https://www.infopro-digital.com/news/acquisition-of-the-british-company-barbour-abi-construction-sales-leads-intelligence-monitoring-market-england), [I7b](https://datarade.ai/data-products/barbour-abi-construction-project-leads-barbour-abi) |
| **PlanIt** (planit.org.uk) | Agrégateur national des demandes de permis (planning applications) actuelles et historiques, à partir des portails des conseils locaux (E·T). Sert de source à plusieurs API commerciales (E·T). | Inconnu. | **Inconnu** (non confirmé par les extraits). | Inconnu. | **Agréger des portails locaux hétérogènes** : c'est notre situation avec les feuilles officielles cantonales et communales. | [I8](https://data.opensite.energy/organization/uk-planit), [I8b](https://searchland.co.uk/our-apis/planning-aplication-api-new) |
| **planning.data.gov.uk** (officiel, Angleterre) | Plateforme publique de données d'urbanisme : carte, téléchargement en masse, API ; licence **Open Government Licence v3** (E·V). Le jeu « planning application » est déclaré **« incomplet, pas encore prêt à l'emploi »** : 100 627 demandes venant de 6 fournisseurs, données au 17 septembre 2025 (E·V). | Gratuit. | Oui, sans clé (E·T). | — | **Afficher honnêtement l'état de chaque jeu de données** (complet / partiel / pas prêt) : à reprendre dans notre catalogue de sources. | [I9](https://www.planning.data.gov.uk/dataset/planning-application), [I9b](https://planning.data.gov.uk/) |
| **HM Land Registry — Price Paid Data** | Transactions immobilières (date, adresse, prix, résidentiel/commercial, type, **neuf ou non**, propriété/bail) ; mise à jour **mensuelle** (E·V). | **Gratuit**, Open Government Licence, usage commercial permis (E·V). | Téléchargement CSV et données liées (E·V). | — | La vente d'un logement **neuf** est un signal **tardif** de fin de chantier : utile pour valider un modèle, pas pour prospecter tôt. | [I10](https://use-land-property-data.service.gov.uk/) |

---

## 3. France

| Fournisseur | Ce qu'il fait, couverture | Modèle et prix | API | Résultats / études | Idée réutilisable | Source |
|---|---|---|---|---|---|---|
| **Vecteur Plus** | Détecte des projets de construction privés « bien avant les annonces officielles », marché français uniquement ; revendique « 5 M+ opportunités » en croisant **BOAMP, JOUE, 400 titres de presse, 12 000 sites web et Sitadel** (E·T, comparatif d'un concurrent citant l'éditeur). | Abonnement ; **prix non public** ; démonstration ou essai gratuit limité à 3 marchés (E·T). | Inconnu. | Inconnu. | **Fusion multi-sources** (marchés publics + permis + presse + sites web) : c'est exactement l'idée de Proxsis, appliquée à la vente B2B. | [I11](https://jorpex.com/fr/compare/vecteur-plus-alternative/) |
| **Explore** (explore.fr) | Outil pour promoteurs, aménageurs et bailleurs sociaux : repérer projets et opportunités de construction, analyser le contexte urbain, économique et commercial (E ; attribution de l'extrait à une page précise incertaine). Cité comme alternative à Vecteur Plus (E·T). | Prix non public (rien trouvé). | Inconnu. | Inconnu. | Ajouter un **contexte territorial** (commune, dynamique locale) à la fiche entreprise. | [I12](https://www.salonsimi.com/app/cache/flux_leni_medias/SIMI25/pdf-a4043915-27ab-f011-a8d8-005056ac7c95.pdf), [I11](https://jorpex.com/fr/compare/vecteur-plus-alternative/) |
| **Sitadel** (SDES, ministère) | Base des autorisations d'urbanisme : permis de construire (PC), d'aménager (PA), déclarations préalables (DP) ; transmission **mensuelle** au SDES (E·V). Les autorisations sont transmises **dans les 6 mois** suivant la décision ; les déclarations d'ouverture et d'achèvement de chantier arrivent généralement **dans les 18 mois** (E·V). Jeu public sur data.gouv.fr, fichiers « logements », « locaux », « aménager », « démolir » (OS). Réutilisation : basedespermis.fr (E). | **Gratuit** (open data). | Téléchargement CSV via data.gouv.fr / DiDo (OS). | En avril 2026, le SDES a modifié le fichier « locaux » (colonnes supprimées, artisanat fusionné rétroactivement dans le commerce) ; un traitement tiers est resté **figé cinq mois sans alerte** (OS). Sitadel ne fournit pas le préfixe cadastral : un géocodage permet de retrouver 97 % des parcelles contre 87 % par reconstruction naïve (mesure du projet tiers sur 1 500 lignes de l'Ain, août 2026, OS). | (1) Le **décalage entre la décision et sa publication** (jusqu'à 6 mois) illustre pourquoi Proxsis distingue `event_date` et `available_at`. (2) **Contrôle de dérive de schéma** à chaque ingestion. (3) Géocoder pour rapprocher les adresses. | [I13](https://www.statistiques.developpement-durable.gouv.fr/la-base-de-donnees-sitadel-methodologie), [I13b](https://github.com/data-fair/processing-sitadel), [I13c](https://www.data.gouv.fr/reuses/basedespermis-fr) |
| **BOAMP** (DILA) | Avis de marchés publics (appels d'offres, MAPA, **avis d'attribution**) de l'État, des collectivités et de leurs établissements (E·V). Formulaires européens « eForms » depuis le 31 janvier 2024 (E). | **Gratuit**, réutilisation sous **Licence Ouverte 2.0** (E). | Oui : API par critères, sortie CSV, JSON ou Excel, données disponibles le jour de publication, **deux fois par jour, 7 jours sur 7** (E·V). | — | Cadence **biquotidienne** et avis d'attribution séparés : modèle pour l'ingestion simap. | [I14](https://www.data.gouv.fr/datasets/boamp), [I14b](https://huggingface.co/datasets/french-open-data/api-boamp/blob/main/README.md) |
| **DECP** (données essentielles de la commande publique) | Données des **marchés attribués**. L'agrégation officielle (dépôt `139bercy/decp-rama`) publie sur data.gouv.fr des fichiers JSON, XML et **OCDS**, plus un fichier quotidien des nouveaux marchés (OS). Un projet indépendant (`decp-processing`) consolide chaque matin de semaine et publie en Parquet, CSV et SQLite ; il juge la documentation officielle « incomplète et éparpillée » et le schéma « DECP 2 » complexe ; son site decp.info a été renommé **colibre** en 2026 (OS). | **Gratuit**. | Fichiers sur data.gouv.fr (OS). | — | **Standard OCDS** pour les adjudications et **fichier « delta » quotidien** : à reprendre pour notre table `marche_attribue`. | [I15](https://github.com/ColinMaudry/decp-processing), [I15b](https://github.com/139bercy/decp-rama), [I15c](https://github.com/ColinMaudry/decp.info) |
| **Batiactu** | **Non vérifié** (recherche impossible après épuisement du quota). | Inconnu. | Inconnu. | Inconnu. | — | — |

---

## 4. Allemagne et Union européenne

| Fournisseur | Ce qu'il fait, couverture | Modèle et prix | API | Résultats / études | Idée réutilisable | Source |
|---|---|---|---|---|---|---|
| **ibau** | Existe : page « ibau Partnernetzwerk : erfolgreich in ganz Europa » (E) ; offre d'emploi d'Ibau GmbH pour « Mitarbeiter Recherche – Bauprojekte & Vergaben (Telefon/Online) » (E), ce qui indique une **recherche humaine** des projets et des marchés. | Abonnement probable ; **prix non public** / inconnu. | Inconnu. | Inconnu. | Même leçon que Glenigan : une couche de vérification humaine. | [I16](https://www.ibau.de/ueber-ibau/partner/), [I16b](https://arbeitsagentur.de/jobsuche/jobdetail/10001-1003763568-S) |
| **Bekanntmachungsservice** (oeffentlichevergabe.de, fédéral) | Flux open data des avis de marchés publics allemands au format **OCDS, licence CC0** (OS). **Le titulaire et le montant ne sont publiés que sur une petite minorité des avis** ; sous les seuils, le montant est souvent omis (OS). | **Gratuit**. | Oui (flux open data) (OS). | — | **Mesurer le taux d'avis d'attribution qui nomment le titulaire** sur simap avant de promettre un signal « adjudication » solide. | [I17](https://github.com/pipeworx-io/mcp-germany-tenders) |
| **service.bund.de** | Flux RSS des appels d'offres fédéraux, utilisé par un agrégateur tiers qui relie 17 sources (Allemagne, UE, Royaume-Uni) (OS). | Gratuit. | RSS (OS). | — | Les flux RSS officiels suffisent souvent pour un premier connecteur. | [I18](https://github.com/shufflethis/ausschreibungsagenten) |
| **TED** (Tenders Electronic Daily, UE) | L'Office des publications de l'UE publie les avis TED en **données liées ouvertes** ; outil d'exploration et éditeur **SPARQL** sur data.ted.europa.eu (OS, dépôt de l'Office). Une API `api.ted.europa.eu` est utilisée par l'agrégateur cité plus haut (OS). Présence des avis suisses sur TED : **inconnue**. | **Gratuit**. | Oui (SPARQL, API) (OS). | — | Modèle de données ouvert et **formulaires eForms** : utile si des entreprises frontalières (France, Allemagne) emploient en Suisse. | [I19](https://github.com/OP-TED/ted-open-data), [I18](https://github.com/shufflethis/ausschreibungsagenten) |
| **Destatis — GENESIS-Online** | Statistiques officielles allemandes (dont la base régionale « Regionaldatenbank ») ; service web/API **réservé aux utilisateurs enregistrés** (identifiant et mot de passe ; jeton possible pour la base Zensus) (OS). La table exacte des **permis de construire (Baugenehmigungen)** n'a pas été vérifiée : **inconnu**. | **Gratuit** (inscription). | Oui (OS). | — | Statistiques officielles de permis comme **contexte macro régional**, à côté des signaux par entreprise. | [I20](https://github.com/CorrelAid/pystatis) |
| **DTAD**, **Baudata** | **Non vérifiés** (quota de recherche épuisé ; domaines bloqués). | Inconnu. | Inconnu. | Inconnu. | — | — |

---

## 5. Pays nordiques

| Fournisseur | Ce qu'il fait, couverture | Modèle et prix | API | Résultats / études | Idée réutilisable | Source |
|---|---|---|---|---|---|---|
| **Doffin** (Norvège, agence DFØ / anskaffelser.no) | Base officielle des marchés publics norvégiens, « nativement eForms », avec des formulaires nationaux sous les seuils (V, dépôt GitHub de l'agence). | **Gratuit** (inscription). | **Deux API** : « Public API » pour chercher et télécharger les avis (clé d'abonnement via un portail Azure API Management) ; « Notices API » pour les éditeurs d'outils qui publient des avis (activation par DFØ) (V, dépôt de l'agence ; OS pour les clients tiers). | — | Séparer clairement **lecture publique** et **écriture** ; documenter l'API sur GitHub. | [I21](https://github.com/anskaffelser/eforms-sdk-nor/blob/main/docs/doffin-api.md), [I21b](https://github.com/reidar80/DoffinMCP) |
| **Hilma** (Finlande, hankintailmoitukset.fi) | Avis de marchés publics finlandais (OS). | **Gratuit** : clé obtenue sur le portail Azure API Management de Hilma ; le produit « avp-read » inclut la Read API (eForms) (OS). | Oui (OS). | — | Même modèle que Doffin : portail d'API avec clé gratuite. | [I22](https://github.com/Aimiten/hilma-mcp) |
| **Byggfakta** (Byggfakta Group), **Visma Opic** | **Non vérifiés** (quota épuisé ; domaine byggfakta.se bloqué ; aucun paquet open source trouvé). | Inconnu. | Inconnu. | Inconnu. | — | — |

---

## 6. Mesure de la demande de travail

| Acteur | Ce qu'il mesure | Modèle et prix | Accès | Résultats / études | Idée réutilisable | Source |
|---|---|---|---|---|---|---|
| **Indeed Hiring Lab** | Indice **quotidien** des offres sur Indeed, base 100 au 1er février 2020, moyenne mobile sur 7 jours, corrigé des variations saisonnières avec la méthode de la Bundesbank pour séries quotidiennes (adoptée en novembre 2024), rafraîchi chaque semaine ; séries nationales, par secteur, et régionales pour US, CA, GB, AU, **DE (Länder)**, **FR (régions)**, IE (M). Pays présents : US, GB, DE, FR, IT, NL, ES, IE, CA, AU ; **absents : CH**, AT, JP, SE, BE, PL (M, test des fichiers le 2026-10-04). Dernière date : 2026-09-25 (M). | **Gratuit**, licence **CC BY 4.0** (M). | CSV sur GitHub ; aussi sur FRED (E). | Indeed déclare des partenariats de recherche avec le FMI, la BCE et la Banque du Canada (V, README). | **Méthode d'indice ouverte et reproductible** (base 100, désaisonnalisation, licence ouverte) : modèle pour un futur « indice Proxsis » par canton. | [I23](https://github.com/hiring-lab/job_postings_tracker), [I23b](https://fred.stlouisfed.org/data/IHLIDXDE) |
| **LinkUp** | Offres indexées chaque jour **directement sur les sites d'employeurs** (« 60 000 entreprises », date du chiffre inconnue) ; prévision des créations d'emplois US (NFP) et de JOLTS à partir des **nouvelles offres et des offres retirées** (une offre retirée sert de proxy d'embauche) (E·V). Des étudiants de l'Université du Minnesota auraient trouvé une forte corrélation avec les statistiques fédérales (E·V). | Prix non public. | Inconnu. | Prévisions mensuelles publiées sur leur blog (E·V). | (1) Sites d'employeurs seulement = moins de doublons. (2) **« Offre retirée » comme cible alternative** (proxy de recrutement réalisé). | [I24](https://www.linkup.com/use-cases/correlation-between-linkup-data-and-the-bls-reports), [I24b](https://www.linkup.com/insights/blog/linkups-job-market-data-foretold-solid-jobs-report-for-october) |
| **Lightcast** | Offres d'emploi, taxonomies de compétences et de métiers, API (Job Postings API OAuth 2.0, 5 requêtes/s) (E·T). Un paquet npm tiers décrit un serveur en lecture seule pour les API de taxonomie de compétences, d'extraction de compétences et de classification de métiers (OS). | **Prix non public** ; cinq à six chiffres par an selon des acheteurs (E·T). | Oui (E·T, OS). | Inconnu. | **Taxonomie de compétences** pour la proximité candidats ↔ métiers (écran « Candidats suggérés ») ; à comparer à CH-ISCO-19. | [I25](https://jobspipe.dev/blog/lightcast-pricing), [I25b](https://www.npmjs.com/package/@hackspaces/lightcast-connect-mcp) |
| **Revelio Labs** | Profils publics + offres (« 350 000 sites d'entreprises », job boards, sites d'agences) ; statistiques publiques « RPLS » ; « Revelio Terminal » (juillet 2026) (E·V). | Prix non public. | Jeux de données documentés (E). | RPLS (E·V). | Statistiques alternatives construites sur des données privées : à suivre, pas à acheter pour un pilote. | [I26](https://www.reveliolabs.com/news/rpls/), [I26b](https://www.reveliolabs.com/data) |
| **BLS JOLTS** (États-Unis, officiel) | Enquête officielle sur les postes vacants et la rotation de la main-d'œuvre ; accessible par l'**API publique v2 du BLS** (OS). Taille d'échantillon et délai de publication : **inconnus** (pages BLS bloquées). LinkUp publie des prévisions de JOLTS (E·V). | **Gratuit** : clé gratuite = 500 requêtes/jour, 25/jour sans clé (OS). | API v2 (OS). | — | **Référence officielle pour calibrer** un indicateur privé ; en Suisse, l'équivalent officiel est à identifier dans `docs/recherche/donnees.md`. | [I27](https://github.com/cyanheads/bls-labor-mcp-server) |
| **OCDE** (travaux sur les offres en ligne), **Eurostat / Cedefop** (Skills-OVATE), **Burning Glass Institute** | **Non vérifiés** dans cette session (domaines bloqués, quota épuisé). | Inconnu. | Inconnu. | Inconnu. | — | — |

---

## 7. Idées réutilisables, par ordre de priorité

| # | Idée | Vue chez | Application dans Proxsis | Source |
|---|---|---|---|---|
| 1 | Rattacher chaque permis / adjudication à une **entité entreprise** | BuildZoom, Shovels | Résolution d'entités sur l'IDE/UID ; c'est l'actif principal, avant tout modèle. | [I4](https://www.ycombinator.com/blog/qa-with-jiyan-wei-and-david-petersen-cofounders-of-buildzoom/), [I5](https://sacra.com/c/shovels/) |
| 2 | **Stade du projet** → fenêtre de besoin | Dodge | Mise à l'enquête, permis, adjudication, début de chantier = fenêtres de besoin différentes par métier. | [I1](https://www.construction.com/what-is-dodge-construction-network-the-dodge-report-explained/) |
| 3 | **Décalage événement / publication** | Sitadel (jusqu'à 6 mois, 18 mois pour les chantiers) | Confirme la règle `available_at <= T` du backtest ; mesurer ce délai pour chaque source suisse. | [I13](https://www.statistiques.developpement-durable.gouv.fr/la-base-de-donnees-sitadel-methodologie) |
| 4 | **Contrôle de dérive de schéma et de fraîcheur** | Incident Sitadel 2026 (5 mois figé sans alerte) | Tests de contrat par connecteur + alerte si une source n'a rien livré depuis N jours. | [I13b](https://github.com/data-fair/processing-sitadel) |
| 5 | **Taux de divulgation du titulaire** | Allemagne (OCDS, minorité d'avis avec titulaire) | Mesurer sur simap la part des adjudications qui nomment l'entreprise avant d'en faire le signal fort. | [I17](https://github.com/pipeworx-io/mcp-germany-tenders) |
| 6 | **Couverture affichée honnêtement** | Shovels (% de population), planning.data.gov.uk (« pas prêt ») | Tableau de couverture par canton, langue et source ; jeu « partiel » marqué comme tel. | [I5](https://sacra.com/c/shovels/), [I9](https://www.planning.data.gov.uk/dataset/planning-application) |
| 7 | **Vérification humaine** | Glenigan (1 M+ appels/an), ibau | Le retour d'appel des consultants sert d'étiquette et de contrôle qualité. | [I6](https://www.glenigan.com/about-us/), [I16b](https://arbeitsagentur.de/jobsuche/jobdetail/10001-1003763568-S) |
| 8 | **Fusion multi-sources** | Vecteur Plus, ConstructConnect | Fiche entreprise unique, sources citées ligne à ligne. | [I11](https://jorpex.com/fr/compare/vecteur-plus-alternative/), [I2](https://www.constructconnect.com/industry-trusted-preconstruction-software) |
| 9 | **Indice ouvert et reproductible** | Indeed Hiring Lab (CC BY 4.0) | Publier un indice hebdomadaire des signaux par canton, avec méthode documentée. | [I23](https://github.com/hiring-lab/job_postings_tracker) |
| 10 | **Prix par zone** | Construction Monitor | Tarification par agence ou par canton couvert. | [I3](https://www.jlconline.com/business/sales-marketing/pulled-permits-as-a-source-of-leads/) |

**Constat d'ensemble.** À l'étranger, les marchés publics sont presque
partout **ouverts et gratuits avec API** (BOAMP, DECP, TED, Doffin, Hilma,
Bekanntmachungsservice), tandis que les données de **projets privés** sont
vendues par des acteurs commerciaux **sans prix public** (Dodge, Glenigan,
Barbour ABI, Vecteur Plus), souvent avec une forte part de recherche humaine.
Aucun des fournisseurs étudiés ne transforme ces données en **besoin en
personnel par métier** pour des agences de placement : ils servent les
vendeurs de matériaux et les entreprises de construction.

---

## 7 bis. Ce qui conviendrait à Flexsis (agence locale) et à Interiman (groupe multi-marques)

*Ajouté après l'audit du 2026-10-05. Déductions tirées des § 1 à 7 ci-dessus (mêmes sources), pas de faits nouveaux.*

| Catégorie | Pour Flexsis (agences locales, VS puis Suisse alémanique) | Pour Interiman (groupe, plusieurs marques et secteurs) |
|---|---|---|
| Marchés publics ouverts (modèle BOAMP, DECP, TED, Doffin) | Équivalent suisse gratuit : simap.ch ; suffit pour démarrer canton par canton. | Même source, mais il faut une couverture nationale et un tableau de couverture par canton (idée 6). |
| Données de projets privés vendues (Dodge, Glenigan, Barbour ABI, Vecteur Plus) | Trop chères et sans prix public ; en Suisse, l'équivalent commercial (Docu Media / Baublatt, Batimag) ne se justifie qu'après le pilote. | Un abonnement de groupe peut se justifier s'il couvre plusieurs marques (construction, industrie) ; à négocier une fois le gain mesuré. |
| Rattachement entreprise (BuildZoom, Shovels) | Priorité n° 1 même à petite échelle : rapprochement par IDE. | Indispensable pour dédoublonner les clients entre marques et éviter que deux marques appellent la même entreprise. |
| Vérification humaine (Glenigan) | Le retour d'appel en un clic des consultants. | Agréger les retours de toutes les marques pour améliorer les règles et les modèles. |
| Indice ouvert (Indeed Hiring Lab) | Peu utile seul. | Un indice hebdomadaire de signaux par canton peut servir la communication du groupe. |
| Prix par zone (Construction Monitor) | Licence par agence ou par canton couvert. | Licence de groupe avec extension par marque et par secteur. |

## 8. Noms non vérifiés ou retirés

- **Non vérifiés (réels selon le cahier des charges, mais rien de vérifiable
  ici)** : Batiactu, DTAD, Baudata, Byggfakta (Byggfakta Group), Visma Opic,
  OCDE (travaux sur les offres en ligne), Eurostat/Cedefop Skills-OVATE,
  Burning Glass Institute. Aucune information n'est donnée sur eux pour ne
  rien inventer.
- **« Bund.de »** : seul le flux RSS de `service.bund.de` est attesté (OS).
- **Builder's Conference** : existence attestée seulement par le titre d'une
  page de partenariat Glenigan.

---

## Sources (consultées le 2026-10-04)

Toutes les URL ont été consultées le **2026-10-04**. Sauf mention « lu
directement », il s'agit d'extraits de recherche (page non consultée).

1. I1 — Dodge Construction Network, « What Is Dodge Construction Network? » : https://www.construction.com/what-is-dodge-construction-network-the-dodge-report-explained/ ; I1b — Dodge, API : https://www.construction.com/apis/
2. I2 — ConstructConnect, « iSqFt · BidClerk · Construction Journal · CMD · Reed — now ConstructConnect » : https://www.constructconnect.com/industry-trusted-preconstruction-software ; I2b — constructionbids.ai, « BidClerk vs ConstructConnect 2026 » (concurrent) : https://constructionbids.ai/blog/bidclerk-vs-constructconnect-comparison-2026
3. I3 — JLC Online, « Pulled Permits as a Source of Leads » : https://www.jlconline.com/business/sales-marketing/pulled-permits-as-a-source-of-leads/ ; I3b — Construction Monitor, brochure PDF : https://www.constructionmonitor.com/assets/pdf/construction-monitor-brochure.pdf ; I3c — Dun & Bradstreet Marketplace : https://www.dnb.com/marketplace/data/construction-monitor.html
4. I4 — Y Combinator, « Q&A with Jiyan Wei and David Petersen, Cofounders of BuildZoom » : https://www.ycombinator.com/blog/qa-with-jiyan-wei-and-david-petersen-cofounders-of-buildzoom/ ; I4b — BuildZoom Data : https://www.buildzoomdata.com ; I4c — Cherre, fiche BuildZoom : https://cherre.com/vendors/buildzoom/
5. I5 — Sacra, Shovels : https://sacra.com/c/shovels/ ; I5b — The GTM Directory, Shovels : https://thegtmdirectory.com/tools/shovels ; I5c — npm, `n8n-nodes-shovels` (**description lue directement** via registry.npmjs.org) : https://www.npmjs.com/package/n8n-nodes-shovels
6. I6 — Glenigan, « About us » : https://www.glenigan.com/about-us/ ; I6b — The Construction Index, « Why use Glenigan » : https://www.theconstructionindex.co.uk/news/view/why-use-glenigan ; I6c — Glenigan, « Exclusive Builders Conference partnership… » : https://www.glenigan.com/exclusive-builders-conference-partnership-delivers-significant-value-to-glenigan-customers/
7. I7 — Infopro Digital, « Acquisition of the British company Barbour ABI » : https://www.infopro-digital.com/news/acquisition-of-the-british-company-barbour-abi-construction-sales-leads-intelligence-monitoring-market-england ; I7b — Datarade, Barbour ABI : https://datarade.ai/data-products/barbour-abi-construction-project-leads-barbour-abi
8. I8 — Opensite Energy, organisation « UK PlanIt » : https://data.opensite.energy/organization/uk-planit ; I8b — Searchland, « Planning applications API » : https://searchland.co.uk/our-apis/planning-aplication-api-new
9. I9 — planning.data.gov.uk, jeu « planning application » : https://www.planning.data.gov.uk/dataset/planning-application ; I9b — planning.data.gov.uk : https://planning.data.gov.uk/
10. I10 — HM Land Registry, « Use land and property data » : https://use-land-property-data.service.gov.uk/
11. I11 — Jorpex, « Alternative à Vecteur Plus » (concurrent) : https://jorpex.com/fr/compare/vecteur-plus-alternative/
12. I12 — SIMI 2025, document PDF (attribution de l'extrait Explore incertaine) : https://www.salonsimi.com/app/cache/flux_leni_medias/SIMI25/pdf-a4043915-27ab-f011-a8d8-005056ac7c95.pdf
13. I13 — SDES, « La base de données Sitadel : méthodologie » : https://www.statistiques.developpement-durable.gouv.fr/la-base-de-donnees-sitadel-methodologie ; I13b — GitHub, `data-fair/processing-sitadel` (**README lu directement**) : https://github.com/data-fair/processing-sitadel ; I13c — data.gouv.fr, réutilisation basedespermis.fr : https://www.data.gouv.fr/reuses/basedespermis-fr
14. I14 — data.gouv.fr, jeu BOAMP : https://www.data.gouv.fr/datasets/boamp ; I14b — Hugging Face, `french-open-data/api-boamp` README : https://huggingface.co/datasets/french-open-data/api-boamp/blob/main/README.md
15. I15 — GitHub, `ColinMaudry/decp-processing` (**README lu directement**) : https://github.com/ColinMaudry/decp-processing ; I15b — GitHub, `139bercy/decp-rama` (**README lu directement**) : https://github.com/139bercy/decp-rama ; I15c — GitHub, `ColinMaudry/decp.info` / colibre (**README lu directement**) : https://github.com/ColinMaudry/decp.info
16. I16 — ibau, « Partnernetzwerk » : https://www.ibau.de/ueber-ibau/partner/ ; I16b — Bundesagentur für Arbeit, offre « Mitarbeiter Recherche – Bauprojekte & Vergaben » chez Ibau GmbH : https://arbeitsagentur.de/jobsuche/jobdetail/10001-1003763568-S
17. I17 — GitHub, `pipeworx-io/mcp-germany-tenders` (**README lu directement**) : https://github.com/pipeworx-io/mcp-germany-tenders
18. I18 — GitHub, `shufflethis/ausschreibungsagenten` (**README lu directement**) : https://github.com/shufflethis/ausschreibungsagenten
19. I19 — GitHub, `OP-TED/ted-open-data` (Office des publications de l'UE ; **README lu directement**) : https://github.com/OP-TED/ted-open-data
20. I20 — GitHub, `CorrelAid/pystatis` (**README lu directement**) : https://github.com/CorrelAid/pystatis
21. I21 — GitHub, `anskaffelser/eforms-sdk-nor`, « Doffin API » (**lu directement**) : https://github.com/anskaffelser/eforms-sdk-nor/blob/main/docs/doffin-api.md ; I21b — GitHub, `reidar80/DoffinMCP` (**README lu directement**) : https://github.com/reidar80/DoffinMCP
22. I22 — GitHub, `Aimiten/hilma-mcp` (**README lu directement**) : https://github.com/Aimiten/hilma-mcp
23. I23 — GitHub, `hiring-lab/job_postings_tracker` (**README et fichiers lus directement** ; tests 404 pour CH, AT, JP, SE, BE, PL) : https://github.com/hiring-lab/job_postings_tracker ; I23b — FRED, « Job Postings on Indeed in Germany » : https://fred.stlouisfed.org/data/IHLIDXDE
24. I24 — LinkUp, « Correlation Between LinkUp Data and the BLS Reports » : https://www.linkup.com/use-cases/correlation-between-linkup-data-and-the-bls-reports ; I24b — LinkUp, blog : https://www.linkup.com/insights/blog/linkups-job-market-data-foretold-solid-jobs-report-for-october
25. I25 — jobspipe.dev, « Lightcast pricing » (concurrent) : https://jobspipe.dev/blog/lightcast-pricing ; I25b — npm, `@hackspaces/lightcast-connect-mcp` (**description lue directement**) : https://www.npmjs.com/package/@hackspaces/lightcast-connect-mcp
26. I26 — Revelio Labs, RPLS : https://www.reveliolabs.com/news/rpls/ ; I26b — Revelio Labs, données : https://www.reveliolabs.com/data
27. I27 — GitHub, `cyanheads/bls-labor-mcp-server` (**README lu directement**) : https://github.com/cyanheads/bls-labor-mcp-server
