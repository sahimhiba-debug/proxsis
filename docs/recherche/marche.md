# Marché et solutions — recherche Proxsis (cahier des charges, section 2a)

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

- **Date de consultation de toutes les sources : 2026-10-04.**
- Auteur : agent de recherche (Claude Code), pour l'équipe Proxsis.
- Périmètre : outils IA des agences de placement, « sales intelligence » pour
  recruteurs, données suisses de chantiers et de marchés publics, publications
  des grands groupes sur la demande de travail, concurrence en Suisse romande.

## Méthode, limites et légende des niveaux de preuve

**Contraintes de l'environnement.** Depuis l'environnement d'exécution, les
sites des éditeurs, des administrations et la plupart des médias renvoient
`EGRESS_BLOCKED` (testé le 2026-10-04 avec WebFetch sur vincere.io,
bullhorn.com, recruitcrm.io, loxo.co, theirstack.com, x28.ch,
planit.org.uk, boamp.fr, wikipedia.org, data.gouv.fr, bls.gov,
cedefop.europa.eu). Presque tous les faits ci-dessous viennent donc des
**extraits renvoyés par le moteur de recherche**, sans lecture de la page.
Seuls `raw.githubusercontent.com`, `pypi.org` et `registry.npmjs.org` étaient
lisibles : quelques faits ont été vérifiés là (fichiers lus directement).
Le quota de recherche web de la session a été épuisé (≈ 60 recherches faites
par cet agent) : certains noms n'ont pas pu être vérifiés et sont listés
comme tels.

**Légende (à lire dans chaque tableau) :**

| Code | Signification |
|---|---|
| **V** | Affirmé par le vendeur / l'éditeur (communiqué, site, brochure). Non vérifié indépendamment. |
| **T** | Source tierce (presse, comparatif, agrégateur, blog d'un concurrent). Fiabilité variable ; les blogs comparatifs de tarifs peuvent être obsolètes. |
| **E** | Extrait de recherche, page non consultée. |
| **M** | Mesuré / vérifié indépendamment par nous le 2026-10-04 (fichier ou README lu directement). |
| **OS** | Attesté par un projet open source tiers dont nous avons lu le README ; pas une confirmation officielle. |

Les combinaisons se lisent ainsi : « E·V » = extrait de recherche rapportant
une affirmation du vendeur.

---

## a. Outils des agences de placement dotés d'IA (ATS/CRM, matching)

### a.1 Éditeurs internationaux

| Outil | Ce qu'il fait | Prix | Résultats publiés | Anticipation de la demande côté clients (BD) ? | Source |
|---|---|---|---|---|---|
| **Bullhorn** (Recruitment Cloud, AI Assistant, **Amplify**, Digital Workers) | ATS/CRM pour agences de staffing. Recruitment Cloud sur la plateforme Salesforce (annonce nov. 2024) avec « Candidate Matching agent actions » et « AI Assistant » (résumés de CV, questions de présélection, e-mails) (E·V). **Amplify** lancé le 28 mai 2025 à Engage Boston : recherche et classement de candidats (job boards + base interne), insights tirés de « 60+ millions de placements historiques », présélection asynchrone voix/chat (E·V). « Amplify Digital Workers » présentés à Engage 2026 (E·V). Le nom « Bullhorn **Copilot** » n'apparaît que chez un agrégateur tiers (E·T) : non confirmé par un communiqué officiel trouvé. | Prix non public. Un agrégateur tiers cite « typiquement 100 USD+/utilisateur/mois » en entreprise (E·T, fiabilité faible). | Clients Amplify : **+51 %** de soumissions, **+22 %** de taux de pourvoi, 85 % d'expérience candidat positive (E·V). Digital Workers : Procom +65 % soumission→placement, Employment Enterprises +23 % de marge brute hebdo, IDR 200 h/semaine économisées, Tential +40 % de soumissions (E·V). **Aucune mesure indépendante trouvée.** | **Oui, via Textkernel Jobfeed intégré** : un article Bullhorn (DE) présente « Arbeitsmarktanalyse und Neukundengewinnung in Bullhorn mit Jobfeed » (E·V). Bullhorn aurait racheté Textkernel le 18 juin 2024 (E·T). | [S1](https://www.bullhorn.com/news-and-press/press-releases/bullhorn-launches-amplify/), [S2](https://www.bullhorn.com/news-and-press/press-releases/bullhorn-unveils-amplify-digital-workers-at-engage-2026/), [S3](https://www.businesswire.com/news/home/20241120815152/en/Bullhorn-Recruitment-Cloud-combines-the-power-of-the-Salesforce-platform-with-new-AI-Agents), [S4](https://www.bullhorn.com/de/blog/jobfeed-in-bullhorn/), [S5](https://subger.com/en/in/service/bullhorn), [S14](https://jobspipe.dev/blog/textkernel-review) |
| **Avionté** | Plateforme unifiée pour agences (surtout US) : ATS, engagement candidat, paie, facturation, conformité, CRM, app mobile, temps de travail (E·T). | Prix non public : devis selon taille, modules, volume (E·T). | Inconnu. | Inconnu (rien trouvé sur la prospection prédictive). | [S6](https://peoplemanagingpeople.com/tools/avionte-review/) |
| **Mercury xRM** | CRM de recrutement bâti sur Microsoft Dynamics 365 / Power Platform ; « Mercury AI Essentials » pour la recherche et les prédictions (E·T). Partenariat avec Textkernel en 2024 (parsing, insights marché) (E·T). | Prix non public (rien trouvé). | « 2 500 abonnés cloud HCM » selon Apps Run The World (E·T). | Partiel : insights marché via Textkernel (E·T) ; pas de détection de besoins clients documentée. | [S7](https://www.appsruntheworld.com/hcm-top-500-software-vendors/mercury-xrm/) |
| **Vincere** | CRM/ATS pour agences ; IA vendue en packs « Access Vincere Evo » (E·T). | Licence CRM/ATS dès **£69/utilisateur/mois** ; packs IA par agence : Base dès £25, Present £139, Automate £235, Elite £349/mois ; contrat minimum 12 mois (E·T, blogs citant la page tarifs). | Inconnu. | Inconnu. | [S8](https://www.noon.ai/blog/articles/320-vincere-pricing-2026), [S8b](https://www.pin.com/blog/vincere-pricing) |
| **Recruit CRM** | ATS + CRM pour agences : parsing de CV, pipelines, tableaux de bord ; séquences e-mail dès « Business » (E·T). | Annuel : Pro **95 $**, Business **135 $**, Enterprise **215 $**/utilisateur/mois ; mensuel 109/159/259 $ (E·T). | Inconnu. | Non documenté. | [S9](https://www.techrepublic.com/article/recruit-crm-review/), [S9b](https://www.noon.ai/blog/articles/319-recruit-crm-pricing-2026) |
| **Loxo** | ATS/CRM avec sourcing (« Loxo Source »), « AI agents », prise de notes IA, outreach multicanal ; un « Sales CRM » dès Basic (E·T). | Free 0 $ (1 utilisateur), Basic **169 $/utilisateur/mois**, Professional et Enterprise sur devis ; des tiers estiment Professional à 250–400 $/utilisateur/mois (E·T). | Inconnu. | Un « Sales CRM » existe (E·T) ; pas de détection automatique de besoins clients documentée. | [S10](https://www.goperfect.com/blog/loxo-pricing-in-2026-complete-breakdown-of-plans-costs-and-alternatives), [S10b](https://www.pin.com/blog/loxo-pricing) |
| **Sense** (Sense Talent Labs) | Engagement candidat piloté par IA (messages, matching) ; a racheté Skillate (matching IA) en sept. 2022 (E·V). | Prix non public. | Inconnu. | Non (côté candidats). | [S11](https://www.businesswire.com/news/home/20220908005391/en/Sense-Expands-AI-Talent-Engagement-Platform-with-Skillate-Acquisition) |
| **Textkernel** (parsing, Search & Match, **Jobfeed**, Market IQ) | Parsing/matching de CV et d'offres ; base d'offres Jobfeed « 3+ milliards d'offres, 33+ millions de sites », 50+ attributs par offre (E·V). **Une version « Jobfeed CH » existe** (option contractuelle) selon la base de connaissances d'un intégrateur (E·T). Manpower Suisse utilise son matching (E·T). | Prix non public ; une page « pricing » existe (contenu non consulté) ; Capterra évoque « dès 2 000 USD » (E·T, non vérifié). | Cas client StepStone pour le développement commercial (E·V). | **Oui** : Jobfeed et Market IQ sont vendus pour la génération de leads et la recherche sur les entreprises clientes (E·V). | [S12](https://www.textkernel.com/products-solutions/labour-market-insights/), [S13](https://mysolution.com/en/feature-kennisbank/matching-french-austrian-and-swiss-vacancies-in-textkernel-search-match), [S15](https://onrec.com/news/news-archive/how-textkernel%E2%80%99s-matching-technology-speeds-manpower-placements-in-switzerland), [S16](https://www.textkernel.com/customer-cases/how-stepstone-enhances-business-development-with-textkernel/), [S17](https://www.capterra.com.sg/software/126982/textkernel) |
| **HireAbility** | Parseurs « ALEX » (CV, offres, contacts) en 50+ langues, sortie XML/JSON ; moteur de matching associé (E·T). Brique technique vendue aux éditeurs d'ATS. | Prix non public. | Inconnu. | Non. | [S18](https://www.trustradius.com/products/hireability) |
| **Eightfold AI** | « Talent intelligence » et agents IA pour grandes entreprises : AI Interviewer (oct. 2025), AI Interview Companion (avril 2026) ; module « Workforce Exchange » (place de marché à trois côtés, orientation secteur public) (E·V). | Prix non public. | Clients : NPS candidat 84 %, délai de pourvoi −33 % environ, délai jusqu'à l'entretien jusqu'à −90 % (E·T citant le vendeur). | Non (employeurs, pas agences). | [S19](https://eightfold.ai/company/press/press-releases/eightfold-ai-expands-talent-agents-across-the-full-interview-journey-introducing-ai-interview-companion-and-new-interview-capabilities/), [S19b](https://pipeline.zoominfo.com/sales/eightfold-ai-features) |
| **Beamery** | « Talent Lifecycle Management » pour grandes entreprises ; TalentGPT (mars 2023) ; « Strategic Challenger » Fosway 9-Grid 2025 (E·V). | Prix non public (« contact sales ») (E·T). | Inconnu. | Non. | [S20](https://microsite.beamery.com/news/beamery-recognized-as-a-strategic-challenger-in-the-2025-fosway-9-grid-for-talent-acquisition) |

**Lecture.** Le matching candidat ↔ poste et l'automatisation du recruteur
sont devenus une fonction standard des ATS de staffing. L'anticipation de la
demande **côté clients** n'est proposée que par la brique « offres d'emploi
publiées » (Textkernel Jobfeed / Market IQ, intégrée à Bullhorn) : elle
détecte une entreprise **après** qu'elle a publié une offre, pas avant.

### a.2 Suisse et DACH

| Nom | Vérifié ? | Ce qu'il fait | Prix | IA / BD | Source |
|---|---|---|---|---|---|
| **zvoove** (ex-clients LANDWEHR-L1) | Oui (E) | Logiciel cloud allemand pour le travail temporaire : ATS, disposition, gestion des collaborateurs, Equal Pay, conformité AÜG (loi allemande), paie ; « agents IA pour le recrutement » ; programme de migration pour les clients LANDWEHR-L1 (E·T). Un CEO « Staffing DACH » couvre Allemagne, Autriche, Suisse (E·V). | Prix non public. | IA côté recrutement ; rien trouvé sur la prospection prédictive. Conformité suisse (LSE, Swissdec) : inconnu. | [S21](https://www.ki-syndikat.de/tools/zvoove/), [S21b](https://www.prnewswire.com/de/news-releases/zvoove-ernennt-markus-budde-zum-ceo-staffing-dach-302511908.html) |
| **Coople** | Oui (E) | **Plateforme suisse de staffing à la demande** (fondée en 2009) : un algorithme apparie travailleurs et missions ; « 98 % des demandes pourvues en 4 heures », « 30 000+ entreprises en Suisse », « 900 000+ travailleurs inscrits » (E·V). C'est un **concurrent** de Flexsis, pas un outil pour elle. | Non public. | Matching algorithmique (E·V). | [S22](https://www.coople.com/ch/en/) |
| **Abacus** (Abacus Research AG) | Oui (E) | ERP suisse pour PME ; paie certifiée Swissdec, utilisée par « 10 000+ entreprises » ; modules RH avec gestion des candidatures (E·V). Aucun module spécifique au travail temporaire trouvé. | Non trouvé. | Non. | [S23](https://abacus.ch/en/company/about-us/portrait) |
| **Proffix**, **SwissSalary** | Oui (E) | Paie certifiée Swissdec (Proffix : ~4 000 PME, CCT spéciales ; SwissSalary : sur Microsoft Dynamics NAV) (E·V). Généralistes. | Non trouvé. | Non. | [S24](https://platform.softwareone.com/product/proffix/PCP-1422-6672) |
| **JobCloud** (jobs.ch, jobup.ch) | Oui (E) | Principal acteur suisse des portails d'emploi ; étude « JobCloud Market Insights » avec la ZHAW, qui compare offres publiées et clics des chercheurs d'emploi, au moins annuelle (E·V). | Annonces : non consulté. | Données de demande agrégées ; pas d'outil de prospection pour agences trouvé. | [S28](https://www.zhaw.ch/en/about-us/news/news-releases/news-detail/event-news/study-on-job-searches-in-switzerland-published) |
| **Prospective** (Prospective Media Services AG, Zurich) | Oui (E) | Gestion d'annonces d'emploi et marketing RH depuis 2000 : multiposting « JobBooster », « JobIQ » (social recruiting), « Trend Report Online-Recruiting Schweiz » (E·V). Pas un ATS de staffing. | Non trouvé. | Non. | [S25](https://www.hrfestival.ch/en/exhibitors/prospective-media-services-ag) |
| **TOPIX** (TOPIX Business Software AG) | Existe, mais hors sujet | ERP/CRM/RH généraliste (Ottobrunn, 1990), « 4 200+ entreprises » en DACH (E·V). Aucun module de travail temporaire trouvé. | Non trouvé. | Non. | [S26](https://softguide.com/company/topix-informationssysteme-ag) |
| **BeskarStaff** | Oui (E) | Logiciel de recrutement IA « pour le marché suisse » : trouver et classer des candidats (E·V). | Non trouvé. | Côté candidats. | [S27b](https://hrfestival.ch/en/ausstellende/beskarstaff/) |
| jacando, Ostendis, Refline | Oui (E) | ATS suisses pour employeurs (PME, secteur public) (E·T). | Non trouvé. | Non. | [S27](https://www.dualoo.com/en/hr-knowledge/best-candidate-management-software-switzerland/) |

**Noms retirés (non vérifiés) :**

- **Persy** : aucun logiciel de ce nom trouvé (seulement des sociétés de
  placement au nom proche : perZone GmbH, persona service GmbH) (E).
- **Kandio** : absent des listes d'ATS suisses consultées (E).
- **ITS**, **peoplefone** : non recherchés faute de quota. Rien n'indique un
  lien avec le staffing ; retirés par prudence.
- **Bullhorn « Copilot »** : gardé seulement comme nom cité par un tiers
  (voir tableau a.1).

---

## b. « Sales intelligence » pour recruteurs (qui recrute ?)

| Fournisseur | Ce qu'il vend | Couverture Suisse | Prix | API | Usage prospection | Source |
|---|---|---|---|---|---|---|
| **x28 AG** (Suisse) | « L'une des entreprises de données du marché du travail les plus abouties de Suisse » : collecte **quotidienne de toutes les offres en Suisse** sur les sites des employeurs et des agences, annotation sémantique (E·V). Publie le **Jobradar** trimestriel : 226 697 postes annoncés mi-août 2025 (T3 2025) ; santé 15 069, **construction 13 968**, commerce de détail 11 096 (E·T). Environ la moitié des annonces vient des agences de placement (E·T). | **Oui, cœur de métier** | Prix non public. | Inconnu (un extrait parle d'API, sans preuve). | Données exploitables pour repérer les entreprises qui recrutent ; un article Blick tire du Jobradar les entreprises « qui licencient et recrutent en même temps » (E·T). | [S29](https://hrfestival.ch/en/ausstellende/x28-ag/), [S29b](https://www.bluewin.ch/de/news/wirtschaft-boerse/in-der-schweiz-sind-fast-227-000-stellen-unbesetzt-2897627.html), [S29c](https://www.blick.ch/wirtschaft/jobradar-zeigt-diese-firmen-werfen-leute-raus-und-suchen-zeitgleich-personal-id19597310.html) |
| **Textkernel Jobfeed** | Base d'offres dédoublonnée, 15 marchés (E·V) ; option **Jobfeed CH** (E·T). | Oui (option) | Non public (voir a.1). | Oui (« Jobs Data » API documentée sur developer.textkernel.com, contenu non consulté) (E). | Leads « entreprises qui publient », intégré à Bullhorn (E·V). | [S12](https://www.textkernel.com/products-solutions/labour-market-insights/), [S13](https://mysolution.com/en/feature-kennisbank/matching-french-austrian-and-swiss-vacancies-in-textkernel-search-match) |
| **Lightcast** (« Emsi Burning Glass » selon le cahier des charges ; filiation non revérifiée ici) | Données d'offres, taxonomies compétences/métiers, logiciel d'analyse, API, conseil (E·T). | Inconnu | **Prix non public** ; des acheteurs évoquent cinq chiffres par an au départ, six pour les licences de données (E·T). Depuis avril 2026, le palier gratuit « Skills » serait réservé aux associations, 50 extractions/mois (E·T). | Oui : Job Postings API OAuth 2.0, 5 requêtes/s par défaut (E·T). | Analyse de marché plutôt que liste d'appels. | [S30](https://jobspipe.dev/blog/lightcast-pricing) |
| **Indeed Hiring Lab** | Indice quotidien des offres Indeed (base 100 = 1er février 2020), corrigé des variations saisonnières (méthode Bundesbank), rafraîchi chaque semaine, licence **CC BY 4.0** (M). | **Non : aucun fichier Suisse** (`CH/aggregate_job_postings_CH.csv` → 404 ; présents : US, GB, DE, FR, IT, NL, ES, IE, CA, AU) (M). Dernière donnée DE/FR : 2026-09-25 (M). | Gratuit (M). | Fichiers CSV sur GitHub (M). | Contexte macro seulement ; pas d'entreprise nommée. | [S31](https://github.com/hiring-lab/job_postings_tracker) |
| **LinkUp** (US) | Offres indexées chaque jour directement sur les sites d'entreprises (« 60 000 sites », chiffre daté inconnu) ; prévisions des créations d'emplois US (NFP) et de JOLTS (E·V). | Inconnu | Prix non public. | Inconnu. | Signal macro et par entreprise (US). | [S32](https://www.linkup.com/use-cases/correlation-between-linkup-data-and-the-bls-reports) |
| **Revelio Labs** | Données RH à partir de profils publics et d'offres (« 350 000 sites d'entreprises », job boards, sites d'agences) ; statistiques « RPLS » ; « Revelio Terminal » lancé en juillet 2026 (E·V). | Inconnu | Prix non public. | Jeux de données documentés (dictionnaire en ligne) (E). | Effectifs, entrées/sorties : utile pour un groupe. | [S33](https://www.reveliolabs.com/data), [S33b](https://www.reveliolabs.com/news/rpls/) |
| **PredictLeads** | Signaux B2B : offres d'emploi (« 165 M+ »), actualités, technologies, firmographie sur « 71 M+ entreprises » ; API, fichiers, webhooks, serveur MCP (E·T). | Inconnu | Gratuit 100 appels/mois ; à l'usage jusqu'à 0,002 $/appel ; entreprise dès **6 000 $/an par jeu de données** (E·T). | Oui. | Alertes « entreprise qui recrute ». | [S34](https://prospeo.io/s/predictleads-pricing-reviews-pros-and-cons) |
| **TheirStack** | Base d'offres (« 223 M », ~313 000 ajoutées/jour) et technographie déduite des offres (E·T). | Inconnu | Gratuit : 50 crédits entreprise + 200 crédits API/mois ; API de **49 $/mois** (1 500 crédits) à **5 500 $/mois** (5 M crédits), 1 crédit par offre (E·T). | Oui (REST). | Signaux d'intention d'achat tirés des recrutements. | [S35](https://jobspipe.dev/blog/theirstack-pricing) |
| **Coresignal** | Données web publiques (offres, entreprises, profils) via API et self-service (E·V). | Inconnu | Starter dès **49 $/mois**, Pro dès 800 $, Premium dès 1 500 $ ; 400 crédits de recherche + 200 de collecte offerts (E·T/V). | Oui. | Enrichissement, signaux. | [S36](https://coresignal.com/lp/jobs-data-api-2), [S36b](https://pipeline.zoominfo.com/sales/coresignal-pricing) |
| **Jobdigger** (Pays-Bas) | Moteur d'offres couvrant tout le web néerlandais, dédoublonnage, **enrichissement avec les coordonnées de contact**, classement ESCO (E·V). Utilisé chaque jour par Manpower/Experis NL pour des **listes de leads** (E·V). Investissement de Main Capital Partners en mai 2025 (E). | **Non (NL)** | Non public. | Inconnu. | **Oui, c'est l'exemple le plus proche du besoin** (mais pays-bas uniquement). | [S37](https://www.emerce.nl/wire/manpowergroup-zet-verdere-digitalisering-haar-diensten-intensiveert-samenwerking-jobdigger), [S37b](https://www.emerce.nl/wire/main-capital-partners-verwerft-meerderheidsbelang-aanbieder-arbeidsmarktdata-jobdigger) |

**Point clé.** Tous ces outils lisent les **offres d'emploi déjà publiées**.
Ils sont utiles comme **cible de vérité** (l'entreprise a-t-elle publié dans
les 8 semaines ?) et comme signal de relance, mais ils ne donnent pas
d'avance sur le besoin. En Suisse, seuls **x28** et **Textkernel Jobfeed CH**
ont une couverture suisse démontrée ; leurs prix ne sont pas publics.

---

## c. Données suisses de chantiers et de marchés publics

| Fournisseur | Ce qu'il vend / publie | Couverture | Prix | API | Source |
|---|---|---|---|---|---|
| **simap.ch** (officiel, Confédération + cantons) | Appels d'offres et adjudications. Nouvelle plateforme en service complet le 1er juillet 2024, ancienne arrêtée le 31 mars 2025 ; **les anciennes publications n'ont pas été reprises** (E·V). | Confédération, cantons, communes (E·V). | Gratuit. | **API de lecture OpenAPI 3 (v1.5.1), recherche et détail sans authentification**, confirmée en direct le 2026-07-26 par un projet tiers (OS) ; non testable d'ici (domaine bloqué). | [S42](https://bkb.admin.ch/fr/simapch-lancement-de-la-nouvelle-plateforme-de-publication), [S42b](https://pypi.org/project/swiss-procurement-mcp/) |
| **amtsblattportal.ch** (FOSC + feuilles officielles cantonales) | Publications officielles ; API de lecture libre, sans clé (OS). Une rubrique **« Baugesuche » (`BP-*`)** existe ; le projet tiers l'exclut volontairement car elle contient des données personnelles (OS). Certaines adjudications cantonales n'y figurent que là : l'exemple cité est le Valais, 150 adjudications absentes de simap (OS). | Couverture cantonale de la rubrique `BP-*` : inconnue. | Gratuit. | Oui (OS). | [S43](https://github.com/malkreide/amtsblatt-mcp) |
| **Docu Media Schweiz GmbH** (Adliswil, docu.ch) — **Baublatt** | Média et services d'information pour la construction ; Baublatt (depuis 1889) publie projets, demandes de permis, permis délivrés et adjudications de toute la Suisse, « de sources officielles et privées » (E·V). | Toute la Suisse (E·V). | Abonnement **numérique CHF 475.–/an** ; print + numérique dès CHF 525.– (25 numéros) (E·V, brochure). Accès à la base de projets : prix non public. | Inconnu. | [S38](https://www.isil.nb.admin.ch/en/institutions/docu-media-schweiz-gmbh-schweizer-baudokumentation-ch-001088-1), [S38b](https://www.baublatt.ch/storage/csGURW5s9YHDo6TA0iaAWX9GSr2mgkimwR5PqPWE.pdf) |
| **Batimag** | Équivalent romand de Baublatt : articles mensuels, projets, mises à l'enquête, autorisations, adjudications de Suisse occidentale (E·V). « Baublatt et Batimag » revendiquent « la plus grande base de projets de construction de Suisse » (E·V). | Suisse romande. | Prix non public. | Inconnu. | [S39](https://ch.linkedin.com/showcase/batimagch), [S39b](https://www.baublatt.ch/bauauftraege/static/pdfs/20251023_Baublatt_Basic_Submissionen.pdf) |
| **Bindexis** (Bâle, fondée en 2007) | Collecte « tous les permis de construire de Suisse » et les enrichit ; « 60 000+ projets », 12 catégories (E·V). Rachetée par NZZ en 2016, puis par **Infopro Digital** (2022 selon un extrait, date non confirmée) (E). | Suisse (E·V). | Abonnement : prix non public. Connecteur CRM SuperOffice : **CHF 51/site/mois** (E·V). | Intégration CRM SuperOffice (E·V) ; API générale inconnue. | [S40](https://www.infopro-digital.com/news/acquisition-of-bindexis-by-the-infopro-digital-group/), [S40b](https://appstore.superoffice.com/superoffice-as/bindexis-construction-data-for-superoffice), [S40c](https://www.markt-kom.com/en/?p=75166) |
| **Infopro Digital** (groupe français) | Se présente comme « le plus grand groupe d'information construction et marchés publics d'Europe » (DE, AT, CH, FR, BE, NL, GB) ; possède en Suisse **Infomanager** et **Bindexis** ; a aussi racheté Barbour ABI (UK) (E·V). Un extrait laisse entendre que Baublatt/Batimag relèveraient d'« Infopro Digital Schweiz » : **non confirmé**. | Europe. | Non public. | Inconnu. | [S40](https://www.infopro-digital.com/news/acquisition-of-bindexis-by-the-infopro-digital-group/) |
| **Houzy** (actionnaires majoritaires UBS et Baloise) | « Baugesuche Pro » (lancé en 2026) : alerte sur les demandes de permis dans un rayon choisi, avec maître d'ouvrage, type de projet, intervenants ; **abonnement payant** (E·V). Cible : propriétaires, locataires, acheteurs (B2C). | « Toute la Suisse » (E·V). | Prix non trouvé. | Non documentée. | [S41](https://www.netzwoche.ch/news/2026-02-13/houzy-wuehlt-sich-durch-die-baugesuche-der-schweiz) |
| opendata.swiss « bâtiments projetés » | Un jeu de données de ce nom apparaît dans les résultats ; producteur, contenu et fraîcheur **inconnus**. | Inconnu. | Gratuit (open data). | CKAN (portail). | [S44](https://opendata.swiss/en/dataset/batiments-projetes) |

**Noms retirés :** « **Bauinfo-Center** » (aucune entité suisse trouvée ;
seulement « BAUinfo » à Berlin), « **Infopro Digital/Bauinfo** » (le groupe
Infopro Digital existe, aucun produit suisse nommé « Bauinfo » trouvé),
« **Kursaal** » (non recherché, aucun lien plausible avec les données de
chantier).

---

## d. Ce que publient les grands groupes et la branche pour anticiper la demande

| Publication | Éditeur | Fréquence / méthode | Dernier chiffre trouvé | Utilité pour Proxsis | Source |
|---|---|---|---|---|---|
| **ManpowerGroup Employment Outlook Survey** (Suisse) | ManpowerGroup | Trimestrielle ; enquête d'intentions d'embauche ; indicateur « Net Employment Outlook » (NEO) (E). | T1 2026 : **NEO +27 %** (+1 point sur le trimestre, −2 points sur un an) ; baisse surtout chez les très grandes entreprises (E·T). Trimestres suivants : non consultés. | Contexte national par trimestre ; pas d'entreprise nommée. | [S45](https://www.organisator.ch/en/?p=42599) |
| **Adecco Group Swiss Job Market Index** | Adecco Group Suisse + Stellenmarkt-Monitor Schweiz (Université de Zurich) | Trimestriel (janvier, avril, juillet, octobre) ; relevés représentatifs des annonces (presse, portails, sites d'entreprises) (E·V). | T2 2026 : **−2,4 %** d'offres sur le trimestre ; T1 2026 : +0,7 % ; T4 2025 : +1,8 % (E·V). T3 2026 : inconnu à la date de consultation. | Meilleure série suisse publique sur les offres ; existe aussi en versions régionales (communiqués Zurich, Suisse centrale) (E). | [S46](https://www.adeccogroup.com/-/media/project/adecco-group/switzerland/job-index/job-index-q2-2026/job_index_q2_2026_medienmitteilung.pdf), [S46b](https://www.adeccogroup.com/de-CH/-/media/project/adecco-group/switzerland/job-index/job-index-q1-2026/job_index_medienmitteilugn_2026_q1_-de.pdf) |
| Adecco Group (Adecco, **LHH**, **Akkodis**) | Adecco Group | Aucun outil public de mesure en temps réel trouvé pour LHH ou Akkodis. Un témoignage sur une page Textkernel dit qu'Adecco utilise des insights marché (Market IQ) pour détecter la demande de clients et prospects (E·V, non confirmé). | — | Montre que les grands groupes **achètent** de la donnée d'offres plutôt que de la construire. | [S51](https://www.textkernel.com/jobs-database/) |
| **Randstad Market Insights (RMI)** (Pays-Bas) | Randstad | Outil interne « fonction × lieu » combinant **50 000+ sources** : statistiques publiques (CBS, UWV), job boards (Jobdigger, Monsterboard), enquêtes Randstad, données internes de 65 clients MSP/broker, données de 1 500 fournisseurs ; apprentissage automatique et taxonomie de compétences (E·V). | — | **Modèle de référence pour un groupe** : fusion données publiques + internes. Déploiement en Suisse : inconnu. | [S47](https://www.randstad.nl/werkgevers/kenniscentrum/artikelen/nieuws/van-yip-naar-rmi) |
| **Randstad Workmonitor 2026** | Randstad | Annuel ; 27 000+ travailleurs, 1 225 employeurs, 3 M+ offres analysées (E·V). | — | Tendances qualitatives ; pas de signal hebdomadaire. | [S47b](https://content.randstad.ca/en-ca/download-workmonitor-2026) |
| **Swiss Staffingindex** | swissstaffing (association de la branche) | Mensuel et trimestriel ; heures de mission des membres (E). | T1 2026 : **+1,3 %** d'heures, première hausse après 12 trimestres négatifs ; janvier +1,5 %, février −0,2 %, mars +1,1 % ; placement fixe **−16,9 %** (11e trimestre de baisse) ; 38 % des CEO membres attendent une hausse (E·T). | Contexte de branche ; utile pour expliquer pourquoi la prospection devient prioritaire. | [S48](https://www.organisator.ch/en/?p=48185), [S48b](https://www.staffingindustry.com/news/global-daily-news/swiss-temp-staffing-returns-to-growth-in-march-quarter) |
| **x28 Jobradar** | x28 AG | Trimestriel ; robot d'indexation à mi-trimestre (E·T). | T3 2025 : 226 697 postes (voir b) (E·T). | Seule série suisse publique avec détail par secteur et entreprises citées dans la presse. | [S29b](https://www.bluewin.ch/de/news/wirtschaft-boerse/in-der-schweiz-sind-fast-227-000-stellen-unbesetzt-2897627.html) |
| **ORTE — Travail intérimaire** | Observatoire romand et tessinois de l'emploi (publié sur le site SECO-TC) | Annuel. | Fin 2024 : **7 308 agences** en Suisse, dont **1 462 en Suisse romande** ; 2024 : **220,5 M d'heures louées**, dont **71,3 M en Suisse romande** (E ; PDF exact non confirmé parmi les rapports ORTE 2021–2025 listés). Calcul : la Romandie pèse ≈ 32 % des heures et ≈ 20 % des agences. | Taille du marché romand ; densité de concurrence. | [S50](https://www.secoalv.admin.ch/dam/secoalv/fr/dokumente/publikationen/studien/orte_travail_interimaire_2025.pdf.download.pdf/orte_travail_interimaire_2025.pdf) |
| **Interiman Group** | Interiman | **Aucune publication sur la demande de travail trouvée.** Données d'entreprise trouvées, non cohérentes entre elles : « 71 agences et 9 sociétés spécialisées », « CA de près de CHF 550 M », mais aussi « 67 agences sous 12 marques » ; « 30 000+ temporaires placés par an », « 4 500+ entreprises clientes » (E·V ; extraits mêlant les deux pages citées, attribution exacte de chaque chiffre incertaine). Un article annonce une hausse de 18 % du chiffre d'affaires annuel (année non précisée dans l'extrait) (E). | — | La vérification relève de `docs/recherche/contexte.md`. | [S49](https://greatplacetowork.ch/en/employer/interiman-group/) |

**Lecture.** Les publications des groupes et de la branche sont
**trimestrielles ou mensuelles, nationales ou régionales, sans nom
d'entreprise**. Elles servent de contexte (« le marché repart ») mais pas de
liste d'appels. Le seul outil de groupe qui ressemble à Proxsis (Randstad
RMI) est interne et néerlandais.

---

## e. Ce qui convient à une agence locale (Flexsis) vs à un groupe multi-marques (Interiman)

| Catégorie | Agence locale comme Flexsis | Groupe multi-marques comme Interiman | Source principale |
|---|---|---|---|
| ATS/CRM IA (Bullhorn, Vincere, Recruit CRM, Loxo, zvoove…) | Prend ce que l'agence a déjà ; Proxsis doit **s'y brancher** (export CSV/API), pas le remplacer. Les prix par utilisateur (69 £ à 215 $/mois, E·T) donnent un ordre de grandeur de ce qu'un consultant « vaut » en logiciel. | Choix d'un ATS commun ou de connecteurs par marque ; intérêt pour les agents IA à grande échelle (Amplify, Digital Workers). | [S1](https://www.bullhorn.com/news-and-press/press-releases/bullhorn-launches-amplify/), [S8](https://www.noon.ai/blog/articles/320-vincere-pricing-2026), [S9](https://www.techrepublic.com/article/recruit-crm-review/) |
| Données d'offres (x28, Jobfeed CH) | Licence trop chère à justifier seule (prix non publics) ; usage minimal : **cible de vérité** et relance. | Licence groupe rentabilisée sur 12 marques ; tableaux de bord par région/secteur. | [S29](https://hrfestival.ch/en/ausstellende/x28-ag/), [S13](https://mysolution.com/en/feature-kennisbank/matching-french-austrian-and-swiss-vacancies-in-textkernel-search-match) |
| Signaux B2B US/globaux (PredictLeads, TheirStack, Coresignal) | Paliers d'entrée bas (49 $/mois, E·T) mais couverture suisse inconnue : **tester avant d'acheter**. | Possible enrichissement pour les grands comptes multinationaux. | [S34](https://prospeo.io/s/predictleads-pricing-reviews-pros-and-cons), [S35](https://jobspipe.dev/blog/theirstack-pricing) |
| Chantiers privés (Baublatt/Batimag, Bindexis) | Abonnement Baublatt numérique CHF 475/an (E·V) : coût faible pour un contrôle manuel ; redistribution dans un logiciel : conditions inconnues. | Négociation d'une licence de données (Infopro Digital possède Bindexis) ; risque de dépendance à un fournisseur. | [S38b](https://www.baublatt.ch/storage/csGURW5s9YHDo6TA0iaAWX9GSr2mgkimwR5PqPWE.pdf), [S40](https://www.infopro-digital.com/news/acquisition-of-bindexis-by-the-infopro-digital-group/) |
| Données publiques (simap, amtsblattportal) | **Gratuites et suffisantes pour un pilote** dans 1 à 3 cantons. | Mêmes sources, à l'échelle des 26 cantons, FR/DE/IT. | [S42b](https://pypi.org/project/swiss-procurement-mcp/), [S43](https://github.com/malkreide/amtsblatt-mcp) |
| Indices macro (Adecco/UZH, Staffingindex, MEOS) | Lecture trimestrielle, contexte pour les conversations clients. | Pilotage des capacités par marque et par région. | [S46](https://www.adeccogroup.com/-/media/project/adecco-group/switzerland/job-index/job-index-q2-2026/job_index_q2_2026_medienmitteilung.pdf), [S48](https://www.organisator.ch/en/?p=48185) |
| Outil interne de fusion (type Randstad RMI) | Hors de portée seule. | **Cible naturelle** : Proxsis peut devenir la brique « signaux publics » d'un futur outil groupe. | [S47](https://www.randstad.nl/werkgevers/kenniscentrum/artikelen/nieuws/van-yip-naar-rmi) |

---

## f. Concurrence directe en Suisse romande pour la prospection

Aucun produit trouvé ne fait ce que vise Proxsis : croiser adjudications,
permis, mutations du registre du commerce et offres publiques pour produire
une **liste d'appels hebdomadaire pour consultants d'agence** en Suisse
romande. C'est une absence de preuve dans nos recherches, pas une preuve
d'absence. Les acteurs qui couvrent **une partie** du besoin :

| Acteur | Ce qui recoupe Proxsis | Ce qui manque | Source |
|---|---|---|---|
| **Bindexis** (Infopro Digital) | Leads tirés des permis de construire, toute la Suisse, intégration CRM (E·V). | Pensé pour les fournisseurs de la construction ; pas de métiers, pas de besoin en personnel estimé. | [S40b](https://appstore.superoffice.com/superoffice-as/bindexis-construction-data-for-superoffice) |
| **Baublatt / Batimag** (Docu Media) | Projets, mises à l'enquête, adjudications ; Batimag couvre la Romandie (E·V). | Médias et bases de projets ; pas de lien avec les besoins en personnel. | [S38b](https://www.baublatt.ch/storage/csGURW5s9YHDo6TA0iaAWX9GSr2mgkimwR5PqPWE.pdf), [S39](https://ch.linkedin.com/showcase/batimagch) |
| **x28** | Toutes les offres suisses, chaque jour (E·V). | Signal tardif (l'offre est déjà publiée) ; prix non public. | [S29](https://hrfestival.ch/en/ausstellende/x28-ag/) |
| **Textkernel Jobfeed CH via Bullhorn** | Leads « entreprises qui publient » dans l'ATS (E·V). | Même limite : réagit à l'offre publiée. | [S4](https://www.bullhorn.com/de/blog/jobfeed-in-bullhorn/) |
| **Coople** | Capte directement la demande des entreprises (30 000+ en Suisse, E·V). | Concurrent commercial de Flexsis, pas un outil. | [S22](https://www.coople.com/ch/en/) |
| **Houzy Baugesuche Pro** | Alertes sur les demandes de permis par rayon (E·V). | B2C (propriétaires), pas de lien avec l'emploi. | [S41](https://www.netzwoche.ch/news/2026-02-13/houzy-wuehlt-sich-durch-die-baugesuche-der-schweiz) |
| Outils internes des grands groupes | Randstad RMI (NL), Manpower + Jobdigger (NL), Adecco + Market IQ (témoignage) (E·V). | Déploiement en Suisse romande : **inconnu**. | [S47](https://www.randstad.nl/werkgevers/kenniscentrum/artikelen/nieuws/van-yip-naar-rmi), [S37](https://www.emerce.nl/wire/manpowergroup-zet-verdere-digitalisering-haar-diensten-intensiveert-samenwerking-jobdigger) |

---

## g. Ce que ça implique pour Proxsis

1. **Ne pas se battre sur le matching.** Le matching candidat ↔ poste est
   déjà fourni par les ATS (Bullhorn, Vincere, Loxo, Textkernel). La valeur de
   Proxsis est l'**avance côté clients** : appeler avant l'offre. Les
   outils de « job-posting intelligence » réagissent à l'offre publiée ; ils
   servent chez nous de **cible de vérité** et de relance, pas de signal
   principal.
2. **simap.ch est le premier connecteur à construire** : gratuit, national,
   adjudications comprises, API de lecture sans authentification (attestée
   par un projet tiers, OS). Attention : l'historique d'avant le 1er juillet
   2024 n'a pas été migré, ce qui limite la profondeur du backtest. Il faut
   compléter avec amtsblattportal.ch pour les cantons qui y publient des
   adjudications absentes de simap (cas du Valais cité).
3. **Permis de construire : passer par les publications officielles et
   filtrer les données personnelles.** La rubrique `BP-*` d'amtsblattportal
   contient des noms de requérants ; un projet tiers l'exclut pour cette
   raison. Proxsis doit garder uniquement les **personnes morales** (règle 3
   de `CONTRIBUTING.md`) et documenter la couverture cantonale réelle (inconnue
   aujourd'hui).
4. **Offres d'emploi : acheter, ne pas aspirer.** La règle 5 interdit
   d'aspirer les portails privés. Les seuls fournisseurs à couverture suisse
   démontrée sont x28 et Textkernel Jobfeed CH ; il faut demander des devis
   (prix non publics). Indeed Hiring Lab ne publie **aucune série suisse**
   (vérifié) : il ne peut pas servir d'indice macro pour la Suisse.
5. **Contexte macro : séries trimestrielles suisses.** Adecco/UZH (offres),
   Swiss Staffingindex (heures de mission) et ManpowerGroup MEOS (intentions)
   suffisent pour le volet « macro » ; aucune n'est hebdomadaire ni nominative.
6. **Se distinguer par la mesure.** Les résultats publiés par les éditeurs
   (+22 % de taux de pourvoi chez Bullhorn, etc.) sont **tous
   auto-déclarés** ; aucune mesure indépendante trouvée. Proxsis doit
   publier P@20, jours d'avance et intervalles de confiance issus d'un
   backtest reproductible, et ne jamais reprendre ces chiffres comme preuves.
7. **S'intégrer à l'ATS existant.** L'ATS de Flexsis est inconnu ici. Prévoir
   un export simple (CSV, webhook) ; le modèle « Jobfeed dans Bullhorn » montre
   que les consultants veulent les leads **dans leur outil**.
8. **Le marché romand justifie l'effort.** Selon l'ORTE (E), la Romandie
   représente ≈ 32 % des heures louées en Suisse (71,3 M sur 220,5 M en
   2024) avec 1 462 agences ; le placement fixe recule (−16,9 % au T1 2026,
   E·T) alors que le temporaire repart (+1,3 %) : la course au premier appel
   s'intensifie.
9. **Penser groupe dès le départ.** Le modèle Randstad RMI (données publiques +
   internes, par fonction et lieu) est la cible naturelle d'Interiman :
   multi-marques, multi-agences, FR/DE, avec les données internes FICTIVES
   tant que les vraies sont absentes.
10. **Budget de données réaliste.** Données publiques gratuites pour le pilote ;
    Baublatt numérique à CHF 475/an (E·V) comme contrôle manuel ; licences
    x28/Jobfeed/Bindexis à chiffrer sur devis avant tout engagement.

---

## Sources (consultées le 2026-10-04)

Toutes les URL ci-dessous ont été consultées le **2026-10-04**. Sauf mention
« lu directement », il s'agit d'extraits de recherche (page non consultée).

1. S1 — Bullhorn, « Bullhorn announces Amplify… » : https://www.bullhorn.com/news-and-press/press-releases/bullhorn-launches-amplify/
2. S2 — Bullhorn, « Bullhorn unveils Amplify Digital Workers at Engage 2026 » : https://www.bullhorn.com/news-and-press/press-releases/bullhorn-unveils-amplify-digital-workers-at-engage-2026/
3. S3 — BusinessWire, « Bullhorn Recruitment Cloud combines the power of the Salesforce platform with new AI Agents » (2024-11-20) : https://www.businesswire.com/news/home/20241120815152/en/Bullhorn-Recruitment-Cloud-combines-the-power-of-the-Salesforce-platform-with-new-AI-Agents
4. S4 — Bullhorn DE, « Arbeitsmarktanalyse und Neukundengewinnung in Bullhorn mit Jobfeed von Textkernel » : https://www.bullhorn.com/de/blog/jobfeed-in-bullhorn/
5. S5 — subger.com, fiche Bullhorn (agrégateur) : https://subger.com/en/in/service/bullhorn
6. S6 — People Managing People, « Avionté Review » : https://peoplemanagingpeople.com/tools/avionte-review/
7. S7 — Apps Run The World, Mercury xRM : https://www.appsruntheworld.com/hcm-top-500-software-vendors/mercury-xrm/
8. S8 — noon.ai, « Vincere pricing 2026 » : https://www.noon.ai/blog/articles/320-vincere-pricing-2026 ; S8b — pin.com : https://www.pin.com/blog/vincere-pricing
9. S9 — TechRepublic, « Recruit CRM Review » : https://www.techrepublic.com/article/recruit-crm-review/ ; S9b — noon.ai : https://www.noon.ai/blog/articles/319-recruit-crm-pricing-2026
10. S10 — goperfect.com, « Loxo Pricing in 2026 » : https://www.goperfect.com/blog/loxo-pricing-in-2026-complete-breakdown-of-plans-costs-and-alternatives ; S10b — pin.com : https://www.pin.com/blog/loxo-pricing
11. S11 — BusinessWire, « Sense Expands AI Talent Engagement Platform with Skillate Acquisition » (2022-09-08) : https://www.businesswire.com/news/home/20220908005391/en/Sense-Expands-AI-Talent-Engagement-Platform-with-Skillate-Acquisition
12. S12 — Textkernel, Labour Market Insights : https://www.textkernel.com/products-solutions/labour-market-insights/
13. S13 — Mysolution, « Matching French, Austrian and Swiss vacancies in Textkernel Search & Match » : https://mysolution.com/en/feature-kennisbank/matching-french-austrian-and-swiss-vacancies-in-textkernel-search-match
14. S14 — jobspipe.dev, « Textkernel review » (tiers, concurrent) : https://jobspipe.dev/blog/textkernel-review
15. S15 — Onrec, « How Textkernel's matching technology speeds Manpower placements in Switzerland » : https://onrec.com/news/news-archive/how-textkernel%E2%80%99s-matching-technology-speeds-manpower-placements-in-switzerland
16. S16 — Textkernel, cas client StepStone : https://www.textkernel.com/customer-cases/how-stepstone-enhances-business-development-with-textkernel/
17. S17 — Capterra SG, Textkernel : https://www.capterra.com.sg/software/126982/textkernel
18. S18 — TrustRadius, HireAbility : https://www.trustradius.com/products/hireability
19. S19 — Eightfold AI, communiqué AI Interview Companion : https://eightfold.ai/company/press/press-releases/eightfold-ai-expands-talent-agents-across-the-full-interview-journey-introducing-ai-interview-companion-and-new-interview-capabilities/ ; S19b — ZoomInfo Pipeline : https://pipeline.zoominfo.com/sales/eightfold-ai-features
20. S20 — Beamery, Fosway 9-Grid 2025 : https://microsite.beamery.com/news/beamery-recognized-as-a-strategic-challenger-in-the-2025-fosway-9-grid-for-talent-acquisition
21. S21 — KI-Syndikat, zvoove : https://www.ki-syndikat.de/tools/zvoove/ ; S21b — PR Newswire, « zvoove ernennt Markus Budde zum CEO Staffing DACH » : https://www.prnewswire.com/de/news-releases/zvoove-ernennt-markus-budde-zum-ceo-staffing-dach-302511908.html
22. S22 — Coople (site) : https://www.coople.com/ch/en/
23. S23 — Abacus, portrait : https://abacus.ch/en/company/about-us/portrait ; personalSCHWEIZ, dossier logiciels de paie (avril 2025, PDF) : https://cms.weka.ch/fileadmin_personal_schweiz/USERDATA/Bilder/personalSCHWEIZ_April_2025_Lohnsoftware.pdf
24. S24 — SoftwareOne, Proffix : https://platform.softwareone.com/product/proffix/PCP-1422-6672
25. S25 — HR Festival, Prospective Media Services AG : https://www.hrfestival.ch/en/exhibitors/prospective-media-services-ag
26. S26 — Softguide, TOPIX Business Software AG : https://softguide.com/company/topix-informationssysteme-ag
27. S27 — dualoo, « The 10 Best Applicant Tracking Systems for Swiss SMEs in 2026 » : https://www.dualoo.com/en/hr-knowledge/best-candidate-management-software-switzerland/ ; S27b — HR Festival, BeskarStaff : https://hrfestival.ch/en/ausstellende/beskarstaff/
28. S28 — ZHAW, « Study on job searches in Switzerland published » (JobCloud Market Insights) : https://www.zhaw.ch/en/about-us/news/news-releases/news-detail/event-news/study-on-job-searches-in-switzerland-published
29. S29 — HR Festival, x28 AG : https://hrfestival.ch/en/ausstellende/x28-ag/ ; S29b — blue News, « In der Schweiz sind fast 227 000 Stellen unbesetzt » : https://www.bluewin.ch/de/news/wirtschaft-boerse/in-der-schweiz-sind-fast-227-000-stellen-unbesetzt-2897627.html ; S29c — Blick, « Jobradar zeigt… » : https://www.blick.ch/wirtschaft/jobradar-zeigt-diese-firmen-werfen-leute-raus-und-suchen-zeitgleich-personal-id19597310.html
30. S30 — jobspipe.dev, « Lightcast pricing » (tiers, concurrent) : https://jobspipe.dev/blog/lightcast-pricing
31. S31 — Indeed Hiring Lab, dépôt `job_postings_tracker` (**lu directement** via raw.githubusercontent.com : README, fichiers DE/FR ; test 404 sur CH, AT, JP, SE, BE, PL) : https://github.com/hiring-lab/job_postings_tracker
32. S32 — LinkUp, « Correlation Between LinkUp Data and the BLS Reports » : https://www.linkup.com/use-cases/correlation-between-linkup-data-and-the-bls-reports
33. S33 — Revelio Labs, données : https://www.reveliolabs.com/data ; S33b — RPLS : https://www.reveliolabs.com/news/rpls/
34. S34 — Prospeo, « PredictLeads Pricing, Reviews » : https://prospeo.io/s/predictleads-pricing-reviews-pros-and-cons
35. S35 — jobspipe.dev, « TheirStack pricing » : https://jobspipe.dev/blog/theirstack-pricing
36. S36 — Coresignal, Jobs API : https://coresignal.com/lp/jobs-data-api-2 ; S36b — ZoomInfo Pipeline, « Coresignal Pricing » : https://pipeline.zoominfo.com/sales/coresignal-pricing
37. S37 — Emerce, « ManpowerGroup… intensiveert samenwerking Jobdigger » : https://www.emerce.nl/wire/manpowergroup-zet-verdere-digitalisering-haar-diensten-intensiveert-samenwerking-jobdigger ; S37b — Emerce, « Main Capital Partners verwerft meerderheidsbelang… Jobdigger » : https://www.emerce.nl/wire/main-capital-partners-verwerft-meerderheidsbelang-aanbieder-arbeidsmarktdata-jobdigger
38. S38 — Bibliothèque nationale, registre ISIL, Docu Media Schweiz GmbH : https://www.isil.nb.admin.ch/en/institutions/docu-media-schweiz-gmbh-schweizer-baudokumentation-ch-001088-1 ; S38b — Baublatt, brochure PDF : https://www.baublatt.ch/storage/csGURW5s9YHDo6TA0iaAWX9GSr2mgkimwR5PqPWE.pdf
39. S39 — LinkedIn, vitrine Batimag : https://ch.linkedin.com/showcase/batimagch ; S39b — Baublatt, « Basic Submissionen » PDF : https://www.baublatt.ch/bauauftraege/static/pdfs/20251023_Baublatt_Basic_Submissionen.pdf
40. S40 — Infopro Digital, « Acquisition of Bindexis by the Infopro Digital group » : https://www.infopro-digital.com/news/acquisition-of-bindexis-by-the-infopro-digital-group/ ; S40b — SuperOffice App Store, « Bindexis construction data » : https://appstore.superoffice.com/superoffice-as/bindexis-construction-data-for-superoffice ; S40c — Markt-kom, « NZZ Media Group buys Bindexis » : https://www.markt-kom.com/en/?p=75166
41. S41 — Netzwoche, « Houzy wühlt sich durch die Baugesuche der Schweiz » (2026-02-13) : https://www.netzwoche.ch/news/2026-02-13/houzy-wuehlt-sich-durch-die-baugesuche-der-schweiz
42. S42 — Centre de compétences des marchés publics (BKB), « simap.ch : lancement de la nouvelle plateforme » : https://bkb.admin.ch/fr/simapch-lancement-de-la-nouvelle-plateforme-de-publication ; S42b — PyPI, `swiss-procurement-mcp` 0.19.0 (**description lue directement**, « live-probe findings 2026-07-26 ») : https://pypi.org/project/swiss-procurement-mcp/
43. S43 — GitHub, `malkreide/amtsblatt-mcp` (**README lu directement**) : https://github.com/malkreide/amtsblatt-mcp
44. S44 — opendata.swiss, « batiments-projetes » : https://opendata.swiss/en/dataset/batiments-projetes
45. S45 — Organisator, « Stable hiring intentions among Swiss companies » (MEOS T1 2026) : https://www.organisator.ch/en/?p=42599
46. S46 — Adecco Group, Job Index T2 2026 (communiqué PDF) : https://www.adeccogroup.com/-/media/project/adecco-group/switzerland/job-index/job-index-q2-2026/job_index_q2_2026_medienmitteilung.pdf ; S46b — Job Index T1 2026 : https://www.adeccogroup.com/de-CH/-/media/project/adecco-group/switzerland/job-index/job-index-q1-2026/job_index_medienmitteilugn_2026_q1_-de.pdf ; Job Index T4 2025 : https://www.adeccogroup.com/-/media/project/adecco-group/switzerland/job-index/job-index-q4-2025/job_index_medienmitteilung_2025_q4_.pdf
47. S47 — Randstad NL, « Wat is Randstad Market Insights? » : https://www.randstad.nl/werkgevers/kenniscentrum/artikelen/nieuws/van-yip-naar-rmi ; S47b — Randstad, Workmonitor 2026 : https://content.randstad.ca/en-ca/download-workmonitor-2026
48. S48 — Organisator, « Swiss Staffingindex: Temporary staffing market turns positive after three years » : https://www.organisator.ch/en/?p=48185 ; S48b — Staffing Industry Analysts, « Swiss temp staffing returns to growth in March quarter » : https://www.staffingindustry.com/news/global-daily-news/swiss-temp-staffing-returns-to-growth-in-march-quarter
49. S49 — Great Place to Work Suisse, Interiman Group : https://greatplacetowork.ch/en/employer/interiman-group/ ; S49b — (référence retirée lors de l'audit du 2026-10-05 : profil personnel) ; allnews.ch, « Interiman Group améliore son chiffre d'affaires annuel de 18 % » : https://allnews.ch/node/93293
50. S50 — ORTE, « Travail intérimaire 2025 » (PDF, site SECO-TC) : https://www.secoalv.admin.ch/dam/secoalv/fr/dokumente/publikationen/studien/orte_travail_interimaire_2025.pdf.download.pdf/orte_travail_interimaire_2025.pdf
51. S51 — Textkernel, « Actionable Insights with Real-Time Labor Market Data » : https://www.textkernel.com/jobs-database/
