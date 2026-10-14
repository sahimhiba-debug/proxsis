# Proxsis : vérification du contexte

> Document de recherche du 04.10.2026, antérieur au nom Proxsis ; relu le 14.10.2026 (passages sur le dépôt d'une autre équipe retirés).

Date de consultation de toutes les sources : **2026-10-04**.

## Méthode et limites

- L'accès direct à presque tous les domaines est bloqué depuis l'environnement de travail (flexsis.ch, interiman.ch, allnews.ch, organisator.ch, staffingindustry.com, bcvs.ch, vs.ch, bfs.admin.ch, luma.com, allai.events, etc. renvoient 403 / EGRESS_BLOCKED). La plupart des faits ci-dessous viennent donc des **extraits renvoyés par le moteur de recherche** pour les URL citées. La page elle-même n'a pas pu être ouverte. Ces faits sont marqués « (extrait) ». Le statut « vérifié » veut dire ici : confirmé par au moins un extrait de source identifiée.
- 37 recherches web ont été faites, puis le quota de recherche de la session a été atteint. Les points restés sans source sont marqués « inconnu » ou « non vérifié ».

## 1. Tableau de synthèse

| # | Affirmation du cahier des charges | Statut | Sources |
|---|---|---|---|
| 1a | Flexsis est une agence de placement temporaire et fixe | **Vérifié** (extrait) | [1][2][3] |
| 1b | Flexsis est une filiale d'Interiman Group | **Vérifié** (extrait) | [1][4] |
| 1c | Secteurs : industrie, construction, horlogerie, logistique, pharma | **Vérifié** pour industrie, technique, horlogerie, logistique et construction. « Pharma » apparaît sous la forme « sciences de la vie » | [1][3] |
| 1d | Agences en Valais : Sion, Monthey, Martigny, Sierre, Brigue/Viège | **Partiellement vérifié** : succursales trouvées à Sion, Monthey et Martigny. Aucune trace d'agence Flexsis à Sierre, Brigue ou Viège | [3][5] |
| 2a | Interiman Group, « premier groupe RH de Suisse » | **Partiellement vérifié** : le groupe se dit lui-même « leader ». D'autres sources présentent Adecco comme n°1 du marché suisse, et Interima se dit « l'un des 4 plus importants acteurs » | [6][7][12][29] |
| 2b | « Plus de 70 sites » | **Partiellement vérifié** : 71 agences dans certaines sources, 67 agences dans une autre datée de mai 2025 | [2][6][13] |
| 2c | « Une dizaine de sociétés » | **Vérifié** (extrait) : 9 sociétés spécialisées, 10 marques ou 12 marques selon la source | [2][11][13] |
| 2d | Marques du groupe : Joblogistique, Prime26, Swisslinx, Teamstaff, Sigma, Tempro | **Non vérifié** : aucune de ces marques n'a été trouvée. Marques confirmées : Interima, Flexsis, Albedis, Medicalis, Hotelis, Humanys Solutions, SPS, Acceleris (Consulting, Academy), Securiman | [6][8] |
| 2e | Chiffre d'affaires, effectifs, siège | **Partiellement vérifié** : CA 2024 de 573 MCHF et 615 MEUR selon SIA 2026. Effectif total et siège : **inconnus** | [8][11] |
| 3 | Reprise des agences Tempro (Suisse alémanique) par Flexsis/Interiman en juin 2026 | **Vérifié le 2026-10-05** (voir `flexsis_offre.md`) ; la recherche du 2026-10-04 ne l'avait pas trouvé : 4 recherches (FR/DE), aucune trace | — |
| 4a | Hack VS 2026 : hackathon valaisan | **Vérifié** (extrait) : 24 h à la Foire du Valais, avec la HES-SO Valais-Wallis, les 3 et 4 octobre 2026 | [20][21] |
| 4b | Défi « anticiper les besoins en personnel » posé par Flexsis | **Partiellement vérifié** : Flexsis figure parmi les entreprises qui posent les défis (thème RH). La formulation exacte du défi n'a pas été trouvée | [21] |
| 4c | Équipes gagnantes | **Inconnu** : la finale (pitch) a lieu le dimanche 4 octobre 2026 après-midi, et aucun résultat n'est publié | [20][21] |
| 4d | Stack de l'équipe gagnante : Next.js 16, React 19, TypeScript, Tailwind 4, shadcn/ui, Supabase | **Inconnu** : les équipes gagnantes ne sont pas connues | [20][21] |
| 6a | Taille du marché suisse de la location de services | **Vérifié** (extrait) : 406 000 temporaires par an, 209 millions d'heures, CA de 10,6 Md CHF | [22] |
| 6b | Part de la construction et de l'industrie | **Partiellement vérifié** : construction ≈ 21 % (2e débouché, chiffre ancien). Part de l'industrie : **inconnue** | [31] |
| 6c | Saisonnalité | **Non vérifié** (pas de donnée swissstaffing trouvée) | — |
| 6d | Dernier Swiss Staffingindex | **Vérifié** (extrait) : T1 2026, +1,3 % d'heures sur un an. Aucune publication T2 2026 trouvée | [23][24] |
| 6e | Concurrents en Suisse romande et en Valais | **Partiellement vérifié** : Adecco, Randstad, Interiman et Gi Group confirmés. Manpower, Kelly, Synergie, Unique et Tempo non vérifiés | [27][29][30][47] |
| 7a | Volume de la construction en Valais | **Non vérifié** : inconnu — à relever sur la table OFS px-x-0904010000_201 (pxweb, bloqué depuis l'environnement) | [32] |
| 7b | Grands projets : 3e correction du Rhône, Lonza Viège (Ibex), A9 Haut-Valais, hôpitaux | **Vérifié** (extrait) | [36]-[46] |
| 7c | Barrages | **Non vérifié** (pas de recherche faite, faute de quota) | — |

## 2. Flexsis

- **Activité** : Flexsis SA recrute et sélectionne des candidats pour l'industrie, la technique, l'horlogerie, la logistique et la construction, en placement fixe ou temporaire. Une autre formulation cite « industrie, construction, logistique et sciences de la vie » [1][3] (extrait). Le but social inscrit au RC couvre le placement de personnel temporaire ou fixe, la gestion des salaires, la formation et le conseil RH [3] (extrait).
- **Groupe** : Flexsis fait partie d'Interiman Group [1]. Une annonce jobs.ch décrit Flexsis AG comme « une société indépendante d'Interiman Group SA, avec plus de 140 collaborateurs sur 47 sites en Suisse » [4] (extrait).
- **Siège et réseau** : un registre secondaire (business-monitor.ch) indique un siège à Renens (VD), une fondation en 1997 et **46 succursales** [3] (extrait, non recoupé). Le jobs.ch cité ci-dessus parle de 47 sites [4].
- **Valais** (succursales inscrites au registre du commerce, d'après business-monitor.ch [3], extrait) :
  - Martigny, avenue de la Gare 38 (inscrite le 19.06.2023)
  - Monthey, rue de Venise 10 (inscrite le 19.06.2023)
  - Sion, avenue de Tourbillon 5 (inscrite le 30.06.2023)
  - **Sierre, Brigue, Viège : aucune agence Flexsis trouvée.** Des annonces signées « Flexsis Sion » existent sur jobup [5].
- **Offres publiées (indicateur secondaire)** : inconnu — flexsis.ch est bloqué depuis l'environnement ; à relever directement sur flexsis.ch (lecture ponctuelle, robots.txt respecté).

## 3. Interiman Group

- **Positionnement** : le groupe se présente comme « le principal prestataire de placement de personnel en Suisse » et revendique l'offre RH la plus complète du pays [6][12] (extrait). D'autres sources présentent **Adecco comme n°1** et Randstad comme n°2 du secteur en Suisse [29][30] (extrait). Le profil jobup d'Interima SA parle de « l'un des 4 plus importants acteurs du secteur en Suisse, avec plus de 60 agences spécialisées » [7] (extrait). La formule « premier groupe RH de Suisse » est donc une **revendication de l'entreprise**, contestable.
- **Réseau** : les chiffres varient selon la source et la date.
  - « 71 agences, 9 sociétés spécialisées, 28 ans d'expérience » [2] (extrait)
  - « 71 succursales et 12 sociétés spécialisées » [6] (extrait)
  - « 67 agences en Suisse sous 12 marques » (mai 2025) [13] (extrait)
  - « 10 marques spécialisées » ainsi que des plateformes de formation (Staffing Industry Analysts, 2026) [11] (extrait)
- **Marques et sociétés confirmées** : Interima, Flexsis, Albedis (nouvelle marque issue d'un rebranding), Medicalis, Hotelis, Humanys Solutions (conseil, évaluation, outplacement), SPS – Switzerland Payroll Services (payrolling, freelances), Acceleris Consulting (rachetée), Acceleris Academy, Hotelis Academy, Medicalis Academy, Securiman [6][8] (extrait).
  - **Non trouvées** : Joblogistique, Prime26, Swisslinx, Teamstaff, Sigma, Tempro.
- **Chiffres d'affaires** :
  - 2021 : 481 MCHF (+33 %) [10]
  - 1er semestre 2024 : 275 MCHF, stable [9]
  - 2024 : 573 MCHF (-3,4 %), alors que le marché du travail temporaire reculait de 10,6 % et le placement fixe de 20,8 % [8]
  - Staffing Industry Analysts (liste 2026) : **615 MEUR** [11]
  - Une autre source parle d'un CA « de près de 550 MCHF » [13]
  - Tous ces chiffres sont des extraits.
- **Volume d'activité revendiqué** : plus de 30 000 temporaires placés par an, plus de 1 000 candidats orientés vers un emploi fixe et plus de 4 500 entreprises clientes [2] (extrait).
- **Divers** :
  - Certifications ISO 9001, 14001 et 45001 [2] (extrait)
  - Direction distinguée dans la liste « Staffing 100 Europe » 2026. Le groupe s'est étendu au Portugal, en Italie et au Liechtenstein [11] (extrait)
  - Nomination d'un Chief Digital & Marketing Officer [8] (extrait)
- **Effectifs internes totaux et siège social** : **inconnus** (pas trouvés dans les extraits consultés).

## 4. Reprise des agences Tempro (juin 2026)

**Non vérifié.** Quatre requêtes (« Interiman Group Tempro reprise agences 2026 », « Tempro Personal Übernahme Interiman Flexsis Filialen Juni 2026 », « Tempro AG Personaldienstleistungen verkauft übernommen 2026 », « "Tempro" Flexsis ») n'ont donné aucun résultat pertinent. Les extraits renvoient seulement à des annonces de filiales alémaniques de Flexsis (Schaffhouse, Berne, Aarau), ce qui confirme une présence en Suisse alémanique mais pas l'acquisition. Il faut garder la mention « affirmé dans le cahier des charges, non vérifié » et demander la source à Flexsis.

## 5. Hack VS 2026

- **Nature** : « Hack VS – la nouvelle génération réinvente le Valais ». C'est un hackathon de 24 heures présenté comme le premier hackathon intégré à une grande manifestation publique en Suisse [20][21] (extrait).
- **Organisation** : en partenariat avec la **Foire du Valais** et la **HES-SO Valais-Wallis** [20][21] (extrait).
- **Date** : les **3 et 4 octobre 2026** [20][21] (extrait). La Foire du Valais 2026 dure du 2 au 11 octobre (extrait de recherche). **Lieu** : au cœur de la Foire du Valais. La ville (Martigny, siège habituel de la Foire) n'est pas confirmée par une source consultée.
- **Format** :
  - environ 50 participants issus de grandes écoles suisses, en équipes mixtes, devant environ 20 000 visiteurs ;
  - les défis sont des problèmes concrets non résolus, posés par des entreprises valaisannes et traitables en 24 h avec des données ouvertes ou un jeu de données simplifié ;
  - le dimanche après-midi, les meilleures équipes pitchent sur scène devant un jury d'investisseurs, de fondateurs et de professionnels [20][21] (extrait).
- **Défis** : les partenaires cités sont **Flexsis, Sinergy et BPM**, sur les thèmes mobilité, RH et eaux usées [21] (extrait). Le défi Flexsis relève du thème RH. La formulation officielle « anticiper les besoins en personnel » n'a pas été trouvée telle quelle.
- **Gagnants** : **inconnus**. Le pitch final tombe le jour même de la consultation (dimanche 4 octobre 2026), et aucun résultat n'est indexé.
- **Stack de « l'équipe gagnante »** : **non vérifiable** tant que les gagnants ne sont pas connus.

## 6. Marché suisse de la location de services

- **Taille** : 406 000 temporaires par an, soit 103 000 équivalents plein temps et 2,4 % de l'emploi total. Ils représentent 209 millions d'heures, une masse salariale de 7,6 Md CHF et un CA de branche de 10,6 Md CHF (présentation swissstaffing du 6 février 2025) [22] (extrait). L'année de référence n'est pas précisée dans l'extrait.
- **Tendance** :
  - 2024 : heures -4,7 % et placement fixe -19,4 % [26]
  - 2025 : heures -7,1 % et placement fixe -23,3 %. C'est la première fois que la branche recule trois années de suite. La construction et les services domestiques ont soutenu l'activité [25]
  - Janvier 2025 : -8,3 %
- **Dernier Swiss Staffingindex trouvé (T1 2026)** :
  - heures +1,3 % sur un an, première hausse après 12 trimestres négatifs ;
  - janvier +1,5 %, février -0,2 %, mars +1,1 % ;
  - placement fixe -16,9 %, 11e trimestre de baisse d'affilée ;
  - Mittelland +5,5 % (horlogerie), Suisse orientale -2,2 % [23][24] (extrait).
  Les chiffres du T2 2026 n'ont pas été trouvés.
- **Part des secteurs** : un extrait attribue à swissstaffing une part de **21 % pour la construction**, deuxième débouché de la branche [31]. C'est un chiffre ancien, et la page exacte n'a pas pu être ouverte. La part de l'industrie est **inconnue**.
- **Recours des entreprises** : 41 % des entreprises utilisent des temporaires et 19 % l'ont fait par le passé (enquête swissstaffing de février 2025, citée par Gi Group) [27] (extrait).
- **Saisonnalité** : **non vérifiée**. Aucune série mensuelle publique n'a été trouvée. Les variations mensuelles du T1 2026 ci-dessus sont des variations sur un an, pas des profils saisonniers.
- **Réglementation** : plus de 7 400 entreprises sont autorisées pour le placement privé ou la location de services (répertoire SECO) [28] (extrait).
- **Concurrents** :
  - Adecco (n°1) et Randstad (n°2, environ 50 à 60 agences en Suisse) [29][30] ;
  - Interiman Group (« un des 4 plus importants acteurs ») [7] ;
  - Gi Group, qui a lancé Gi Group Medical en octobre 2024 [27].
  - En Valais, des extraits montrent Adecco (Adecco Valais Permanent), Randstad et Interiman à Sion [47].
  - **Non vérifiés** dans cette session : Manpower, Kelly, Synergie, Unique, Tempo et les agences locales valaisannes.

## 7. Contexte valaisan

- **Volume de construction** : inconnu — à relever sur la table OFS « Dépenses de construction par canton » px-x-0904010000_201 [32] (non consultée : domaine bloqué). Correction d'audit du 2026-10-05 : des valeurs d'une source non autorisée ont été retirées.

- **Conjoncture** : la BCVS (lettre économique de décembre 2025) prévoit une reprise de la construction, avec +2,8 % de valeur ajoutée contre -0,7 % l'année précédente [33] (extrait). Le Canton signale un manque de relève dans la construction (maçons, électriciens, métiers du bois et du verre) [34] (extrait).
- **Investissements cantonaux** : 533 MCHF bruts en 2024 (557,8 MCHF en 2023), dont environ 78 MCHF pour les routes nationales et 82 MCHF pour les routes cantonales [35] (extrait).
- **3e correction du Rhône (R3)** : c'est le plus grand projet de protection contre les crues du pays, sur 162 km, avec un achèvement prévu vers 2062. Le coût initial était estimé à 3,6 Md CHF, et une analyse parle de 5 à 6 Md CHF (les sites pollués sont un risque majeur selon le Contrôle fédéral des finances) [37][38]. Dans le Chablais :
  - la digue des Grandes Îles est terminée depuis fin 2025 (12 MCHF) ;
  - le premier projet bi-cantonal, aux Îles des Clous, est lancé ;
  - la mesure prioritaire Delta a été mise à l'enquête de janvier à février 2026 [36] (extrait).
- **Lonza, Viège (Ibex Biopark)** : le grand site de production mammalienne doit passer en exploitation commerciale complète mi-2026 [39]. Deux extensions en bioconjugaison ajoutent trois suites et environ 300 emplois, et le grand site de bioconjugaison doit démarrer en 2028 [39][40] (extrait).
- **A9 Haut-Valais** :
  - le tronçon Gampel/Steg – Viège Ouest a été inauguré le 27 octobre 2025 (7,6 km entre Rarogne et Viège Ouest, 420 MCHF) [41] ;
  - l'A9 doit être achevée fin 2027, sauf la traversée du Bois de Finges, et le tunnel du Riedberg doit ouvrir en décembre 2027. Coût total : 4,4 Md CHF [41][42] ;
  - les mesures d'économies de la Confédération risquent de retarder les travaux [43] (extrait).
- **Hôpitaux** :
  - le Valais concentre ses soins aigus à Sion (Valais romand) et à Brigue (Haut-Valais), entre 2020 et 2030 ; l'agrandissement de Sion a commencé à l'automne 2020 [44] ;
  - 78 MCHF couvrent les surcoûts des agrandissements de Brigue et de Sion, et environ 100 MCHF de travaux sont prévus à Brigue [45] ;
  - le Grand Conseil a voté une garantie supplémentaire de 294 MCHF pour l'Hôpital du Valais [46] (extrait).
- **Barrages et hydroélectricité** : **non vérifié** (pas de recherche possible, faute de quota).

## Sources

Toutes consultées le 2026-10-04. « (extrait) » = contenu lu dans l'extrait du moteur de recherche, la page étant bloquée par le proxy.

1. jobup.ch, profil Flexsis SA : https://www.jobup.ch/fr/societes/3393-flexsis-sa/ (extrait)
2. jobup.ch, profil Flexsis (Morges) / Interiman Group : https://www.jobup.ch/en/enterprises/3393-flexsis-morges/ (extrait)
3. business-monitor.ch, Flexsis SA (succursales, but, siège) : https://business-monitor.ch/fr/companies/159995-flexsis-sa (extrait)
4. jobs.ch, annonces Flexsis AG (Berne, Schaffhouse) : https://www.jobs.ch/en/vacancies/detail/90ac070e-8e2e-4b10-baba-41da386edb67/ ; https://www.jobs.ch/en/vacancies/detail/5bad13d6-e1cd-4e2e-ac84-981d30e358a5/ (extrait)
5. jobup.ch, annonce « Flexsis Sion » : https://www.jobup.ch/fr/emplois/detail/44f373bc-b891-42fc-89ab-3503c23414a4/ (extrait)
6. HR Festival, exposant Interiman Group : https://hrfestival.ch/en/ausstellende/interiman-group/ (extrait)
7. jobup.ch, profil Interima SA : https://www.jobup.ch/en/enterprises/3393-interima/ (extrait)
8. allnews.ch, « Interiman Group : surperformance du marché, acquisition et nomination clé » : https://allnews.ch/node/137154 (extrait)
9. allnews.ch, « chiffre d'affaires stable au premier semestre 2024 » : https://allnews.ch/node/126893 (extrait)
10. allnews.ch, « chiffre d'affaires en augmentation de 33 % pour 2021 » : https://allnews.ch/node/66417 (extrait)
11. Staffing Industry Analysts, liste « Staffing 100 Europe » 2026 : https://www.staffingindustry.com/lists/staffing-100-europe/2026-staffing-100-europe (extrait ; la page individuelle consultée n'est pas citée)
12. organisator.ch, « Interiman Group consolidates position as Swiss market leader » : https://www.organisator.ch/en/?p=18594 (extrait)
13. Great Place to Work Suisse, Interiman Group : https://greatplacetowork.ch/en/employer/interiman-group/ (extrait)
14. (référence retirée)
15. (référence retirée)
16. (référence retirée)
17. (référence retirée)
18. (référence retirée)
19. (référence retirée)
20. allai.events, « Hack VS – la nouvelle génération réinvente le Valais » : https://allai.events/uk/event/hack-vs---la-nouvelle-gnration-rinvente-le-valais (extrait)
21. luma.com, page de l'événement Hack VS : https://luma.com/n9981ooe?locale=fr (extrait)
22. swissstaffing, présentation « flexibilisation du travail » (6 février 2025), HR Neuchâtel : https://www.hr-neuchatel.ch/files/1738737315-1-presentation-wp-swissstaffing_ardien-laha-15335.pdf (extrait)
23. organisator.ch, « Swiss Staffingindex: Temporary staffing market turns positive after three years » : https://www.organisator.ch/en/?p=48185 (extrait)
24. Staffing Industry Analysts, « Swiss temp staffing returns to growth in March quarter » : https://www.staffingindustry.com/news/global-daily-news/swiss-temp-staffing-returns-to-growth-in-march-quarter (extrait)
25. organisator.ch, « Swiss Staffingindex: Turnover of personnel service providers falls after economic slowdown » : https://www.organisator.ch/en/?p=43952 (extrait)
26. Staffing Industry Analysts, « Swiss permanent hiring down 19.4% as temporary hours also decline » : https://www.staffingindustry.com/news/global-daily-news/swiss-permanent-hiring-down-194-as-temporary-hours-also-decline (extrait)
27. Gi Group Suisse, « Between skills shortages and uncertainty… » : https://ch.gigroup.com/blog/between-skills-shortages-and-uncertainty-why-flexible-staffing-solutions-are-crucial-now/ (extrait)
28. SECO, placement privé et location de services : https://www.seco.admin.ch/fr/placement-prive-et-la-location-de-services (extrait)
29. Le Temps, « Le travail temporaire se remettra de la crise » : https://www.letemps.ch/economie/travail-temporaire-se-remettra-crise (extrait, date de l'article inconnue)
30. b-sharpe, « Switzerland: 10 recruitment and employment agencies » : https://www.b-sharpe.com/en/blog/switzerland-10-recruitment-and-employment-agencies/ (extrait)
31. EKAS, présentation « Branchenlösung 82 Personalverleih » (2023), source probable du chiffre de 21 % pour la construction : https://www.ekas.admin.ch/fileadmin/Dokumente/Tagungen/Traegerschaftstagung/2023/Referate/DE/TT03_Cantagallo_Diethelm_Vorstellung_Branchenloesung_82_Personalverleih_d.pdf (extrait, attribution exacte à confirmer)
32. OFS, dépenses de construction par canton (px-x-0904010000_201) : https://www.pxweb.bfs.admin.ch/pxweb/fr/px-x-0904010000_201/-/px-x-0904010000_201.px/ (non consultée directement : domaine bloqué)
33. BCVS, Lettre économique de décembre 2025 : https://www.bcvs.ch/fileadmin/user_upload/site/publications/Lettre_economique/2025/BCVS_-_Lettre_Economique_-_Decembre_2025.pdf (extrait)
34. État du Valais, rapport annuel 2024, Économie et formation : https://www.vs.ch/web/rapport-annuel-2024/economie-et-formation (extrait)
35. La Télé, « Valais : le Grand Conseil valide les comptes 2024 » : https://latele.ch/articles/valais-le-grand-conseil-valide-les-comptes-2024-sans-opposition (extrait)
36. Canton de Vaud, « La 3e correction du Rhône franchit de nouvelles étapes dans le Chablais » : https://www.vd.ch/typo3temp/assets/pdfs/la-3e-correction-du-rhone-franchit-de-nouvelles-etapes-dans-le-chablais.pdf (extrait)
37. Le Temps, « Valais : les sites pollués pourraient bousculer la correction du Rhône » : https://www.letemps.ch/suisse/valais-sites-pollues-pourraient-bousculer-correction-rhone (extrait)
38. La Télé, « Troisième correction du Rhône : lignes directrices adoptées » : https://latele.ch/articles/troisieme-correction-du-rhone-lignes-directrices-adoptees (extrait)
39. Pharma Manufacturing, « Lonza's large-scale mammalian site in Visp continues ramp-up » : https://www.pharmamanufacturing.com/sector/contract-manufacturing/article/55378861/lonzas-large-scale-mammalian-site-in-visp-switzerland-continues-ramp-up-process (extrait)
40. GGBa, « Lonza expands bioconjugation capacity in Visp and creates 300 jobs » : https://ggba.swiss/en/lonza-expands-bioconjugation-capacity-in-visp-and-creates-300-jobs/ (extrait)
41. La Télé, « Autoroute A9 de Gampel/Steg à Brigue sans interruption » : https://latele.ch/articles/autoroute-a9-de-gampel-steg-a-brigue-vs-sans-interruption (extrait)
42. swissinfo.ch, « Traversée du Bois de Finges : travaux préliminaires bien avancés » : https://www.swissinfo.ch/fre/travers%c3%a9e-du-bois-de-finges%3a-travaux-pr%c3%a9liminaires-bien-avanc%c3%a9s/91848472 (extrait)
43. Le Temps, « Les mesures d'économies de la Confédération retarderont encore les travaux de l'autoroute du Haut-Valais » : https://www.letemps.ch/suisse/valais/les-mesures-d-economies-de-la-confederation-retarderont-encore-les-travaux-de-l-autoroute-du-haut-valais (extrait)
44. Le Temps, « Le Valais poursuit la concentration de ses hôpitaux » : https://www.letemps.ch/suisse/valais-poursuit-concentration-hopitaux (extrait)
45. La Télé, « Hôpitaux VS : 76 millions pour les équipements de Sion et de Brigue » : https://latele.ch/articles/hopitaux-vs-76-millions-pour-les-equipements-de-sion-et-de-brigue (extrait)
46. La Télé, « Le Parlement valaisan valide un soutien massif à son hôpital » : https://latele.ch/articles/le-parlement-valaisan-valide-un-soutien-massif-a-son-hopital (extrait)
47. talent.com, « agence de recrutement, Valais » : https://ch.talent.com/fr/jobs/k-agence-de-recrutement-l-valais-vs (extrait, source faible)
48. (référence retirée lors de l'audit du 2026-10-05 : profil personnel d'une personne nommée)
49. (référence retirée)
50. (référence retirée)
