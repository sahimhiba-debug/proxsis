# Kit de la semaine témoin : deux consultants de Flexsis, une semaine

Brief « à distance », § 6 et § 14, étape 3. Hiba essaie d'organiser une semaine d'essai avec deux consultants de
Flexsis. Ce kit dit quoi relever, comment, et comment en rendre compte, échecs compris. **Notre équipe ne contacte
aucun client** : ce sont les consultants qui appellent, comme d'habitude.

## 0. Ce que l'essai mesure, et ce qu'il ne mesure pas

- Il mesure : le temps de préparation d'un appel, la suite de chaque appel (dont les « conversations utiles »), et ce
  que les consultants disent de la liste.
- Il ne mesure pas : les commandes à plus long terme, le chiffre d'affaires, ni un effet sur toute l'agence. Une
  semaine et deux consultants donnent un résultat **exploratoire**, annoncé comme tel.
- **Une conversation utile, c'est une date fixée, un besoin confirmé ou une prochaine étape acceptée** (les trois
  dernières suites du carnet : rappel convenu le…, besoin confirmé, prochaine étape acceptée).

## 1. Avant l'essai : la pratique habituelle (fiche, un consultant à la fois, 15 minutes)

À remplir avec chaque consultant, sur sa semaine habituelle, **avant** de lui montrer Proxsis. Pas de nom de client :
seulement des nombres et des choix.

| Question | Réponse |
|---|---|
| Combien d'entreprises appelez-vous en prospection une semaine normale ? | |
| Comment les choisissez-vous ? (clients connus, chantiers vus, annonces, bouche-à-oreille, autre) | |
| Combien de temps pour préparer un appel de prospection, en moyenne (minutes) ? | |
| Sur dix appels de prospection, combien mènent à une conversation utile (date fixée, besoin confirmé, prochaine étape) ? | |
| Où notez-vous la suite de vos appels aujourd'hui ? (logiciel, carnet, rien) | |
| Regardez-vous les marchés publics (simap) ou les demandes de permis ? À quelle fréquence ? | |
| Spécialité et agence (pour comparer à la bonne liste) | |

## 2. Pendant l'essai : la grille (dans l'application, mode essai)

1. Le lundi, sur son téléphone ou son ordinateur, le consultant ouvre « Ma semaine » et active **« Mode essai »**.
2. Pour chaque entreprise qu'il décide d'appeler, il note dans le carnet du dossier :
   - sa décision (À appeler, À vérifier, Revoir le…, Écarter avec un motif) ;
   - son **temps de préparation** en minutes ;
   - après l'appel, la suite en un geste (pas joint, pas de besoin, rappel convenu le…, besoin confirmé, prochaine
     étape acceptée).
3. Rien n'est saisi en texte libre : aucun nom de personne ne peut être écrit.
4. Le vendredi, il touche **« Exporter l'essai »** : un fichier (`proxsis-essai-<code>-<lundi>.json`) avec les
   identifiants d'entreprises et ses choix, sans nom. Il nous le transmet par le canal convenu avec Hiba.
   **Ce fichier ne va jamais dans le dépôt ni sur le site** : il reste sur le poste de Hiba, hors de git.

La même grille sur papier, si l'application ne convient pas un jour :

| Rang | Entreprise (rang dans la liste, pas de nom de personne) | Décision | Préparation (min) | Suite | Conversation utile ? |
|---|---|---|---|---|---|
| 1 | | | | | |
| … | | | | | |

## 3. Après l'essai : le compte rendu (modèle)

Copier dans `docs/essai/comptes-rendus/semaine-temoin-<date>.md`, sans nom de personne ni de client, et sans le
fichier exporté lui-même (seulement les totaux).

```
# Semaine témoin du <lundi> au <vendredi>
Consultants : 2 (codes C1, C2) · agence(s) : … · spécialité : …
Pratique habituelle (avant) : C1 … appels / semaine, … min de préparation, … conversations utiles sur 10 ; C2 …

## Ce qui a été fait
- Entreprises de la liste regardées : C1 … / 10, C2 … / 10
- Décisions : à appeler …, à vérifier …, revoir le … …, écartées … (motifs : déjà client …, déjà en contact …,
  pas pertinent …, autre …)
- Appels passés : …   Temps de préparation médian : … min (avant : … min)
- Suites : pas joint …, pas de besoin …, rappel convenu …, besoin confirmé …, prochaine étape acceptée …
- Conversations utiles : … sur … appels (avant : … sur 10)

## Ce qui n'a pas marché (obligatoire, même si c'est peu)
- Entreprises jugées sans intérêt, et pourquoi (motif du carnet) : …
- Moments où l'application a gêné ou manqué : …
- Ce que les consultants auraient voulu voir : …

## Ce que cela dit, et ce que cela ne dit pas
- Résultat exploratoire : deux consultants, une semaine ; pas de conclusion sur les commandes ni sur l'agence.
- Comparaison avec la pratique habituelle : …
- Décision proposée pour la suite (poursuivre vers le pilote, ajuster, arrêter) : …
```

## 4. Règles

- Aucun contact client par notre équipe ; aucun enregistrement d'appel ; aucun nom de personne, ni dans le carnet, ni
  dans l'export, ni dans le compte rendu.
- Les exports restent hors du dépôt et du site (le test `python/tests/test_public_data_sweep.py` balaie tout ce que git
  suit ; un export n'a rien à y faire).
- Les résultats réels, s'ils existent, sont datés et ne se mélangent jamais aux exemples illustratifs de la visite
  (brief, 4.2).
