# Consigne de collecte manuelle — jeu de test réel (une page)

**But** : réunir 150 vraies publications officielles (100 en français, 50 en
allemand) pour mesurer l'extraction automatique. Vous consultez les portails
**vous-même, comme d'habitude** ; aucun script ne navigue sur ces sites à
notre place (décision du 2026-10-05). Lisez aussi le guide d'annotation
(`docs/annotation/guide_annotation.md`).

## Quoi chercher

| Source | Où | Rubrique | Langues |
|---|---|---|---|
| **Bulletin officiel du Valais** | bulletin-officiel.vs.ch (portail amtsblattportal.ch) | **Demandes d'autorisation de construire** (BA-VS05) | français (Valais romand) et allemand (Haut-Valais) |
| **Feuille officielle suisse du commerce (FOSC)** | amtsblattportal.ch, rubrique Registre du commerce | **Nouvelles inscriptions** (HR01) et **mutations** (HR02) | français (cantons romands) et allemand (cantons alémaniques) |

**Période** : publications du **1er août au 30 septembre 2026**.

**On exclut** (passez à la publication suivante ; la page refuse de toute
façon de les enregistrer) : **faillites, poursuites, successions, état
civil**, appels aux créanciers, concordats, et toute autre rubrique.

## Combien, et lesquelles (sans choisir « les intéressantes »)

30 publications par personne. Pour chaque jour attribué, ouvrez la rubrique
filtrée sur ce jour et prenez les **2 premières publications dans l'ordre
affiché** qui sont dans la bonne langue et pas exclues. Un jour trop maigre :
prenez un jour de réserve. Ne sautez jamais une publication parce qu'elle
vous semble « sans intérêt ».

| Personne | Strate | Nombre | Jours (2026) | Réserve |
|---|---|---|---|---|
| Personne 1 | BO VS · français | 30 | 04.08, 07.08, 12.08, 14.08, 19.08, 21.08, 25.08, 27.08, 31.08, 01.09, 08.09, 10.09, 22.09, 24.09, 28.09 | 10.08, 18.08, 17.09 |
| Personne 2 | BO VS · français | 20 | 05.08, 06.08, 20.08, 28.08, 02.09, 03.09, 14.09, 18.09, 21.09, 29.09 | 11.08, 24.08, 15.09 |
| Personne 2 | BO VS · allemand | 10 | 06.08, 04.09, 08.09, 29.09, 30.09 | 04.08, 05.08, 14.09 |
| Personne 3 | BO VS · allemand | 15 | 12.08, 14.08, 21.08, 24.08, 27.08, 01.09, 16.09, 25.09 | 18.08, 11.09, 28.09 |
| Personne 3 | FOSC · allemand | 15 | 03.08, 05.08, 06.08, 11.08, 24.08, 31.08, 08.09, 28.09 | 10.08, 19.08, 20.08 |
| Personne 4 | FOSC · français | 30 | 05.08, 10.08, 14.08, 25.08, 31.08, 04.09, 07.09, 08.09, 09.09, 15.09, 16.09, 21.09, 22.09, 23.09, 29.09 | 12.08, 02.09, 25.09 |
| Personne 5 | FOSC · français | 20 | 03.08, 06.08, 13.08, 17.08, 19.08, 20.08, 24.08, 28.08, 03.09, 11.09 | 11.08, 01.09, 14.09 |
| Personne 5 | FOSC · allemand | 10 | 27.08, 07.09, 11.09, 16.09, 21.09 | 13.08, 14.08, 01.09 |

Totaux : BO VS 50 FR + 25 DE ; FOSC 50 FR + 25 DE. Tirage reproductible :
`proxsis plan-collecte` (graine 20261005).

## Comment enregistrer une publication

1. Une fois : `cd python && . .venv/bin/activate` (installation : `CONTRIBUTING.md`),
   puis `proxsis collecte-manuelle` ; ouvrez `http://127.0.0.1:8766/`.
2. Saisissez vos **initiales**, la source, la rubrique, la langue, la date de
   publication et le **lien** de la publication (copié depuis le portail).
3. Copiez le **texte entier** de la publication et collez-le.
4. « Aperçu filtré » : les noms de particuliers et leurs adresses sont
   remplacés par `[masqué]` ; les entreprises restent. **Vérifiez** : s'il
   reste un nom de particulier, sélectionnez-le dans le texte, « Masquer la
   sélection », refaites l'aperçu.
5. « Enregistrer ». Le filtre est réappliqué **avant** l'écriture.

## Où vont les données

- Le texte filtré reste sur **votre poste**, dans `data/manuel/textes/`
  (**exclu de git**). À la fin, remettez votre fichier
  `data/manuel/textes/<initiales>.jsonl` à Hiba par un canal privé, jamais
  par git ni par e-mail non chiffré.
- Seuls `data/manuel/index/<initiales>.jsonl` (lien, date, langue, source,
  empreinte SHA-256 du texte), les annotations et l'empreinte du jeu gelé
  sont **commités**.
- simap.ch continue de passer par son **API**, qui est autorisée.

## Ensuite

Hiba rassemble les fichiers (`proxsis etat-collecte` pour suivre
l'avancement), répartit l'annotation (**20 publications en double
annotation**, à l'aveugle), calcule l'accord, puis **gèle** le jeu avant
toute mesure.
