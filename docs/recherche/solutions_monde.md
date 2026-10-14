# Solutions dans le monde : chantiers, IA des agences, mesure de la demande, recherche

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

- **Date de consultation de toutes les sources : 2026-10-05.**
- Auteur : agent de recherche (Claude Code), pour l'équipe Proxsis.
- But : voir ce que font d'autres pays et les grands groupes, et en tirer des
  choix concrets pour Proxsis (Flexsis, agence locale) et pour Interiman
  (groupe multi-marques).
- Ce document **complète** sans les répéter :
  `international.md` (Dodge, ConstructConnect, Shovels, BuildZoom, Glenigan,
  PlanIt, Sitadel, BOAMP, DECP, TED, Doffin, Indeed Hiring Lab, LinkUp…),
  `marche.md` (ATS et outils IA, x28, Textkernel, Baublatt, Bindexis,
  Randstad Market Insights, Jobdigger…), `etat-de-l-art.md` (méthodes d'IA,
  OCDE, Turrell et al., CITB, Wong et al., équité) et
  `acces_offres_emploi.md` (accès légal aux offres suisses). Quand un sujet y
  est déjà traité, nous renvoyons au fichier.

## Méthode, limites et légende

**Méthode.** Recherche web (WebSearch) et lecture de pages publiques
(WebFetch). Les PDF publics importants ont été téléchargés dans un dossier
temporaire et leur **texte intégral** extrait par nous (`pdftotext`) : FAQ du
Dodge Momentum Index, rapport annuel 2023 de Byggfakta, rapports annuels 2025
de Randstad et d'Adecco, rapport semestriel 2025 de Synergie, méthodologie du
Swiss Job Tracker, note technique HWOL, méthodologie ONS–Adzuna, article de Le
Barbanchon et al., article BLS de 2011. Aucun compte créé. Aucun portail
d'emploi interrogé : **ni jobs.ch, ni jobup.ch, ni Indeed (indeed.com,
hiringlab.org), ni LinkedIn**, ni amtsblattportal.ch, ni le Bulletin officiel
du Valais, ni shab.ch. Les faits sur Indeed viennent du blog de sa maison mère
(Recruit Holdings) ou d'extraits de recherche.

**Limites.**
- Plusieurs pages ont été lues par un **outil de résumé automatique**. Nous
  avons trouvé deux erreurs de cet outil : il datait la méthodologie ONS de
  2022 (le PDF dit 14 juin 2021) et il ajoutait un chiffre (« 80 travailleurs »)
  à l'article de Gugler et al. que nous n'avons retrouvé nulle part. Ces
  erreurs ne sont **pas** reprises ici. Pour les chiffres clés, nous avons
  demandé le texte mot à mot ou lu le PDF nous-mêmes.
- Pages bloquées (403) ou trop lentes : ScienceDirect, Taylor & Francis, SSRN,
  Cedefop, ABC (PDF de méthode), BusinessWire, Infrastructure Australia,
  relations investisseurs de Kelly. Pour ces sources, seul l'extrait du moteur
  de recherche est utilisé, et c'est indiqué (**E**).
- Rien n'a été recalculé par nous. Les résultats des entreprises sont des
  **affirmations**. Les résultats des chercheurs sont **leurs** résultats.

**Légende (dans chaque tableau).**

| Code | Signification |
|---|---|
| **A** | **Affirmé par l'entreprise** (communiqué, rapport annuel, page produit). Non vérifié de façon indépendante. |
| **P** | Publication publique de méthode ou de recherche (office statistique, université, revue, document de travail). |
| **T** | Source tierce (presse, comparatif, agrégateur). |
| **L** | Source primaire **lue** par nous le 2026-10-05 (texte intégral ou citation demandée mot à mot). |
| **L\*** | Source primaire lue via l'outil de résumé automatique (risque d'imprécision). |
| **E** | **Extrait** de moteur de recherche seulement ; page non lue. |
| **Vérifié** | Point contrôlé par nous dans la source primaire (présence ou absence d'une mention, chiffre recopié du PDF). |

Exemple : « A·L » = affirmation de l'entreprise, lue dans son propre document.

---

## Résumé en huit points

1. **Deux groupes rachètent les fournisseurs de données de chantiers** en
   Europe et au-delà : **Hubexo** (ex-Byggfakta : Glenigan, BCI, Construction
   Monitor, **Olmero en Suisse**, INFO-TECHNO en Autriche) et **Infopro
   Digital** (Barbour ABI, ibau, Vecteur Plus, Bindexis). Leur modèle :
   l'abonnement ([W5](https://storage.mfn.se/6c117b66-56c8-445c-88e1-a54f8a654b19/byggfakta-group-annual-report-2023.pdf), [W9](https://www.ibau.de/ueber-ibau/unsere-geschichte/)).
2. **Leur méthode publique mélange collecte automatique et beaucoup de
   recherche humaine** (téléphone). Aucun ne publie de mesure indépendante de
   la qualité de ses leads.
3. **Un seul fournisseur étudié vend explicitement aux recruteurs** :
   Barbour ABI (Royaume-Uni). Il promet d'appeler avant la publication des
   postes. Il ne publie aucun résultat chiffré pour les agences ([W7](https://barbour-abi.com/business-type/recruiters/)).
4. **Les indicateurs avancés de la construction** (Dodge Momentum Index,
   Architecture Billings Index) annoncent un délai de **9 à 12 mois** entre la
   planification et la dépense ([W1](http://www.chapters.cfma.org/Update/Dodge_Momentum_Index.pdf), [W2](https://www.aia.org/resource-center/abi-may-2026-architecture-firm-billings-weaken-further)). En Suisse, le
   plus proche est l'enquête trimestrielle du Schweizerischer
   Baumeisterverband ([W19](https://baumeister.swiss/baumeister-5-0/konjunktur-statistiken/baukonjunktur/)).
5. **Les grands groupes de placement mettent leur IA surtout côté candidats**
   (tri, entretiens automatiques, matching). Côté clients, seul Randstad
   affirme prévoir la demande avant qu'elle soit visible. Aucun ne publie sa
   méthode ni une mesure indépendante ([W20](https://www.randstad.com/s3fs-media/rscom/public/2026-02/Randstad_Annual_Report_2025_F.pdf), [W24](https://www.adeccogroup.de/wp-content/uploads/the-adecco-group-annual-report-2025.pdf),
   [W27](https://go.manpowergroup.com/ceo-letter)).
6. **Les indices sérieux d'offres en ligne retirent les annonces d'agences**
   (Swiss Job Tracker, HWOL aux États-Unis). En Suisse, la Romandie et les
   petites entreprises peuvent être sous-couvertes ([W36](https://swissjobtracker.ch/Methodology%20Swiss%20Job%20Tracker.pdf),
   [W39](https://www.conference-board.org/pdf_free/press/TCB-Lightcast-HWOL-Technical-Note.pdf)).
7. **La recherche** montre que gagner un marché public augmente l'emploi
   **vite** (le mois ou le trimestre suivant), que les permis précèdent l'emploi
   de **plusieurs trimestres**, et que des recommandations algorithmiques
   aident l'appariement, à condition de surveiller l'équité ([R1](https://doi.org/10.3386/w21219),
   [R2](https://doi.org/10.1016/j.jpubeco.2019.104112), [R6](https://doi.org/10.1080/01446193.2025.2511833), [R8](https://doi.org/10.1086/689213), [R13](https://doi.org/10.3386/w27736)).
8. **Interiman utilise l'ATS EOLIA**, selon l'éditeur : 270 utilisateurs, une
   quinzaine d'entités, quatre langues ([W35](https://eolia-software.fr/cas-client/faciliter-la-relation-entre-clients-candidats-et-collaborateurs-interiman-group/)). Proxsis doit s'y
   brancher.

---

## 1. Renseignement sur les chantiers dans d'autres pays

### 1.1 Les deux groupes consolidateurs

| Groupe | Marques et pays | Modèle économique | Ce qui est public sur la méthode | Pour Flexsis | Pour Interiman | Sources |
|---|---|---|---|---|---|---|
| **Hubexo** (ex-Byggfakta Group, renommé le 1er octobre 2024) | Glenigan, NBS, CIS (Royaume-Uni, Irlande) ; BCI (Asie-Pacifique) ; Vortal ; **Construction Monitor** (États-Unis, racheté le 7 novembre 2023 via BCI Central) ; **OLMERO AG** (Opfikon, CH) ; **INFO-TECHNO Baudatenbank** (Autriche). 2 500 employés, plus de 20 pays (A·L\*). | Logiciels et contenus vendus par **abonnement**. En 2023 : 85,5 % du chiffre d'affaires en abonnements, taux de rétention nette 86,3 %, plus de 50 000 clients (A·L, rapport annuel p. 4). | Collecte propre. Plus de 250 chercheurs à Manille pour les pays anglophones (p. 5). La recherche repose sur le « cold calling » (p. 50). Le groupe prévoit d'investir davantage dans l'extraction automatique et la lecture de sites web (p. 50). Une équipe à Lisbonne travaille sur l'IA (p. 5) (A·L). | Sa filiale suisse Olmero est un **fournisseur possible** de permis et d'appels d'offres (voir 1.8). Utile pour tester notre couverture, pas pour bâtir l'outil. | Un fournisseur unique pour CH, AT et d'autres pays. Risque : dépendance et prix non publics. | [W4](https://www.prnewswire.com/news-releases/byggfakta-group-becomes-hubexo-and-announces-new-leadership-structure-302262331.html), [W5](https://storage.mfn.se/6c117b66-56c8-445c-88e1-a54f8a654b19/byggfakta-group-annual-report-2023.pdf), [W6](https://www.glenigan.com/about-us/) |
| **Infopro Digital** (France) | Barbour ABI (Royaume-Uni), ibau (Allemagne), Vecteur Plus (France), Bindexis (Suisse, voir `marche.md` S40). Selon ibau : 18 pays, 4 000 employés, 550 M€ de chiffre d'affaires (A·L\*). | Abonnements ; prix non publics (inconnu). | Recherche humaine forte (voir les pays ci-dessous). | Bindexis : déjà étudié dans `marche.md`. | Négociation possible à l'échelle du groupe, plusieurs pays. | [W7](https://barbour-abi.com/business-type/recruiters/), [W8](https://www.vecteurplus.com/sources-de-donnees-vecteur-plus/), [W9](https://www.ibau.de/ueber-ibau/unsere-geschichte/) |

### 1.2 États-Unis : des indicateurs avancés publics

| Acteur | Données et méthode publique | Modèle économique | Pour Flexsis | Pour Interiman | Sources |
|---|---|---|---|---|---|
| **Dodge Momentum Index** (Dodge, ex-McGraw-Hill Construction) | Indice mensuel des **premiers rapports de projets non résidentiels au stade de la planification**. Sur janvier 2002 à février 2012, corrélation de 91 % avec la dépense de construction non résidentielle du Département du Commerce, **avec 12 mois d'avance**. Données venant de reporters dans plus de 80 grandes villes, qui appellent 35 000 sources. Dodge se disait en 2012 le seul fournisseur privé de données de mises en chantier au Census Bureau (A·L, FAQ de 2012). | Indice publié ; base de projets vendue par abonnement (voir `international.md` I1). | Idée à reprendre : **le stade « planification » prédit l'activité un an plus tard**. Pour une cible à 8 semaines, c'est trop tôt ; c'est un contexte. | Indice cantonal « projets entrés en planification » pour piloter les capacités des marques construction. | [W1](http://www.chapters.cfma.org/Update/Dodge_Momentum_Index.pdf) |
| **Architecture Billings Index** (AIA, avec Deltek) | Indice de diffusion mensuel tiré d'une enquête auprès d'un panel de bureaux d'architectes (facturation en hausse, stable ou en baisse). 50 = pas de changement. L'AIA affirme qu'il **précède la construction non résidentielle d'environ 9 à 12 mois**. Valeur de mai 2026 : 44,5 (P·L\*). | Publication gratuite. | Montre qu'une **simple enquête mensuelle** (hausse/baisse) peut être un bon signal avancé. | Une enquête courte auprès des clients du groupe pourrait jouer ce rôle. | [W2](https://www.aia.org/resource-center/abi-may-2026-architecture-firm-billings-weaken-further) |
| **Construction Backlog Indicator** (ABC, association d'entrepreneurs) | Enquête mensuelle confidentielle auprès des membres. Réserve de travail convertie en mois : (réserve du mois ÷ chiffre d'affaires de l'année précédente) × 12. Ventilation par taille, région, segment (P·E). | Publication gratuite. | Concept utile : **« mois de travail en réserve »** d'un client. | Comparable à l'enquête SBV en Suisse (voir 1.8). | [W3](https://www.abc.org/Portals/1/ABC%20CBI_CCI%20Methodology%20June%202023.pdf) |
| **Construction Monitor** | Permis de construire (voir `international.md` I3). **Racheté le 7 novembre 2023 par BCI Central (Hubexo)**, vendu par abonnement aux fabricants et entrepreneurs (A·L). | Abonnement. | Aucun usage direct (marché américain). | Signe de la consolidation (point 1.1) : les mêmes groupes achètent les données de plusieurs pays. | [W5](https://storage.mfn.se/6c117b66-56c8-445c-88e1-a54f8a654b19/byggfakta-group-annual-report-2023.pdf) |

### 1.3 Royaume-Uni : un fournisseur qui vise les recruteurs

| Acteur | Données et méthode publique | Modèle économique | Pour Flexsis | Pour Interiman | Sources |
|---|---|---|---|---|---|
| **Barbour ABI** (Infopro Digital) | Page dédiée aux **recruteurs de la construction**. Promesse : repérer les projets à venir, les **attributions de contrats** et les entreprises impliquées, « often before roles are publicly advertised ». Contacts de décideurs (téléphones, e-mails). Équipe de recherche au Royaume-Uni : **plus d'un million d'appels par an**. 3 000 entreprises clientes. Aucun cas client d'agence de recrutement cité (A·L, textes demandés mot à mot). | Abonnement ; prix non public. | **C'est la thèse de Proxsis**, vendue au Royaume-Uni. Différence : Proxsis ne stocke **pas** de contacts de personnes (nLPD, règle 4) et estime un besoin par métier. | Preuve qu'un marché « leads de chantier pour recruteurs » existe. Aucune mesure de résultat publiée : Proxsis peut se distinguer par son backtest. | [W7](https://barbour-abi.com/business-type/recruiters/) |
| **Glenigan** (Hubexo) | Renseignement sur la construction au Royaume-Uni depuis 1973 ; appartient à Hubexo (A·L\*). Détails de méthode : voir `international.md` I6. | Abonnement. | Aucun usage direct (Royaume-Uni). | Même propriétaire qu'Olmero en Suisse : un interlocuteur commun possible. | [W6](https://www.glenigan.com/about-us/) |

### 1.4 France : IA et qualification par téléphone

| Acteur | Données et méthode publique | Modèle économique | Pour Flexsis | Pour Interiman | Sources |
|---|---|---|---|---|---|
| **Vecteur Plus** (Infopro Digital) | Plus de 12 000 sources en ligne (préfectures, communes, plateformes de marchés, BOAMP, JOUE, bases de permis, presse). Une IA indexe et trie les documents ; des analystes vérifient, enrichissent et **qualifient par téléphone et e-mail**. Plus de 6 000 clients, plus de 20 000 utilisateurs, « plus de 5 millions d'opportunités » détectées, 30 ans d'activité (A·L\*). | Abonnement ; prix non public. | Même schéma que Proxsis : **la machine trie, l'humain confirme**. Chez nous, le consultant confirme par son appel. | Une cellule centrale de qualification pourrait servir plusieurs marques. | [W8](https://www.vecteurplus.com/sources-de-donnees-vecteur-plus/) |

### 1.5 Allemagne et Autriche

| Acteur | Données et méthode publique | Modèle économique | Pour Flexsis | Pour Interiman | Sources |
|---|---|---|---|---|---|
| **ibau** (Münster, Infopro Digital) | Fondé en 1957. Annonce 130 collaborateurs de recherche, un contact direct avec les sources et une **double vérification humaine** (A·L\*). Offre d'emploi « Mitarbeiter Recherche Bauprojekte – Telefonie/Online » (E). Date d'entrée dans Infopro : inconnue. | Abonnement ; prix non public. | Aucun usage direct (Allemagne). Leçon : la double vérification. | Couvre l'Allemagne ; utile seulement pour des clients frontaliers. | [W9](https://www.ibau.de/ueber-ibau/unsere-geschichte/) |
| **DTAD** (Berlin) | Plus de 12 000 sources ; affirme couvrir 99,99 % des appels d'offres publics allemands ; assistant IA conversationnel « Frank » et recherche sémantique ; **équipe éditoriale** pour la qualité ; projets de construction DACH en option (A·L\*). | Abonnement ; prix non public. | Montre que les éditeurs ajoutent un assistant LLM **par-dessus** des données vérifiées, pas à la place. | Couverture DACH annoncée, à tester pour la Suisse. | [W10](https://www.dtad.com/en/) |
| **Hubexo Austria** (ex-INFO-TECHNO, Mondsee) | Portails ausschreibung.at et baudatenbank.at, actif depuis 1992 (E). **Racheté par Olmero le 1er juillet 2021** pour développer l'e-tendering en DACH (A·L\*). | Abonnement. | Aucun usage direct (Autriche). | Même groupe qu'Olmero : un contrat DACH serait possible. | [W11](https://www.olmero.ch/blog/olmero-uebernimmt-info-techno-baudatenbank-gmbh/) |
| **DOCUmedia** (Autriche) | Suit les phases discussion, planification, permis déposé, permis accordé, en construction, terminé. Recherche par IA sur Internet, **vérifiée par des chercheurs**. Environ 8 500 nouveaux projets commerciaux et 80 000 mises à jour par an ; plus de 100 000 projets (A·L\*). Propriétaire : inconnu. | Abonnement ; prix non public. | Exemple clair de **phases de projet** : modèle pour notre champ « stade ». | Même modèle « IA + chercheurs » qu'une éventuelle cellule de qualification du groupe. | [W12](https://www.documedia.at/services-und-leistungen/bauprojekte/) |

### 1.6 Pays-Bas

| Acteur | Données et méthode publique | Modèle économique | Pour Flexsis | Pour Interiman | Sources |
|---|---|---|---|---|---|
| **Cobouw Pro** et **Bouwberichten** (VMN media) | Page publique « Dataverantwoording » : environ 30 fournisseurs de données, dont registres publics (BAG, CBS, PDOK), marchés publics (TenderNed), base Bouwberichten, instituts (ABF Research, EIB, PBL, TNO). Elle dit elle-même que la liste **n'est pas complète** (A·L\*). Bouwberichten : plus de 400 000 projets aux Pays-Bas et en Belgique ; essai de 14 jours (A·E). | Abonnements séparés. | **Publier une page « d'où viennent nos données »** : bonne pratique à copier (catalogue des sources). | Idem, au niveau du groupe. | [W13](https://www.cobouw.nl/pro/dataverantwoording) |

Pour la demande de travail aux Pays-Bas (Jobdigger, Randstad Market
Insights), voir `marche.md`.

### 1.7 Australie et Canada : du portefeuille de projets au besoin par métier

| Acteur | Données et méthode publique | Modèle économique | Pour Flexsis | Pour Interiman | Sources |
|---|---|---|---|---|---|
| **Cordell Connect** (Cotality, ex-CoreLogic) | Base de projets de construction : environ 2 000 nouveaux projets et 5 000 mises à jour par mois, 650 sources, toutes phases (A·L\*). | **Prix public** : offre « Lite » dès 577,50 AUD par mois, minimum 6 930 AUD par an, un État, deux utilisateurs (A·L\*). | Un des rares prix publics : ordre de grandeur pour une **licence par région**. | Tarification par région et par nombre d'utilisateurs, transposable par canton et par marque. | [W14](https://www.cotality.com/products/cordellconnect) |
| **BCI Central / Hubexo APAC** | Service de leads de projets depuis 1998 ; 6 000 clients, 9 pays, 700 employés (A·L\*). | Abonnement. | Aucun usage direct (Asie-Pacifique). | Aucun usage direct ; confirme la taille de Hubexo. | [W15](https://apac.hubexo.com/about/) |
| **Infrastructure Australia** (organisme public) — *Market Capacity Report* | Estime la main-d'œuvre nécessaire au **portefeuille des grands projets publics**, plus l'investissement privé : la dépense mensuelle de chaque projet est multipliée par des ratios de ressources par type de projet, pour obtenir des équivalents plein temps par métier (P·E). Rapport 2025 : pénurie de métiers et manœuvres qui culminerait vers 126 000 personnes mi-2027 (P·E). | Rapport public, gratuit. | Même logique que notre module « coefficient × gabarit » (`etat-de-l-art.md` §2), à l'échelle d'un pays. | **Modèle pour un tableau de bord groupe** : besoin par métier et par canton, tiré des adjudications et des permis. | [W16](https://www.infrastructureaustralia.gov.au/reports/2025-infrastructure-market-capacity-report) |
| **BuildForce Canada** (organisme sectoriel) | Traduit les prévisions d'investissement en emploi pour plus de 30 métiers de la construction (34 selon un extrait), par province, sur 10 ans. Les chiffres sont revus par des **comités régionaux** (employeurs, syndicats, pouvoirs publics, formation) (P·L\*). Suit près de 800 grands projets de plus de 500 G$ (T·E). | Synthèses gratuites ; séries détaillées payantes (P·L\*). | Aucun usage direct (Canada). Idée : faire relire les estimations de besoin par les consultants. | **Validation par des comités régionaux** : équivalent possible avec les chefs d'agence d'Interiman. | [W17](https://www.buildforce.ca/en/about-the-data/) |

### 1.8 Suisse : à comparer avec ce qui précède

| Acteur | Données et méthode publique | Modèle économique | Pour Flexsis | Pour Interiman | Sources |
|---|---|---|---|---|---|
| **Olmero / Hubexo Switzerland AG** (Opfikon) | Absent de `marche.md`. Plateforme suisse d'appels d'offres et de **données de construction** : demandes de permis (Baugesuche), permis accordés, appels d'offres publics et privés, du dépôt jusqu'à l'attribution. Module « SMART » : plus de 40 000 projets, plus de 500 filtres, contacts de décideurs ; **aucune IA mentionnée** (A·L\*). Information quotidienne sur les nouveaux permis de toute la Suisse (A·E). | Abonnement ; prix non public (inconnu). | **Référence pour mesurer la couverture** de nos connecteurs de permis (recommandation 3). Ne pas reprendre les contacts de personnes. | Licence de groupe possible, à négocier seulement après mesure du gain. | [W5](https://storage.mfn.se/6c117b66-56c8-445c-88e1-a54f8a654b19/byggfakta-group-annual-report-2023.pdf), [W18](https://www.olmero.ch/en/smart-en/) |
| **Enquête trimestrielle du SBV** (Schweizerischer Baumeisterverband) | Enquête trimestrielle auprès des entreprises du gros œuvre : activité, entrées de commandes, **réserves de travail**, etc. ; ventilation par région, branche et taille ; en partie publique (P·L\*). Elle sert de base au « Bauindex » du SBV (P·E). | Publication de branche. | Contexte trimestriel pour la conversation client (« les carnets de commandes montent en Suisse romande »). | Variable **régionale** pour le modèle et pour piloter les capacités. Équivalent suisse de l'indicateur ABC. | [W19](https://baumeister.swiss/baumeister-5-0/konjunktur-statistiken/baukonjunktur/) |

### 1.9 Ce qu'on retient du volet chantiers

- **Partout, la donnée vient d'un mélange machine + humain** : reporters
  (Dodge), un million d'appels par an (Barbour ABI), 250 chercheurs et appels
  à froid (Byggfakta), qualification téléphonique (Vecteur Plus), double
  vérification (ibau), chercheurs + IA (DOCUmedia).
- **Le stade du projet est la variable centrale** (planification, permis,
  appel d'offres, attribution, chantier). Les délais vers l'activité vont de
  quelques semaines (attribution) à un an (planification).
- **Le marché « leads de chantier pour recruteurs » existe** (Barbour ABI),
  mais sans mesure publique du résultat.
- **Le besoin en personnel par métier** n'est calculé que par des
  organismes publics, au niveau d'un pays ou d'une province (Infrastructure
  Australia, BuildForce Canada, CITB au Royaume-Uni dans `etat-de-l-art.md`
  §2). Aucun fournisseur privé étudié ne le calcule **par entreprise**.

---

## 2. L'IA des agences de placement : ce que les groupes disent publiquement

Tout ce tableau est **affirmé par les entreprises**. Aucun chiffre n'a été
vérifié de façon indépendante.

| Groupe | Côté clients (prospection, prévision de la demande) | Côté candidats (tri, matching) | Chiffres affirmés | Pour Flexsis | Pour Interiman | Sources |
|---|---|---|---|---|---|---|
| **Randstad** | Rapport annuel 2025 : « we forecast staffing demand before the need becomes apparent to clients » (p. 17). Passage annoncé d'un placement réactif vers des solutions fondées sur la prévision (avril 2025). **Randstad Market Insights en service dans 11 pays** (p. 35). Méthode : non publiée (inconnu). | Plateforme interne « Randstad Talent Platform » avec matching par IA ; **audit des systèmes de matching** annoncé ; programme « IA responsable » inspiré du règlement européen sur l'IA (p. 29 et 104 du PDF). Partenariat Workday (février 2025) : un agent IA de Workday cherche des candidats aussi dans le réseau Randstad. | Places de marché numériques : environ 4 G€ de revenu annualisé ; aux États-Unis (activité opérationnelle), taux de pourvoi hebdomadaire passé de 71 % à 78 % en un an ; la plupart des commandes pourvues en moins de trois heures (A·L). | La promesse « prévoir avant que le client voie le besoin » est **exactement** celle de Proxsis. Randstad ne publie pas comment : Proxsis peut publier son backtest. | Modèle de groupe : une couche « marché » (RMI) + une plateforme commune. Proxsis peut être la brique « signaux publics » d'un tel outil. | [W20](https://www.randstad.com/s3fs-media/rscom/public/2026-02/Randstad_Annual_Report_2025_F.pdf), [W21](https://www.randstad.com/press/2025/randstad-executes-its-partner-talent-strategy-to-become-digital-first-talent-company/), [W22](https://www.randstad.com/press/2025/workday-randstad-partner-to-transform-hiring-with-ai/), [W23](https://www.randstad.com/press/2026/fy-2025-perform-transform/) |
| **Adecco Group** | Aucune mention d'IA pour la prospection client trouvée dans le rapport annuel 2025 (**vérifié** par recherche de mots-clés, non exhaustive). Un témoignage sur Market IQ (Textkernel) est cité dans `marche.md`. | Agents IA « agentiques » lancés au Royaume-Uni et en France : sourcing, tri, matching, aide aux consultants (p. 14). Objectif : que des agents IA **couvrent plus de 50 % du chiffre d'affaires** de la marque Adecco fin 2026 (p. 12). Licence illimitée Salesforce Agentforce jusqu'en 2027 (mars 2026). | +550 points de base de taux de pourvoi sur les grands comptes ; 5 solutions agentiques en service ; 50 % des interactions hors heures de bureau (p. 14) ; environ 27 000 recruteurs et 100 000 clients ; 15 % de temps gagné au Royaume-Uni ; premier test : 28 entreprises servies, satisfaction 4,6/5 (A·L / A·L\*). | Le tri et le premier contact des candidats sont déjà automatisés chez les concurrents : Proxsis ne doit pas se battre là-dessus. | Montre l'ampleur du virage chez le n° 1 suisse (voir `contexte.md`). | [W24](https://www.adeccogroup.de/wp-content/uploads/the-adecco-group-annual-report-2025.pdf), [W25](https://www.adeccogroup.com/our-group/media/press-releases/the-adecco-group-completes-successful-first-agentic-ai-implementation-at-scale), [W26](https://www.prnewswire.com/news-releases/the-adecco-group-to-scale-agentic-ai-at-speed-with-unlimited-agentforce-license-agreement-302711588.html) |
| **ManpowerGroup** | Plateforme IA « Sophie » pour les flux de travail des **recruteurs et des commerciaux** (lettre du CEO 2025). « Hub IA RH » à Paris avec un axe « solutions clients » par IA et analyse prédictive (A·E). Méthode : inconnue. | Entretiens structurés par IA avec Hubert (mars 2026), annoncés comme plus cohérents et moins biaisés. | Environ 90 % de l'activité sur la plateforme PowerSuite, plus de 70 pays ; plus de 60 % des entretiens IA hors heures de bureau (A·L\*). | Concurrent : le premier contact candidat est déjà automatisé chez lui. | Plateforme technique commune à toutes les marques : condition pour que des signaux clients soient utiles partout. | [W27](https://go.manpowergroup.com/ceo-letter), [W28](https://investor.manpowergroup.com/news-releases/news-release-details/manpowergroup-scales-human-first-ai-interviewing-address-global), [W29](https://investor.manpower.com/news-releases/news-release-details/manpowergroup-announces-investment-new-paris-based-ai-hr-hub) |
| **Kelly Services** | Rien trouvé sur la prospection. | Agent IA qui **appelle, trie et répond aux candidats**, déployé pour un grand client industriel multinational afin de staffer une ligne d'assemblage (appel des résultats du 4e trimestre 2025) (A·E). | Aucun chiffre trouvé. | Cas proche de l'industrie suisse : le premier contact candidat s'automatise. | Aucun chiffre publié : rien à reprendre tel quel. | [W30](https://ir.kellyservices.com/static-files/a9ae6095-23ff-4c3f-9782-4e94d2782054) |
| **Recruit Holdings / Indeed** | Indeed vend aux employeurs, pas aux agences. Talent Scout aide les employeurs à trouver des candidats (A·L\*) et à améliorer leurs annonces (A·E). | Deux agents IA annoncés en septembre 2025 : Career Scout (candidats) et Talent Scout (employeurs) (A·L\*). | Pour Career Scout, premiers résultats annoncés : recherche sept fois plus rapide et 38 % de chances d'embauche en plus (A·E). | Indeed n'est **pas** interrogé par Proxsis (règle 5). | Concurrence indirecte : les employeurs reçoivent des candidats sans passer par une agence. | [W31](https://recruit-holdings.com/en/blog/post_20251030_0001/) |
| **Gi Group** | Rien trouvé sur la prospection. | En Italie : « Spinner + », gestion de la relation candidats avec sourcing et « Search & Match » sur plus de 2,5 millions de candidats potentiels ; « Hirematic », plateforme propre de diffusion programmatique des annonces avec IA (A·L, textes mot à mot). | 2,5 millions de candidats potentiels (A·L). | Concurrent confirmé en Suisse romande (`contexte.md`) ; son outillage vise les candidats. | Aucun outil client publié : l'espace « signaux clients » reste libre. | [W32](https://www.gigroup.it/aziende/soluzioni/rpo/) |
| **Synergie** | **Aucune mention de l'IA** dans le rapport financier semestriel 2025 ; seule la « transformation digitale » apparaît, dans la partie risques informatiques (**vérifié**, texte intégral lu). Rapport annuel 2025 : non lu. | Idem. | — (aucun chiffre) | Aucun usage direct. | Aucun usage direct. | [W33](https://www.synergie.com/system/files/RAPPORT_FINANCIER_SEMESTRIEL_2025.pdf) |
| **Interiman Group** | Rien trouvé sur la prospection. | Article du groupe (7 juillet 2025) : près d'**un million de candidatures par an** ; l'IA sert aux dossiers numériques, à la gestion documentaire, aux tâches répétitives ; « L'IA nous permet de dégager du temps pour ce qui compte vraiment » (directeur digital et marketing) (A·L\*). ATS **EOLIA** déployé pour 270 utilisateurs, une quinzaine d'entités, quatre langues, avec lien vers l'outil de contrats E@syTemp (cas client publié par Eolia le 6 mars 2024) (A·L, texte lu). | 1 million de candidatures par an (A). | Le discours du groupe (« l'humain au centre ») colle à la règle « l'outil aide, le consultant décide ». | **Point d'intégration concret** : EOLIA. À confirmer avec Interiman : version, API, champs disponibles, et si Flexsis l'utilise. | [W34](https://www.interiman-group.ch/ia-et-recrutement-lhumain-au-coeur-du-projet-de-interiman-group/), [W35](https://eolia-software.fr/cas-client/faciliter-la-relation-entre-clients-candidats-et-collaborateurs-interiman-group/) |

**Lecture.**
- L'IA publique des groupes porte surtout sur **les candidats** : tri,
  premier contact, entretiens, matching. C'est là que les gains de
  productivité sont annoncés.
- Côté **clients**, parmi les groupes étudiés, seuls Randstad (prévision,
  RMI dans 11 pays) et ManpowerGroup (Sophie pour les commerciaux) en parlent. **Aucun ne publie sa
  méthode, ses données ou une mesure de précision.**
- Tous les chiffres sont auto-déclarés. Proxsis doit rester sur sa ligne :
  P@10, jours d'avance et intervalles issus d'un backtest reproductible.

---

## 3. Mesurer la demande de travail en temps réel

L'Indeed Hiring Lab (pas de série suisse) et les travaux OCDE sur la
représentativité sont déjà traités dans `international.md` (I23) et
`etat-de-l-art.md` (§1, réf. [3] et [4]). L'accès juridique aux offres
suisses est traité dans `acces_offres_emploi.md`. Ici : **méthodes et
limites**.

| Dispositif | Méthode | Annonces d'agences | Limites déclarées | Pour Flexsis | Pour Interiman | Sources |
|---|---|---|---|---|---|---|
| **Swiss Job Tracker** (KOF ETH Zurich, Université de Lausanne, x28 ; méthodologie de novembre 2022) | Données x28 lues chaque semaine par API. Indices hebdomadaires d'**offres uniques** par branche, grand groupe de métiers et canton. Un portail = site avec plus de 100 entreprises ; règle pour gérer l'entrée et la sortie des portails. Corrélation de **0,96** avec la statistique officielle des postes vacants (BESTA, trimestrielle, publiée avec plusieurs mois de retard). Couverture estimée : au moins 90 % des postes publiés en ligne et environ 72 % de tous les postes (P·L). | **Toutes retirées.** Elles font jusqu'à la moitié des annonces certains trimestres, alors que le travail temporaire pèse 2 à 3 % de l'emploi ; séries erratiques ; certaines seraient des annonces « fantômes » pour remplir un vivier (P·L). | Possible **sous-couverture de la Suisse romande** (et plus nettement de la Suisse italienne) ; trous possibles pour les entreprises de 25 employés ou moins (P·L). | Contexte régional hebdomadaire. **Attention** : la Romandie peut être sous-représentée. | Indice gratuit par canton et métier pour le pilotage. | [W36](https://swissjobtracker.ch/Methodology%20Swiss%20Job%20Tracker.pdf), [W37](https://kof.ethz.ch/en/forecasts-and-indicators/indicators/swiss-job-tracker.html) |
| **Lightcast** (Job Posting Analytics) | Plus de 220 000 sources ; dédoublonnage en deux étapes qui retire jusqu'à 80 % des annonces collectées ; fenêtre de 60 jours ; une annonce expire au plus tard après 120 jours. « Job postings are not necessarily the same as job vacancies » (A·L\*). | Pas de règle spécifique trouvée sur la page lue. | Annonces ≠ postes vacants ; identification de l'employeur plus faible dans certains marchés (A·L\*). | Trop cher et peu suisse (voir `marche.md`). | Possible pour des clients multinationaux. | [W38](https://kb.lightcast.io/en/articles/6957446-job-posting-analytics-jpa-methodology) |
| **Help Wanted OnLine** (Conference Board + Lightcast, États-Unis) | Plus de 45 000 domaines. Exclut les agrégateurs (sources de doublons) et les annonces anonymes. Depuis 2020, l'indice est **calé sur la statistique officielle JOLTS**. Séries par État, métropole, métier (P·L). | **Exclues** : jugées trop volatiles et peu révélatrices des embauches réelles (P·L). | Sous-couverture si une grande source manque ; sur-couverture si des doublons restent ; erreurs de codage métier et lieu (P·L). | Même règle que le Swiss Job Tracker : **exclure les agences**. | Caler un indice privé sur la statistique officielle (BESTA en Suisse). | [W39](https://www.conference-board.org/pdf_free/press/TCB-Lightcast-HWOL-Technical-Note.pdf) |
| **Eurostat — Web Intelligence Hub (OJA)** et **Cedefop — Skills-OVATE** | Inventaire des portails par des experts nationaux, collecte, nettoyage, dédoublonnage, extraction par ontologies et apprentissage automatique ; statistiques **expérimentales** (P·L\*). Environ 200 millions d'offres collectées depuis 2018 ; concours public de dédoublonnage (doublons complets, sémantiques, temporels, partiels) (P·E). | Les agences sont une des sources collectées (P·L\*). | Pas toutes les offres sont en ligne ; certains métiers sont plus publiés que d'autres ; erreurs de classification (P·L\*). **Couverture de la Suisse : non confirmée** (un extrait cite les pays de l'AELE ; un article de 2019 citait sept pays) (E, T). | Aucun usage direct tant que la Suisse n'est pas confirmée. | Typologie des doublons réutilisable telle quelle. | [W40](https://cros.ec.europa.eu/wih/oja), [W41](https://cros.ec.europa.eu/book-page/issue-23-lessons-learned-eurostats-deduplication-challenge), [W42](https://www.cedefop.europa.eu/en/tools/skills-intelligence/skills-online-job-advertisements) |
| **ONS + Adzuna** (Royaume-Uni, statistique expérimentale, 14 juin 2021) | Indices hebdomadaires d'annonces en ligne, publiés six jours après l'extraction ; base février 2020 = 100 ; dédoublonnage par similarité de texte, volontairement strict (P·L). | Une baisse d'activité des agences peut faire baisser les doublons, donc le nombre d'annonces. L'enquête officielle britannique sur les postes vacants **exclut les agences d'emploi** pour éviter le double comptage (P·L). | Une annonce n'est pas une mesure directe de la demande ; annonces pas retirées à temps ; travail occasionnel annoncé hors ligne (P·L). | Rappel : **une annonce n'est qu'un indicateur** (déjà dans `docs/backtest/cibles.md`). | Méthode de dédoublonnage strict, simple à reprendre. | [W43](https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/conditionsanddiseases/methodologies/usingadzunadatatoderiveanindicatorofweeklyvacanciesexperimentalstatistics/pdf) |
| **Emploi intérimaire comme indicateur avancé** (BLS, États-Unis) | L'intérim « mène régulièrement » les fluctuations de l'emploi total. Il a perdu 93 000 emplois dans les 16 mois **avant** la récession de 2007–2009, puis 31 % de ses effectifs (P·L). | Sans objet. | Série nationale américaine. | Argument commercial : quand l'intérim baisse, la prospection devient prioritaire. | Les heures de mission du groupe pourraient **elles-mêmes** servir d'indicateur avancé régional (hypothèse à tester). | [W44](https://www.bls.gov/opub/mlr/2011/04/art6full.pdf) |

**Limites communes (à retenir pour Proxsis).**
1. Une annonce n'est pas un poste vacant, ni une embauche ([W38](https://kb.lightcast.io/en/articles/6957446-job-posting-analytics-jpa-methodology),
   [W43](https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/conditionsanddiseases/methodologies/usingadzunadatatoderiveanindicatorofweeklyvacanciesexperimentalstatistics/pdf)).
2. Les doublons sont la première source d'erreur ; ils prennent plusieurs
   formes ([W41](https://cros.ec.europa.eu/book-page/issue-23-lessons-learned-eurostats-deduplication-challenge)).
3. Les annonces d'agences faussent les séries : les indices sérieux les
   retirent ([W36](https://swissjobtracker.ch/Methodology%20Swiss%20Job%20Tracker.pdf), [W39](https://www.conference-board.org/pdf_free/press/TCB-Lightcast-HWOL-Technical-Note.pdf), [W43](https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/conditionsanddiseases/methodologies/usingadzunadatatoderiveanindicatorofweeklyvacanciesexperimentalstatistics/pdf)).
4. La couverture varie selon la région, la taille d'entreprise et le métier
   ([W36](https://swissjobtracker.ch/Methodology%20Swiss%20Job%20Tracker.pdf)).
5. L'entrée ou la sortie d'un portail crée de fausses ruptures
   ([W36](https://swissjobtracker.ch/Methodology%20Swiss%20Job%20Tracker.pdf)).
6. Les changements de canal (obligation d'annonce, voir `etat-de-l-art.md`
   §1) déplacent les offres sans changer la demande.

---

## 4. Littérature académique

Déjà couverts dans `etat-de-l-art.md` : Turrell et al., Hershbein & Kahn,
OCDE, Kureková et al., Hangartner et al., Wong et al., Zhao et al., CITB,
Census (délai permis → démarrage), Raghavan et al., Bertrand & Mullainathan,
méthodes de survie, de classement et d'équité. Ci-dessous : **références
nouvelles**.

### 4.1 Marchés publics et emploi

| Référence | Données et méthode | Résultat principal | Usage Flexsis / Interiman | Lien |
|---|---|---|---|---|
| Ferraz, Finan & Szerman (2015), *Procuring Firm Growth*, NBER WP 21219 | Brésil 2004–2010 : toutes les entreprises formelles (données employeurs-salariés) et tous les marchés fédéraux. Comparaison gagnants / perdants de la même procédure (P·L\*). | Gagner au moins un marché dans un trimestre augmente la croissance de l'entreprise de **2,2 points dans ce trimestre** ; 93 % des nouvelles embauches viennent du chômage ou de l'informel ; effet durable (P·L\*). | **Flexsis** : l'adjudication est un signal **rapide** (même trimestre). **Interiman** : l'effet dure, donc suivre les gagnants réguliers. | https://doi.org/10.3386/w21219 |
| Gugler, Weichselbaumer & Zulehner (2020), *Journal of Public Economics* 182, 104112 | **Autriche, construction**, 2006–2009 : environ 600 entreprises, plus de 2 500 enchères, emploi quotidien. Gagnants comparés aux deuxièmes (P·L\*). | Avant la crise, les gagnants ajoutent des emplois par rapport aux deuxièmes ; pendant la crise, non (rétention de main-d'œuvre). L'ajustement se fait **surtout dans le mois qui suit l'enchère**, et passe plutôt par moins de licenciements. Pas d'effet sur les salaires (P·L\* ; délai et licenciements : P·E). | **Flexsis** : fenêtre courte après une adjudication ; l'effet dépend de la conjoncture (en creux, l'entreprise garde ses gens au lieu d'embaucher). **Interiman** : ajouter une variable de conjoncture régionale. | https://doi.org/10.1016/j.jpubeco.2019.104112 |
| Hebous & Zimmermann (2021), *Journal of Monetary Economics* 118, 178–194 | États-Unis, marchés fédéraux, données d'entreprises (P·L\*). | 1 $ de commande publique augmente l'investissement de l'entreprise de 7 à 11 cents, surtout chez les entreprises contraintes financièrement (P·L\*). | Indirect : l'effet est plus fort chez les entreprises **contraintes financièrement**. DOI non relevé. | https://ideas.repec.org/p/imf/imfwpa/2016-060.html |

### 4.2 Permis de construire, signaux économiques et emploi

| Référence | Données et méthode | Résultat principal | Usage Flexsis / Interiman | Lien |
|---|---|---|---|---|
| Strauss (2013), *Journal of Urban Economics* 73(1), 77–93 | États américains, trois décennies ; prévisions hors échantillon (P·L\*). | Les permis précèdent l'activité dans presque tous les États et prévoient mieux l'emploi que l'indice avancé et les prix immobiliers ; avance d'environ **quatre trimestres** (P·E pour ce délai). | **Interiman** : les permis servent à prévoir l'activité **régionale** à un an. **Flexsis** : trop lent pour la cible de 8 semaines. | https://doi.org/10.1016/j.jue.2012.07.005 |
| Ghent & Owyang (2010), *Journal of Urban Economics* 67(3) | 51 villes américaines (P·E). | Les **permis nationaux** prévoient mieux l'emploi d'une ville que les permis de la ville elle-même (P·E). | Prudence : un signal local est bruité ; combiner local et national/cantonal. DOI non relevé. | https://ideas.repec.org/p/fip/fedlwp/2009-007.html |
| Shiha & El-adaway (2025), *Construction Management and Economics* 43(10), 765–793 | Données publiques ; tests de Granger, cointégration, panels à effets fixes ; États-Unis, Canada, UE, Royaume-Uni (P·L\*). | UE et Royaume-Uni : +1 % de permis → **+0,63 % de postes vacants dans la construction cinq trimestres plus tard** ; aux États-Unis et au Canada, taux d'intérêt et exportations mènent de 12 à 15 mois (P·L\*). | **Interiman** : ordre de grandeur pour un modèle cantonal de pénurie. À recaler sur des données suisses. | https://doi.org/10.1080/01446193.2025.2511833 |
| Conlon (2011), *Monthly Labor Review* (BLS), avril 2011 | Séries d'emploi américaines 1990–2010 (P·L). | L'intérim mène régulièrement l'emploi total (voir section 3) (P·L). | Contexte. | https://www.bls.gov/opub/mlr/2011/04/art6full.pdf |
| Forsythe, Kahn, Lange & Wiczer (2020), *Journal of Public Economics* 189 ; NBER WP 27061 | Offres Burning Glass en temps réel, demandes d'assurance chômage, BLS (P·E). | Les offres ont chuté de plus de 40 % fin avril 2020, dans tous les États (P·E). | Les offres réagissent vite aux chocs : bonne **cible**, pas bonne avance. | https://www.nber.org/papers/w27061 |

### 4.3 Appariement candidats–postes et équité

| Référence | Données et méthode | Résultat principal | Usage Flexsis / Interiman | Lien |
|---|---|---|---|---|
| Horton (2017), *Journal of Labor Economics* 35(2), 345–385 | Expérience randomisée sur oDesk : recommandations algorithmiques de candidats aux employeurs (P·L\*). | **+20 % de taux de pourvoi** pour les offres techniques recommandées ; pas d'éviction des candidats non recommandés (P·L\*). | **Flexsis** : proposer 3 à 5 candidats peut aider, sans exclure les autres. | https://doi.org/10.1086/689213 |
| Le Barbanchon, Hensvik & Rathelot (2023), document de travail (J-PAL) | Service public de l'emploi suédois : recommandeur par filtrage collaboratif, **59 millions de recommandations**, expérience randomisée des deux côtés ; registre AEA AEARCTR-0003616 (P·L). | +0,6 % d'emploi à six mois ; recommander une offre augmente de 5 % la probabilité de travailler dans cet établissement ; effets plus forts pour les moins diplômés et les chômeurs ; peu de congestion (P·L). | Les recommandations aident surtout les **profils les moins favorisés** : à mesurer par groupe. | https://www.povertyactionlab.org/sites/default/files/research-paper/WP4642_How-can-AI-improve-search-and-matching-in-Sweden_Rathelot-et-al_July2023.pdf |
| Bied et al. (2023), IJCAI, 5906–5914 | Service public de l'emploi français ; matrice très creuse, millions de demandeurs (P·L\*). | Rappel égal ou meilleur que l'état de l'art, inférence 100 fois plus rapide ; l'écart lié au genre est statistiquement semblable dans les vraies données et dans les recommandations (P·L\*). | Méthode d'**audit** réutilisable : comparer l'écart par groupe avant et après recommandation. | https://doi.org/10.24963/ijcai.2023/655 |
| Bied et al. (2026), arXiv:2603.21699 | Deux expériences randomisées avec le service public de l'emploi français (P·L\*). | Classer les offres sur une seule dimension (goût du candidat **ou** chance d'embauche) est sous-optimal ; il faut combiner les deux (P·L\*). | Pour « Candidats suggérés » : combiner **adéquation** et **chance réelle d'être retenu**. | https://arxiv.org/abs/2603.21699 |
| Hoffman, Kahn & Li (2018), *Quarterly Journal of Economics* 133(2), 765–800 ; NBER WP 21709 | Introduction de tests d'embauche dans 15 entreprises de services peu qualifiés (P·L\*). | Les managers qui passent outre les recommandations du test embauchent **en moyenne des personnes qui restent moins longtemps** (P·L\*). | **Journaliser** quand le consultant ne suit pas la proposition, et pourquoi ; mesurer ensuite. Le consultant garde la décision (nLPD art. 21). | https://doi.org/10.3386/w21709 |
| Li, Raymond & Bergman (2026), *Review of Economic Studies* 93(2), 1200–1240 ; NBER WP 27736 | Tri de CV dans une grande entreprise de services ; algorithme d'« exploration » (UCB) comparé à l'apprentissage supervisé (P·L\*). | L'exploration améliore la qualité des candidats retenus pour entretien **et** la diversité ; l'apprentissage supervisé classique réduisait fortement la part de candidats noirs et hispaniques (P·L\*). | Garder une **place d'exploration** dans la liste de candidats (profil moins habituel mais plausible). | https://doi.org/10.3386/w27736 |
| Fabris et al. (2025), *ACM Transactions on Intelligent Systems and Technology* ; arXiv:2309.13933 | Revue pluridisciplinaire : systèmes, biais, mesures, correctifs, jeux de données, droit (P·L\*). | Synthèse équilibrée des risques et des moyens de mesure (P·L\*). | Liste de contrôle pour l'audit d'équité (`fairness`). DOI 10.1145/3696457 (E). | https://arxiv.org/abs/2309.13933 |
| de Ruijt & Bhulai (2021), arXiv:2111.13576 | Revue des systèmes de recommandation d'emploi 2011–2021 (P·E). | Insiste sur la nature **réciproque** et **temporelle** de l'appariement, et sur l'équité (P·E). | Rappel : le client doit aussi vouloir le candidat. | https://arxiv.org/abs/2111.13576 |
| Bogen & Rieke (2018), *Help Wanted*, Upturn | Rapport sur les outils d'embauche prédictifs (T·E). | Les données d'entraînement reflètent les inégalités passées ; décisions peu transparentes (T·E). | Ne pas apprendre le matching sur les placements passés sans audit. | https://www.upturn.org/reports/2018/hiring-algorithms/ |

### 4.4 Notation de prospects (lead scoring)

| Référence | Données et méthode | Résultat principal | Usage Flexsis / Interiman | Lien |
|---|---|---|---|---|
| Wu, Andreev & Benyoucef (2024), *Information Technology and Management* 25(1), 69–98 | Revue systématique de 44 études publiées de 2005 à 2022 (P·E). | La classification domine ; arbres de décision et régression logistique sont les plus utilisés ; 14 mesures d'impact sur la vente ; les modèles prédictifs devraient remplacer les règles d'expérience (P·E). | Conforte le choix « logistique d'abord » (`etat-de-l-art.md` §4). DOI non relevé. | https://ouci.dntb.gov.ua/en/works/4wd0qLdl/ |
| González-Flores, Rubiano-Moreno & Sosa-Gómez (2025), *Frontiers in Artificial Intelligence* | Un éditeur de logiciels B2B, janvier 2020 à avril 2024, 16 600 prospects après nettoyage, 15 algorithmes, découpage 70/30 (P·L\*). | Gradient boosting le meilleur : exactitude 98,4 %, AUC 0,989 (P·L\*). | **Mise en garde (notre lecture)** : des scores aussi hauts sur une seule entreprise appellent un contrôle de fuite ; nous n'avons pas vérifié si le découpage respecte l'ordre du temps. Exemple de ce que Proxsis ne doit pas faire (règle « vu à la date T »). | https://doi.org/10.3389/frai.2025.1554325 |

---

## 5. Carte des solutions

Pertinence : **forte**, **moyenne**, **faible**. Jugement de l'auteur tiré
des sections 1 à 4, pas un fait.

| Catégorie | Acteurs (pays) | Données | Pertinence Flexsis (agence locale) | Pertinence Interiman (groupe) |
|---|---|---|---|---|
| Indicateurs avancés de la construction | Dodge Momentum Index (US), AIA ABI (US), ABC CBI (US), enquête SBV (CH) | Projets en planification, facturation d'architectes, réserves de travail | **Faible** : trop agrégé pour une liste d'appels ; utile en conversation client. | **Moyenne** : variable régionale et pilotage des capacités (SBV). |
| Bases de projets privés avec recherche humaine | Dodge (US), Glenigan et Barbour ABI (UK), Vecteur Plus (FR), ibau et DTAD (DE), DOCUmedia et Hubexo Austria (AT), Cobouw/Bouwberichten (NL), Cordell (AU) | Projets par stade, intervenants, contacts | **Faible** : hors Suisse. Leçon de méthode : stade du projet + vérification humaine. | **Moyenne** : modèle de cellule centrale de qualification. |
| Données suisses de construction (achat) | Olmero / Hubexo Switzerland, Baublatt/Batimag, Bindexis (voir `marche.md`) | Demandes et permis, appels d'offres, attributions | **Moyenne** : référence pour mesurer notre couverture ; achat seulement si gain prouvé. | **Forte** : licence de groupe possible, couverture nationale FR/DE. |
| Leads de chantier vendus aux recruteurs | Barbour ABI (UK) | Attributions de contrats, entreprises, contacts | **Forte comme preuve de concept** ; **à ne pas copier** pour les contacts de personnes (nLPD). | **Forte** : prouve l'existence du marché ; aucun résultat publié, donc place pour une offre mesurée. |
| Prévision publique de main-d'œuvre par métier | Infrastructure Australia (AU), BuildForce Canada (CA), CITB (UK, voir `etat-de-l-art.md`) | Portefeuille de projets × ratios par métier | **Moyenne** : la logique « dépense × ratio » est celle de notre module de besoin estimé. | **Forte** : tableau de bord par métier et par canton, validé par les chefs d'agence. |
| IA des groupes, côté candidats | Adecco + Salesforce, ManpowerGroup + Hubert, Kelly, Indeed, Gi Group | Candidatures, CV, conversations | **Faible** pour Proxsis : déjà couvert par les ATS. | **Moyenne** : contexte concurrentiel ; ne pas dupliquer. |
| IA des groupes, côté clients et demande | Randstad (RTP, RMI dans 11 pays), ManpowerGroup (Sophie, commerciaux) | Internes + publiques ; méthode non publiée | **Forte** : c'est la promesse de Proxsis ; se distinguer par la mesure publiée. | **Forte** : cible naturelle (couche « marché » du groupe). |
| ATS du groupe | EOLIA chez Interiman (selon l'éditeur) | Candidats, candidatures, contrats (lien E@syTemp) | **Forte** : là où le consultant travaille. | **Forte** : un connecteur pour toutes les entités. |
| Indices d'offres en ligne | Swiss Job Tracker (CH), Lightcast et HWOL (US), Eurostat/Cedefop (UE), ONS–Adzuna (UK), Indeed Hiring Lab (voir `international.md`) | Annonces dédoublonnées, agrégées | **Moyenne** : contexte et règles de nettoyage (exclure les agences). | **Moyenne** : pilotage hebdomadaire par canton (Swiss Job Tracker). |
| Recherche : signaux → emploi | Ferraz et al., Gugler et al., Hebous & Zimmermann, Strauss, Ghent & Owyang, Shiha & El-adaway | Marchés publics, permis, emploi | **Forte** : fixe des délais plausibles par type de signal. | **Forte** : modèles régionaux à un an. |
| Recherche : appariement et équité | Horton, Le Barbanchon et al., Bied et al., Hoffman et al., Li et al., Fabris et al. | Expériences randomisées, audits | **Forte** : conception de « Candidats suggérés ». | **Forte** : politique d'IA responsable du groupe. |
| Recherche : notation de prospects | Wu et al., González-Flores et al. | Conversions B2B | **Moyenne** : confirme « simple d'abord » et le risque de fuite. | **Moyenne**. |

---

## 6. Cinq recommandations pour Proxsis

1. **Donner à chaque type de signal sa propre fenêtre de délai, puis la
   tester.**
   - Adjudication simap : fenêtre **courte** (0 à 8 semaines). Les gagnants
     d'enchères de construction en Autriche ajustaient leur emploi (avant la
     crise de 2008) surtout dans le mois qui suit ([R2](https://doi.org/10.1016/j.jpubeco.2019.104112)) ; au Brésil, l'effet apparaît dès le
     trimestre du gain ([R1](https://doi.org/10.3386/w21219)).
   - Mise à l'enquête et permis : fenêtre **longue** (environ 2 à 5
     trimestres). La planification précède l'activité de 9 à 12 mois
     ([W1](http://www.chapters.cfma.org/Update/Dodge_Momentum_Index.pdf), [W2](https://www.aia.org/resource-center/abi-may-2026-architecture-firm-billings-weaken-further)) ; les permis précèdent les postes vacants
     de la construction d'environ cinq trimestres en Europe ([R6](https://doi.org/10.1080/01446193.2025.2511833)).
   - Concrètement : variables « adjudication il y a 0–4 / 5–8 semaines » et
     « permis il y a 1–2 / 3–5 trimestres » ; on garde une fenêtre seulement
     si elle améliore P@10 au backtest (règle 9). Ces délais viennent de
     l'étranger : ce sont des **hypothèses** à recaler sur la Suisse.
   - Flexsis : les adjudications d'abord (cible à 8 semaines). Interiman : les
     permis pour la planification régionale à un an.

2. **Retirer et marquer les annonces d'agences, et mesurer la couverture par
   région linguistique.**
   - Le Swiss Job Tracker retire toutes les annonces d'agences (jusqu'à la
     moitié des annonces certains trimestres) ; l'indice HWOL aussi ;
     l'enquête britannique sur les postes vacants exclut les agences
     ([W36](https://swissjobtracker.ch/Methodology%20Swiss%20Job%20Tracker.pdf), [W39](https://www.conference-board.org/pdf_free/press/TCB-Lightcast-HWOL-Technical-Note.pdf), [W43](https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/conditionsanddiseases/methodologies/usingadzunadatatoderiveanindicatorofweeklyvacanciesexperimentalstatistics/pdf)).
   - Le même document suisse signale une possible sous-couverture de la
     **Suisse romande** et des entreprises de 25 employés ou moins
     ([W36](https://swissjobtracker.ch/Methodology%20Swiss%20Job%20Tracker.pdf)).
   - Concrètement : un champ obligatoire « annonceur = intermédiaire (oui /
     non / inconnu) » sur chaque offre ; les cibles A, B, C de
     `docs/backtest/cibles.md` ne comptent que les offres directes ; résultats
     du backtest ventilés **FR / DE** et par taille d'entreprise. Pas de
     comparaison Romandie–Suisse alémanique sans correction de couverture.

3. **Mesurer la couverture de nos connecteurs de permis contre un
   fournisseur suisse avant d'acheter ou de construire davantage.**
   - Olmero (Hubexo Switzerland) annonce des données quotidiennes de demandes
     et de permis de construire et d'appels d'offres pour toute la Suisse,
     plus de 40 000 projets ([W18](https://www.olmero.ch/en/smart-en/)) ; Baublatt/Batimag et Bindexis
     existent aussi (`marche.md`).
   - Concrètement : demander un échantillon ou un essai sous contrat sur deux
     cantons pilotes (Valais et un canton alémanique) ; mesurer le **rappel**
     de nos sources publiques (part des projets du fournisseur que nous
     trouvons aussi) et le **délai** de détection. Décision dans une ADR. Aucune
     redistribution sans licence ; aucun contact de personne repris.
   - Flexsis : un test, pas un abonnement. Interiman : une licence de groupe
     seulement si le gain est mesuré.

4. **Pour « Candidats suggérés » : recommander sans décider, garder une place
   d'exploration et journaliser les écarts.**
   - Des recommandations algorithmiques augmentent le taux de pourvoi (+20 %
     pour des offres techniques sur une plateforme en ligne) et l'emploi des moins favorisés (Suède), sans évincer les
     autres candidats ([R8](https://doi.org/10.1086/689213), [R9](https://www.povertyactionlab.org/sites/default/files/research-paper/WP4642_How-can-AI-improve-search-and-matching-in-Sweden_Rathelot-et-al_July2023.pdf)).
   - Il faut combiner l'adéquation **et** la chance réelle d'être retenu
     ([R11](https://arxiv.org/abs/2603.21699)). Un algorithme supervisé classique peut réduire la
     diversité ; l'exploration la protège ([R13](https://doi.org/10.3386/w27736)).
   - Dans une étude sur 15 entreprises, les managers qui passaient outre un
     test d'embauche recrutaient moins bien ([R12](https://doi.org/10.3386/w21709)) : il faut donc **mesurer**, pas supposer.
   - Concrètement : liste de 3 à 5 candidats avec raisons, dont **une place
     d'exploration** (profil plausible mais moins habituel) ; journal « suivi /
     non suivi + raison » ; audit par groupe avant chaque version, sur le
     modèle de Bied et al. ([R10](https://doi.org/10.24963/ijcai.2023/655)). Le consultant décide toujours.
   - Flexsis : simple et explicable. Interiman : un même audit pour toutes les
     marques.

5. **Se brancher sur l'outil du groupe et faire de chaque appel une
   vérification.**
   - Tous les fournisseurs étrangers étudiés vérifient leurs données par des humains,
     souvent au téléphone ([W1](http://www.chapters.cfma.org/Update/Dodge_Momentum_Index.pdf), [W5](https://storage.mfn.se/6c117b66-56c8-445c-88e1-a54f8a654b19/byggfakta-group-annual-report-2023.pdf), [W7](https://barbour-abi.com/business-type/recruiters/),
     [W8](https://www.vecteurplus.com/sources-de-donnees-vecteur-plus/), [W9](https://www.ibau.de/ueber-ibau/unsere-geschichte/)). Chez nous, l'appel du consultant joue ce
     rôle, à condition que son retour soit saisi là où il travaille.
   - Interiman utilise l'ATS EOLIA selon l'éditeur ([W35](https://eolia-software.fr/cas-client/faciliter-la-relation-entre-clients-candidats-et-collaborateurs-interiman-group/)).
   - Concrètement : (a) vérifier avec Interiman la version d'EOLIA, son API et
     si Flexsis l'utilise ; (b) export des alertes vers l'ATS (CSV puis API) ;
     (c) retour en un clic après l'appel (besoin confirmé / pas de besoin /
     déjà pourvu / mauvaise entreprise / plus tard) ; (d) **taux de
     confirmation** publié chaque semaine par famille de signaux et par
     canton. Ces retours deviennent des étiquettes, avec la réserve des labels
     sélectifs (`etat-de-l-art.md` §4).
   - Flexsis : la saisie doit prendre moins d'une minute (objectif, pas une
     mesure). Interiman : les retours de toutes les marques améliorent les
     règles pour tous.

---

## 7. Non vérifié ou inconnu

- Méthode détaillée de Randstad Market Insights, de Sophie (ManpowerGroup) et
  des agents d'Adecco : **inconnue** (non publiée).
- Chiffres d'Indeed pour Career Scout (sept fois plus rapide, 38 %) : extrait seulement.
- Appel de résultats de Kelly : extrait seulement (page trop lente).
- Méthode de l'indicateur ABC et détails d'Infrastructure Australia : extraits
  seulement (pages bloquées ou trop lentes).
- Couverture de la Suisse par Cedefop Skills-OVATE : **non confirmée**.
- Date d'entrée d'ibau dans Infopro Digital, propriétaire de DOCUmedia, prix
  d'Olmero, d'ibau, de DTAD, de Barbour ABI : **inconnus**.
- Usage d'EOLIA par Flexsis elle-même : **inconnu** (le cas client parle du
  groupe).
- DOI de Hebous & Zimmermann, Ghent & Owyang, Wu et al. : non relevés.
- Rapport annuel 2025 de Synergie : non lu (seul le semestriel 2025 l'a été).

---

## Sources

Toutes consultées le **2026-10-05**. Code de statut entre parenthèses.

**Chantiers (section 1)**

- W1 — McGraw-Hill Construction / Dodge, « Dodge Momentum Index: FAQs » (2012, PDF, texte intégral lu) : http://www.chapters.cfma.org/Update/Dodge_Momentum_Index.pdf — consulté le 2026-10-05 (A·L)
- W2 — AIA, « ABI May 2026: Architecture firm billings weaken further » : https://www.aia.org/resource-center/abi-may-2026-architecture-firm-billings-weaken-further — consulté le 2026-10-05 (P·L\*)
- W3 — ABC, « Methodology for ABC's Construction Backlog Indicator » (juin 2023, PDF) : https://www.abc.org/Portals/1/ABC%20CBI_CCI%20Methodology%20June%202023.pdf — consulté le 2026-10-05 (P·E, page 403)
- W4 — PR Newswire, « Byggfakta Group becomes Hubexo and announces new leadership structure » (1er octobre 2024) : https://www.prnewswire.com/news-releases/byggfakta-group-becomes-hubexo-and-announces-new-leadership-structure-302262331.html ; version Glenigan : https://www.glenigan.com/byggfakta-group-becomes-hubexo-and-announces-new-leadership-structure/ — consulté le 2026-10-05 (A·L\* ; A·E)
- W5 — Byggfakta Group, « Annual and Sustainability Report 2023 » (PDF, texte intégral lu ; p. 4, 5, 44, 50, liste des filiales) : https://storage.mfn.se/6c117b66-56c8-445c-88e1-a54f8a654b19/byggfakta-group-annual-report-2023.pdf — consulté le 2026-10-05 (A·L)
- W6 — Glenigan, « About us » : https://www.glenigan.com/about-us/ — consulté le 2026-10-05 (A·L\*)
- W7 — Barbour ABI, « Supporting Construction Recruiters » (textes demandés mot à mot) : https://barbour-abi.com/business-type/recruiters/ — consulté le 2026-10-05 (A·L)
- W8 — Vecteur Plus, « Le traitement de la donnée chez Vecteur Plus » : https://www.vecteurplus.com/sources-de-donnees-vecteur-plus/ ; « Who we are » : https://www.vecteurplus.com/en/who-we-are/ — consulté le 2026-10-05 (A·L\*)
- W9 — ibau, « Geschichte & Entwicklung von ibau » : https://www.ibau.de/ueber-ibau/unsere-geschichte/ ; offre « Mitarbeiter Recherche Bauprojekte – Telefonie/Online » : https://www.ibau.de/ueber-ibau/karriere/telefonrecherche-m-w-d-bauwirtschaft/ — consulté le 2026-10-05 (A·L\* ; A·E)
- W10 — DTAD, page d'accueil (anglais) : https://www.dtad.com/en/ — consulté le 2026-10-05 (A·L\*)
- W11 — Olmero, « Olmero übernimmt INFO-TECHNO Baudatenbank GmbH » : https://www.olmero.ch/blog/olmero-uebernimmt-info-techno-baudatenbank-gmbh/ ; INFO-TECHNO : https://www.info-techno.at/ — consulté le 2026-10-05 (A·L\* ; A·E)
- W12 — DOCUmedia, « Bauprojekte » : https://www.documedia.at/services-und-leistungen/bauprojekte/ — consulté le 2026-10-05 (A·L\*)
- W13 — Cobouw Pro, « Dataverantwoording » : https://www.cobouw.nl/pro/dataverantwoording ; Bouwberichten, « Over ons » : https://bouwberichten.nl/over-ons — consulté le 2026-10-05 (A·L\* ; A·E)
- W14 — Cotality, « Cordell Connect » : https://www.cotality.com/products/cordellconnect — consulté le 2026-10-05 (A·L\*)
- W15 — Hubexo APAC, « About » : https://apac.hubexo.com/about/ — consulté le 2026-10-05 (A·L\*)
- W16 — Infrastructure Australia, « 2025 Infrastructure Market Capacity Report » : https://www.infrastructureaustralia.gov.au/reports/2025-infrastructure-market-capacity-report ; annexes : https://www.infrastructureaustralia.gov.au/sites/default/files/2025-11/IA25_Market%20Capacity%20Report_Appendices.pdf — consulté le 2026-10-05 (P·E, pages trop lentes)
- W17 — BuildForce Canada, « About The Data » : https://www.buildforce.ca/en/about-the-data/ ; Daily Commercial News, « BuildForce's national 10-year forecast tracks $500B in major projects » (juillet 2026) : https://canada.constructconnect.com/dcn/news/uncategorized/2026/07/buildforces-national-10-year-forecast-tracks-500b-in-major-projects — consulté le 2026-10-05 (P·L\* ; T·E)
- W18 — Olmero, « Olmero SMART » : https://www.olmero.ch/en/smart-en/ ; « Aus Byggfakta wird Hubexo » (2 octobre 2024) : https://www.olmero.ch/blog/aus-byggfakta-wird-hubexo/ — consulté le 2026-10-05 (A·L\*)
- W19 — Schweizerischer Baumeisterverband, « Baukonjunktur » : https://baumeister.swiss/baumeister-5-0/konjunktur-statistiken/baukonjunktur/ ; « Bauindex » : https://baumeister.swiss/baumeister-5-0/konjunktur-statistiken/bauindex/ — consulté le 2026-10-05 (P·L\* ; P·E)

**Agences de placement (section 2)**

- W20 — Randstad, « Annual Report 2025 » (PDF, texte intégral lu ; p. 17, 29, 35 et 104 du PDF) : https://www.randstad.com/s3fs-media/rscom/public/2026-02/Randstad_Annual_Report_2025_F.pdf — consulté le 2026-10-05 (A·L)
- W21 — Randstad, « Randstad executes its partner for talent strategy to become a digital-first talent company » (24 avril 2025) : https://www.randstad.com/press/2025/randstad-executes-its-partner-talent-strategy-to-become-digital-first-talent-company/ — consulté le 2026-10-05 (A·L\*)
- W22 — Randstad, « Workday and Randstad partner to transform hiring with AI » (26 février 2025) : https://www.randstad.com/press/2025/workday-randstad-partner-to-transform-hiring-with-ai/ — consulté le 2026-10-05 (A·L\*)
- W23 — Randstad, « FY 2025: perform and transform » (11 février 2026) : https://www.randstad.com/press/2026/fy-2025-perform-transform/ — consulté le 2026-10-05 (A·L\*)
- W24 — The Adecco Group, « Annual Report 2025 » (PDF, texte intégral lu ; p. 12, 14, 50) : https://www.adeccogroup.de/wp-content/uploads/the-adecco-group-annual-report-2025.pdf — consulté le 2026-10-05 (A·L)
- W25 — The Adecco Group, « The Adecco Group completes successful first agentic AI implementation at scale » (30 juillet 2025) : https://www.adeccogroup.com/our-group/media/press-releases/the-adecco-group-completes-successful-first-agentic-ai-implementation-at-scale — consulté le 2026-10-05 (A·L\*)
- W26 — PR Newswire, « The Adecco Group to scale agentic AI at speed with unlimited Agentforce license agreement » (12 mars 2026) : https://www.prnewswire.com/news-releases/the-adecco-group-to-scale-agentic-ai-at-speed-with-unlimited-agentforce-license-agreement-302711588.html — consulté le 2026-10-05 (A·L\*)
- W27 — ManpowerGroup, « 2025 Year In Review — CEO Letter To Shareholders » : https://go.manpowergroup.com/ceo-letter — consulté le 2026-10-05 (A·L\*)
- W28 — ManpowerGroup, « ManpowerGroup Scales Human-First AI Interviewing to Address Global Talent Shortage » (3 mars 2026) : https://investor.manpowergroup.com/news-releases/news-release-details/manpowergroup-scales-human-first-ai-interviewing-address-global — consulté le 2026-10-05 (A·L\*)
- W29 — ManpowerGroup, « ManpowerGroup Announces Investment in New Paris-Based AI HR Hub » : https://investor.manpower.com/news-releases/news-release-details/manpowergroup-announces-investment-new-paris-based-ai-hr-hub — consulté le 2026-10-05 (A·E, page trop lente)
- W30 — Kelly Services, « Fourth-Quarter and Full-Year 2025 Conference Call » : https://ir.kellyservices.com/static-files/a9ae6095-23ff-4c3f-9782-4e94d2782054 — consulté le 2026-10-05 (A·E, page trop lente)
- W31 — Recruit Holdings, « Reimagining Hiring Using AI: Indeed FutureWorks 2025 » (30 octobre 2025) : https://recruit-holdings.com/en/blog/post_20251030_0001/ ; BusinessWire, communiqué Indeed du 10 septembre 2025 : https://www.businesswire.com/news/home/20250910809034/en/Indeed-Introduces-New-Suite-of-Hiring-Products-Career-Scout-Talent-Scout-Premium-Sponsored-Jobs-and-Indeed-Connect — consulté le 2026-10-05 (A·L\* ; A·E, page 403)
- W32 — Gi Group Italia, « RPO » (textes demandés mot à mot) : https://www.gigroup.it/aziende/soluzioni/rpo/ — consulté le 2026-10-05 (A·L)
- W33 — Synergie, « Rapport financier semestriel 2025 » (PDF, texte intégral lu) : https://www.synergie.com/system/files/RAPPORT_FINANCIER_SEMESTRIEL_2025.pdf — consulté le 2026-10-05 (A·L, vérifié)
- W34 — Interiman Group, « IA et recrutement : l'humain au cœur du projet de Interiman Group » (7 juillet 2025) : https://www.interiman-group.ch/ia-et-recrutement-lhumain-au-coeur-du-projet-de-interiman-group/ — consulté le 2026-10-05 (A·L\*)
- W35 — Eolia Software, « Faciliter la relation entre clients, candidats et collaborateurs – Interiman Group » (6 mars 2024, texte lu) : https://eolia-software.fr/cas-client/faciliter-la-relation-entre-clients-candidats-et-collaborateurs-interiman-group/ — consulté le 2026-10-05 (A·L)

**Mesure de la demande de travail (section 3)**

- W36 — Bannert, Klaeui, Kopp, Siegenthaler, Thöni & Winkelmann, « Swiss Job Tracker: New Weekly Indices of Online Job Postings in Switzerland — Methodology » (novembre 2022, PDF, texte intégral lu) : https://swissjobtracker.ch/Methodology%20Swiss%20Job%20Tracker.pdf — consulté le 2026-10-05 (P·L)
- W37 — KOF, « Swiss Job Tracker » : https://kof.ethz.ch/en/forecasts-and-indicators/indicators/swiss-job-tracker.html — consulté le 2026-10-05 (P·E)
- W38 — Lightcast, « Job Posting Analytics (JPA) Methodology » : https://kb.lightcast.io/en/articles/6957446-job-posting-analytics-jpa-methodology — consulté le 2026-10-05 (A·L\*)
- W39 — The Conference Board, « The Conference Board-Lightcast Help Wanted OnLine® Technical Note » (PDF, texte intégral lu) : https://www.conference-board.org/pdf_free/press/TCB-Lightcast-HWOL-Technical-Note.pdf — consulté le 2026-10-05 (P·L)
- W40 — Eurostat, « WIH – OJA Data » : https://cros.ec.europa.eu/wih/oja — consulté le 2026-10-05 (P·L\*)
- W41 — Eurostat, « Issue 23 – Lessons learned from Eurostat's Deduplication Challenge » : https://cros.ec.europa.eu/book-page/issue-23-lessons-learned-eurostats-deduplication-challenge — consulté le 2026-10-05 (P·E)
- W42 — Cedefop, « Skills in online job advertisements » : https://www.cedefop.europa.eu/en/tools/skills-intelligence/skills-online-job-advertisements (P·E, page 403) ; Swisscore, « Cedefop debuts a new skills and job offers tool » : https://www.swisscore.org/cedefop-debuts-a-new-skills-and-job-offers-tool/ (T·L\*) — consultés le 2026-10-05
- W43 — Office for National Statistics, « Using Adzuna data to derive an indicator of weekly vacancies: Experimental Statistics » (14 juin 2021, PDF, texte intégral lu) : https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/conditionsanddiseases/methodologies/usingadzunadatatoderiveanindicatorofweeklyvacanciesexperimentalstatistics/pdf — consulté le 2026-10-05 (P·L)
- W44 — Conlon, F. (2011), « Professional and business services: employment trends in the 2007–09 recession », *Monthly Labor Review*, avril 2011, BLS (PDF, texte intégral lu) : https://www.bls.gov/opub/mlr/2011/04/art6full.pdf — consulté le 2026-10-05 (P·L)

**Recherche académique (section 4)**

- R1 — Ferraz, C., Finan, F. & Szerman, D. (2015). *Procuring Firm Growth: The Effects of Government Purchases on Firm Dynamics*. NBER WP 21219. https://doi.org/10.3386/w21219 (page : https://www.nber.org/papers/w21219) — consulté le 2026-10-05 (P·L\*)
- R2 — Gugler, K., Weichselbaumer, M. & Zulehner, C. (2020). Employment behavior and the economic crisis: Evidence from winners and runners-up in procurement auctions. *Journal of Public Economics*, 182, 104112. https://doi.org/10.1016/j.jpubeco.2019.104112 (résumé RePEc : https://ideas.repec.org/a/eee/pubeco/v182y2020ics0047272719301744.html) — consulté le 2026-10-05 (P·L\* ; P·E pour le délai d'un mois)
- R3 — Hebous, S. & Zimmermann, T. (2021). Can government demand stimulate private investment? Evidence from U.S. federal procurement. *Journal of Monetary Economics*, 118, 178–194. https://ideas.repec.org/p/imf/imfwpa/2016-060.html — consulté le 2026-10-05 (P·L\*)
- R4 — Strauss, J. (2013). Does housing drive state-level job growth? Building permits and consumer expectations forecast a state's economic activity. *Journal of Urban Economics*, 73(1), 77–93. https://doi.org/10.1016/j.jue.2012.07.005 (RePEc : https://ideas.repec.org/a/eee/juecon/v73y2013i1p77-93.html) — consulté le 2026-10-05 (P·L\* ; P·E pour « quatre trimestres »)
- R5 — Ghent, A. C. & Owyang, M. T. (2010). Is housing the business cycle? Evidence from US cities. *Journal of Urban Economics*, 67(3). Document de travail : https://ideas.repec.org/p/fip/fedlwp/2009-007.html — consulté le 2026-10-05 (P·E)
- R6 — Shiha, A. & El-adaway, I. H. (2025). Identifying early warning signs of construction labor shortages. *Construction Management and Economics*, 43(10), 765–793. https://doi.org/10.1080/01446193.2025.2511833 (RePEc : https://ideas.repec.org/a/taf/conmgt/v43y2025i10p765-793.html) — consulté le 2026-10-05 (P·L\*)
- R7 — Forsythe, E., Kahn, L. B., Lange, F. & Wiczer, D. (2020). Labor demand in the time of COVID-19: Evidence from vacancy postings and UI claims. *Journal of Public Economics*, 189. NBER WP 27061 : https://www.nber.org/papers/w27061 — consulté le 2026-10-05 (P·E)
- R8 — Horton, J. J. (2017). The Effects of Algorithmic Labor Market Recommendations: Evidence from a Field Experiment. *Journal of Labor Economics*, 35(2), 345–385. https://doi.org/10.1086/689213 (RePEc : https://ideas.repec.org/a/ucp/jlabec/doi10.1086-689213.html) — consulté le 2026-10-05 (P·L\*)
- R9 — Le Barbanchon, T., Hensvik, L. & Rathelot, R. (2023). *How can AI improve search and matching? Evidence from 59 million personalized job recommendations*. Document de travail, version préliminaire de juillet 2023 (PDF, résumé lu) : https://www.povertyactionlab.org/sites/default/files/research-paper/WP4642_How-can-AI-improve-search-and-matching-in-Sweden_Rathelot-et-al_July2023.pdf ; SSRN : https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4604814 — consulté le 2026-10-05 (P·L)
- R10 — Bied, G., Nathan, S., Perennes, E., Hoffmann, M., Caillou, P., Crépon, B., Gaillac, C. & Sebag, M. (2023). Toward Job Recommendation for All. *IJCAI 2023*, 5906–5914. https://doi.org/10.24963/ijcai.2023/655 — consulté le 2026-10-05 (P·L\*)
- R11 — Bied, G., Caillou, P., Crépon, B., Gaillac, C., Pérennes, E. & Sebag, M. (2026). *A Job I Like or a Job I Can Get: Designing Job Recommender Systems Using Field Experiments*. arXiv:2603.21699. https://arxiv.org/abs/2603.21699 — consulté le 2026-10-05 (P·L\*)
- R12 — Hoffman, M., Kahn, L. B. & Li, D. (2018). Discretion in Hiring. *Quarterly Journal of Economics*, 133(2), 765–800. NBER WP 21709 : https://doi.org/10.3386/w21709 — consulté le 2026-10-05 (P·L\*)
- R13 — Li, D., Raymond, L. R. & Bergman, P. (2026). Hiring as Exploration. *Review of Economic Studies*, 93(2), 1200–1240. NBER WP 27736 : https://doi.org/10.3386/w27736 — consulté le 2026-10-05 (P·L\*)
- R14 — Fabris, A., Baranowska, N., Dennis, M. J., Graus, D., Hacker, P., Saldivar, J., Zuiderveen Borgesius, F. & Biega, A. J. (2025). Fairness and Bias in Algorithmic Hiring: A Multidisciplinary Survey. *ACM Transactions on Intelligent Systems and Technology*. arXiv:2309.13933 : https://arxiv.org/abs/2309.13933 (DOI 10.1145/3696457 selon un extrait) — consulté le 2026-10-05 (P·L\* ; P·E pour le DOI)
- R15 — de Ruijt, C. & Bhulai, S. (2021). *Job Recommender Systems: A Review*. arXiv:2111.13576 : https://arxiv.org/abs/2111.13576 — consulté le 2026-10-05 (P·E)
- R16 — Bogen, M. & Rieke, A. (2018). *Help Wanted: An Examination of Hiring Algorithms, Equity, and Bias*. Upturn : https://www.upturn.org/reports/2018/hiring-algorithms/ — consulté le 2026-10-05 (T·E)
- R17 — Wu, M., Andreev, P. & Benyoucef, M. (2024). The state of lead scoring models and their impact on sales performance. *Information Technology and Management*, 25(1), 69–98. Notice : https://ouci.dntb.gov.ua/en/works/4wd0qLdl/ — consulté le 2026-10-05 (P·E)
- R18 — González-Flores, L., Rubiano-Moreno, J. & Sosa-Gómez, G. (2025). The relevance of lead prioritization: a B2B lead scoring model based on machine learning. *Frontiers in Artificial Intelligence*. https://doi.org/10.3389/frai.2025.1554325 (PMC : https://pmc.ncbi.nlm.nih.gov/articles/PMC11925937/) — consulté le 2026-10-05 (P·L\*)
