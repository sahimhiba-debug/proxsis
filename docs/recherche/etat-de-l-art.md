# État de l'art — méthodes d'IA pour PROXSIS (cahier des charges, section 2c)

> **Note d'audit (2026-10-05).** Les seuils chiffrés sans référence (« quelques centaines », « 300 à 500 », « au plus 2 points »…) sont des ordres de grandeur d'expérience, pas des résultats publiés : ils sont marqués *heuristique* et doivent être validés sur nos données.

Date de consultation de toutes les sources : **2026-10-04**.

Objet : pour chacun des 10 thèmes techniques de PROXSIS, ce document présente le problème, les méthodes de référence, ce qui marche avec peu de données, les pièges et une recommandation concrète. Pour rappel, PROXSIS est le radar qui dit chaque semaine à chaque consultant de Flexsis / Interiman Group quelle entreprise appeler, pour quel besoin, quand et avec quels candidats, en expliquant pourquoi. Il s'appuie sur des signaux publics en français et en allemand : simap, permis de construire, offres d'emploi et registre du commerce. Les sources de données suisses (simap, Baublatt, FOSC, etc.) sont traitées dans `marche.md`. Le cadre juridique est traité dans `legal.md`.

## Méthode et limites

- L'accès direct à presque tous les sites d'éditeurs était bloqué (arxiv.org, aclanthology.org, huggingface.co, jmlr.org, dl.acm.org, sciencedirect.com, bfs.admin.ch, epfl.ch, etc. renvoient EGRESS_BLOCKED). Les références ont été vérifiées de trois façons :
  1. **recherche web** (43 recherches, jusqu'à épuisement du quota de la session) : titre, auteurs, revue, année et résumé lus dans les extraits renvoyés par le moteur ;
  2. **lecture directe des dépôts officiels** sur GitHub (README, CITATION, BibTeX), du miroir CRAN sur GitHub (fichiers DESCRIPTION / CITATION) et de PyPI (métadonnées des paquets, licences) ;
  3. **bibliographies secondaires fiables** lues directement, par exemple le chapitre 7 du livre *Fairness and Machine Learning*, la bibliographie de Fairlearn, les références de scikit-learn ou de CausalML. Dans ce cas, le lien donné dans la liste des références est celui de la source qui a permis la vérification.
- **Références écartées faute de vérification** : aucune revue de littérature académique sur le *lead scoring* B2B, l'article GBERT, le papier de Kaufman et al. sur la fuite de données et les détails de la nomenclature CH-ISCO-19 n'ont pu être vérifiés. Ils ne sont donc pas cités comme références. GBERT, Textkernel et CH-ISCO-19 sont nommés seulement comme exemples.
- **Chiffres** : chaque chiffre cité renvoie à sa source. Les calculs de puissance statistique (thème 8) et d'intervalle de confiance (thème 9) sont **les miens**. Ils reposent sur des hypothèses explicites et sont marqués « calcul propre ».

---

## Synthèse exécutive

1. **Commencer simple, mesurer honnêtement.** Règles transparentes, puis régression logistique ou LightGBM sur des lignes *entreprise × semaine*, évaluées par un backtest « vu à la date T » avec précision@k et intervalles bootstrap. Le *learning to rank*, le deep learning et l'uplift ne viennent qu'une fois des conditions chiffrées remplies (tableau final).
2. **Le délai compte autant que le score.** La survie à temps discret hebdomadaire colle au rythme du radar et gère la censure. Un simple classifieur suffit à l'estimer.
3. **Le rapprochement d'entités est la fondation.** Jointure exacte par IDE/UID quand il existe, sinon Fellegi–Sunter (Splink) avec normalisation des formes juridiques (SA/AG/Sàrl/GmbH). Un LLM n'arbitre que les cas ambigus.
4. **Extraction FR/DE : d'abord un LLM contraint par un schéma JSON** (par exemple Apertus : ouvert, suisse, Apache 2.0), mesuré sur un jeu de test annoté et gelé. On ne distille vers GLiNER ou XLM-R que si le coût ou la latence l'exigent. SwissBERT est sous licence **non commerciale**.
5. **Équité et causalité ne sont pas des options.** Audits contrefactuels du matching avant chaque version. Essai randomisé **au niveau entreprise, stratifié par consultant** : avec 2 agences, randomiser par consultant serait très probablement sous-dimensionné (calcul propre, thème 8).

---

## 1. Mesure en temps réel de la demande de travail à partir des offres d'emploi en ligne

**(1) Problème.** Les offres d'emploi en ligne sont un indicateur quasi immédiat de la demande de travail. Les statistiques officielles, elles, sont trimestrielles et publiées avec retard. PROXSIS a besoin de l'équivalent micro : détecter qu'une **entreprise donnée** recrute plus que d'habitude pour un **métier donné** dans une **région donnée**.

**(2) Méthodes de référence.**
- *Des annonces aux statistiques.* Turrell et al. (Bank of England) ont tiré de 15 millions d'annonces britanniques des statistiques de vacances par profession : un algorithme associe le texte libre aux codes SOC, ce qui permet d'analyser courbes de Beveridge et *mismatch* [1]. Hershbein & Kahn, sur environ 100 millions d'annonces américaines (Burning Glass, devenu Lightcast), montrent que les exigences de compétences ont augmenté davantage là où la Grande Récession a frappé le plus fort [2].
- *Représentativité.* L'OCDE a comparé les données Burning Glass aux statistiques officielles d'emploi par profession dans six pays. Elle conclut que ces données ont de bonnes propriétés statistiques, **surtout pour les professions très qualifiées et les recrutements qui passent davantage par Internet**. Elle propose aussi des pondérations pour corriger la représentativité [3]. Un papier OCDE plus récent compare Lightcast aux sources nationales de dix pays européens sur 2019–2022, par région, secteur et profession [4]. Kureková et al. soulignent la difficulté de corriger la représentativité des annonces en ligne, tout en recommandant de les exploiter [5].
- *Indices publics.* L'Indeed Hiring Lab publie un indice quotidien des annonces (moyenne mobile sur 7 jours, base 1er février 2020). Il est désaisonnalisé par la méthode de la Bundesbank pour séries journalières, appliquée série par série [6]. **Le dépôt public ne contient pas de série suisse** à la date de consultation : on y trouve notamment les États-Unis, le Royaume-Uni, l'Allemagne, la France, l'Irlande, le Canada et l'Australie [6]. Eurostat et le Cedefop ont mis en place en 2020 le *Web Intelligence Hub*. Il collecte des annonces depuis des portails privés, des services publics de l'emploi et des agences, applique une méthode de « landscaping » des sources et un dédoublonnage, et produit des statistiques expérimentales (OJAR) [7][8].
- *Suisse.* Le Stellenmarkt-Monitor Schweiz de l'Université de Zurich étudie les annonces d'emploi suisses depuis longtemps [9]. L'**obligation d'annoncer les postes vacants** s'applique aux professions dont le taux de chômage national atteint 5 % (seuil abaissé de 8 % à 5 % au 1er janvier 2020). Elle impose de signaler ces postes aux ORP avant toute publication [10]. Cela change donc les canaux par lesquels certaines offres apparaissent.

**(3) Avec peu de données.** On n'entraîne pas de modèle pour mesurer la demande : on **compte**. Les briques simples suffisent :
- dédoublonnage des annonces entre portails, par empreinte du titre normalisé, de l'employeur et du lieu ;
- classification du métier, par dictionnaire et règles, puis par embeddings ou LLM (thème 6) ;
- normalisation par rapport à l'historique de l'entreprise elle-même, par exemple « 3 annonces de maçon en 2 semaines contre 0,2 par semaine en moyenne sur 52 semaines ».
Un score d'anomalie robuste (médiane et écart absolu médian) par entreprise × métier fonctionne dès quelques mois d'historique. *(heuristique non sourcée, à valider par le backtest — audit du 2026-10-05)*

**(4) Pièges.**
- **Biais de couverture.** Les annonces en ligne sur-représentent les métiers qualifiés [3]. Or l'intérim en construction et en industrie recrute aussi par bouche-à-oreille et par agences.
- **Annonces d'agences concurrentes.** Une offre publiée par Adecco ou Manpower pour le compte d'un client signale un besoin **déjà intermédié**. Il faut distinguer l'employeur direct de l'intermédiaire.
- **Changements de canal** dus à l'obligation d'annonce [10].
- **Saisonnalité.** Le BTP connaît la reprise de printemps et des creux en fin d'année. Il faut désaisonnaliser ou comparer à la même semaine des années précédentes [6].
- **Fuite temporelle.** Il faut utiliser la date de **première détection** de l'annonce, pas sa date de collecte ou de mise à jour.
- **Biais de discrimination** dans les plateformes elles-mêmes. Sur la plateforme suisse de recrutement étudiée, les candidats étrangers reçoivent environ 6,5 % de contacts de recruteurs en moins que les candidats suisses comparables [11]. Les signaux issus des plateformes ne sont donc pas neutres (voir le thème 7).

**(5) Recommandation pour PROXSIS.** En V1, on construit un compteur hebdomadaire d'offres **directes** (hors agences) par entreprise × métier (CH-ISCO-19 ou ESCO) × région, dédoublonné, avec un score d'écart à la ligne de base de l'entreprise. C'est un signal parmi d'autres, et il est expliqué en clair au consultant (« +3 offres de grutier depuis 10 jours »). **Condition de passage au complexe** (pondérations de représentativité, nowcasting agrégé) : seulement si PROXSIS doit produire des indicateurs **macro** par région, par exemple pour la direction d'Interiman. Il faut alors une comparaison à une source officielle sur au moins 8 trimestres.

---

## 2. Prévision de la main-d'œuvre de chantier à partir des permis et des projets

**(1) Problème.** Un permis de construire ou un marché attribué annonce un besoin de main-d'œuvre **futur**, avec un décalage (délai avant démarrage, puis montée en charge) et une ampleur qui dépend du montant et du type d'ouvrage. Il faut estimer **quand** et **combien** de personnes, par corps de métier.

**(2) Méthodes de référence.**
- *Coefficients de main-d'œuvre.* Le Construction Skills Network (CITB, avec Experian) prévoit l'emploi par métier au Royaume-Uni. Il part de la production prévue par sous-secteur et lui applique des **coefficients de main-d'œuvre**, c'est-à-dire le nombre de travailleurs de chaque métier nécessaires pour produire 1 M£ de production. Il ajoute des flux de productivité, d'entrées et de sorties du secteur [12]. C'est l'équivalent agrégé d'un ratio « heures par CHF de travaux ».
- *Modèles par projet.* Wong, Chan & Chiang ont construit 11 modèles de régression multiple (main-d'œuvre totale et dix métiers) sur 54 projets. La demande dépend du coût, de la complexité, des conditions du site et du type de projet [13].
- *Revue de littérature.* Zhao et al. ont analysé 27 articles sur la prévision de main-d'œuvre dans la construction. La production de construction est l'indicateur économique le plus influent, et la plupart des méthodes gèrent mal les ruptures brutales du marché du travail [14].
- *Courbes en S et histogrammes de main-d'œuvre.* La pratique de planification répartit l'effort total dans le temps avec une montée, un plateau et une décrue. Les courbes en S cumulées servent à suivre l'avancement (voir aussi [14]).
- *Délai permis → démarrage.* Aux États-Unis, le Census Bureau publie ce délai chaque année : en moyenne 1,5 mois en 2023 pour les logements neufs privés, avec des variations selon le type de construction [15]. **Ce chiffre ne se transpose pas à la Suisse** (procédures, recours, saisons). En Suisse, le RegBL/GWR enregistre les projets de construction au plus tard à l'octroi du permis [16], et des jeux de données publics sur les demandes et autorisations de construire existent [17]. Ce sont les bases pour estimer **localement** la distribution des délais.

**(3) Avec peu de données.**
- Une **table de coefficients** : montant de travaux × ratio heures/CHF par type d'ouvrage × répartition par métier. Elle est **calibrée avec les consultants et les données de missions passées** de Flexsis.
- Un **gabarit temporel paramétrique** : délai avant démarrage, puis courbe en cloche ou trapèze.
- Une **distribution empirique des délais** permis → démarrage par canton et type d'ouvrage, estimée par Kaplan-Meier si certains démarrages ne sont pas encore observés (censure, voir le thème 3).
Quelques centaines de projets suffisent pour des médianes par catégorie, pas pour un modèle fin par projet. *(heuristique non sourcée, à valider par le backtest — audit du 2026-10-05)*

**(4) Pièges.**
- **Montant déclaré** souvent indicatif ; ratios très variables entre gros œuvre et second œuvre.
- **Projets abandonnés ou retardés** (recours, permis jamais utilisés) : ne pas les compter comme « démarrage immédiat ».
- **Fuite temporelle** : la date de démarrage effective n'est connue qu'après coup et ne doit jamais servir de variable à la date T.
- **Double comptage** : permis, appel d'offres simap et attribution sont trois signaux du même projet, à relier (thème 5).
- **Transposition** de ratios étrangers (CITB) sans recalage local.

**(5) Recommandation pour PROXSIS.** En V1, on applique un modèle « coefficient × gabarit » transparent : « permis de 4 MCHF, immeuble locatif → environ X personnes-semaines de gros œuvre entre S+8 et S+30 ». Les fourchettes sont larges et affichées comme telles. On estime aussi les délais permis → démarrage par Kaplan-Meier sur les données suisses disponibles. **Condition de passage au complexe** (régression ou GBM par projet, ARIMA/VEC agrégés) : au moins quelques centaines de projets suivis avec une main-d'œuvre réelle connue (missions Flexsis rattachées au projet), et un gain mesuré en backtest sur l'erreur de délai et de volume.

---

## 3. Modèles de survie pour le délai avant embauche ou avant besoin

**(1) Problème.** On veut prédire **dans combien de temps** une entreprise aura un besoin (commande de personnel) après un signal. Beaucoup d'entreprises n'ont pas encore eu de besoin à la date d'analyse : ce sont des observations **censurées à droite**. Les exclure ou les compter comme « jamais » biaise le modèle.

**(2) Méthodes de référence.**
- *Cox à risques proportionnels* : modèle semi-paramétrique de référence [18].
- *Survie à temps discret* : le temps est découpé en intervalles (ici des semaines), et on modélise le risque conditionnel de chaque intervalle par une régression logistique sur des données « individu-période » [19].
- *Forêts de survie aléatoires* (RSF) [20].
- *Gradient boosting* : XGBoost implémente nativement un modèle de temps de défaillance accéléré (AFT) qui gère différents types de censure [21]. scikit-survival propose Cox pénalisé, RSF, boosting et métriques adaptées à la censure (licence GPL-3.0) [22].
- *Réseaux profonds* : DeepSurv (Cox neuronal) [23], DeepHit (distribution discrète des temps, risques concurrents) [24], extensions Cox-Time / Cox-CC (pycox) [25].
- *Métriques* : le C-index d'Uno ne dépend pas de la distribution de censure, contrairement au C-index usuel [27]. Le score de Brier pondéré par la censure, et son intégrale (IBS), mesurent à la fois discrimination et calibration [26]. Le Brier score a des limites en cas de censure administrative [29].

**(3) Avec peu de données.** Les études comparatives montrent que les modèles complexes battent rarement nettement les modèles simples sur de petits échantillons. Le grand benchmark de Herrmann et al. (18 jeux de 35 à 1 000 observations) constate notamment un apport prédictif limité des données haute dimension [28]. Avec quelques centaines à quelques milliers d'événements :
- **régression logistique à temps discret** sur des lignes *entreprise × semaine*, avec quelques variables (type de signal, montant, secteur, historique client, saison) ;
- ou **Cox pénalisé**.
Les RSF et le boosting deviennent intéressants au-delà de quelques milliers d'événements, avec des interactions non linéaires plausibles. Les réseaux profonds demandent nettement plus de données et n'apportent pas d'explicabilité native. *(heuristique non sourcée, à valider par le backtest — audit du 2026-10-05)*

**(4) Pièges.**
- **Définir l'origine du temps** : la date de publication du signal, pas celle de l'événement réglementaire non public.
- **Événement observé seulement chez les clients** : un besoin couvert par un concurrent n'est pas observé. C'est un risque concurrent non observé. Il faut le traiter comme une censure et documenter le biais.
- **Censure informative** : une entreprise radiée du registre ne « censure » pas au hasard.
- **Variables qui évoluent dans le temps** : en temps discret, chaque ligne-semaine ne doit contenir que l'information disponible à cette semaine.
- **Évaluation** : C-index et IBS sur une période **future**, jamais par validation croisée aléatoire.

**(5) Recommandation pour PROXSIS.** En V1, on retient une survie à temps discret hebdomadaire, estimée par régression logistique, puis par LightGBM sur les mêmes lignes. On en tire directement P(besoin dans 4 semaines) et P(besoin dans 8 semaines), ce qui alimente le « quand » du radar. Évaluation : C-index d'Uno, Brier à 4 et 8 semaines, courbes de calibration. **Condition de passage au complexe** (RSF, XGBoost-AFT, DeepHit pour plusieurs types de besoins) : au moins quelques milliers d'événements, et un gain d'IBS ou de C-index dont l'intervalle bootstrap exclut zéro sur au moins 3 périodes de backtest successives.

---

## 4. Classement appris (learning to rank) pour prioriser les entreprises

**(1) Problème.** Un consultant ne peut passer qu'un nombre limité d'appels par semaine. Il faut **ordonner** les entreprises pour que les k premières soient les plus utiles. Ce qui compte, c'est la qualité du haut de liste, pas la précision globale.

**(2) Méthodes de référence.**
- *Learning to rank* : RankNet → LambdaRank → **LambdaMART**, la version arbres boostés qui optimise directement des métriques de rang comme le NDCG [30]. LightGBM l'implémente efficacement (objectif `lambdarank`) [31]. Métrique de référence : le NDCG [32], et en pratique la **précision@k** avec k égal au nombre d'appels réalisables.
- *Lead scoring prédictif* : dans la pratique B2B, il s'agit d'un classifieur de propension, du type « probabilité de conversion » appliqué à une liste triée. **Je n'ai pas pu vérifier de revue académique de référence sur le lead scoring B2B.** La littérature accessible est surtout faite d'études de cas et de documentation de vendeurs.
- *Uplift contre propension* : un modèle de propension classe les entreprises qui **auront** un besoin. Un modèle d'**uplift** classe celles pour lesquelles **l'appel change** le résultat. L'uplift a été popularisé en marketing par les arbres d'uplift de Radcliffe & Surry [33]. Il est estimé par des méta-apprenants (T-, S- et X-learner) [34], des arbres et forêts causaux [35][36], et outillé par CausalML [37] et scikit-uplift, avec les métriques Qini et uplift@k [38]. L'uplift **exige des données où l'appel a été attribué aléatoirement** (voir le thème 8).

**(3) Avec peu de données.** Avec quelques centaines d'exemples positifs, un **classifieur ponctuel** (logistique ou GBM) trié par score fait généralement aussi bien qu'un ranker par paires. Il est aussi plus stable et plus facile à calibrer. LambdaMART n'apporte un gain que si l'on dispose de **groupes de requêtes** (listes consultant × semaine) assez nombreux et de pertinences graduées (taille de la commande).

**(4) Pièges.**
- **Labels sélectifs** : le résultat n'est observé que pour les entreprises appelées ; un modèle entraîné sur le CRM apprend les habitudes des consultants, pas le besoin réel.
- **Boucle de rétroaction** : le radar oriente les appels, donc les futurs labels.
- **Confondre propension et uplift** : appeler une entreprise qui allait de toute façon appeler l'agence n'apporte rien.
- **Métrique** : précision@k **par consultant et par semaine**, agrégée avec intervalles de confiance (thème 9).

**(5) Recommandation pour PROXSIS.** En V1, le score combine P(besoin à 4 semaines) (thème 3) et la valeur attendue (taille, marge, adéquation au vivier de candidats), et la liste est triée par consultant. On conserve dès le départ un **groupe témoin aléatoire** (thème 8) pour créer les données d'uplift. **Condition de passage** : (a) LambdaMART quand on dispose d'au moins quelques centaines de listes consultant × semaine labellisées et d'un gain de précision@k en backtest ; (b) uplift (X-learner ou forêt causale) quand on a accumulé assez de données randomisées pour estimer un Qini significativement positif sur des données tenues à l'écart.

---

## 5. Rapprochement d'entités (entity resolution / record linkage)

**(1) Problème.** Il faut relier entre elles les mentions d'une même entreprise dans simap, les permis, les offres d'emploi, le registre du commerce et le CRM de Flexsis. On rencontre des orthographes et des langues différentes (« Muster Bau SA » / « Muster Bau AG »), des formes juridiques variables (SA/AG/Sàrl/GmbH/Sagl), des succursales, et des changements de nom ou des fusions.

**(2) Méthodes de référence.**
- *Fellegi–Sunter* : c'est le modèle probabiliste fondateur. Il compare des paires sur plusieurs champs et estime des probabilités m (accord si même entité) et u (accord par hasard), souvent par l'algorithme EM [39]. Ses variantes modernes gèrent les données manquantes [40]. Pour un ouvrage de synthèse, voir [48].
- *Splink* : implémentation libre (MIT) et passant à l'échelle de Fellegi–Sunter [41]. **Son README précise qu'il n'est pas conçu pour une seule colonne « nom d'entreprise ».** Il marche mieux avec plusieurs colonnes peu corrélées (nom, NPA, rue, téléphone, secteur…) [41].
- *dedupe* : apprentissage actif, l'utilisateur étiquetant les paires les plus informatives. Il s'appuie sur les travaux de Bilenko (licence MIT) [42][43].
- *Magellan / py_entitymatching* : chaîne complète (blocage, appariement supervisé, débogage, échantillonnage) sous licence BSD [44].
- *Ditto* : appariement par fine-tuning de modèles de langue pré-entraînés, chaque fiche étant sérialisée en texte [45].
- *LLM* : les modèles de fondation peuvent apparier des entités en zéro ou peu d'exemples [46]. Une étude du groupe de Mannheim compare des LLM hébergés et open source pour cette tâche et les présente comme une alternative plus robuste et moins gourmande en données d'entraînement que les transformers fine-tunés [47].
- *Identifiant suisse* : l'IDE/UID se compose du préfixe « CHE » et de 9 chiffres, dont le dernier est une clé de contrôle modulo 11. Le format actuel date de 2011 et a remplacé l'ancien en 2014. Un service web public SOAP permet d'interroger le registre IDE par numéro [49].

**(3) Avec peu de données.**
- Quand l'**UID est présent**, une jointure exacte, après validation de la clé de contrôle [49], règle une grande partie des cas sans aucun apprentissage.
- Pour le reste : **blocage** sur NPA ou commune et premiers caractères du nom normalisé, puis Fellegi–Sunter non supervisé (EM) avec Splink. L'apprentissage actif (dedupe) avec **quelques centaines de paires étiquetées** suffit souvent à bien calibrer. *(heuristique non sourcée, à valider par le backtest — audit du 2026-10-05)*
- Les LLM sont utiles en **arbitrage des paires ambiguës** (zone grise des scores), pas sur toutes les paires, pour des raisons de coût et de reproductibilité.
- La normalisation est décisive : retirer les formes juridiques FR/DE/IT, « en liquidation » / « in Liquidation », les accents, la ponctuation, et les traductions usuelles (Genossenschaft / Société coopérative).

**(4) Pièges.**
- **Fermeture transitive** : A=B et B=C donne A=C et peut fusionner deux entreprises différentes. Contrôler la taille des grappes.
- **Siège et succursale** : vérifier comment chaque source identifie les établissements.
- **Homonymes** (« Bâtiment SA ») et **groupes** (holding contre filiale opérationnelle).
- **Temporalité** : noms et adresses changent ; le rapprochement doit être reproductible « à la date T » pour les backtests.
- **Évaluation biaisée** : mesurer précision et rappel sur des paires **tirées au hasard dans toutes les zones de score**, pas seulement sur les cas faciles.

**(5) Recommandation pour PROXSIS.** En V1, le rapprochement se fait en cascade :
1. jointure par UID ;
2. Splink (nom normalisé, NPA, rue, domaine web, téléphone) avec seuils ;
3. file de revue humaine pour la zone grise, avec un LLM comme suggestion et non comme décision.
On mesure précision et rappel sur 300 à 500 paires annotées et stratifiées. **Condition de passage au complexe** (Ditto ou LLM fine-tuné) : seulement si le rappel reste insuffisant sur les cas sans UID après optimisation des règles, et avec un jeu d'au moins 1 000 paires annotées. *(heuristique non sourcée, à valider par le backtest — audit du 2026-10-05)*

---

## 6. Extraction d'informations multilingue FR/DE à partir de publications officielles

**(1) Problème.** Il faut transformer des avis simap, des publications FOSC/registre du commerce, des avis de permis cantonaux et des offres d'emploi en **champs structurés** : maître d'ouvrage, adjudicataire, montant, CPV, lieu, dates, métiers, nombre de postes, UID. Les textes sont en français et en allemand, et parfois en italien.

**(2) Méthodes de référence.**
- *LLM avec sortie structurée.* On contraint le décodage par un schéma JSON ou une grammaire, ce qui garantit une sortie syntaxiquement valide [63]. L'appel d'outil (*tool calling*) sert à la même chose. Une revue fait le point sur l'extraction générative par LLM [65]. Dagdelen et al. montrent qu'un LLM fine-tuné peut extraire des relations structurées complexes à partir de texte scientifique [64].
- *Apertus* (faits vérifiés) :
  - publié le **2 septembre 2025** par l'EPFL, l'ETH Zurich et le CSCS (Swiss AI Initiative) ;
  - deux tailles, **8B et 70B** (versions de base et *Instruct*) ;
  - **licence Apache 2.0**, avec poids, données, recettes et points de contrôle publiés [51][52] ;
  - entraîné sur **15 000 milliards de tokens**, dont environ **40 % non anglais** ;
  - nombre de langues : la fiche modèle parle de 1 811 langues prises en charge, le rapport technique de « plus de 1 800 langues », le communiqué de presse de « plus de 1 000 langues » [50][51][52]. Les deux chiffres sont rapportés tels quels.
  - données d'entraînement uniquement ouvertes, respect rétroactif des exclusions robots.txt, filtrage des données personnelles, objectif « Goldfish » contre la mémorisation verbatim [50] ;
  - rapport technique : arXiv:2509.14233, publié à ACL 2026 [50].
  - **Apertus 1.5** est sorti le **24 juillet 2026**, toujours en 8B et 70B. Il apporte la compréhension d'images, une entrée audio expérimentale, un meilleur raisonnement avec mode « Thinking » optionnel, ainsi que de meilleurs suivi d'instructions et appel d'outils [53][55]. La fenêtre de contexte est annoncée à 262 144 tokens par Public AI [55]. Certains fournisseurs exposent une limite plus basse : ce point est à vérifier sur la fiche du modèle utilisé.
  - **accès** : téléchargement sur Hugging Face (`swiss-ai/Apertus-70B-2509`, `swiss-ai/Apertus-v1.5-70B`, etc.) [52] ; **Swisscom** pour ses clients entreprises, sur sa plateforme « Swiss AI Platform » souveraine [51][56] ; **Public AI Inference Utility**, avec chat public et API compatible OpenAI (`api.publicai.co/v1/chat/completions`, servie par vLLM, gratuite grâce à du calcul donné et disponible comme fournisseur d'inférence Hugging Face) [54].
- *Modèles spécialisés entraînés.*
  - NER spaCy [61] ;
  - fine-tuning d'encodeurs multilingues : XLM-R [58], CamemBERT pour le français [59], SwissBERT pour les quatre langues nationales [57]. **SwissBERT est sous licence CC BY-NC 4.0, donc non commerciale** [57]. Des modèles allemands comme GBERT existent aussi.
  - **GLiNER**, un NER « généraliste » à encodeur bidirectionnel capable d'extraire des types d'entités arbitraires sans réentraînement [60]. La bibliothèque est sous Apache 2.0 ; la licence des poids varie selon le modèle.
  - *Few-shot* : SetFit fine-tune des sentence-transformers sans prompt. Ses auteurs rapportent qu'avec 8 exemples étiquetés par classe, SetFit rivalise avec RoBERTa-large entraîné sur 3 000 exemples pour un jeu d'avis clients [62].

**(3) Avec peu de données.** C'est là que **les LLM changent la donne** : contraint par un schéma JSON, avec 3 à 10 exemples dans le prompt, un LLM extrait de façon utilisable **sans jeu d'entraînement**. Les modèles spécialisés (GLiNER, XLM-R fine-tuné) deviennent en général compétitifs avec quelques centaines à quelques milliers d'exemples annotés, que le LLM peut pré-annoter avant correction humaine (distillation). Coûts et latence : aucun chiffre vérifiable et transposable trouvé. Ils dépendent du fournisseur, de la taille du modèle et du volume hebdomadaire (à estimer). **Il faut les mesurer sur un échantillon réel** : coût par document, latence p50/p95, taux de JSON invalide. *(heuristique non sourcée, à valider par le backtest — audit du 2026-10-05)*

**(4) Pièges.**
- **Hallucination de champs** : le LLM remplit un montant ou un UID absent du texte. Il faut mesurer le taux de « faux remplissage » sur les champs vides de la référence.
- **Normalisation** des montants (HT ou TTC, CHF), des dates (publication, décision, délai de recours) et des noms.
- **Dérive** : les formats de publication changent, par exemple avec la nouvelle plateforme simap (voir `marche.md`), et les modèles changent de version.
- **Fuite du jeu de test** : ajuster les prompts sur le jeu de test le contamine.
- **Licences** : SwissBERT n'est pas utilisable commercialement sans accord [57]. Il faut vérifier la licence des poids GLiNER choisis.
- **Souveraineté** des données (voir `legal.md`) : c'est un argument pour Apertus hébergé en Suisse.

**(5) Recommandation pour PROXSIS.**
- **Jeu de test gelé.** On tire 300 à 500 documents, stratifiés par source (simap, FOSC, permis par canton, offres), par langue (FR/DE) et par période. Chaque document est **annoté deux fois** de manière indépendante selon un guide d'annotation écrit, avec arbitrage des désaccords. On mesure l'accord inter-annotateurs par champ. Le jeu est versionné et gelé (empreinte du fichier), **jamais utilisé pour ajuster les prompts**. Un jeu de développement séparé sert aux itérations. *(heuristique non sourcée, à valider par le backtest — audit du 2026-10-05)*
- **Métriques** : *exact match* par champ après normalisation (montant, date, UID, CPV), F1 par champ pour les listes (métiers, entités), taux de faux remplissage, taux de JSON invalide, coût et latence.
- **V1** : Apertus 70B (Swisscom ou Public AI) ou un autre LLM, en sortie JSON contrainte, avec un post-traitement déterministe : validation de l'UID [49], du format de date et des montants.
- **Condition de passage** à un modèle spécialisé distillé (GLiNER ou XLM-R fine-tuné, hébergé en interne) : volume ou coût LLM jugé trop élevé, ou besoin de latence faible, **et** F1 du modèle distillé à au plus 2 points du LLM sur le jeu gelé. *(heuristique non sourcée, à valider par le backtest — audit du 2026-10-05)*

---

## 7. Matching candidat-poste et équité

**(1) Problème.** Pour chaque besoin détecté, PROXSIS propose « avec quels candidats ». Il faut rapprocher un besoin (métier, compétences, lieu, dates, permis de travail) des profils du vivier, **sans discriminer** selon le genre, la nationalité ou l'âge. C'est la fonction la plus sensible du système.

**(2) Méthodes de référence.**
- *Taxonomies* : ESCO (classification européenne multilingue des compétences et professions, liée à ISCO-08), ISCO-08 et sa déclinaison suisse CH-ISCO-19 (OFS). Elles servent de pivot commun entre offres, besoins et CV.
- *Embeddings* : modèles multilingues, dont certains sont pré-entraînés spécifiquement sur le marché de l'emploi avec la taxonomie ESCO, comme ESCOXLM-R [66]. On les combine avec des contraintes dures : distance, disponibilité, permis, certifications.
- *Analyseurs commerciaux* de CV et d'offres, comme Textkernel (voir `marche.md`).
- *Mesures d'équité* :
  - parité démographique et ratio d'impact disparate [76]. La **règle des 4/5** en est un seuil historique, mais elle ne se confond pas avec la notion juridique d'impact disparate [77] ;
  - *equal opportunity* : taux de vrais positifs égaux entre groupes [75] ;
  - synthèse critique : Barocas, Hardt & Narayanan [78].
- *Preuves de biais dans les systèmes d'emploi* : des annonces STEM neutres en genre moins montrées aux femmes, à cause des enchères publicitaires [67] ; une diffusion optimisée biaisée même sans ciblage discriminatoire [68] ; des annonces de coaching pour postes très bien payés montrées plus souvent à des utilisateurs simulés « hommes » [69] ; des représentations de professions qui reproduisent les écarts de genre [74] ; des promesses de « débiaisage » des outils de présélection rarement vérifiables [73] ; en Suisse, une discrimination des recruteurs envers les étrangers mesurée sur une plateforme [11].
- *Audits* :
  - tests de correspondance, c'est-à-dire des CV fictifs appariés qui ne diffèrent que par l'attribut testé [70]. Une méta-analyse montre une discrimination raciale à l'embauche stable dans le temps aux États-Unis [71]. Les critiques de validité de ces tests sont discutées dans [72] ;
  - **tests contrefactuels** : on change le nom, la nationalité ou l'âge d'un profil et on observe le rang ;
  - tests de permutation pour l'inférence sur les métriques d'équité [82] ;
  - boîtes à outils : Fairlearn [79], AIF360 [80], LiFT de LinkedIn [81].

**(3) Avec peu de données.** Le matching **n'a pas besoin d'apprentissage supervisé** au départ : des filtres durs (métier ESCO/CH-ISCO, distance, disponibilité, permis, certifications), puis une similarité d'embeddings, puis la décision humaine du consultant. Les audits contrefactuels n'ont pas non plus besoin de données réelles : il suffit de **50 à 200 profils fictifs** appariés. *(heuristique non sourcée, à valider par le backtest — audit du 2026-10-05)*

**(4) Pièges.**
- **Variables proxy** : photo, nom, nationalité, année de naissance, commune, langue maternelle, trous dans le parcours.
- **Apprendre des placements passés** reproduit les biais passés des clients et des recruteurs [11][70].
- Une **règle des 4/5 appliquée mécaniquement** est trompeuse sur de petits effectifs, d'où des intervalles ou tests de permutation [77][82].
- **Statut du permis de travail** : il est juridiquement pertinent, mais c'est un proxy de la nationalité. Il ne doit servir que de contrainte d'éligibilité légale, jamais de facteur de score.
- **Réglementation** : le recrutement assisté par IA est traité comme un usage à haut risque par le règlement européen sur l'IA. L'applicabilité à Flexsis et les obligations suisses (nLPD, profilage) sont à faire valider (voir `legal.md`).

**(5) Recommandation pour PROXSIS.**
- **V1** : filtres durs, puis similarité d'embeddings (ESCO comme pivot), puis une **liste courte présentée avec ses raisons** (compétences communes, distance, disponibilité). Aucun attribut protégé ni proxy évident dans le score. Le consultant décide.
- **Avant chaque version** : un **audit contrefactuel** avec des paires de profils fictifs identiques sauf le genre, la nationalité ou l'âge. Critère : aucune différence de rang systématique (test de permutation). On ajoute un suivi des taux de sélection par groupe là où la collecte est légale.
- **Condition de passage** à un matching appris (ranker entraîné sur les placements) : seulement après un audit d'équité documenté sur les données d'entraînement, avec la contrainte *equal opportunity* surveillée en production.

---

## 8. Mesurer l'effet réel d'un appel anticipé (inférence causale)

**(1) Problème.** Si les consultants appellent les entreprises signalées et décrochent des missions, est-ce **grâce** au radar ? Ces entreprises auraient peut-être appelé l'agence de toute façon. Seule une comparaison avec un **contrefactuel** crédible répond à la question.

**(2) Méthodes de référence.**
- **Essai randomisé contrôlé** : c'est la référence. On peut randomiser par entreprise, ou par grappe (consultant, agence). Déclarer et diagnostiquer le plan d'expérience à l'avance, par simulation, est une bonne pratique outillée [84][85].
- **Différence de différences** quand la randomisation est impossible, avec une attention particulière aux traitements échelonnés dans le temps [83].
- **Modèles d'uplift** et effets hétérogènes [33][34][35][36] pour cibler, une fois des données randomisées disponibles.

**(3) Avec peu de données : puissance statistique (calcul propre).** Hypothèses :
- critère principal binaire : « demande de personnel obtenue de l'entreprise dans les 30 jours » ;
- test bilatéral à α = 5 %, puissance 80 %.
Effectifs **par bras** pour une randomisation au niveau entreprise :

| Taux témoin → taux traité (hypothèses) | Entreprises par bras |
|---|---|
| 5 % → 7,5 % | ≈ 1 470 |
| 5 % → 10 % | ≈ 430 |
| 10 % → 15 % | ≈ 680 |
| 20 % → 30 % | ≈ 290 |

Avec une **randomisation par consultant**, l'effet de plan vaut DE = 1 + (m − 1)·CCI (formule classique), où m est le nombre d'entreprises par consultant et CCI la corrélation intra-consultant. Exemple avec 2 agences, 30 consultants (15 par bras), m = 100 et CCI = 0,05 : DE ≈ 5,95, soit un effectif effectif d'environ **250 entreprises par bras**. Ce plan ne détecte que des effets très importants (de l'ordre de 20 % → 30 %). **Conclusion : avec 2 agences sur 6 semaines, il faut randomiser au niveau entreprise, à l'intérieur de chaque consultant (stratification), et prolonger le suivi des résultats au-delà des 6 semaines.**

**(4) Pièges.**
- **Contamination** : les consultants parlent entre eux et les témoins peuvent être appelés quand même. Acceptable si le témoin signifie « usage habituel », mais à mesurer.
- **Déplacement d'effort** : les appels « radar » remplacent d'autres appels (interférence entre unités). Il faut mesurer aussi l'activité totale du consultant.
- **Fenêtre trop courte** : un placement peut arriver après les 6 semaines. Critère intermédiaire préenregistré et suivi à 8–12 semaines.
- **Tests multiples** et critère choisi *a posteriori* : préenregistrer le critère principal [84].
- **Biais de sélection** si les consultants choisissent quelles recommandations suivre : analyse en **intention de traiter**.

**(5) Recommandation pour PROXSIS.** Pilote de 6 semaines dans les 2 agences, avec un plan préenregistré :
- chaque semaine, pour chaque consultant, les entreprises éligibles sont **tirées au sort** entre « affichées dans le radar » et « témoin calculé mais masqué » ;
- critère principal : demande de personnel à 30 jours ; critères secondaires : missions, heures facturées, délai d'avance ;
- analyse en intention de traiter, avec des intervalles clusterisés par consultant.
**Condition de passage au complexe** (uplift, forêts causales) : uniquement avec les données randomisées accumulées, et après un effet moyen estimé non nul. **Différence de différences** : en repli seulement si la randomisation est refusée par le métier, avec des agences témoins aux tendances préalables comparables [83].

---

## 9. Calibration et évaluation honnête

**(1) Problème.** Un radar qui « marche en démo » peut échouer en production si l'évaluation a utilisé de l'information future, si les intervalles ne sont pas rapportés, ou si les scores ne sont pas des probabilités. Le consultant doit pouvoir lire « 30 % » comme « 3 fois sur 10 ».

**(2) Méthodes de référence.**
- **Fuite de données** : toute information indisponible au moment de la prédiction et utilisée à l'entraînement ou à l'évaluation [86].
- **Validation temporelle** : séparation chronologique, avec par exemple `TimeSeriesSplit` [87], et évaluation à origine glissante (*walk-forward*) [96].
- **Calibration** :
  - méthode de Platt (sigmoïde) [89], régression isotonique [90], comparaison des deux [91] ;
  - les réseaux modernes sont souvent mal calibrés [92] ;
  - le score de Brier se décompose en fiabilité, résolution et incertitude [93] ;
  - hiérarchie des notions de calibration [94] ;
  - la documentation de scikit-learn, s'appuyant sur [91], indique que l'isotonique fait aussi bien ou mieux que la sigmoïde **au-delà d'environ 1 000 échantillons**, et que la sigmoïde est préférable sur de petits échantillons [88].
- **Intervalles** : bootstrap [95], **par blocs** (consultant-semaine) quand les observations sont groupées.

**(3) Avec peu de données.**
- Calibration sigmoïde plutôt qu'isotonique [88].
- Intervalles **toujours** affichés. Calcul propre : sur 1 000 recommandations avec une précision de 20 %, la demi-largeur de l'IC à 95 % binomial est d'environ ±2,5 points. Sur 300 recommandations, elle est d'environ ±4,5 points. Le regroupement par consultant et par semaine élargit encore ces intervalles.
- Délai d'avance **médian**, plus robuste que la moyenne.

**(4) Pièges (liste de contrôle « point-in-time »).**
- Variables horodatées par leur **date de publication ou de première détection**, jamais de mise à jour.
- Statut du registre *connu à T* (pas de radiation future).
- Rapprochement d'entités et encodages de cible recalculés **avec les seules données antérieures à T**.
- Aucun champ CRM rempli **après** l'appel.
- Hyperparamètres choisis sur une validation **antérieure** à la période de test.
- **Délai de garde** (*gap*) entre la fin de l'entraînement et l'horizon de prédiction.

**(5) Recommandation pour PROXSIS.** On met en place un **backtest hebdomadaire walk-forward** sur au moins 52 semaines : à chaque date T, on reconstruit les variables « vues à T », on prédit, puis on compare aux besoins des semaines T+1 à T+8. Le tableau de bord rapporte :
- la précision@k par consultant-semaine (k = capacité d'appels), avec IC par bootstrap par blocs ;
- le Brier et la courbe de fiabilité ;
- le délai d'avance médian (date du besoin moins date de la première alerte, sur les vrais positifs) ;
- la comparaison systématique à une **référence naïve** : entreprises triées par activité récente.
**Condition de passage à la calibration isotonique** : plus d'environ 1 000 exemples de calibration [88]. **Condition de mise en production d'un nouveau modèle** : gain de précision@k dont l'IC exclut zéro sur la période de test la plus récente.

---

## 10. Prévision par métier et par région (séries courtes hiérarchiques)

**(1) Problème.** Il faut prévoir, sur quelques semaines à quelques mois, la demande (offres, permis, commandes) par métier × région, avec des agrégats par canton, par famille de métiers et au total. Les séries sont **courtes**, souvent **intermittentes** (beaucoup de zéros) et **hiérarchiques**.

**(2) Méthodes de référence.**
- *Références naïves* : naïf saisonnier, ETS et ARIMA automatiques [99][96] ; méthodes pour la demande intermittente (Croston et variantes, disponibles dans statsforecast) [110].
- *Modèles globaux à arbres* : un seul LightGBM entraîné sur toutes les séries, avec retards, calendrier et variables exogènes. Les meilleures solutions de la compétition M5 reposaient largement sur LightGBM [98][31]. mlforecast l'outille [110].
- *Réconciliation hiérarchique* : *bottom-up*, *top-down*, combinaison optimale [100] et **MinT** [101], implémentés dans hierarchicalforecast [102].
- *Deep learning* : N-BEATS [103], TFT avec covariables et interprétabilité [104], PatchTST [105] ; *modèles de fondation* utilisables en zéro-shot : TimesFM [106] et Chronos [107].
- *Quand le DL gagne-t-il ?*
  - dans M4 (100 000 séries), les meilleures méthodes étaient des hybrides et des combinaisons, et les méthodes d'apprentissage automatique « pures » ont déçu [97] ;
  - dans M5 (ventes hiérarchiques avec covariables), les arbres boostés globaux ont dominé [98] ;
  - des modèles linéaires très simples battent plusieurs transformers sur les benchmarks de prévision longue [108] ;
  - sur données tabulaires, les arbres restent souvent supérieurs au DL [109].
  Le DL l'emporte surtout avec **beaucoup de séries apparentées, de longs historiques et des covariables riches**.

**(3) Avec peu de données.** Avec des historiques de quelques dizaines de points par série :
- naïf saisonnier et ETS comme références obligatoires ;
- **modèle global** (LightGBM) qui partage l'information entre séries ;
- **réconciliation** pour la cohérence entre niveaux.
Les modèles de fondation (TimesFM, Chronos) sont une option sérieuse en **démarrage à froid**, puisqu'ils ne demandent aucun entraînement [106][107]. Ils doivent néanmoins battre le naïf saisonnier en backtest avant d'être retenus.

**(4) Pièges.**
- **Ruptures** : changements de source ou de couverture, comme une nouvelle plateforme simap ou l'obligation d'annonce [10].
- **Agrégation incohérente** sans réconciliation.
- **Métriques inadaptées** aux zéros : le MAPE est indéfini. Il faut préférer des erreurs mises à l'échelle et des quantiles.
- **Fuite temporelle** via des variables exogènes connues seulement après coup (montants révisés, par exemple).
- **Sur-interprétation** des petites séries.

**(5) Recommandation pour PROXSIS.** En V1, on prévoit le naïf saisonnier et l'ETS par série, et un LightGBM global (mlforecast). La réconciliation MinT porte sur la hiérarchie métier × région → canton → total. L'évaluation se fait par origine glissante. **Condition de passage au DL** (TFT, N-BEATS) : plus de quelques centaines de séries avec au moins 2 ans d'historique hebdomadaire, et un gain en backtest sur au moins 3 origines. **Modèles de fondation** : à tester dès la V1 comme concurrents zéro-shot, et à retenir seulement s'ils battent le naïf saisonnier et le LightGBM global.

---

## Tableau de synthèse

| Thème | Méthode simple (V1) | Méthode avancée | Condition de passage | Référence clé |
|---|---|---|---|---|
| 1. Demande via offres en ligne | Comptage hebdomadaire dédoublonné d'offres directes par entreprise × métier × région, score d'écart à la ligne de base | Pondérations de représentativité, nowcasting agrégé | Besoin d'indicateurs macro et au moins 8 trimestres comparés à une source officielle | [1][3] |
| 2. Main-d'œuvre de chantier | Coefficient (heures/CHF) × gabarit temporel, délais permis → démarrage par Kaplan-Meier | Régression ou GBM par projet, ARIMA/VEC agrégés | Quelques centaines de projets avec main-d'œuvre réelle connue et gain en backtest | [12][13] |
| 3. Délai avant besoin | Survie à temps discret hebdomadaire (logistique, puis LightGBM) | RSF, XGBoost-AFT, DeepHit (risques concurrents) | Quelques milliers d'événements et gain d'IBS/C-index significatif sur 3 périodes | [19][21] |
| 4. Priorisation des entreprises | Classifieur de propension trié, groupe témoin dès le départ | LambdaMART (LightGBM) ; uplift (X-learner, forêt causale) | Centaines de listes consultant × semaine (LTR) ; données randomisées et Qini > 0 (uplift) | [30][34] |
| 5. Rapprochement d'entités | Jointure par UID, puis Fellegi–Sunter (Splink), puis revue humaine | Ditto, LLM fine-tuné | Rappel insuffisant sans UID et au moins 1 000 paires annotées | [39][41] |
| 6. Extraction FR/DE | LLM (Apertus) en sortie JSON contrainte, validation déterministe, jeu de test gelé | Distillation vers GLiNER / XLM-R hébergé en interne | Coût ou latence trop élevés et F1 du distillé à au plus 2 points du LLM | [50][60] |
| 7. Matching et équité | Filtres durs, puis embeddings (ESCO), puis décision humaine, audit contrefactuel | Ranker appris sur placements, sous contrainte d'équité | Audit d'équité documenté et suivi *equal opportunity* en production | [75][70] |
| 8. Effet causal | Essai randomisé par entreprise, stratifié par consultant, en intention de traiter | Uplift, effets hétérogènes ; différence de différences en repli | Effet moyen non nul sur données randomisées | [84][34] |
| 9. Évaluation honnête | Backtest walk-forward « vu à T », précision@k avec IC bootstrap par blocs, calibration sigmoïde | Calibration isotonique, suivi de dérive | Plus d'environ 1 000 exemples de calibration | [88][91] |
| 10. Prévision métier × région | Naïf saisonnier, ETS, LightGBM global et réconciliation MinT | TFT, N-BEATS ; modèles de fondation (TimesFM, Chronos) | Plus de quelques centaines de séries avec au moins 2 ans d'historique et gain sur au moins 3 origines | [98][101] |

---

## Références

Toutes consultées le 2026-10-04. « Vérifiée via » indique la source qui a servi à la vérification quand le site de l'éditeur était inaccessible.

1. Turrell, A., Speigner, B. J., Djumalieva, J., Copple, D., & Thurgood, J. (2019). Transforming Naturally Occurring Text Data Into Economic Statistics: The Case of Online Job Vacancy Postings. NBER Working Paper 25837 (chapitre dans *Big Data for Twenty-First-Century Economic Statistics*, 2022). https://www.nber.org/papers/w25837 — consulté le 2026-10-04
2. Hershbein, B., & Kahn, L. B. (2018). Do Recessions Accelerate Routine-Biased Technological Change? Evidence from Vacancy Postings. *American Economic Review*, 108(7), 1737–1772. https://research.upjohn.org/jrnlarticles/189 — consulté le 2026-10-04
3. Cammeraat, E., & Squicciarini, M. (2021). Burning Glass Technologies' data use in policy-relevant analysis: An occupation-level assessment. *OECD Science, Technology and Industry Working Papers*. https://www.oecd.org/en/publications/burning-glass-technologies-data-use-in-policy-relevant-analysis_cd75c3e7-en.html — consulté le 2026-10-04
4. Vermeulen, W., & Gutierrez Amaros, F. (2024). How well do online job postings match national sources in European countries? *OECD Local Economic and Employment Development (LEED) Papers*, No. 2024/02. https://www.oecd.org/en/publications/how-well-do-online-job-postings-match-national-sources-in-european-countries_e1026d81-en.html — consulté le 2026-10-04
5. Kureková, L. M., Beblavý, M., & Thum-Thysen, A. (2015). Using online vacancies and web surveys to analyse the labour market: a methodological inquiry. *IZA Journal of Labor Economics*, 4:18. https://doi.org/10.1186/s40172-015-0034-4 — consulté le 2026-10-04
6. Indeed Hiring Lab (2026). Indeed Job Postings Index — données et méthodologie (dépôt `job_postings_tracker`, README lu directement). GitHub. https://github.com/hiring-lab/job_postings_tracker — consulté le 2026-10-04
7. Eurostat (s. d.). Web Intelligence Hub — Online Job Advertisements (OJA) data. CROS, Commission européenne. https://cros.ec.europa.eu/wih/oja — consulté le 2026-10-04
8. Cedefop (s. d.). Big data analysis from online vacancies (Skills-OVATE). https://www.cedefop.europa.eu/en/events-and-projects/projects/big-data-analysis-online-vacancies — consulté le 2026-10-04
9. Swiss Job Market Monitor / Stellenmarkt-Monitor Schweiz (s. d.). Institut de sociologie, Université de Zurich. https://www.stellenmarktmonitor.uzh.ch/en.html — consulté le 2026-10-04
10. SECO (s. d.). Obligation d'annoncer les postes vacants — rapport de monitoring 2023. travail.swiss. https://www.arbeit.swiss/dam/secoalv/fr/dokumente/unternehmen/Stellenmeldepflicht/monitoringbericht_2023_fr.pdf.download.pdf/monitoringbericht_2023_fr.pdf — consulté le 2026-10-04
11. Hangartner, D., Kopp, D., & Siegenthaler, M. (2021). Monitoring hiring discrimination through online recruitment platforms. *Nature*, 589(7843), 572–576. https://doi.org/10.1038/s41586-020-03136-0 — consulté le 2026-10-04
12. CITB (s. d.). Construction Skills Network — CSN explained (technical report). Construction Industry Training Board, avec Experian. https://www.citb.co.uk/media/vpjhw03m/csn-explained-technical-report.pdf — consulté le 2026-10-04
13. Wong, J. M. W., Chan, A. P. C., & Chiang, Y. H. (2008). Modeling and Forecasting Construction Labor Demand: Multivariate Analysis. *Journal of Construction Engineering and Management*, 134(9), 664–672. https://ascelibrary.com/doi/abs/10.1061/%28ASCE%290733-9364%282008%29134%3A9%28664%29 — consulté le 2026-10-04
14. Zhao, Y., Qi, K., Chan, A. P. C., Chiang, Y. H., & Siu, M. F. F. (2022). Manpower forecasting models in the construction industry: a systematic review. *Engineering, Construction and Architectural Management*, 29(8), 3137–3156. https://doi.org/10.1108/ECAM-05-2020-0351 — consulté le 2026-10-04
15. U.S. Census Bureau (s. d.). Length of Time from Authorization to Start (Survey of Construction). https://www.census.gov/construction/nrc/data/time.html — consulté le 2026-10-04
16. République et canton de Genève (s. d.). Registre des bâtiments et logements (RegBL). https://www.ge.ch/registre-batiments-logements-regbl — consulté le 2026-10-04
17. opendata.swiss (s. d.). Baugesuche und Baubewilligungen nach Gebäudeart, Gemeinde und Jahr ab 1991 (jeu de données). https://opendata.swiss/en/dataset/baugesuche-und-baubewilligungen-nach-gebaudeart-gemeinde-und-jahr-ab-1991 — consulté le 2026-10-04
18. Cox, D. R. (1972). Regression models and life-tables. *Journal of the Royal Statistical Society: Series B (Methodological)*, 34(2), 187–220. https://www.stat.cmu.edu/~ryantibs/journalclub/cox_1972.pdf — consulté le 2026-10-04
19. Tutz, G., & Schmid, M. (2016). *Modeling Discrete Time-to-Event Data*. Springer Series in Statistics. https://www.springer.com/978-3-319-28158-2 — consulté le 2026-10-04
20. Ishwaran, H., Kogalur, U. B., Blackstone, E. H., & Lauer, M. S. (2008). Random survival forests. *The Annals of Applied Statistics*, 2(3), 841–860. https://projecteuclid.org/journals/annals-of-applied-statistics/volume-2/issue-3/Random-survival-forests/10.1214/08-AOAS169.pdf — consulté le 2026-10-04
21. Barnwal, A., Cho, H., & Hocking, T. (2022). Survival regression with accelerated failure time model in XGBoost. *Journal of Computational and Graphical Statistics*, 31(4), 1292–1302. https://arxiv.org/abs/2006.04920 — consulté le 2026-10-04
22. Pölsterl, S. (2020). scikit-survival: A Library for Time-to-Event Analysis Built on Top of scikit-learn. *Journal of Machine Learning Research*, 21(212), 1–6. http://jmlr.org/papers/v21/20-729.html — consulté le 2026-10-04
23. Katzman, J. L., Shaham, U., Cloninger, A., Bates, J., Jiang, T., & Kluger, Y. (2018). DeepSurv: personalized treatment recommender system using a Cox proportional hazards deep neural network. *BMC Medical Research Methodology*, 18(1). https://doi.org/10.1186/s12874-018-0482-1 — consulté le 2026-10-04
24. Lee, C., Zame, W. R., Yoon, J., & van der Schaar, M. (2018). DeepHit: A Deep Learning Approach to Survival Analysis With Competing Risks. *Proceedings of the AAAI Conference on Artificial Intelligence*, 32(1). https://ojs.aaai.org/index.php/AAAI/article/view/11842 — consulté le 2026-10-04
25. Kvamme, H., Borgan, Ø., & Scheel, I. (2019). Time-to-Event Prediction with Neural Networks and Cox Regression. *Journal of Machine Learning Research*, 20(129), 1–30. https://www.jmlr.org/papers/v20/18-424.html — consulté le 2026-10-04
26. Graf, E., Schmoor, C., Sauerbrei, W., & Schumacher, M. (1999). Assessment and comparison of prognostic classification schemes for survival data. *Statistics in Medicine*, 18(17–18), 2529–2545. Vérifiée via la documentation scikit-survival : https://scikit-survival.readthedocs.io/en/v0.14.0/api/generated/sksurv.metrics.brier_score.html — consulté le 2026-10-04
27. Uno, H., Cai, T., Pencina, M. J., D'Agostino, R. B., & Wei, L. J. (2011). On the C-statistics for evaluating overall adequacy of risk prediction procedures with censored survival data. *Statistics in Medicine*, 30(10), 1105–1117. https://pmc.ncbi.nlm.nih.gov/articles/PMC3079915 — consulté le 2026-10-04
28. Herrmann, M., Probst, P., Hornung, R., Jurinovic, V., & Boulesteix, A.-L. (2021). Large-scale benchmark study of survival prediction methods using multi-omics data. *Briefings in Bioinformatics*, 22(3). https://arxiv.org/abs/2003.03621 — consulté le 2026-10-04
29. Kvamme, H., & Borgan, Ø. (2019). The Brier Score under Administrative Censoring: Problems and Solutions. arXiv:1912.08581. https://arxiv.org/abs/1912.08581 — consulté le 2026-10-04
30. Burges, C. J. C. (2010). From RankNet to LambdaRank to LambdaMART: An Overview. Microsoft Research Technical Report MSR-TR-2010-82. https://www.microsoft.com/en-us/research/publication/from-ranknet-to-lambdarank-to-lambdamart-an-overview/ — consulté le 2026-10-04
31. Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). LightGBM: A Highly Efficient Gradient Boosting Decision Tree. *Advances in Neural Information Processing Systems 30*, 3149–3157. https://proceedings.neurips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html — consulté le 2026-10-04
32. Järvelin, K., & Kekäläinen, J. (2002). Cumulated gain-based evaluation of IR techniques. *ACM Transactions on Information Systems*, 20(4), 422–446. Vérifiée via la documentation de `sklearn.metrics.ndcg_score` : https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html — consulté le 2026-10-04
33. Radcliffe, N. J., & Surry, P. D. (2011). Real-world uplift modelling with significance-based uplift trees. White Paper TR-2011-1, Stochastic Solutions. Vérifiée via la bibliographie de CausalML : https://github.com/uber/causalml — consulté le 2026-10-04
34. Künzel, S. R., et al. (2019). Metalearners for estimating heterogeneous treatment effects using machine learning. *Proceedings of the National Academy of Sciences*, 116(10), 4156–4165. Vérifiée via la bibliographie de CausalML : https://github.com/uber/causalml — consulté le 2026-10-04
35. Athey, S., & Imbens, G. (2016). Recursive partitioning for heterogeneous causal effects. *Proceedings of the National Academy of Sciences*, 113(27), 7353–7360. Vérifiée via la bibliographie de CausalML : https://github.com/uber/causalml — consulté le 2026-10-04
36. Athey, S., Tibshirani, J., & Wager, S. (2019). Generalized Random Forests. *Annals of Statistics*, 47(2). Vérifiée via le dépôt grf : https://github.com/grf-labs/grf — consulté le 2026-10-04
37. Uber (2026). CausalML: A Python Package for Uplift Modeling and Causal Inference with ML. GitHub. https://github.com/uber/causalml — consulté le 2026-10-04
38. scikit-uplift (2026). Uplift modeling in scikit-learn style in Python (métriques Qini, AUUC, uplift@k). GitHub. https://github.com/maks-sh/scikit-uplift — consulté le 2026-10-04
39. Fellegi, I. P., & Sunter, A. B. (1969). A Theory for Record Linkage. *Journal of the American Statistical Association*, 64(328), 1183–1210. https://doi.org/10.1080/01621459.1969.10501049 — consulté le 2026-10-04
40. Enamorado, T., Fifield, B., & Imai, K. (2019). Using a Probabilistic Model to Assist Merging of Large-scale Administrative Records. *American Political Science Review*. https://doi.org/10.1017/S0003055418000783 — consulté le 2026-10-04
41. Linacre, R., Lindsay, S., Manassis, T., Slade, Z., Hepworth, T., Kennedy, R., & Bond, A. (2022). Splink: Free software for probabilistic record linkage at scale. *International Journal of Population Data Science*, 7(3). https://doi.org/10.23889/ijpds.v7i3.1794 (README Splink lu directement : https://github.com/moj-analytical-services/splink) — consulté le 2026-10-04
42. Gregg, F., & Eder, D. (2022). Dedupe. GitHub. https://github.com/dedupeio/dedupe — consulté le 2026-10-04
43. Bilenko, M. (2006). *Learnable Similarity Functions and their Application to Record Linkage and Clustering*. Thèse de doctorat, University of Texas at Austin. http://www.cs.utexas.edu/~ml/papers/marlin-dissertation-06.pdf — consulté le 2026-10-04
44. AnHai Doan's group (2026). py_entitymatching (projet Magellan), licence BSD. GitHub. https://github.com/anhaidgroup/py_entitymatching — consulté le 2026-10-04
45. Li, Y., Li, J., Suhara, Y., Doan, A., & Tan, W.-C. (2020). Deep Entity Matching with Pre-Trained Language Models (Ditto). *Proceedings of the VLDB Endowment*, 14(1). https://arxiv.org/abs/2004.00584 (dépôt : https://github.com/megagonlabs/ditto) — consulté le 2026-10-04
46. Narayan, A., et al. (2022). Can Foundation Models Wrangle Your Data? *Proceedings of the VLDB Endowment* (VLDB 2023). https://arxiv.org/abs/2205.09911 (dépôt : https://github.com/HazyResearch/fm_data_tasks) — consulté le 2026-10-04
47. Peeters, R., et al. (2023). Entity Matching using Large Language Models. arXiv:2310.11244. https://arxiv.org/abs/2310.11244 (dépôt : https://github.com/wbsg-uni-mannheim/MatchGPT) — consulté le 2026-10-04
48. Herzog, T. N., Scheuren, F. J., & Winkler, W. E. (2007). *Data Quality and Record Linkage Techniques*. Springer. ISBN 978-0-387-69502-0. Vérifiée via le paquet R reclin2 : https://github.com/cran/reclin2 — consulté le 2026-10-04
49. de Jong, A. (2024). python-stdnum, module `stdnum.ch.uid` (format, clé de contrôle et service web public de l'IDE/UID suisse). GitHub. https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ch/uid.py — consulté le 2026-10-04
50. Swiss AI Initiative — équipe Apertus (EPFL, ETH Zurich, CSCS) (2025 ; ACL 2026). Apertus: Democratizing Open and Compliant LLMs for Global Language Environments. arXiv:2509.14233 ; *Proceedings of ACL 2026 (Long Papers)*. https://aclanthology.org/2026.acl-long.2172/ — consulté le 2026-10-04
51. EPFL, ETH Zurich & CSCS (2025-09-02). Apertus: a fully open, transparent, multilingual language model (communiqué). https://ai.epfl.ch/apertus-a-fully-open-transparent-multilingual-language-model — consulté le 2026-10-04
52. Swiss AI (2025). Fiche modèle Apertus-70B-2509. Hugging Face. https://huggingface.co/swiss-ai/Apertus-70B-2509 — consulté le 2026-10-04
53. ETH Zurich, EPFL & CSCS (2026-07-24). Apertus 1.5: Building the next generation of open AI infrastructure. CSCS. https://www.cscs.ch/science/computer-science-hpc/2026/apertus-15-building-the-next-generation-of-open-ai-infrastructure — consulté le 2026-10-04
54. Public AI (s. d.). About the Inference Utility. https://publicai.co/utility ; documentation du fournisseur sur Hugging Face : https://huggingface.co/docs/inference-providers/en/providers/publicai — consulté le 2026-10-04
55. Public AI (2026). With 1.5x the love, from Switzerland (Apertus 1.5). https://publicai.co/stories/apertus-1-5 — consulté le 2026-10-04
56. Swisscom (s. d.). Swiss AI Platform — factsheet. https://documents.swisscom.com/product/filestore/lib/6b28311c-ec6a-4716-a268-6b25363afde3/factsheet_swissaiplatform-en.pdf — consulté le 2026-10-04
57. Vamvas, J., Graën, J., & Sennrich, R. (2023). SwissBERT: The Multilingual Language Model for Switzerland. *Proceedings of the 8th Swiss Text Analytics Conference (SwissText 2023)*. https://aclanthology.org/2023.swisstext-1.6/ (licence du modèle CC BY-NC 4.0 selon https://github.com/ZurichNLP/swissbert) — consulté le 2026-10-04
58. Conneau, A., Khandelwal, K., Goyal, N., Chaudhary, V., Wenzek, G., Guzmán, F., Grave, E., Ott, M., Zettlemoyer, L., & Stoyanov, V. (2020). Unsupervised Cross-lingual Representation Learning at Scale (XLM-R). ACL 2020 ; arXiv:1911.02116. https://arxiv.org/abs/1911.02116 — consulté le 2026-10-04
59. Martin, L., Muller, B., Ortiz Suárez, P. J., Dupont, Y., Romary, L., de la Clergerie, É. V., Seddah, D., & Sagot, B. (2020). CamemBERT: a Tasty French Language Model. *Proceedings of the 58th Annual Meeting of the ACL*. Vérifiée via fairseq : https://github.com/facebookresearch/fairseq/tree/main/examples/camembert — consulté le 2026-10-04
60. Zaratiana, U., Tomeh, N., Holat, P., & Charnois, T. (2024). GLiNER: Generalist Model for Named Entity Recognition using Bidirectional Transformer. *Proceedings of NAACL 2024 (Long Papers)*, 5364–5376. https://aclanthology.org/2024.naacl-long.300 — consulté le 2026-10-04
61. Honnibal, M., Montani, I., Van Landeghem, S., & Boyd, A. (2020). spaCy: Industrial-strength Natural Language Processing in Python. Zenodo. https://doi.org/10.5281/zenodo.1212303 — consulté le 2026-10-04
62. Tunstall, L., Reimers, N., Jo, U. E. S., Bates, L., Korat, D., Wasserblat, M., & Pereg, O. (2022). Efficient Few-Shot Learning Without Prompts (SetFit). arXiv:2209.11055. https://arxiv.org/abs/2209.11055 (affirmation « 8 exemples par classe » tirée du README : https://github.com/huggingface/setfit) — consulté le 2026-10-04
63. Willard, B. T., & Louf, R. (2023). Efficient Guided Generation for Large Language Models. arXiv:2307.09702. https://arxiv.org/abs/2307.09702 (bibliothèque Outlines : https://github.com/dottxt-ai/outlines) — consulté le 2026-10-04
64. Dagdelen, J., Dunn, A., Lee, S., Walker, N., Rosen, A. S., Ceder, G., Persson, K., & Jain, A. (2024). Structured information extraction from scientific text with large language models. *Nature Communications*. Vérifiée via le dépôt des auteurs : https://github.com/lbnlp/nerre-llama — consulté le 2026-10-04
65. Xu, D., et al. (2024). Large language models for generative information extraction: A survey. *Frontiers of Computer Science*, 18(6), 186357. Vérifiée via https://github.com/quqxui/Awesome-LLM4IE-Papers — consulté le 2026-10-04
66. Zhang, M., van der Goot, R., & Plank, B. (2023). ESCOXLM-R: Multilingual Taxonomy-driven Pre-training for the Job Market Domain. *Proceedings of ACL 2023 (Long Papers)*. https://aclanthology.org/2023.acl-long.662 — consulté le 2026-10-04
67. Lambrecht, A., & Tucker, C. (2019). Algorithmic Bias? An Empirical Study of Apparent Gender-Based Discrimination in the Display of STEM Career Ads. *Management Science*. Vérifiée via Barocas, Hardt & Narayanan, chap. 7 : https://fairmlbook.org/testing.html — consulté le 2026-10-04
68. Ali, M., Sapiezynski, P., Bogen, M., Korolova, A., Mislove, A., & Rieke, A. (2019). Discrimination Through Optimization: How Facebook's Ad Delivery Can Lead to Biased Outcomes. *Proceedings of the ACM on Human-Computer Interaction*, 3(CSCW), 199. Vérifiée via https://fairmlbook.org/testing.html — consulté le 2026-10-04
69. Datta, A., Tschantz, M. C., & Datta, A. (2015). Automated Experiments on Ad Privacy Settings. *Proceedings on Privacy Enhancing Technologies*, 2015(1), 92–112. Vérifiée via https://fairmlbook.org/testing.html — consulté le 2026-10-04
70. Bertrand, M., & Mullainathan, S. (2004). Are Emily and Greg More Employable Than Lakisha and Jamal? A Field Experiment on Labor Market Discrimination. *American Economic Review*, 94(4), 991–1013. Vérifiée via https://fairmlbook.org/testing.html — consulté le 2026-10-04
71. Quillian, L., et al. (2017). Meta-Analysis of Field Experiments Shows No Change in Racial Discrimination in Hiring over Time. *Proceedings of the National Academy of Sciences*, 114(41), 10870–10875. Vérifiée via https://fairmlbook.org/testing.html — consulté le 2026-10-04
72. Pager, D. (2007). The Use of Field Experiments for Studies of Employment Discrimination: Contributions, Critiques, and Directions for the Future. *The Annals of the American Academy of Political and Social Science*, 609(1), 104–133. Vérifiée via https://fairmlbook.org/testing.html — consulté le 2026-10-04
73. Raghavan, M., et al. (2019). Mitigating Bias in Algorithmic Employment Screening: Evaluating Claims and Practices. arXiv:1906.09208. https://arxiv.org/abs/1906.09208 — consulté le 2026-10-04
74. De-Arteaga, M., Romanov, A., Wallach, H., Chayes, J., Borgs, C., Chouldechova, A., Geyik, S., Kenthapadi, K., & Kalai, A. T. (2019). Bias in Bios: A Case Study of Semantic Representation Bias in a High-Stakes Setting. *Conference on Fairness, Accountability, and Transparency (FAT\*)*, 120–128. Vérifiée via https://fairmlbook.org/testing.html — consulté le 2026-10-04
75. Hardt, M., Price, E., & Srebro, N. (2016). Equality of Opportunity in Supervised Learning. *NeurIPS*, 3315–3323. https://proceedings.neurips.cc/paper/2016/hash/9d2682367c3935defcb1f9e247a97c0d-Abstract.html — consulté le 2026-10-04
76. Feldman, M., et al. (2015). Certifying and Removing Disparate Impact. *KDD 2015*. https://doi.org/10.1145/2783258.2783311 (vérifiée via https://github.com/Trusted-AI/AIF360) — consulté le 2026-10-04
77. Watkins, E. A., McKenna, M., & Chen, J. (2022). The four-fifths rule is not disparate impact: a woeful tale of epistemic trespassing in algorithmic fairness. arXiv:2202.09519. https://arxiv.org/abs/2202.09519 — consulté le 2026-10-04
78. Barocas, S., Hardt, M., & Narayanan, A. (2023). *Fairness and Machine Learning: Limitations and Opportunities*. fairmlbook.org (édité par MIT Press). https://fairmlbook.org/ — consulté le 2026-10-04
79. Bird, S., et al. (2020). Fairlearn: A toolkit for assessing and improving fairness in AI. Microsoft, Tech. Rep. MSR-TR-2020-32. https://www.microsoft.com/en-us/research/uploads/prod/2020/05/Fairlearn_whitepaper.pdf — consulté le 2026-10-04
80. Bellamy, R. K. E., et al. (2018). AI Fairness 360: An Extensible Toolkit for Detecting, Understanding, and Mitigating Unwanted Algorithmic Bias. arXiv:1810.01943. https://arxiv.org/abs/1810.01943 — consulté le 2026-10-04
81. Vasudevan, S., & Kenthapadi, K. (2020). LiFT: A Scalable Framework for Measuring Fairness in ML Applications. *CIKM '20*. https://github.com/linkedin/LiFT — consulté le 2026-10-04
82. DiCiccio, C., Vasudevan, S., Basu, K., Kenthapadi, K., & Agarwal, D. (2020). Evaluating Fairness Using Permutation Tests. *KDD '20*. Vérifiée via https://github.com/linkedin/LiFT — consulté le 2026-10-04
83. Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-Differences with multiple time periods. *Journal of Econometrics*. https://doi.org/10.1016/j.jeconom.2020.12.001 — consulté le 2026-10-04
84. Blair, G., Cooper, J., Coppock, A., & Humphreys, M. (2019). Declaring and Diagnosing Research Designs. *American Political Science Review*, 113(3), 838–859. https://declaredesign.org/paper.pdf — consulté le 2026-10-04
85. Blair, G., Coppock, A., & Humphreys, M. (2023). *Research Design in the Social Sciences: Declaration, Diagnosis, and Redesign*. Princeton University Press. https://book.declaredesign.org — consulté le 2026-10-04
86. scikit-learn developers (2026). Common pitfalls and recommended practices — Data leakage. https://scikit-learn.org/stable/common_pitfalls.html — consulté le 2026-10-04
87. scikit-learn developers (2026). Cross-validation — Time Series Split. https://scikit-learn.org/stable/modules/cross_validation.html — consulté le 2026-10-04
88. scikit-learn developers (2026). Probability calibration (guide utilisateur). https://scikit-learn.org/stable/modules/calibration.html — consulté le 2026-10-04
89. Platt, J. (1999). Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods. https://www.cs.colorado.edu/~mozer/Teaching/syllabi/6622/papers/Platt1999.pdf — consulté le 2026-10-04
90. Zadrozny, B., & Elkan, C. (2002). Transforming Classifier Scores into Accurate Multiclass Probability Estimates. *KDD 2002*. https://dl.acm.org/doi/pdf/10.1145/775047.775151 — consulté le 2026-10-04
91. Niculescu-Mizil, A., & Caruana, R. (2005). Predicting Good Probabilities with Supervised Learning. *ICML 2005*. https://www.cs.cornell.edu/~alexn/papers/calibration.icml05.crc.rev3.pdf — consulté le 2026-10-04
92. Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. *ICML 2017*. https://proceedings.mlr.press/v70/guo17a/guo17a.pdf — consulté le 2026-10-04
93. Murphy, A. H. (1973). A New Vector Partition of the Probability Score. *Journal of Applied Meteorology*, 12(4), 595–600. https://doi.org/10.1175/1520-0450(1973)012%3C0595:ANVPOT%3E2.0.CO;2 — consulté le 2026-10-04
94. Van Calster, B., et al. (2016). A calibration hierarchy for risk models was defined: from utopia to empirical data. *Journal of Clinical Epidemiology*. https://doi.org/10.1016/j.jclinepi.2015.12.005 — consulté le 2026-10-04
95. Davison, A. C., & Hinkley, D. V. (1997). *Bootstrap Methods and Their Application*. Cambridge University Press. Vérifiée via le paquet R boot : https://github.com/cran/boot — consulté le 2026-10-04
96. Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3e éd.). OTexts. https://otexts.com/fpp3/ — consulté le 2026-10-04
97. Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2020). The M4 Competition: 100,000 time series and 61 forecasting methods. *International Journal of Forecasting*, 36(1), 54–74. https://www.sciencedirect.com/science/article/pii/S0169207019301128 — consulté le 2026-10-04
98. Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2022). M5 accuracy competition: Results, findings, and conclusions. *International Journal of Forecasting*, 38(4). https://www.sciencedirect.com/science/article/pii/S0169207021001874 — consulté le 2026-10-04
99. Hyndman, R. J., & Khandakar, Y. (2008). Automatic time series forecasting: the forecast package for R. *Journal of Statistical Software*, 27(3), 1–22. https://doi.org/10.18637/jss.v027.i03 — consulté le 2026-10-04
100. Hyndman, R. J., et al. (2011). Optimal combination forecasts for hierarchical time series. *Computational Statistics & Data Analysis*. https://doi.org/10.1016/j.csda.2011.03.006 — consulté le 2026-10-04
101. Wickramasuriya, S. L., Athanasopoulos, G., & Hyndman, R. J. (2019). Optimal forecast reconciliation for hierarchical and grouped time series through trace minimization. *Journal of the American Statistical Association*, 114(526), 804–819. https://doi.org/10.1080/01621459.2018.1448825 — consulté le 2026-10-04
102. Olivares, K. G., Garza, A., Luo, D., Challú, C., Mergenthaler, M., Ben Taieb, S., Wickramasuriya, S. L., & Dubrawski, A. (2024). HierarchicalForecast: A Reference Framework for Hierarchical Forecasting in Python. arXiv:2207.03517. https://arxiv.org/abs/2207.03517 — consulté le 2026-10-04
103. Oreshkin, B. N., Carpov, D., Chapados, N., & Bengio, Y. (2020). N-BEATS: Neural basis expansion analysis for interpretable time series forecasting. *ICLR 2020*. https://openreview.net/forum?id=r1ecqn4YwB — consulté le 2026-10-04
104. Lim, B., Arık, S. Ö., Loeff, N., & Pfister, T. (2021). Temporal Fusion Transformers for interpretable multi-horizon time series forecasting. *International Journal of Forecasting*. https://www.sciencedirect.com/science/article/pii/S0169207021000637 — consulté le 2026-10-04
105. Nie, Y., Nguyen, N. H., Sinthong, P., & Kalagnanam, J. (2023). A Time Series is Worth 64 Words: Long-term Forecasting with Transformers (PatchTST). *ICLR 2023*. https://arxiv.org/abs/2211.14730 — consulté le 2026-10-04
106. Das, A., et al. (2024). A decoder-only foundation model for time-series forecasting (TimesFM). *ICML 2024*. https://arxiv.org/abs/2310.10688 (dépôt : https://github.com/google-research/timesfm) — consulté le 2026-10-04
107. Ansari, A. F., et al. (2024). Chronos: Learning the Language of Time Series. *Transactions on Machine Learning Research*. https://openreview.net/forum?id=gerNCVqqtR — consulté le 2026-10-04
108. Zeng, A., Chen, M., Zhang, L., & Xu, Q. (2023). Are Transformers Effective for Time Series Forecasting? *Proceedings of the AAAI Conference on Artificial Intelligence*. https://arxiv.org/abs/2205.13504 — consulté le 2026-10-04
109. Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? *NeurIPS 2022 (Datasets and Benchmarks)*. https://github.com/LeoGrin/tabular-benchmark — consulté le 2026-10-04
110. Nixtla (2026). statsforecast, mlforecast, hierarchicalforecast, neuralforecast (bibliothèques Python, licence Apache 2.0). GitHub. https://github.com/Nixtla/statsforecast ; https://github.com/Nixtla/mlforecast ; https://github.com/Nixtla/hierarchicalforecast ; https://github.com/Nixtla/neuralforecast — consulté le 2026-10-04
