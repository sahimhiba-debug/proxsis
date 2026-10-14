# Protocole de pilote : deux agences, six semaines, une comparaison

Statut : **proposition à valider par Flexsis** (choix des agences, seuils, responsables) **et par un juriste**. Mis à
jour le 07.10.2026 selon le brief « à distance », § 11. Les taux de base de la taille d'échantillon (§ 5) sont des
**hypothèses**, à remplacer par les chiffres de Flexsis.

## 1. La question

Une seule comparaison principale : **la pratique actuelle des consultants, et Proxsis**.

Appeler les entreprises de la liste du lundi, avec le dossier préparé et le carnet, produit-il plus de conversations
utiles, de commandes et de journées supplémentaires facturées que la prospection habituelle ? Et à quel coût, temps des
équipes compris ? Le consultant décide de chaque appel ; Proxsis prépare et garde ses décisions.

## 2. Le dispositif

- **Agences** : deux agences Flexsis du Valais (choix par Flexsis). **Durée** : six semaines de listes, puis le suivi
  des commandes **au-delà des six semaines** (au moins huit semaines après la dernière liste, l'horizon de la mesure).
- **Départ sans attendre l'historique** : le pilote ne dépend pas de l'historique de commandes de Flexsis. Cet
  historique (12 mois) sert à une **étude complémentaire**, sous accord de confidentialité
  (`docs/affaires/modele_accord_confidentialite.md`, `docs/affaires/demande-donnees-pilote.md`).
- **Règle de sélection** : la règle simple, inchangée pendant tout le pilote. Ce sont les entreprises de la spécialité
  et de la région qui ont remporté le plus de marchés publics dans les 52 semaines, celle de la visite et de la mesure
  CLAIMS REEL-SPEC-BAT. Aucune autre méthode de sélection n'est essayée pendant le pilote.
- **Tirage au sort par entreprise, dans chaque agence** : la première fois qu'une entreprise entre dans la liste d'une
  agence, elle est tirée au sort, avec une graine publiée avant le départ.
  - **Groupe Proxsis** : l'entreprise apparaît dans « Ma semaine », avec son dossier et son carnet.
  - **Groupe pratique actuelle** : l'entreprise n'apparaît pas, et le consultant prospecte comme d'habitude, y
    compris cette entreprise s'il le veut.
  - **Chaque entreprise garde son groupe** jusqu'à la fin. Le tirage est stratifié par consultant et par rang dans la
    liste (trois premières, sept suivantes).
- **Pourquoi pas par consultant** : avec une dizaine de consultants, l'effectif utile serait trop faible, et chaque
  consultant sert de point de comparaison à lui-même.
- **Analyse en intention de traiter** : on compare les deux groupes tels que tirés, appelés ou non.

## 3. Ce qui est fixé avant le départ

Rien ne commence avant que ce tableau soit rempli et signé par Flexsis et par nous (empreinte du dépôt notée) :

| Point | Proposition | Fixé avec Flexsis |
|---|---|---|
| Indicateur principal | conversations utiles dans les 4 semaines (§ 4) ; le directeur peut en choisir un autre dans la visite (« Une décision ») | … |
| Seuil de réussite | par exemple : au moins 5 points de conversations utiles de plus dans le groupe Proxsis, intervalle à 95 % au-dessus de zéro | … |
| Coût maximal | service et temps des équipes, calculés comme dans « Un seuil » de la visite (`apps/web/src/lib/seuil.ts`) | … |
| Responsables | un référent Flexsis par agence ; un responsable chez nous | … |
| Conditions d'arrêt | voir § 8 | … |

## 4. Les indicateurs

| Indicateur | Définition | Rôle |
|---|---|---|
| **Conversations utiles** | une date fixée, un besoin confirmé ou une prochaine étape acceptée, dans les 4 semaines après la première apparition de l'entreprise (carnet pour le groupe Proxsis, relevé habituel ou CRM pour l'autre) | **principal proposé** |
| Commandes | commande reçue de l'entreprise (CRM de Flexsis), suivie au-delà des six semaines | secondaire (puissance limitée, § 5) |
| Journées supplémentaires facturées | journées facturées sur les commandes des entreprises de chaque groupe ; c'est l'unité du seuil de la visite | secondaire, et décisif pour le coût |
| Temps de préparation | minutes par appel, relevées en mode essai et comparées à la pratique d'avant (`docs/essai/semaine-temoin.md`) | secondaire |
| Usage | les consultants préparent-ils leurs appels plus vite, et reviennent-ils à la liste sans qu'on les pousse (listes ouvertes, décisions notées) | descriptif |
| Équité | audit des candidats proposés (`docs/modeles/`) | contrôle |

## 5. Taille d'échantillon (α = 5 % bilatéral, puissance 80 %, test de deux proportions)

Calcul : n = (z₀,₉₇₅ + z₀,₈)² · (p₁q₁ + p₂q₂) / (p₁ − p₂)² par groupe.

| Taux pratique actuelle → taux Proxsis (hypothèses) | Entreprises par groupe |
|---|---|
| 5 % → 7,5 % (commandes) | 1 468 |
| 10 % → 15 % | 683 |
| 15 % → 25 % (conversations utiles) | 248 |
| 10 % → 20 % | 197 |

Avec 2 agences × 6 semaines × environ 40 entreprises par agence et par semaine (20 par groupe), on obtient environ
240 entreprises par groupe. C'est **suffisant pour un effet net sur les conversations utiles, insuffisant pour les
commandes**. Les commandes et les journées facturées sont donc rapportées avec leur intervalle de confiance, sans
conclusion ferme. **Si le volume est faible, le résultat est annoncé comme exploratoire.** Mesurer les commandes
demanderait environ six fois plus d'entreprises (plus d'agences ou plus de semaines).

## 6. Pré-enregistrement et règles

- Hypothèses, indicateurs, seuils, plan d'analyse et graine sont figés dans le dépôt **avant** le début (empreinte du
  commit).
- La règle de sélection, la liste et les textes ne changent pas pendant le pilote, sauf correction approuvée et notée.
- **Allemand** : la lecture des publications allemandes n'est mesurée avant le pilote que sur les champs structurés
  (entreprise ou particulier, raison sociale, commune, dates, présence de la parcelle et des coordonnées). La lecture
  des **métiers** en allemand sera vérifiée pendant le pilote avec des consultants germanophones de Flexsis. Aucune
  traduction automatique ne sert de référence.
- Les consultants sont informés du dispositif. Les entreprises sont prospectées comme d'habitude (démarchage entre
  entreprises, opposition respectée). Notre équipe ne contacte aucun client.
- **Préalables juridiques** : validation du mémo (`docs/recherche/legal.md`), analyse d'impact pour la partie
  candidats, information des candidats, registre des traitements.
- **Obligations de simap.ch transmises aux utilisateurs** (conditions de l'API, ch. 5 al. 2 et 3, citées dans
  `docs/DONNEES.md`). Les consultants et les agences qui utilisent Proxsis voient des données de simap.ch ; ils
  s'engagent à :
  - garder la mention « Ceci n'est pas une publication officielle. Les données publiées sur la plateforme
    www.simap.ch font foi. » partout où ils reprennent ces données ;
  - ne pas en modifier le contenu ;
  - ne jamais les présenter comme une publication officielle ;
  - les utiliser selon les conditions de simap.ch.

  Cette clause figure dans l'accord de pilote.

## 7. Analyse

- Différence de proportions (groupe Proxsis − groupe pratique actuelle) avec intervalle de confiance à 95 %.
  Régression logistique avec effets fixes du consultant et de la semaine, en analyse de sensibilité.
- Contamination : part des entreprises du groupe pratique actuelle appelées quand même, à partir du CRM.
- **Échanges entre groupes.** Les deux groupes partagent les mêmes consultants et le même vivier d'intérimaires. Un
  intérimaire placé grâce à une entreprise d'un groupe n'est plus disponible pour une entreprise de l'autre. Un écart
  entre groupes peut donc venir de missions déplacées d'un groupe à l'autre, plutôt que de missions en plus.
  - À suivre chaque semaine et par groupe : les demandes reçues, celles pourvues, celles non pourvues faute
    d'intérimaire disponible. Pour chaque mission démarrée, noter le groupe de l'entreprise.
  - À signaler dans l'analyse : les semaines où des demandes sont restées sans réponse faute de personnel, car la
    capacité limitait alors le résultat. Montrer aussi le total des deux groupes à côté de leur écart.
  - Si des demandes du groupe pratique actuelle sont restées sans réponse pendant que le groupe Proxsis en recevait,
    l'écart n'est pas un gain net pour l'agence.
- **Lecture selon l'expérience des consultants.** Les résultats sont aussi présentés par tranche d'ancienneté des
  consultants, fixée avant le départ (par exemple : moins de deux ans, deux ans et plus). C'est une analyse
  secondaire et descriptive.
  - Une même aide peut servir surtout les moins expérimentés. Dans le support client, une étude portant sur 5 172
    agents a trouvé en moyenne 15 % de demandes résolues en plus par heure, surtout chez les agents récents ; les plus
    expérimentés gagnaient peu en vitesse et perdaient un peu en qualité (Brynjolfsson, Li et Raymond, « Generative
    AI at Work », arXiv 2304.11771, résumé vérifié le 07.10.2026).
  - Avec une dizaine de consultants, aucune conclusion ferme par tranche : elle indique où regarder ensuite.
  - Seule la tranche est notée, avec l'accord du consultant ; aucun classement individuel.
- Les résultats sont publiés tels quels, y compris un effet nul ou négatif.

## 8. Règle de décision et conditions d'arrêt (à fixer avec Flexsis avant le départ)

- **Poursuivre** si le seuil de réussite fixé au § 3 est atteint, que le temps de préparation n'augmente pas, et
  qu'aucun problème d'équité ou juridique n'est relevé.
- **Ajuster puis refaire** si l'effet est positif sans atteindre le seuil.
- **Arrêter** si l'effet est nul ou négatif. Arrêter aussi avant la fin si le coût maximal est atteint, si les
  consultants n'utilisent plus la liste deux semaines de suite, ou à la demande de Flexsis, sans justification.

## 9. Calendrier

| Semaine | Étape |
|---|---|
| S0 | Choix des agences, remplissage du § 3, formation (une heure par consultant), relevé de la pratique actuelle (`docs/essai/semaine-temoin.md`), pré-enregistrement |
| S1–S6 | Listes du lundi, carnet des consultants (décisions et suites, sans texte libre) |
| S7–S14 | Suivi des commandes et des journées facturées, sans nouvelles listes du pilote |
| S15 | Analyse, rapport, décision |
