# Accès légal aux offres d'emploi en Suisse — pistes pour la cible « offre dans les huit semaines »

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

> **Ce n'est pas un avis juridique.** Note de travail rédigée par un assistant d'IA (Claude).
> Un juriste doit valider les points marqués **[INT]** (interprétation) avant tout usage.
>
> **Date de consultation de toutes les sources web : 2026-10-05**, sauf mention contraire.
> Les sources sont numérotées [n] ; la liste complète (lien + date) est en fin de document.

**Méthode.** Recherche web et lecture de pages publiques uniquement. Aucun compte créé. Aucune API
appelée. Aucune protection contournée. Seuls des fichiers `robots.txt` et des pages d'information
ont été lus. La documentation technique de l'API Job-Room n'a **pas** été lue : son hôte
(`test-api.job-room.ch`) interdit tout aux robots [9]. La page d'accueil de careerjet.ch a renvoyé
une page de vérification anti-robot : elle n'a pas été contournée.

## 0. Ce que la cible exige

Cible B du projet (`docs/backtest/cibles.md`) : l'entreprise publie une offre dans les 56 jours
après T, et aucune dans les 56 jours avant T. Il faut donc, **par entreprise** :

- la raison sociale (et l'IDE si possible) de l'employeur réel ;
- la **date de publication** de chaque offre ;
- le métier et le lieu ;
- un moyen d'exclure les offres d'agences ;
- un **historique** : simap n'a pas de données avant le 2024-07-01
  (`docs/backtest/backtest_reel.md`). Il faut donc des offres depuis environ le **2024-05-01**.

Ce dernier point est décisif. Une source qui ne montre que les offres en cours ne permet pas de
backtest rétroactif. Elle permet seulement une mesure **prospective** (à partir d'aujourd'hui).

---

## a) Job-Room (SECO)

### Ce qui est public

- Job-Room est la plateforme du service public de l'emploi. Les employeurs y annoncent leurs postes
  vacants [2].
- Le site offre une banque de postes vacants avec un moteur de recherche [8]. Un catalogue tiers cite environ
  78 774 annonces en Suisse au 2026-08-28 (non vérifié ; `data/catalogue.csv`, ligne
  `jobroom_api`). Une page du canton de Berne cite plus de 80 000 postes (page non datée) [14].
- Le `robots.txt` de www.job-room.ch et de api.job-room.ch interdit `/job-search/` aux robots [9].
  Commentaire du fichier : « Do not crawl Job Adverts ».
- Le SECO dispose d'un **historique au niveau de l'annonce**. Une étude du KOF pour le SECO a utilisé
  près de 300 000 offres publiées sur Job-Room entre le 1.7.2018 et le 31.12.2019 [12]. Durée de
  conservation des annonces au SECO : **inconnue**.

### Conditions d'utilisation

- Le texte des conditions d'utilisation de Job-Room **n'est pas public** : on l'accepte en cochant
  une case lors de l'inscription [5]. Contenu : **inconnu**.
- Les informations juridiques d'arbeit.swiss exigent une **autorisation écrite** des détenteurs des
  droits pour reproduire des contenus ou des données [8]. Un simple lien est permis [8]. Que ces
  informations couvrent aussi job-room.ch : probable, **à confirmer**.
- Le projet a déjà fixé sa règle : accord écrit du SECO avant tout usage automatisé
  (`docs/recherche/conditions_2026-10-05.md`).

### L'API Job-Room

- L'API sert à **publier** des annonces (canal électronique pour les grandes entreprises) [1].
  Un témoignage de 2018 confirme cet usage [13].
- Les identifiants s'obtiennent sur demande à jobroom-api@seco.admin.ch, avec les données de
  l'entreprise et le volume prévu [1][13].
- **Aucune API publique de lecture** des annonces n'a été trouvée. L'API de recherche utilisée par le
  site est interne et non documentée (`docs/recherche/donnees.md` § 4.7).

### Qui a accès à quoi (LSE, état au 1.9.2023)

- Accès sécurisé à la plateforme (art. 35 al. 3ter LSE) [7] :
  - demandeurs d'emploi inscrits à l'ORP : les annonces de postes vacants ;
  - employeurs : annoncer et contacter des demandeurs d'emploi ;
  - **placeurs privés autorisés : consulter les profils non anonymisés des demandeurs d'emploi**.
- Les placeurs autorisés accèdent aussi à des données **anonymisées** sur les demandeurs d'emploi.
  L'anonymat ne tombe qu'avec le consentement écrit de la personne (art. 35a al. 2 LSE) [7].
- Pendant les 5 jours ouvrables de l'obligation d'annonce, **seuls les demandeurs inscrits à l'ORP**
  voient les postes annoncés [1]. Aucun accès particulier des agences à ces annonces n'a été trouvé
  [1][3].
- Les agences s'inscrivent via IAM ALV. Leurs données sont vérifiées dans le répertoire des agences
  autorisées. Un code d'activation est envoyé par la poste [4].
- Le compte Job-Room des placeurs privés est régi par une **convention** [6]. Une copie tierce d'une
  convention SECO–swissstaffing (2012) limite les données au placement. Elle interdit la
  transmission à des tiers et le transfert technique vers ses propres applications [10]. Version en
  vigueur : **inconnue**.

**Conséquence.** L'accès « agence autorisée » de Flexsis concerne les **candidats**, pas un flux
d'annonces. Il ne doit **pas** servir à Proxsis [INT].

### Ce que la loi permet au SECO de communiquer

- Art. 34 LSE : les personnes du service public de l'emploi gardent le secret sur les employeurs et
  les places vacantes [7].
- Art. 34a al. 3 LSE : des données d'intérêt général peuvent être publiées. « L'anonymat des
  demandeurs d'emploi et des employeurs doit être garanti. » [7]
- Art. 34a al. 4 let. a LSE : dans les autres cas, des **données non personnelles** peuvent être
  communiquées à des tiers si un intérêt prépondérant le justifie [7].
- Art. 34a al. 5 et 7 LSE : seulement les données nécessaires ; en principe par écrit et gratuitement ;
  émolument possible pour les gros travaux [7].
- Les données de Job-Room alimentent LAMDA, utilisé de façon **anonymisée** pour la statistique, la
  recherche et la planification [11].
- **[INT]** Depuis la nLPD (1.9.2023), les données des personnes morales ne sont plus des données
  personnelles (`docs/recherche/legal.md` § 1). Des annonces d'entreprises (SA, Sàrl) pourraient
  donc relever de l'al. 4 let. a. Le secret de l'art. 34 reste un obstacle possible. Seul le SECO
  peut trancher. Versions de la LSE postérieures au 1.9.2023 : **non vérifiées**.

### Obligation d'annonce (rappel)

- Seuil : taux de chômage de 5 % depuis le 1.1.2020 [1].
- Interdiction de publier ailleurs pendant 5 jours ouvrables [1].
- La liste des professions paraît chaque automne pour l'année suivante [1].
- Base légale : art. 21a et 117a LEI ; art. 53a ss OSE [1].
- Si une agence recrute pour un employeur, c'est elle qui annonce le poste [1].
- Utile pour nous : les métiers soumis à l'obligation passent **obligatoirement** par Job-Room.
  En 2026, la liste comprend notamment des métiers élémentaires du bâtiment
  (`docs/recherche/legal.md` § 3.3, extrait de recherche du 2026-10-04).

### Verdict Job-Room

| Question | Réponse |
|---|---|
| Lecture automatisée sans accord | **Non** (robots.txt, mentions juridiques, règle du projet) |
| Historique au niveau annonce | Existe au SECO [12] ; pas public |
| Niveau entreprise | Oui dans Job-Room ; communication à un tiers : **à décider par le SECO** [7] |
| Démarche | Demande écrite au SECO : `docs/demandes/seco_job_room.md` |

---

## b) Pages carrières des entreprises

### Principe

- Beaucoup de pages carrières décrivent chaque offre en JSON-LD `schema.org/JobPosting`.
- Google exige `title`, `description`, `datePosted`, `hiringOrganization`, `jobLocation` [15].
  `validThrough` et `identifier` sont recommandés [15].
- Google demande de **retirer** les offres closes (date passée, page 404/410 ou balisage supprimé)
  [15]. Donc une page carrière ne montre que **les offres en cours**.

### Ce qu'on peut faire (avec prudence)

- Lire la page carrière **publique** d'une entreprise de notre liste.
- Avant chaque site : lire son `robots.txt` et ses CG. Ne rien lire si l'un ou l'autre l'interdit
  (règle du projet). Le `robots.txt` n'est pas une autorisation d'accès au sens de la RFC 9309 [16],
  mais il exprime la volonté de l'exploitant (`docs/recherche/legal.md` § 4.7).
- N'extraire que des **faits** : date, intitulé, métier, lieu. Ne pas republier le texte.
- Faible débit, agent identifiable, cache, provenance (`source`, `url`, `retrieved_at`).
- **[INT]** Un signal dérivé (« l'entreprise publie ») n'est pas une reprise du résultat du travail
  d'autrui comme produit concurrent. Le risque LCD paraît faible.

### Ce qu'on ne peut pas faire

- **Contourner** un login, un captcha ou un blocage (`docs/recherche/legal.md` § 4.7).
- **Aspirer des portails privés** ou des ATS tiers sans accord (jobs.ch, Indeed, LinkedIn…) : règle
  du projet (CONTRIBUTING.md, règle 6).
- **Reprendre des annonces telles quelles** pour un produit concurrent. Art. 5 let. c LCD : reprise
  d'un résultat de travail prêt à être commercialisé, par un procédé technique, sans effort propre
  suffisant [17]. Le tribunal compare les efforts et tient compte de l'amortissement [17]. Portée de
  l'ATF 131 III 384 : **à vérifier** (`docs/recherche/legal.md` § 4.7).
- **Copier les textes** : un texte d'annonce peut être une œuvre s'il a un caractère individuel
  [INT]. La Suisse n'a pas transposé la directive européenne sur les bases de données [17].
  L'exception de recherche de l'art. 24d LDA exige un accès licite [17] ; son application à un
  projet commercial est **à vérifier**.
- **Stocker des noms, e-mails ou téléphones de recruteurs.** Les données personnelles accessibles en
  ligne restent protégées [18]. L'art. 30 al. 3 nLPD ne crée qu'une présomption, sous conditions
  (publication volontaire par la personne elle-même) [19].
- **Supposer que les CG ne s'appliquent pas.** Visiter un site ne vaut pas à lui seul acceptation de
  ses CG [17] ; mais une interdiction claire aggrave le risque [INT].

### Limites pratiques

- **Pas d'historique** : impossible de reconstituer les offres de 2024–2026 [15]. Mesure
  **prospective** seulement.
- Couverture : seules les entreprises qui ont une page carrière balisée. Part des PME du bâtiment
  concernées : **inconnue**.
- `datePosted` est déclaré par le site lui-même [15]. Fiabilité : **inconnue**.
- Archives web (Internet Archive) pour l'historique : **non étudié**, CG non lues.

### Verdict pages carrières

Légal au cas par cas, **sans inscription**, pour une mesure prospective sur une petite liste.
**Inutilisable pour le backtest historique.**

---

## c) Agrégateurs avec une API officielle

| Agrégateur | Inscription | Suisse | Usage commercial ou analytique | Verdict |
|---|---|---|---|---|
| **Adzuna** | Oui : `app_id` + `app_key` [20] ; accès à la discrétion d'Adzuna [21] | `ch` selon une doc tierce (catalogue, 2026-09-02) ; la doc officielle consultée ne montre que `gb` [20] | Organisations commerciales, publiques ou académiques : **essai de 14 jours** [21]. Pas d'usage brut ou agrégé (ex. nombre d'offres) pour un travail suivi **sans accord écrit** [21]. « a licence agreement may be required » [21]. Quotas par défaut 25/min, 250/jour, 1 000/semaine, 2 500/mois [21]. Logo et lien Adzuna obligatoires [21]. Données à retirer à la résiliation [21]. | **Accord écrit + licence** |
| **Careerjet** | Oui : compte éditeur ; une clé par site éditeur [22] | Locales `de_CH`, `fr_CH` (catalogue) | Paramètres `user_ip` et `user_agent` obligatoires [22] : API conçue pour afficher des offres à des visiteurs. Conditions détaillées : **inconnues**. | **Non adapté** (affichage, pas analyse) |
| **Jooble** | Oui : formulaire (nom, fonction, e-mail, site web, téléphone) [23] ; une clé par domaine pays [24] | Page `ch.jooble.org/api/about` existe [23] | Destinée aux webmasters pour enrichir leur site [23]. Conditions propres à l'API : **non trouvées** [24]. | **Inconnu** ; probablement affichage |
| Autres (Talent.com, WhatJobs…) | — | — | **Non étudiés** | — |

**Points communs.** Tous exigent une inscription. Aucun ne donne d'historique au niveau de l'offre
pour 2024–2026 dans la documentation lue. Les offres d'agrégateurs viennent elles-mêmes de portails
et de sites tiers.

---

## d) Sources statistiques et fournisseurs de données

| Source | Contenu | Niveau | Accès | Utile pour la cible ? |
|---|---|---|---|---|
| **Swiss Job Tracker** (KOF, UNIL, x28) | Offres en ligne uniques, hebdomadaire [25] | National, canton, branche, métier [25][26] | Données publiques téléchargeables [25] | **Non** (agrégé). Contexte seulement |
| **x28 AG** (Jobradar, données) | Collecte des offres sur portails et sites d'entreprises [27]. Selon la méthodologie SJT (nov. 2022) : au moins 72 % de tous les postes vacants et 90 % des postes publiés [26] | **Entreprise** : l'API peut livrer « all job ads from selected companies » [27] | Contrat commercial ; prix non public [27] | **Oui**, si contrat. Historique disponible : **inconnu** |
| **Adecco Group Swiss Job Market Index** (UZH, Stellenmarkt-Monitor) | Indice trimestriel depuis 2008 ; 12 grands portails + env. 1 500 sites d'entreprises [28] | National, métier, branche [28] | Fichier Excel public [28] | **Non** (agrégé) |
| **Stellenmarkt-Monitor Schweiz** (données de recherche) | Échantillon d'annonces depuis 2001 (sites d'entreprises) et 2006 (portails) [29] | Annonce (fichier de recherche) | Recherche et enseignement **non commerciaux** ; interdiction d'identifier des institutions [30] | **Non** (usage commercial exclu) |
| **SECO AMSTAT / statistiques** | Chômage, demandeurs d'emploi, postes vacants [31] | Régions et branches [31] | Public | **Non** (agrégé) |

**À retenir.** Les sources publiques sont **agrégées**. Le seul fournisseur privé avec un niveau
entreprise démontré est x28, **sous contrat**. La presse a déjà cité des entreprises tirées du
Jobradar (`docs/recherche/marche.md`, S29c).

---

## Conclusion

**Non.** La cible « offre dans les huit semaines » n'est **pas constructible légalement
aujourd'hui sans inscription ni accord**.

- Job-Room : pas de lecture automatisée sans accord du SECO [8][9].
- Agrégateurs : inscription obligatoire ; Adzuna exige un accord écrit pour un usage suivi [21].
- Statistiques publiques : agrégées, pas de niveau entreprise [25][28][31].
- Pages carrières : légales au cas par cas, mais **sans historique** [15]. Elles ne permettent qu'une
  mesure prospective, partielle, sur une petite liste.

**Meilleure piste : Job-Room, par un accord écrit du SECO.**

1. Source officielle, gratuite en principe (art. 34a al. 7 LSE) [7].
2. Historique au niveau de l'annonce déjà exploité pour la recherche [12].
3. Les métiers du bâtiment soumis à l'obligation d'annonce y passent obligatoirement [1].
4. Base légale possible pour des données non personnelles (art. 34a al. 4 let. a LSE) [7] [INT].

**Ce qu'il faut demander au SECO** (message prêt : `docs/demandes/seco_job_room.md`) :

- un extrait unique des annonces depuis le 2024-05-01, Suisse romande au minimum ;
- par annonce : raison sociale, IDE si connu, date de publication, métier (CH-ISCO-19), lieu,
  obligation d'annonce (oui/non), type d'annonceur (employeur/agence), origine (Job-Room, API,
  externe) ;
- ou, plus minimal : un appariement fait par le SECO sur notre liste de lauréats simap ;
- les conditions (contrat, émolument, durée de conservation, publication des résultats) ;
- le statut des annonces « externes » (droits de tiers : **inconnu**) ;
- la possibilité, plus tard, d'une livraison hebdomadaire pour le produit.

**Plan B : x28.** Demander une offre chiffrée : historique depuis 2024-05, champs, indicateur
agence, conditions d'usage commercial [27].

**En attendant :** garder la cible T0 (simap) et ne lire aucune annonce de façon automatisée.

**À valider par un juriste :** art. 34 et 34a LSE (communication de données d'entreprises),
art. 5 let. c LCD et art. 24d LDA pour les pages carrières, opposabilité des CG.

---

## Sources

Toutes consultées le **2026-10-05**, sauf mention contraire.

1. arbeit.swiss, *FAQ on the job registration requirement* — https://www.arbeit.swiss/en/employers/faq-on-the-job-registration-requirement
2. arbeit.swiss, *Recherche de personnel* — https://www.arbeit.swiss/fr/employeurs/recherche-de-personnel
3. arbeit.swiss, *Recruitment and staffing agencies in Switzerland* — https://www.arbeit.swiss/en/employment-agencies/recruitment-and-staffing-agencies-in-switzerland
4. arbeit.swiss, *Registration (employment agencies)* — https://www.arbeit.swiss/en/employment-agencies/registration-employment-agencies
5. SECO, *Manuel d'enregistrement pour les agences de placement privées possédant un login* (copie swissstaffing, non datée) — https://www.swissstaffing.ch/docs/fr/service_juridique/mementos/SECO_Job-Room_Manuel_denregistrement_avec_login.pdf
6. SECO (seco.trainingplus.ch), *Datenschutz* — https://seco.trainingplus.ch/de/page/datenschutz
7. Loi fédérale sur le service de l'emploi et la location de services (LSE, RS 823.11), état le 1.9.2023, Fedlex (PDF) — https://fedlex.data.admin.ch/filestore/fedlex.data.admin.ch/eli/cc/1991/392_392_392/20230901/fr/pdf-a/fedlex-data-admin-ch-eli-cc-1991-392_392_392-20230901-fr-pdf-a.pdf (art. 34, 34a, 35, 35a)
8. arbeit.swiss, *Informations juridiques* — https://www.arbeit.swiss/fr/informations-juridiques
9. robots.txt : https://www.job-room.ch/robots.txt et https://test-api.job-room.ch/robots.txt (lus le 2026-10-05) ; https://api.job-room.ch/robots.txt (archivé dans `data/conditions/2026-10-05/`)
10. *Vereinbarung SECO – swissstaffing* (2012), copie tierce non officielle — https://silo.tips/download/vereinbarung-zwischen-der-schweizerischen-eidgenossenschaft-vertreten-durch-staa
11. arbeit.swiss, *Information on the processing of data* — https://www.arbeit.swiss/en/jobseekers/unemployment/information-on-the-processing-of-data
12. KOF Bulletin, *Digital divide? An analysis of the usage data from the Job-Room* (déc. 2021) — https://kof.ethz.ch/en/news-and-events/kof-bulletin/kof-bulletin/2021/12/Digital-divide-An-analysis-of-the-usage-data-from-the-Job-Room-online-job-exchange.html
13. HR Cosmos, question sur l'API SECO/RAV (message du 20.7.2018) — https://www.hr-cosmos.ch/de/question/hat-jemand-bereits-erfahrung-mit-der-api-schnittstelle-vom-seco-rav-fur-die-stellenmeldung/
14. Canton de Berne (WEU), *Job-Room* (non datée) — https://www.weu.be.ch/de/start/themen/wirtschaft-und-arbeit/unternehmen/personalsuche/job-room.html
15. Google Search Central, *Job posting structured data* (mise à jour 2026-09-08) — https://developers.google.com/search/docs/appearance/structured-data/job-posting
16. RFC 9309, *Robots Exclusion Protocol* (sept. 2022) — https://www.rfc-editor.org/rfc/rfc9309.html
17. R. Oertli (MLL), *Switzerland as data scraping heaven?*, Université de Turin, 14.11.2023 — https://mll-legal.com/wp-content/uploads/2023/11/Data-Scraping-Torino-Reinhard-Oertli.pdf
18. PFPDT, *Déclaration commune sur le data scraping et la protection des données* (24.8.2023) — https://www.edoeb.admin.ch/fr/24082023-data-scraping-2
19. V. Conrad, swissprivacy.law, art. 30 al. 3 nLPD (5.11.2021) — https://swissprivacy.law/100/
20. Adzuna, *API overview* et *Search* — https://developer.adzuna.com/overview ; https://developer.adzuna.com/docs/search
21. Adzuna, *Terms of Service* (API, non datées) — https://developer.adzuna.com/docs/terms_of_service
22. Careerjet, *Getting your API key* — https://www.careerjet.com/partners/api
23. Jooble Suisse, *API* — https://ch.jooble.org/api/about
24. Jooble Help Center, *REST API Documentation* — https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation
25. KOF, *Swiss Job Tracker* — https://kof.ethz.ch/en/forecasts-and-indicators/indicators/swiss-job-tracker.html
26. Bannert et al., *Swiss Job Tracker: Methodology* (nov. 2022) — https://swissjobtracker.ch/Methodology%20Swiss%20Job%20Tracker.pdf
27. x28 AG, *Services* — https://www.x28.ch/en/main/services/
28. UZH Stellenmarkt-Monitor, *Adecco Group Swiss Job Market Index* — https://www.stellenmarktmonitor.uzh.ch/en/indices/asjmi.html
29. UZH Stellenmarkt-Monitor, *Dateninfrastruktur* — https://www.stellenmarktmonitor.uzh.ch/de/infrastructure.html
30. Zenodo, *Swiss Job Market Monitor Scientific Use File* (v2, 14.7.2026) — https://zenodo.org/records/21351265
31. SECO, *Arbeitsmarktstatistiken* — https://www.seco.admin.ch/de/arbeitsmarktstatistiken

Documents du dépôt utilisés : `docs/recherche/legal.md` (sources du 2026-10-04),
`docs/recherche/conditions_2026-10-05.md`, `docs/recherche/donnees.md`, `docs/recherche/marche.md`,
`docs/backtest/cibles.md`, `docs/backtest/backtest_reel.md`, `data/catalogue.csv`.
