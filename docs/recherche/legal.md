# Mémo juridique : PROXSIS (section 2d)

> **Avertissement important.** Ce mémo a été préparé par un assistant d'IA (Claude). **Ce n'est pas un avocat, et ce document n'est pas un avis juridique.** C'est une note de travail destinée à préparer la discussion avec un juriste qualifié : droit suisse de la protection des données, droit du travail et LSE, et droit de l'UE si nécessaire. Ce juriste doit **valider chaque point avant le pilote**.
>
> **Date de rédaction et de consultation de toutes les sources : 2026-10-04.**

**Méthode et limites.** Pendant la rédaction, l'accès direct à fedlex.admin.ch, edoeb.admin.ch, eur-lex.europa.eu, opendata.swiss, amtsblattportal.ch, arbeit.swiss et à la plupart des sites juridiques était bloqué. Les affirmations reposent donc sur des **extraits de moteur de recherche** (44 requêtes). Ces extraits sont signalés par « (extrait de recherche) ». Les textes légaux n'ont pas pu être lus en entier. Tout numéro d'article, alinéa ou lettre que ces extraits ne confirment pas porte la mention **« article à vérifier »**.

**Légende de statut juridique**

| Code | Signification |
|---|---|
| **[EV]** | Droit en vigueur au 2026-10-04 |
| **[PR]** | Projet, ou droit adopté mais pas encore applicable |
| **[INT]** | Interprétation de l'auteur, non tranchée par un texte ou un tribunal : à valider |

**Contexte produit.** Chaque semaine, PROXSIS indique aux consultants de Flexsis (filiale d'Interiman Group ; placement temporaire et fixe ; Suisse romande et alémanique) quelles **entreprises** appeler. Il croise pour cela des signaux publics : marchés attribués sur simap.ch, permis de construire publiés, offres d'emploi, registre du commerce et FOSC. Il **suggère aussi des candidats** tirés des données internes de l'agence.

---

## 1. Résumé exécutif

1. **Le volet « entreprises » (B2B) est peu exposé au regard de la LPD.** Depuis le 1.9.2023, la LPD ne protège plus que les personnes physiques. Les personnes morales relèvent désormais d'autres régimes (art. 28 CC, art. 162 CP, LCD, LCart) [3][4] [EV]. **Mais** les raisons individuelles, les dirigeants inscrits, les propriétaires privés cités dans les permis et les interlocuteurs nommés sont des personnes physiques. Un filtre de données personnelles est donc obligatoire [INT].
2. **Le volet « candidats » concentre le risque.** Il s'agit de données personnelles, parfois sensibles, traitées par un placeur. Selon l'art. 7 al. 3 LSE, celui-ci ne peut traiter ces données que « dans la mesure où et aussi longtemps » qu'elles sont nécessaires au placement, et il est tenu au secret [11] [EV].
3. **Le rapprochement candidat-besoin est très probablement un « profilage »** au sens de la LPD. Il pourrait constituer un « profilage à risque élevé » (art. 5 LPD) [1][2]. **Une analyse d'impact (AIPD, art. 22 LPD) doit être menée avant le pilote** [6] [EV/INT].
4. **L'outil n'est pas une décision individuelle automatisée (art. 21 LPD)** tant que le consultant décide réellement. Trois conditions sont nécessaires pour cela : une marge d'appréciation humaine effective, aucune exclusion automatique de candidats, et une logique affichée pour chaque suggestion [5] [INT].
5. **L'obligation d'annonce des postes vacants s'applique aussi aux agences** (art. 21a LEI ; art. 53a ss OSE) :
   - seuil de chômage de 5 % par genre de profession ;
   - 5 jours ouvrables de priorité aux demandeurs inscrits ;
   - liste 2026 en vigueur ;
   - l'exception « 6 mois d'ancienneté » ne s'appliquerait pas aux bailleurs de services (extrait de recherche) ;
   - amende jusqu'à 40 000 CHF en cas d'intention [13]–[18] [EV].
   
   Le produit doit afficher une alerte et ne jamais aider à contourner cette obligation.
6. **Les actes officiels ne sont pas protégés par le droit d'auteur** (art. 5 LDA) [24]. Leur réutilisation reste pourtant encadrée :
   - conditions opendata.swiss (OPEN / BY / ASK / BY-ASK) [19] ;
   - FOSC : le SECO peut régler l'usage par contrat [20] ;
   - Zefix : requêtes individuelles uniquement, pas d'extraction de la base [26] ;
   - CGU des portails d'emploi privés et art. 5 let. c LCD [22][23].
   
   **Il faut privilégier les API officielles et les licences, pas l'aspiration de sites.**
7. **FOSC.** N'ingérer que les rubriques « registre du commerce » (et « marchés publics »). **Exclure faillites, poursuites, concordats, appels aux créanciers et successions.** **Ne pas stocker** les noms des dirigeants [INT].
8. **Prospection.**
   - Appels : respecter l'astérisque de l'annuaire et ne pas appeler les numéros non inscrits (art. 3 al. 1 let. u LCD) [28].
   - E-mails de masse : consentement préalable requis, sauf pour les clients existants (let. o) [27].
   - E-mails générés par l'outil : relus, vérifiés et envoyés **un par un** par le consultant [EV/INT].
9. **Équité.** L'art. 3 LEg interdit la discrimination fondée sur le sexe, notamment à l'embauche. Un refus d'embauche discriminatoire peut coûter jusqu'à 3 mois de salaire [29]. L'art. 328b CO limite le traitement aux données liées aux aptitudes [30]. Conséquences : aucun critère protégé dans le modèle et un audit de biais régulier [EV].
10. **UE et IA.**
    - Si la suggestion de candidats est utilisée dans l'UE, elle relèverait de l'**annexe III, point 4 a), du règlement (UE) 2024/1689** (haut risque). Comme il y a profilage, la dérogation de l'art. 6 par. 3 ne s'applique pas [31][32].
    - L'échéance pour ces systèmes a été **repoussée au 2.12.2027** par le règlement « Omnibus » (UE) 2026/1744, en vigueur depuis le 27.7.2026 (extraits de recherche) [33] [EV/PR].
    - Le volet B2B n'est a priori pas à haut risque [INT].
    - En Suisse, il n'existe pas de loi IA spécifique. Selon le PFPDT, la LPD s'applique directement à l'IA [9] [EV].

### Tableau risque → mesure dans le produit → statut

| # | Risque | Mesure dans le produit | Statut |
|---|---|---|---|
| R1 | Données personnelles (propriétaires privés, dirigeants, raisons individuelles, contacts) aspirées dans les signaux publics | Filtre de données personnelles à l'ingestion ; liste blanche des rubriques ; personnes physiques non stockées ; journal de provenance | **Obligatoire avant pilote** (à implémenter) |
| R2 | Profilage des candidats sans base claire ni transparence | Information des candidats ; finalité limitée au placement ; AIPD ; registre des traitements | **Obligatoire avant pilote** |
| R3 | Glissement vers une décision automatisée (art. 21 LPD / art. 22 RGPD) | Bouton « le consultant décide » ; aucune exclusion automatique ; justification affichée ; recherche manuelle toujours possible ; journal des décisions humaines | **Obligatoire** |
| R4 | Discrimination (sexe, origine, âge, nationalité ou permis comme indicateurs indirects) | Critères protégés exclus des caractéristiques ; audit de biais trimestriel ; revue des listes de suggestions | **Obligatoire** (audit : à définir) |
| R5 | Violation de l'obligation d'annonce des postes vacants | Correspondance métier ↔ CH-ISCO-19 ; alerte « métier soumis à l'obligation d'annonce » ; blocage de la publication anticipée | **Obligatoire** |
| R6 | Non-respect des CGU ou de la LCD lors de la collecte (scraping) | API officielles et licences ; liste des sources avec base d'accès ; respect de robots.txt ; pas de portail privé sans contrat | **Obligatoire** |
| R7 | Prospection illicite (astérisque, spam) | Vérification de l'astérisque et de la liste d'opposition interne avant l'appel ; aucun envoi d'e-mails en masse ; mention de l'expéditeur et désinscription | **Obligatoire** |
| R8 | Informations inexactes dans les e-mails générés (responsabilité, LCD) | Chaque fait est cité avec sa source et sa date ; relecture humaine obligatoire ; aucune donnée de candidat identifiable dans les e-mails | **Obligatoire** |
| R9 | Transfert à l'étranger (hébergement, API de LLM) | Hébergement en Suisse ou dans l'UE ; aux États-Unis seulement avec un prestataire certifié Swiss-US DPF ou des clauses types ; contrats de sous-traitance | **À décider par Flexsis** (exigence : documenter) |
| R10 | Conservation excessive | Durées de conservation par catégorie ; purge automatique | **Obligatoire** |
| R11 | Utilisation dans l'UE (RGPD / RIA haut risque) | Ne pas déployer le volet candidats dans l'UE sans analyse ; géo-cloisonnement | **À décider** |

---

## 2. Protection des données : nLPD (RS 235.1) et OPDo (RS 235.11)

### 2.1 Champ d'application

- **Personnes physiques uniquement** [EV]. Depuis le 1.9.2023, la nLPD protège la personnalité et les droits fondamentaux des personnes physiques. Les données des personnes morales sont exclues de son champ, contrairement à l'ancienne loi [3][4] (extrait de recherche). Les personnes morales restent protégées par l'art. 28 CC (personnalité), l'art. 162 CP (secret de fabrication ou commercial), la LCart et la LCD [4] (extrait de recherche).
- **Conséquences pour PROXSIS** [INT] :
  - Le score d'une SA ou d'une Sàrl n'est pas un traitement de données personnelles au sens de la LPD.
  - En revanche, les catégories suivantes sont des données personnelles :
    - **raison individuelle** (le titulaire est une personne physique ; ex. « Jean Dupont, maçonnerie ») ;
    - **noms de dirigeants ou d'associés** inscrits au RC ;
    - **interlocuteurs nommés** (recruteurs cités dans les annonces) ;
    - **propriétaires privés** dans les permis de construire ;
    - **toutes les données des candidats**.
  - Recommandation : traiter les raisons individuelles comme des personnes physiques. Le produit les signale, mais ne les profile pas au-delà de la donnée « entreprise ».

### 2.2 Principes

Les principes de licéité, bonne foi, proportionnalité, finalité reconnaissable, exactitude et minimisation figurent dans la LPD : art. 6 LPD, **article à vérifier** [36]. Protection des données dès la conception et par défaut : art. 7 LPD, **article à vérifier**.

Traduction produit [INT] :
- **Finalité** : prospection B2B (entreprises) et placement (candidats). Ces deux finalités restent séparées, et aucune autre réutilisation n'est permise.
- **Proportionnalité et minimisation** : ne collecter que les champs utiles au score (entreprise, lieu, type de chantier ou de marché, date, montant si public, métiers recherchés).
- **Exactitude** : chaque signal conserve son URL source et sa date de publication.
- **Par défaut** : les profils candidats ne sont visibles que des consultants de l'agence concernée.

### 2.3 Profilage et « profilage à risque élevé »

- **Profilage** : art. 5 LPD, lettre exacte à vérifier, a priori let. f. Il s'agit de tout traitement automatisé qui utilise des données personnelles pour évaluer certains aspects personnels d'une personne physique, notamment son rendement au travail [2]. Cette formulation est une paraphrase : le texte exact est à vérifier.
- **Profilage à risque élevé** : art. 5 LPD, lettre à vérifier, a priori let. g. Définition (extrait de recherche) : « tout profilage entraînant un risque élevé pour la personnalité ou les droits fondamentaux de la personne concernée, parce qu'il conduit à un appariement de données qui permet d'apprécier les caractéristiques essentielles de la personnalité d'une personne physique » [1][2] [EV]. Cette qualification déclenche surtout l'obligation d'AIPD. Elle exige aussi un consentement exprès lorsque le consentement est la base du traitement : **article à vérifier**.
- **Application** [INT] :
  - **Priorisation d'entreprises** : pas de profilage au sens de la LPD si elle ne porte que sur des personnes morales.
  - **Suggestion de candidats** : il s'agit de profilage, puisque les aptitudes et l'adéquation professionnelle sont évaluées automatiquement.
  - **Risque élevé ?** Il dépend de l'étendue de l'appariement : CV, historique de missions, évaluations des clients, disponibilités, absences. Plus l'outil croise de sources internes, plus il se rapproche d'une appréciation des « caractéristiques essentielles de la personnalité ».
  - **Recommandation** : partir du principe que c'est un profilage à risque élevé tant que l'AIPD n'a pas conclu le contraire.

### 2.4 Décisions individuelles automatisées (art. 21 LPD)

- **Droit** [EV] :
  - Le responsable doit informer la personne de toute décision prise **exclusivement** sur la base d'un traitement automatisé, lorsque cette décision produit des effets juridiques pour elle ou l'affecte de manière significative.
  - Sur demande, la personne peut faire valoir son point de vue et exiger qu'une personne physique revoie la décision [5] (extrait de recherche). Article : 21 al. 1 et 2.
- **Pourquoi PROXSIS n'en est pas une** [INT] :
  - L'outil **propose**. Le consultant **décide** d'appeler une entreprise, de présenter un candidat ou de l'écarter.
  - La décision n'est donc pas « exclusivement » automatisée, à condition que l'intervention humaine soit **réelle** : le consultant doit pouvoir s'écarter de la proposition, comprendre la logique de chaque suggestion, et avoir accès au vivier complet par une recherche manuelle.
- **Risques de requalification** [INT] :
  1. Le produit **filtre** automatiquement des candidats que le consultant ne voit jamais. Un score sous un seuil vaut alors exclusion.
  2. Les consultants suivent mécaniquement le classement (biais d'automatisation).
  3. Une réponse négative est envoyée automatiquement au candidat.
  
  Dans l'UE, la CJUE a jugé qu'un score pouvait constituer une « décision » lorsqu'il joue un rôle déterminant (arrêt *SCHUFA*, C-634/21, décembre 2023). **Ce point n'a pas pu être vérifié pendant la session : à vérifier.**
- **Mesures** : bouton « le consultant décide » ; motif obligatoire si le consultant écarte la première suggestion (journal) ; aucune exclusion ni aucun message automatique au candidat ; indicateurs de suivi du taux d'acceptation, pour détecter un suivi aveugle des suggestions.

### 2.5 Devoir d'informer (art. 19 LPD)

- **Droit** [EV] : la personne concernée doit être informée de manière adéquate de la collecte de ses données, même si elles ne sont pas collectées auprès d'elle [36]. Contenu minimal à vérifier : identité du responsable, finalité, destinataires, pays étrangers. Article 19 ; les exceptions de l'art. 20 sont **à vérifier**.
- **Candidats** : il faut mettre à jour la déclaration de confidentialité de Flexsis. Elle doit mentionner l'usage d'un outil d'aide à la décision qui rapproche leur profil de besoins détectés, la logique générale, l'intervention humaine, les durées de conservation et le droit d'accès (art. 25 LPD, **article à vérifier**). Le PFPDT recommande la transparence sur la finalité, le fonctionnement et les sources de données des systèmes d'IA [9] (extrait de recherche ; contenu exact à vérifier).
- **Personnes physiques des sources publiques** [INT] : il est plus simple **de ne pas les stocker** (§ 2.10). Sinon, l'information individuelle des propriétaires ou dirigeants serait difficile à assurer.

### 2.6 Analyse d'impact (art. 22 LPD) et consultation du PFPDT (art. 23 LPD)

- **Droit** [EV] :
  - Une AIPD est requise lorsque le traitement est susceptible d'entraîner un risque élevé pour la personnalité ou les droits fondamentaux.
  - Le risque élevé résulte notamment de l'usage de nouvelles technologies, de la nature, de l'étendue et de la finalité du traitement, en particulier en cas de traitement de données sensibles à grande échelle ou de profilage à risque élevé.
  - Contenu minimal : description du traitement, évaluation des risques, mesures [6] (extrait de recherche).
  - Si le risque reste élevé malgré les mesures, il faut consulter le PFPDT (art. 23 LPD) [6].
- **Recommandation** : mener l'AIPD **avant le pilote**, sur le volet candidats et sur la chaîne d'ingestion des sources publiques. Une version mise à jour sera nécessaire à chaque nouvelle source ou caractéristique du modèle.

### 2.7 Registre des activités de traitement (art. 12 LPD ; art. 24 OPDo)

- **Droit** [EV] :
  - Le responsable et le sous-traitant tiennent un registre.
  - Les entreprises de moins de 250 collaborateurs en sont dispensées, **sauf** si elles traitent des données sensibles à grande échelle ou font du profilage à risque élevé (art. 12 LPD et art. 24 OPDo) [7] (extrait de recherche).
  - Contenu : identité du responsable, finalités, catégories de personnes et de données, destinataires, durée de conservation, mesures de sécurité, pays étrangers [7].
- **PROXSIS** : quel que soit l'effectif de Flexsis (**à vérifier**), il faut **inscrire le traitement au registre**. Le risque de profilage à risque élevé fait tomber la dispense.

### 2.8 Sous-traitance et communication à l'étranger

- **Sous-traitance** [EV] : elle est permise par contrat si le sous-traitant ne traite les données que comme le responsable pourrait le faire et garantit leur sécurité. Art. 9 LPD, **article à vérifier**. Les prestataires concernés sont l'hébergeur, le fournisseur de LLM et le prestataire de données.
- **Communication à l'étranger** [EV] : les données peuvent être communiquées vers un État que le Conseil fédéral reconnaît comme offrant une protection adéquate, listé à l'**annexe 1 OPDo**. À défaut, il faut des garanties appropriées, par exemple des clauses contractuelles types. Art. 16 et 17 LPD, **articles à vérifier**. La liste exacte des États adéquats est **à vérifier sur fedlex** ; elle comprend notamment les États de l'UE et de l'EEE (**à vérifier**).
- **Swiss-US Data Privacy Framework** [EV] : le 14.8.2024, le Conseil fédéral a ajouté les États-Unis à l'annexe 1 OPDo, **à condition que le destinataire soit certifié** selon le Swiss-US DPF. Entrée en vigueur : **15.9.2024**. Les transferts vers ces entreprises certifiées n'exigent plus de clauses types ni d'évaluation de transfert [8] (extrait de recherche).
- **Options d'hébergement** [INT] :

| Option | Statut juridique | Commentaire |
|---|---|---|
| Suisse | Aucun transfert | Recommandé pour les données des candidats ; argument commercial |
| UE / EEE | État adéquat (annexe 1 OPDo, **à vérifier**) | Acceptable avec un contrat de sous-traitance |
| États-Unis | Adéquat seulement si le destinataire est certifié DPF ; sinon clauses types et évaluation | Vérifier la certification sur la liste officielle du DPF ; vérifier aussi les sous-traitants ultérieurs |
| API de LLM (souvent aux États-Unis) | Communication à l'étranger et sous-traitance | **N'envoyer aucune donnée de candidat identifiable dans les prompts** ou utiliser une région CH/UE ; exclure l'entraînement sur les données ; secret LSE (§ 3.2) |

### 2.9 Sécurité

Il faut garantir une sécurité adaptée au risque (art. 8 LPD ; art. 1 ss OPDo, **articles à vérifier**) et annoncer au PFPDT les violations de la sécurité des données (art. 24 LPD, **article à vérifier** ; un guide du PFPDT sur l'art. 24 existe [6bis]).

Mesures produit :
- chiffrement au repos et en transit ;
- authentification forte ;
- droits par rôle et par agence ;
- journalisation des accès aux profils candidats ;
- cloisonnement entre les données B2B et les données candidats ;
- procédure de gestion des incidents.

### 2.10 Cas particuliers des sources publiques

| Source | Données personnelles possibles | Règle produit | Fondement |
|---|---|---|---|
| Permis de construire (feuilles officielles cantonales) | Propriétaire ou maître d'ouvrage **personne physique**, parfois avec adresse | **Exclusion** : si le requérant ou le propriétaire est une personne physique, le signal est ignoré ou réduit à « projet de construction à [commune], type, catégorie » sans nom. On ne conserve que les entreprises (bureau d'architectes SA/Sàrl, entreprise générale) | Proportionnalité, finalité [INT] ; la publication sert la procédure d'opposition, pas la prospection |
| FOSC : faillites, concordats, poursuites, appels aux créanciers, successions | Situation économique de personnes physiques (raisons individuelles, débiteurs, défunts) | **Exclusion totale à l'ingestion**, par liste blanche de rubriques | Ces rubriques existent dans la FOSC [20] (extrait de recherche) ; données révélant la situation économique d'une personne, pertinence nulle pour le placement [INT] |
| FOSC / RC : inscriptions, mutations, radiations | Noms et fonctions des dirigeants et associés | **Minimisation** : on garde l'événement (« nouvelle société », « changement de but », « augmentation de capital ») mais **on ne stocke pas les noms de personnes** | Minimisation [INT] |
| Offres d'emploi | Nom ou e-mail du recruteur | Ne pas stocker les contacts nommés tirés des annonces ; utiliser le contact d'entreprise générique ou le CRM existant | Minimisation [INT] |
| simap.ch (attributions) | Adjudicataire parfois personne physique (raison individuelle) | Marquer comme « raison individuelle » et ne garder que la donnée entreprise | [INT] |

### 2.11 Données des candidats

- **Données sensibles** (art. 5 let. c LPD) [EV] : opinions ou activités religieuses, philosophiques, politiques ou syndicales ; santé, sphère intime, origine raciale ou ethnique ; données génétiques ; données biométriques identifiant une personne ; poursuites et sanctions pénales et administratives [10] (extrait de recherche). Les **mesures d'aide sociale** figureraient aussi dans la liste (ch. 6, **à vérifier**).
- **Nationalité et permis de séjour** : ils ne figurent pas dans la liste des données sensibles (art. 5 let. c LPD) [10] (extrait de recherche ; à confirmer). Leur traitement est nécessaire pour vérifier l'autorisation de travailler. Ce sont pourtant des **indicateurs indirects de l'origine** et donc des facteurs de discrimination [INT]. **Règle** : le permis ne sert que de contrôle binaire (« autorisé à travailler pour ce poste : oui / non / à vérifier »). Il n'est **jamais** une caractéristique du score.
- **Santé** : sauf exigence objective du poste et consentement (ex. aptitude médicale à un travail en hauteur), **aucune donnée de santé dans l'outil**. Les absences maladie et les accidents sont exclus du score.
- **Casier judiciaire** : il est exclu du score. Il ne peut être traité que si l'emploi l'exige légalement, sur décision humaine.
- **Art. 328b CO** : ce plafond s'applique déjà en phase de candidature (§ 6.2) [30].

### 2.12 Position du PFPDT sur l'IA

- Le PFPDT a publié une prise de position selon laquelle **la législation sur la protection des données en vigueur est directement applicable à l'IA**. Cette publication a été **mise à jour** ; l'extrait de recherche mentionne une confirmation du **8 mai 2025** [9].
- La date de la prise de position initiale (annoncée comme **novembre 2023**) **n'a pas pu être confirmée pendant la session : à vérifier.**
- Les exigences mises en avant (transparence sur la finalité, le fonctionnement et les sources de données ; droit d'opposition au traitement automatisé ; AIPD pour les traitements à risque élevé) **sont à vérifier** sur la page officielle [9] [EV].

---

## 3. LSE (RS 823.11) et OSE (RS 823.111)

### 3.1 Autorisations

- **Placement privé** (art. 2 LSE) [EV] : est placeur quiconque met en relation employeurs et demandeurs d'emploi en vue de conclure un contrat de travail. Exercé régulièrement et contre rémunération, il exige une **autorisation cantonale**. Pour le placement de ou vers l'étranger, une **autorisation du SECO** s'ajoute [12] (extrait de recherche).
- **Location de services** (art. 12 LSE) [EV] : le bailleur cède à une entreprise locataire l'essentiel du pouvoir de direction sur un travailleur qu'il emploie. Cette activité exige une autorisation cantonale. La location de services vers l'étranger exige en plus une autorisation du SECO [12] (extrait de recherche).
- **Conséquence pour le produit** [INT] : l'outil ne change pas la nature de l'activité de Flexsis. Il doit cependant respecter les règles de comportement liées à ces autorisations, notamment la protection des données (§ 3.2). Vérifier que les autorisations couvrent tous les cantons et activités visés : **question à Flexsis**.

### 3.2 Traitement des données des demandeurs d'emploi

- **Art. 7 al. 3 LSE** (placement) [EV] : le placeur « n'est habilité à traiter les informations concernant des demandeurs d'emploi et des places vacantes que dans la mesure où et aussi longtemps que ces données sont nécessaires au placement » et il est tenu de garder le secret sur ces données [11] (extrait de recherche).
- **Concrétisations** :
  - pour le placement : **art. 19 OSE** [11] ;
  - pour la location de services : **art. 18 al. 3 LSE** et **art. 47 OSE** [11] (extrait de recherche ; contenu exact des articles **à vérifier**).
- **Consentement à la communication** : selon un extrait de recherche lié à ces règles, aucune donnée ne peut être communiquée à des tiers, notamment à de nouveaux employeurs, **sans le consentement écrit** de la personne concernée [11]. La forme exacte (écrite ?) et l'article (art. 19 OSE ?) sont **à vérifier**.
- **Implications** [INT] :
  1. **Rapprocher des candidats d'un besoin anticipé** (ex. un chantier attribué, sans offre de l'entreprise) reste « nécessaire au placement » si le candidat est inscrit pour être placé. C'est défendable, **à faire valider**.
  2. **« Aussi longtemps que »** : il faut une durée de conservation des dossiers inactifs, avec purge ou renouvellement du consentement. Exemple à décider : 24 mois après le dernier contact, **à valider**.
  3. **E-mails de prospection** : ils ne doivent contenir **aucun profil identifiable** sans consentement écrit. Seuls des profils anonymisés sont permis (« maçon CFC, 8 ans d'expérience, disponible dès le 1.11 »).
  4. **Secret** : l'envoi de données de candidats à un fournisseur de LLM étranger exige un contrat strict (pas d'entraînement, pas de conservation). Il vaut mieux l'éviter, ou pseudonymiser.

### 3.3 Obligation d'annonce des postes vacants (art. 21a LEI ; art. 53a ss OSE)

- **Principe** [EV] : dans les genres de profession où le taux de chômage national atteint ou dépasse le seuil, les postes vacants doivent être annoncés à l'ORP **avant** toute publication. Le seuil est de **5 % depuis le 1.1.2020** (8 % auparavant). L'obligation existe depuis le 1.7.2018 [14] (extrait de recherche).
- **Délai** : interdiction de publier pendant **5 jours ouvrables** à compter du jour ouvrable qui suit la confirmation de réception de l'ORP [14][16] (extrait de recherche).
- **Agences** : l'obligation incombe à l'acteur qui recrute, que ce soit l'employeur, une agence de placement privée ou une entreprise de location de services. Si la tâche est déléguée, c'est l'intermédiaire qui annonce et assume les obligations de l'employeur [14][16] (extrait de recherche).
- **Exceptions** (art. 53d OSE ; lettres et alinéas **à vérifier**) :
  - engagement de **14 jours calendaires** au plus ;
  - apprenti engagé à la suite de son apprentissage ;
  - personnes employées depuis au moins **6 mois** dans l'entreprise ;
  - proches de personnes ayant le pouvoir de signature ;
  - engagement d'un demandeur d'emploi inscrit [14][16] (extrait de recherche).
  
  **Point clé** : selon la doctrine, **l'exception des « 6 mois » ne s'applique pas aux bailleurs de services**. Sinon, la location de services aurait été favorisée [17] (extrait de recherche ; disposition exacte **à vérifier**).
- **Liste 2026** : elle est valable du **1.1.2026 au 31.12.2026** et repose sur la période T4 2024 à T3 2025, avec la nomenclature CH-ISCO-19. Exemples de professions qui y figurent : cuisiniers, agents d'entretien (5,3 %), « professions élémentaires du bâtiment » (le genre qui compte le plus d'actifs) [15] (extrait de recherche). La **liste 2027** devrait être publiée à l'automne 2026 : **à surveiller**.
- **Sanctions** (art. 117a LEI) : amende jusqu'à **40 000 CHF** en cas d'intention et jusqu'à **20 000 CHF** en cas de négligence, pour violation de l'obligation d'annonce (art. 21a al. 3 LEI) ou de l'obligation de convoquer des candidats à un entretien ou à un test (art. 21a al. 4 LEI, selon l'extrait) [18] (extrait de recherche).

### 3.4 Ce que cela implique pour le produit

1. **Table métier ↔ code CH-ISCO-19 ↔ liste annuelle**, mise à jour chaque 1er janvier.
2. **Alerte automatique** sur chaque proposition, par exemple : « Ce métier (CH-ISCO … ) est soumis à l'obligation d'annonce en 2026. Annoncez le poste à l'ORP et attendez 5 jours ouvrables avant toute publication. Exceptions possibles (≤ 14 jours…) : à vérifier avec le responsable. »
3. **Aucune fonction de contournement** : pas de suggestion de fractionner une mission en contrats de 14 jours ni de publier ailleurs avant le délai ; les candidats inscrits à l'ORP ne sont pas défavorisés.
4. **Journal** : date d'annonce à l'ORP, numéro de confirmation, date de fin de la restriction.

---

## 4. Réutilisation des données publiques

### 4.1 Statut des publications officielles et droit d'auteur

- **Art. 5 LDA** (RS 231.1) [EV] : ne sont pas protégés les lois, ordonnances, accords internationaux et autres actes officiels, ainsi que les décisions, procès-verbaux et rapports des autorités [24] (extrait de recherche).
- Le droit suisse ne connaîtrait **pas de droit *sui generis* sur les bases de données** comparable à celui de l'UE (**à vérifier**). Les compilations ne sont protégées que si elles sont originales (art. 4 LDA, **article à vérifier**).
- **Limite** : l'absence de droit d'auteur **ne supprime ni les CGU des plateformes ni la LCD**, ni l'éventuelle protection technique des sites [INT].

### 4.2 FOSC / SHAB et Amtsblattportal

- Le SECO gère la FOSC, qui publie notamment les rubriques registre du commerce, faillites, concordats, poursuites, appels aux créanciers, titres disparus et marchés publics. Les données sont hébergées en Suisse (ordonnance sur la FOSC, RS 221.415) [20] (extrait de recherche).
- Un extrait mentionne une disposition (art. 13, **article à vérifier**) qui permet au SECO de régler **l'utilisation et l'exploitation des données** par contrats de droit public. Ces contrats peuvent être conclus en ligne, notamment par l'acceptation de CGU [20] (extrait de recherche).
- L'Amtsblattportal propose une **API publique** au format XML [21] (extrait de recherche ; CGU de l'API **à vérifier**).
- **Recommandation** : utiliser l'API officielle, vérifier les CGU (usage commercial, fréquence, mention de la source), et filtrer par **liste blanche** de rubriques (RC uniquement, § 2.10).

### 4.3 simap.ch

- simap.ch est exploité par l'association simap.ch (Confédération et cantons) pour les publications légales des adjudicateurs [37] (extrait de recherche).
- **Les CGU de réutilisation et les conditions d'une éventuelle API n'ont pas pu être consultées : à vérifier.**
- **Recommandation** : demander à l'association simap.ch l'autorisation écrite de réutiliser les avis d'attribution dans un usage commercial, ou un flux officiel. Limiter la fréquence de collecte et citer la source.

### 4.4 opendata.swiss

Conditions d'utilisation standard [19] (extrait de recherche) [EV] :

| Catégorie | Usage non commercial | Usage commercial | Source |
|---|---|---|---|
| OPEN (`terms_open`) | Libre | Libre | Recommandée |
| BY (`terms_by`) | Libre | Libre | **Obligatoire** |
| ASK (`terms_ask`) | Libre | **Autorisation préalable** | Recommandée |
| BY ASK (`terms_by_ask`) | Libre | **Autorisation préalable** | **Obligatoire** |

PROXSIS est un **usage commercial**. Pour chaque jeu de données, il faut stocker la catégorie et, pour ASK ou BY ASK, la preuve de l'autorisation. Les licences Creative Commons éventuellement acceptées sont **à vérifier**.

### 4.5 Zefix

- Zefix offre une application web, une **API REST** et une application mobile. Selon l'extrait, l'offre se limite aux **requêtes individuelles** : aucun abonnement, et pas d'obtention de tout ou partie de la base. Contact : zefix@bj.admin.ch [26] (extrait de recherche).
- Un jeu de données de base des entités actives, mis à jour quotidiennement, serait disponible sur opendata.swiss [26] (extrait de recherche ; conditions **à vérifier**).
- **Recommandation** : utiliser l'API Zefix pour **enrichir à la demande** (forme juridique, siège, but) et non pour reconstituer la base. Utiliser le jeu opendata.swiss pour l'identification de masse, selon sa catégorie de conditions.

### 4.6 Feuilles officielles cantonales, permis de construire, eConstruction Valais

- **Valais** :
  - Les demandes d'autorisation de construire sont mises à l'enquête pendant **30 jours**, durant lesquels des tiers peuvent consulter le dossier (article à vérifier — l'audit du 2026-10-05 signale un extrait citant les art. 42 et 47 ; RS/VS 705.1 à vérifier).
  - L'accès en ligne passe par **eConstruction**, avec un moyen d'identification électronique (SwissID) et le numéro de référence publié au Bulletin officiel [25] (extrait de recherche).
  - L'extrait ne dit **pas** que l'accès serait réservé aux personnes concernées : les CGU exactes de la plateforme sont **à vérifier**.
- **Interprétation** [INT] : la consultation des dossiers sert la **procédure d'opposition**. Un accès authentifié, utilisé à grande échelle pour la prospection, détournerait cette finalité, et les dossiers contiennent des données personnelles (plans, propriétaires). **Recommandation : n'utiliser que l'avis publié** au Bulletin officiel (commune, objet, requérant entreprise), **jamais les dossiers eConstruction**.
- **Autres cantons** : les CGU des feuilles officielles et de l'Amtsblattportal sont **à vérifier** canton par canton. Une matrice des sources est à tenir.

### 4.7 Portails d'emploi privés, robots.txt et LCD

- **Art. 5 let. c LCD** [EV] : agit de façon déloyale celui qui reprend, par des procédés techniques de reproduction et sans sacrifice correspondant, le résultat de travail d'un tiers prêt à être mis sur le marché, et l'exploite comme tel. La doctrine souligne que la reprise n'est illicite qu'en présence de circonstances déloyales, notamment une reprise sans investissement propre [22] (extrait de recherche).
- **ATF 131 III 384** :
  - Ce litige concernait un moteur de recherche (« spider ») qui reprenait systématiquement des annonces immobilières d'autres plateformes.
  - Selon un article de presse, le Tribunal fédéral (février 2005) a **rejeté** l'action des portails immobiliers contre l'exploitant d'anzeiger.ch [23] (extrait de recherche).
  - **Portée exacte et motivation à vérifier.** Ne pas en déduire une autorisation générale du scraping.
- **CGU des portails** (jobs.ch, Indeed, LinkedIn, etc.) : elles interdisent en général l'aspiration (**à vérifier pour chacun**). Leur opposabilité dépend de leur acceptation (compte, API), et la violation peut entraîner une responsabilité contractuelle [INT].
- **robots.txt** : à notre connaissance, aucune valeur légale propre en droit suisse (**à vérifier**). Ce fichier est cependant un indice de la volonté de l'exploitant, et son non-respect aggrave le risque LCD et réputationnel [INT].
- Contourner des protections techniques (connexion, captcha) pourrait soulever des questions pénales (accès indu à un système informatique, **article à vérifier**) : **interdit dans le produit**.
- **Recommandation** : offres d'emploi uniquement via des **licences ou API** (agrégateur sous contrat, partenariat), via les sites carrière publics des entreprises en respectant robots.txt et une fréquence faible, ou via des données saisies par les consultants.

### 4.8 Synthèse : mode d'accès par source

| Source | Accès recommandé | Points à vérifier |
|---|---|---|
| simap.ch | Flux ou API officiels, ou accord écrit | CGU, usage commercial |
| FOSC / Amtsblattportal | API officielle, liste blanche « RC » | CGU de l'API, fréquence |
| Feuilles officielles cantonales | API Amtsblattportal ou flux cantonaux, avis seulement | CGU cantonales |
| Zefix | API REST à la demande, jeu opendata.swiss | Conditions de l'API |
| opendata.swiss | Selon la catégorie OPEN / BY / ASK | Autorisations ASK |
| Portails d'emploi privés | Licence uniquement | CGU, contrat |
| eConstruction VS | **Ne pas utiliser** | — |

---

## 5. Démarchage commercial B2B

- **Appels téléphoniques (art. 3 al. 1 let. u LCD)** [EV] :
  - Il est déloyal de ne pas respecter la mention de l'annuaire (**astérisque**) selon laquelle un abonné ne souhaite pas recevoir de publicité de tiers.
  - Selon le SECO, le télémarketing vers des numéros marqués d'un astérisque **ou non inscrits** à l'annuaire est interdit. Les let. v et w complètent cette règle (affichage d'un numéro inscrit, utilisation de données obtenues en violation) [28] (extrait de recherche).
  - **B2B ?** Le texte vise le « client » de l'annuaire, sans distinguer personnes physiques et morales. Un numéro d'entreprise marqué d'un astérisque doit donc être respecté [INT, **à vérifier**].
  - L'exception pour les relations clients existantes est **à vérifier**.
  - **Mesure** : avant tout appel suggéré, contrôler l'astérisque (via le fournisseur d'annuaire, sous licence), le statut client et la liste d'opposition interne de Flexsis (« ne plus contacter »).
- **E-mails (art. 3 al. 1 let. o LCD)** [EV] :
  - La publicité **de masse** par télécommunication exige le consentement préalable, l'indication correcte de l'expéditeur et un moyen simple et gratuit de refuser.
  - Exception : un client dont on a obtenu les coordonnées lors d'une vente peut recevoir de la publicité pour des produits ou services propres semblables, s'il a été informé de la possibilité de refuser [27] (extrait de recherche).
  - La disposition ne distinguerait pas B2B et B2C (**à vérifier**).
  - **Mesure** : pas d'envoi automatisé ni groupé. Le consultant envoie **individuellement** un message personnalisé depuis sa messagerie, avec expéditeur identifiable et mention de désinscription. Un volume important de messages quasi identiques, même « personnalisés » par l'IA, risque d'être qualifié de publicité de masse [INT].
- **Interlocuteurs nommés** : l'e-mail nominatif d'un responsable RH est une donnée personnelle. La LPD s'applique (finalité, information, opposition) ; l'intérêt prépondérant comme motif justificatif relève de l'art. 31 LPD (**article à vérifier**).
- **E-mails générés : exactitude et responsabilité** [INT] :
  - Flexsis reste responsable du contenu envoyé.
  - Une affirmation inexacte sur l'entreprise (« vous avez remporté le marché X ») peut nuire à la relation et, si elle est trompeuse, poser problème au regard de la LCD (art. 3 al. 1 let. b, **article à vérifier**).
  - **Mesures** : chaque fait est cité avec sa source et sa date ; pas d'invention ; relecture obligatoire ; ton factuel ; pas de données de candidats identifiables (§ 3.2).

---

## 6. Discrimination et équité

### 6.1 Cadre suisse

- **Art. 8 Cst.** (RS 101) : égalité et interdiction de la discrimination (origine, sexe, âge, langue, situation sociale, handicap, etc.). Ce droit fondamental lie l'État. Son effet entre particuliers est **indirect** [INT ; liste exacte des critères **à vérifier**].
- **LEg** (RS 151.1) [EV] :
  - L'art. 3 interdit de discriminer les travailleurs en raison du sexe, directement ou indirectement, **notamment à l'embauche** [29] (extrait de recherche).
  - En cas de refus d'embauche discriminatoire, l'indemnité est fixée selon les circonstances et ne peut excéder **trois mois de salaire** (art. 5 al. 2 LEg). Elle ne suppose ni dommage ni faute [29] (extrait de recherche).
  - **L'application de la LEg à un placeur** qui présélectionne pour le compte d'un employeur est **à vérifier** [INT].
- **Art. 328b CO** [EV] :
  - L'employeur ne peut traiter des données sur le travailleur que si elles portent sur ses **aptitudes** à remplir l'emploi ou sont nécessaires à l'exécution du contrat. La règle vaut aussi pendant la **candidature** [30] (extrait de recherche).
  - Selon un extrait, l'arrêt **4A_518/2020** pose une présomption de licéité pour ces données et d'illicéité pour les autres, sauf motif justificatif [30] (extrait de recherche ; **à vérifier**).
- Il n'existe pas de loi générale contre la discrimination dans le secteur privé (**à vérifier**). Le risque de discrimination fondée sur l'origine ou l'âge est encadré par la protection de la personnalité (art. 28 CC, art. 328 CO) [INT].

### 6.2 Implications pour la suggestion de candidats

1. **Caractéristiques interdites dans le score** : sexe, âge ou date de naissance, nationalité, permis (sauf contrôle binaire d'autorisation), origine, photo, état civil, enfants, religion, santé, nom et prénom (indicateurs indirects), adresse fine (indicateur indirect d'origine sociale ; la distance au chantier est permise, sous forme agrégée).
2. **Caractéristiques permises** : compétences, certificats (CFC, permis de conduire, CACES/SUVA…), expérience métier, disponibilité, zone de mobilité déclarée, langues **requises par le poste**, préférences déclarées par le candidat.
3. **Audit** :
   - tests de disparité trimestriels sur les suggestions, à partir de statistiques agrégées par sexe et par tranche d'âge, calculées hors modèle par une personne habilitée ;
   - documentation des résultats ;
   - correction des écarts.
4. **Explicabilité** : chaque suggestion affiche les 3 à 5 critères qui l'expliquent.
5. **Pas d'apprentissage sur les décisions historiques** des clients ou consultants sans contrôle des biais : risque de reproduire des discriminations passées.

---

## 7. Utilisation dans l'UE : RGPD et règlement sur l'IA ; position suisse sur l'IA

### 7.1 RGPD (règlement (UE) 2016/679) [34]

Le texte n'a pas été consulté pendant la session : accès bloqué. Contenu notoire, **à vérifier**.

- **Art. 3 par. 2** (extraterritorialité) : le RGPD s'applique à un responsable hors de l'UE s'il **offre des biens ou services** à des personnes dans l'UE ou **suit leur comportement** dans l'UE.
  - *Frontaliers français* : si Flexsis cible activement des résidents français (annonces en France, recrutement en France), le RGPD pourrait s'appliquer à leurs données [INT].
  - *Filiales d'Interiman dans l'UE* : si elles utilisent l'outil, le RGPD s'applique directement (art. 3 par. 1) [INT].
- **Art. 22** : droit de ne pas faire l'objet d'une décision **fondée exclusivement** sur un traitement automatisé, y compris le profilage, produisant des effets juridiques ou affectant de manière significative. Pour le risque de requalification d'un score, voir l'arrêt *SCHUFA* (§ 2.4, **à vérifier**).
- **Art. 35** : AIPD obligatoire en cas de risque élevé, notamment en cas d'évaluation systématique d'aspects personnels fondée sur un traitement automatisé.

### 7.2 Règlement sur l'IA (RIA, règlement (UE) 2024/1689) [35]

- **Champ territorial** : le RIA s'appliquerait aussi aux fournisseurs et déployeurs établis hors de l'UE **lorsque les sorties du système sont utilisées dans l'Union** (art. 2 par. 1 let. c, **article à vérifier**).
  - Un usage purement suisse (consultants en Suisse, postes en Suisse, même pour des frontaliers) ne serait a priori pas couvert [INT].
  - Un usage par une entité de l'UE, ou pour des postes dans l'UE, le serait [INT].
- **Annexe III, point 4 a)** [EV] : sont à haut risque les systèmes d'IA destinés au **recrutement ou à la sélection** de personnes physiques, notamment pour diffuser des offres ciblées, **analyser et filtrer les candidatures et évaluer les candidats** [31] (extrait de recherche).
  - Le point 4 b) vise les décisions sur les relations de travail (promotion, licenciement, attribution de tâches selon le comportement, suivi des performances) [31].
  - **La suggestion de candidats** (classement de candidats pour un besoin) **tomberait dans le point 4 a)** [INT].
- **Art. 6 par. 3** [EV] : un système de l'annexe III n'est pas à haut risque s'il ne présente pas de risque important. Les cas visés sont une tâche procédurale étroite, l'amélioration d'une activité humaine déjà réalisée, la détection d'écarts, ou une **tâche préparatoire**. **Cependant, un système de l'annexe III est toujours à haut risque lorsqu'il effectue un profilage de personnes physiques.** Le fournisseur qui invoque la dérogation doit la documenter [32] (extrait de recherche).
  - Le rapprochement candidat-besoin étant un profilage, **la dérogation ne serait pas disponible** [INT].
- **Volet « priorisation d'entreprises »** : il n'évalue pas des personnes physiques et ne figure pas à l'annexe III. **Il n'est a priori pas à haut risque** [INT].
  - Les obligations de transparence de l'art. 50 RIA (contenus générés, e-mails) sont **à vérifier** au regard du projet de lignes directrices de la Commission sur l'art. 50, publié le 8.5.2026 (extrait de recherche).
- **Calendrier** [EV/PR] :
  - Le **règlement « Omnibus numérique sur l'IA » (UE) 2026/1744** a été publié au JO le **24.7.2026** et est **entré en vigueur le 27.7.2026**. Il reporte l'application des obligations des systèmes à haut risque de l'**annexe III** du **2.8.2026 au 2.12.2027** [33] (extraits de recherche concordants de plusieurs sources ; texte officiel **à vérifier sur EUR-Lex**).
  - Le report pour l'annexe I (produits réglementés) au **2.8.2028** n'a pas été confirmé par les extraits : **à vérifier**.
  - Des modifications de l'obligation de maîtrise de l'IA (art. 4) par l'Omnibus sont **à vérifier**.
- **Si le volet candidats était déployé dans l'UE** [INT] :
  - Flexsis serait **fournisseur** si elle développe l'outil, et **déployeur** si elle l'utilise.
  - Obligations à prévoir (articles **à vérifier**) : système de gestion des risques, gouvernance des données, documentation technique, journalisation, contrôle humain, information des travailleurs ou de leurs représentants, et éventuellement analyse d'impact sur les droits fondamentaux.
  - **Recommandation** : jusqu'à décision contraire, **ne pas déployer le volet candidats dans l'UE** et prévoir un géo-cloisonnement.

### 7.3 Position suisse sur l'IA

Faits non vérifiés par l'agent de recherche (budget épuisé) ; l'audit du 2026-10-05 les a confirmés par extraits de recherche et fournit ces sources, **à relire** : communiqué du Conseil fédéral, https://www.admin.ch/fr/nsb?id=104110 ; ICTjournal, article du 27.3.2025 sur la signature de la Convention (extraits de recherche, consultés le 2026-10-05).
- le **12.2.2025**, le Conseil fédéral a décidé de **ratifier la Convention-cadre du Conseil de l'Europe sur l'IA** ;
- il a choisi d'adapter le droit suisse **de manière sectorielle**, sans loi horizontale de type RIA, et prévoyait de soumettre un projet en consultation vers la fin 2026 ;
- la Suisse aurait signé la Convention le 27.3.2025.

En attendant, la **LPD s'applique directement à l'IA** (§ 2.12) [9] [EV].

---

## 8. Liste de contrôle pour le produit

| # | Exigence | Implémentation dans PROXSIS | Base | Priorité |
|---|---|---|---|---|
| C1 | Filtre de données personnelles | Liste blanche des rubriques ; détection des personnes physiques (NER) ; écartement des propriétaires privés et des dirigeants ; signalement des raisons individuelles | LPD (proportionnalité) ; § 2.10 | Bloquant |
| C2 | Journal de provenance | Chaque signal stocke l'URL, la date de publication, la date de collecte, la source, la licence ou catégorie et le mode d'accès (API / licence) | Exactitude ; CGU ; § 4 | Bloquant |
| C3 | Logique visible de chaque proposition | Panneau « Pourquoi cette entreprise / ce candidat ? » : signaux, poids, dates, sources | Art. 21 LPD ; PFPDT IA ; § 2.4 | Bloquant |
| C4 | Bouton « le consultant décide » | Accepter / modifier / écarter + motif ; recherche manuelle toujours disponible | Art. 21 LPD ; § 2.4 | Bloquant |
| C5 | Pas de décision automatique | Aucune exclusion par seuil ; aucun message automatique au candidat ou au client | Art. 21 LPD ; art. 22 RGPD | Bloquant |
| C6 | Conservation limitée | Signaux B2B : 12 mois (à valider) ; dossiers candidats inactifs : durée à fixer, avec purge ; journaux : 12 mois | Art. 7 al. 3 LSE ; LPD | Bloquant |
| C7 | Droits d'accès par rôle | Consultant (son agence), manager, administrateur, auditeur ; journal d'accès aux profils | LPD (sécurité) ; secret LSE | Bloquant |
| C8 | Hébergement en Suisse possible | Déploiement CH par défaut ; aucune donnée candidat vers une API de LLM non contractualisée | Art. 16 LPD (à vérifier) ; § 2.8 | Élevée |
| C9 | AIPD avant le pilote | Document d'AIPD ; revue juridique ; mise à jour à chaque nouvelle source | Art. 22 LPD | Bloquant |
| C10 | Information des candidats | Déclaration de confidentialité mise à jour ; mention de l'outil, de l'intervention humaine et des droits | Art. 19 LPD ; § 2.5 | Bloquant |
| C11 | Registre des traitements | Inscription « PROXSIS prospection » et « PROXSIS matching » | Art. 12 LPD ; art. 24 OPDo | Bloquant |
| C12 | Obligation d'annonce | Table CH-ISCO-19 ; alerte ; suivi ORP | Art. 21a LEI ; OSE | Bloquant |
| C13 | Prospection conforme | Contrôle de l'astérisque et de la liste d'opposition ; pas d'envoi de masse ; expéditeur et désinscription | Art. 3 al. 1 let. o/u LCD | Bloquant |
| C14 | Équité | Liste de caractéristiques interdites ; audit trimestriel ; rapport | LEg ; art. 328b CO | Élevée |
| C15 | Sources licites | Matrice des sources (CGU, licence, autorisation) validée par le juriste | LCD ; CGU | Bloquant |
| C16 | E-mails générés vérifiés | Faits sourcés ; relecture ; aucune donnée candidat identifiable | LCD ; LSE | Bloquant |
| C17 | Géo-cloisonnement UE | Volet candidats désactivé pour les entités ou postes de l'UE | RGPD ; RIA | Élevée |

---

## 9. Questions ouvertes

**Au juriste**

1. Le rapprochement candidat-besoin constitue-t-il un **profilage à risque élevé** (art. 5 LPD) ? Faut-il un **consentement exprès** des candidats, ou un intérêt prépondérant ou l'exécution du contrat de placement suffit-il ?
2. Le rapprochement avec des **besoins anticipés** (avant toute offre de l'entreprise) est-il couvert par « nécessaire au placement » (art. 7 al. 3 LSE ; art. 19 et 47 OSE) ?
3. Quelle est la **forme exacte du consentement** exigée pour communiquer des données de candidats à un client ou prospect (écrite ?), et quel est l'article applicable ?
4. Quelle **durée de conservation** est défendable pour les dossiers de candidats inactifs et pour les signaux B2B ?
5. Les **raisons individuelles** doivent-elles être exclues totalement ou seulement minimisées ?
6. La consultation automatisée des **feuilles officielles cantonales** et de la **FOSC** pour un usage commercial est-elle conforme aux CGU de l'Amtsblattportal et des cantons ? Faut-il un contrat avec le SECO ?
7. Quelles sont les **conditions de réutilisation de simap.ch** ? Une autorisation est-elle nécessaire ?
8. Quelle est la portée de l'**ATF 131 III 384** et de l'art. 5 let. c LCD pour la collecte de sites carrière d'entreprises ?
9. L'**astérisque** et l'art. 3 al. 1 let. o/u LCD s'appliquent-ils pleinement en B2B ? À partir de quel volume des e-mails personnalisés par IA deviennent-ils de la « publicité de masse » ?
10. La **LEg** s'applique-t-elle à un placeur qui présélectionne pour un client ? Quelles obligations d'audit recommander ?
11. Le volet candidats tombe-t-il sous le **RGPD** pour des frontaliers résidant en France, et sous le **RIA** si une entité d'Interiman dans l'UE l'utilise ?
12. Quelles sont les conséquences du règlement **(UE) 2026/1744** (Omnibus) pour un éventuel déploiement dans l'UE, et comment s'articulent les art. 4 et 50 RIA ?
13. Le recours à un **LLM hébergé aux États-Unis** (certifié DPF ou non) est-il compatible avec le **secret de l'art. 7 al. 3 LSE** ?

**À Flexsis / Interiman Group**

14. Quel est l'**effectif** de Flexsis (seuil de 250 pour le registre) ? Un registre et une AIPD existent-ils déjà ? Un conseiller à la protection des données est-il désigné ?
15. Quelles **autorisations LSE** (cantonales, SECO) Flexsis détient-elle, pour quelles activités et quels cantons ?
16. Que contient la **déclaration de confidentialité candidats** actuelle ? Quels consentements sont recueillis à l'inscription ?
17. Des **entités d'Interiman dans l'UE** ou des clients situés dans l'UE utiliseraient-ils l'outil ?
18. Quel **hébergement** est préféré (Suisse, UE) ? Quels fournisseurs de LLM sont envisagés ?
19. Existe-t-il des **contrats ou licences de données** (agrégateur d'offres d'emploi, annuaire avec astérisque) ?
20. Comment l'**obligation d'annonce** est-elle gérée aujourd'hui (processus ORP, accès Job-Room) ?
21. Qui assumera le **rôle d'auditeur** (biais, accès, qualité des sources) ?

---

## 10. Sources

Toutes les sources ont été consultées le **2026-10-04**, via des extraits de moteur de recherche sauf mention contraire. Pour celles marquées « non consultée », l'accès direct était bloqué.

1. OFJ, *FAQ sur la révision de la loi sur la protection des données*, https://www.bj.admin.ch/dam/bj/fr/data/staat/datenschutz/faq-dsr.pdf.download.pdf/faq-dsr-f.pdf (extrait de recherche).
2. Onlinekommentar, commentaire de l'art. 5 let. f et g LPD (profilage), https://onlinekommentar.ch/fr/kommentare/dsg5fundg (extrait de recherche).
3. Portail PME de la Confédération (SECO), *Nouvelle loi sur la protection des données (nLPD)*, https://www.kmu.admin.ch/kmu/fr/home/fakten-und-trends/digitalisierung/datenschutz/neues-datenschutzgesetz-revdsg.html (extrait de recherche).
4. USAM, *Aide-mémoire LPD/OPDo*, https://www.sgv-usam.ch/media/19662/20221222_merkblatt_dsg_dsv_fr.pdf (extrait de recherche).
5. Onlinekommentar, commentaire de l'art. 21 LPD, https://onlinekommentar.ch/fr/kommentare/dsg21 ; CDBF, https://cdbf.ch/fr/1400/ (extraits de recherche).
6. PFPDT, *Aide-mémoire sur l'analyse d'impact relative à la protection des données personnelles (art. 22 et 23 LPD)*, https://www.edoeb.admin.ch/dam/edoeb/fr/Dokumente/datenschutz/merkblatt_dsfa.pdf.download.pdf/Merkblatt_DSFA_FR.pdf (extrait de recherche).
   6bis. PFPDT, *Guide relatif à l'annonce des violations de la sécurité des données (art. 24 LPD)*, https://www.edoeb.admin.ch/dam/fr/sd-web/T64CAUyvAMcF/1_2%20Leitfaden%20des%20ED%C3%96B%20betreffend%20die%20Meldung%20von%20Datensicherheitsverletzungen%20und%20Information%20der%20Betroffenen%20nach%20Art.%2024%20DSG_FR.pdf (titre seul, extrait de recherche).
7. Legiscope, *Registre des traitements nLPD*, https://www.legiscope.com/blog/registre-traitements-nlpd-suisse.html ; Onlinekommentar art. 12 LPD, https://onlinekommentar.ch/fr/kommentare/dsg12 ; ARTISET, guide 2023, https://blog.insos.ch/files/CAWBSSV/mise_sur_pied_de_la_protection_des_donnees_dans_les_etablissements_guide_artiset_2023.pdf (extraits de recherche).
8. Walder Wyss, *Federal Council: Swiss-US Data Privacy Framework in force on 15 September 2024* (14.8.2024), https://www.walderwyss.com/en/news/2024-08-14_federal-council-swiss-us-data-privacy-framework-in-force-on-15-september-2024 ; Homburger, https://homburger.ch/en/insights/new-swiss-u-s-data-privacy-framework (extraits de recherche).
9. PFPDT, *Update – Current data protection legislation is directly applicable to AI*, https://www.edoeb.admin.ch/en/update-current-legislation-directly-applicable-ai (titre et extrait de recherche ; page non consultée, date initiale à vérifier).
10. Onlinekommentar, art. 5 let. c LPD, https://onlinekommentar.ch/fr/kommentare/dsg5c ; Juriup, https://juriup.ch/terme-juridique/donnees-personnelles-sensibles-en-suisse-lpd/ (extraits de recherche).
11. SECO, *Protection de la personnalité dans le placement privé et la location de services*, https://www.secoalv.admin.ch/dam/secoalv/fr/dokumente/publikationen/arbeitsvermittlung-personalverleih/persoenlichkeit/SchutzPersoenlichkeit.pdf.download.pdf/SchutzPersoenlichkeit.pdf (extraits de recherche : art. 7 al. 3 LSE, art. 19 OSE, art. 18 al. 3 LSE, art. 47 OSE).
12. Canton de Vaud, *FAQ LSE*, https://www.vd.ch/fileadmin/user_upload/themes/economie_emploi/emploi/fichiers_pdf/FAQ_AVG_fr_TA_LSE.pdf ; État du Valais, *Placement privé*, https://www.vs.ch/web/sict/placement-prive (extraits de recherche).
13. SECO, *Directive relative à l'obligation d'annoncer les postes vacants*, https://www.arbeit.swiss/dam/secoalv/fr/dokumente/unternehmen/Stellenmeldepflicht/Weisung_Stellenmeldepflicht_FR.pdf.download.pdf/Weisung_Stellenmeldepflicht_FR.pdf (titre, extrait de recherche).
14. Ville de Lausanne, *Obligation d'annonce des postes vacants*, https://www.lausanne.ch/vie-pratique/travail/protection-des-travailleurs/travailleur/contrat-de-travail-regles/obligation-annonce-postes-vacants.html (extrait de recherche).
15. SECO, *Liste des genres de professions soumis à l'obligation d'annonce 2026*, https://www.arbeit.swiss/dam/secoalv/fr/dokumente/unternehmen/Stellenmeldepflicht/liste_meldepflichtige_berufsarten_2026_fr.pdf.download.pdf/liste_meldepflichtige_berufsarten_2026_fr.pdf ; État de Genève, https://www.ge.ch/actualite/obligation-annoncer-emplois-vacants-2026-11-03-2026 (extraits de recherche).
16. Canton de Soleure, *Handout Stellenmeldepflicht für private Arbeitsvermittler*, https://so.ch/fileadmin/internet/vwd/vwd-awa/Arbeitsmarkt_RAV/02_RAV_fuer_Arbeitgebende_Unternehmen/Handout_Stellenmeldepflicht_fuer_pAV.pdf ; Canton de Schwyz, https://www.sz.ch/behoerden/verwaltung/volkswirtschaftsdepartement/amt-fuer-arbeit/unternehmen.html (extraits de recherche).
17. Wenger Vieli, *Die neue Stellenmeldepflicht*, https://www.wengervieli.ch/getattachment/d4a276a3-fa19-4d30-9a91-7ab959332366/Die-neue-Stellenmeldepflicht.aspx (extrait de recherche : exception des 6 mois non applicable aux bailleurs de services).
18. LEI, art. 117a (texte bilingue), https://www.droit-bilingue.ch/fr-en/1/14/142.20-117a-190.html (extrait de recherche).
19. opendata.swiss, *Terms of use*, https://opendata.swiss/en/terms-of-use (extrait de recherche).
20. Ordonnance sur la FOSC (RS 221.415), LexFind, https://www.lexfind.ch/tolv/142390/fr et https://www.lexfind.ch/tolv/142397/de (extraits de recherche).
21. PyPI, *shab-parser* (API publique Amtsblattportal), https://pypi.org/project/shab-parser/ (extrait de recherche ; source non officielle).
22. Droit pour la pratique, arrêt commenté, art. 5 let. c LCD, https://droitpourlapratique.ch/arret/21110 (extrait de recherche).
23. ATF 131 III 384, mentions : Netzwoche, https://www.netzwoche.ch/news/2014-01-31/auch-immosearchch-will-spider-technologie-einfuehren ; Omnilex, commentaire de l'art. 3 LCD, https://app.omnilex.ai/fr/sources/commentaries/ch-fedlex--241--3 (extraits de recherche ; arrêt non lu).
24. OMPI, WIPO Lex, Loi sur le droit d'auteur (RS 231.1), https://www.wipo.int/wipolex/fr/legislation/details/715 (extrait de recherche : art. 5 LDA).
25. État du Valais, *eConstruction – FAQ*, https://www.vs.ch/web/sajmte/faq2 ; https://www.vs.ch/web/sajmte/econstruction (extraits de recherche).
26. OFJ, *Registre du commerce, Zefix et Regix*, https://www.bj.admin.ch/fr/registre-du-commerce-zefix-et-regix ; Rister, https://www.rister.ch/post/zefix-le-portail-du-registre-du-commerce-suisse (extraits de recherche).
27. OFCOM, *When is mass sending allowed?*, https://www.bakom.admin.ch/en/when-is-mass-sending-allowed (extrait de recherche : art. 3 al. 1 let. o LCD).
28. SECO, *Appels publicitaires indésirables*, https://www.seco.admin.ch/fr/appels-publicitaires-indesirables (extrait de recherche : art. 3 al. 1 let. u, v, w LCD).
29. Omnilex, commentaires de la LEg (RS 151.1), https://app.omnilex.ai/fr/sources/commentaries/ch-fedlex--151.1--2 ; Weka, https://www.weka.ch/themes/droit/droit-du-travail/droit-du-travail-suisse/article/loi-sur-legalite-egalite-et-diversite-dans-les-rapports-de-travail/ (extraits de recherche : art. 3 et 5 al. 2 LEg).
30. Weka, *Droit du travail et protection des données*, https://www.weka.ch/themes/droit/protection-des-donnees-et-droit-informatique/protection-des-donnees/article/droit-du-travail-et-protection-des-donnees-comprendre-les-dispositions-actuelles/ ; Omnilex, commentaire de l'art. 328b CO, https://app.omnilex.ai/fr/sources/commentaries/ch-fedlex--220--328b (extraits de recherche).
31. Ropes & Gray, *Computer says you're hired*, https://www.ropesgray.com/en/insights/viewpoints/102lu44/computer-says-youre-hired-fired-promoted ; Legal Nodes, https://legalnodes.com/article/ai-in-recruitment-processes-navigating-high-risk-systems-for-ai-deployers (extraits de recherche : annexe III, point 4 RIA).
32. Commission européenne, *AI Act Service Desk – Article 6*, https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6 (extrait de recherche).
33. Règlement Omnibus IA (UE) 2026/1744 : Lewis Silkin (27.7.2026), https://www.lewissilkin.com/insights/2026/07/27/the-digital-omnibus-on-ai-enters-into-force-today-102nedo ; K&L Gates, https://www.klgates.com/EU-Digital-Omnibus-on-AI-Enters-Into-Force-7-31-2026 ; NicFab, https://www.nicfab.eu/en/posts/digital-omnibus-ai-official-journal/ ; Praxikon, https://www.praxikon.com/en/posts/digital-omnibus-high-risk-postponement-december-2027 (extraits de recherche).
34. Règlement (UE) 2016/679 (RGPD), EUR-Lex, https://eur-lex.europa.eu/eli/reg/2016/679/oj (**non consulté** : accès bloqué).
35. Règlement (UE) 2024/1689 (RIA), EUR-Lex, https://eur-lex.europa.eu/eli/reg/2024/1689/oj (**non consulté** : accès bloqué).
36. LPD, RS 235.1, Fedlex, https://www.fedlex.admin.ch/eli/cc/2022/491/fr (**non consultée** : accès bloqué). OPDo (RS 235.11), LSE (RS 823.11), OSE (RS 823.111), LEI (RS 142.20), LCD (RS 241), LDA (RS 231.1), LEg (RS 151.1), CO (RS 220) et Cst. (RS 101) : à consulter sur https://www.fedlex.admin.ch avec le numéro RS (**non consultés** : accès bloqué).
37. Wikipedia, *Simap.ch*, https://en.wikipedia.org/wiki/Simap.ch (extrait de recherche).

---

*Fin du mémo. Version 1, 2026-10-04. À faire valider par un juriste avant tout pilote.*
