# Backtest réel — ce que les données publiques permettent de mesurer, et ce qu'elles ne permettent pas

Couloir : évaluation (session Mac). Code : `python/src/proxsis/real_backtest.py`
(tests `tests/test_real_backtest.py`). Résultat : `docs/backtest/reel_t0.json`.

## Trois cibles, de la plus accessible à la plus utile

| Cible | Définition (semaine de référence T, horizon 8 semaines) | Données nécessaires | Mesurable aujourd'hui ? |
|---|---|---|---|
| **T0 — activité publique** | l'entreprise **remporte un nouveau marché public** (adjudication simap publiée dans [T, T + 56 j[) | simap.ch (API autorisée, CG lues) | **oui** |
| T1 — besoin visible | l'entreprise **publie une offre d'emploi** du métier visé (cible B de `cibles.md`) | offres d'emploi par entreprise : Job-Room (**accord écrit du SECO**), x28 ou KOF par entreprise (**contrat**), pages carrières (lecture au cas par cas) | **non** : aucune source d'offres par entreprise n'est autorisée à ce jour ; le KOF Job Tracker public n'est disponible qu'au niveau national |
| **T2 — vérité métier** | l'entreprise **passe une commande à Flexsis** | **historique des commandes de Flexsis** | **non** : voir `docs/affaires/demande-donnees-pilote.md` |

### Pourquoi T0 n'est qu'un indicateur

T0 mesure si le radar retrouve les entreprises **actives sur les marchés
publics**. Une entreprise qui gagne des marchés a plus de travail, mais :

- elle peut le faire avec son personnel fixe ;
- les marchés publics ne sont qu'une partie de l'activité (le privé n'est pas
  publié) ;
- gagner souvent des marchés est très persistant : une méthode qui « bat le
  hasard » sur T0 peut simplement reconnaître les habitués. C'est pour cela
  que T0 est comparé à la **récence** et à la **fréquence**, pas seulement au
  hasard.

**Un bon score T0 ne prouve pas la valeur commerciale ; un mauvais score T0 ne
la réfute pas.** Seul T2 tranche (historique Flexsis, puis pilote randomisé).

## Protocole T0

- **Données** : adjudications simap (`award_tender`, `direct_award`), marchés
  de **construction**, lieu d'exécution en **Suisse romande** (VD, VS, GE, FR,
  NE, JU), publiées du 2024-07-01 (début de la nouvelle plateforme ; pas
  d'historique antérieur dans l'API) au 2026-09-30. Collecte reprenable,
  filtrée avant écriture : `proxsis collecte-simap`.
- **Entreprises** : lauréats personnes morales, rapprochés par nom normalisé
  (forme juridique retirée ; les réponses simap observées le 2026-10-05 ne
  contiennent pas d'IDE de lauréat — non vérifié dans la documentation). Les
  lauréats personnes physiques sont exclus.
- **Vu à la date T** : seules les adjudications publiées avant T servent ;
  seules les entreprises déjà vues avant T peuvent être classées.
- **Semaines évaluées** : du premier lundi après 52 semaines d'historique
  (2025-06-30) au dernier lundi dont l'horizon de 8 semaines est couvert par
  les données (2026-08-03).
- **Méthodes** : hasard (espérance exacte = taux de base), récence (dernier
  marché gagné), fréquence sur 52 semaines, « M0 marchés » (nombre de marchés
  pondéré par l'ancienneté, demi-vie 8 semaines : ce à quoi se réduit le radar
  à règles quand le seul signal est un marché attribué).
- **Mesure** : précision des 20 premières (P@20) chaque semaine ; moyenne et
  intervalle de confiance à 95 % par bootstrap par blocs de **8 semaines**
  (la longueur de l'horizon : deux semaines voisines partagent 7 semaines de
  cible ; audit M6), avec une sensibilité à 12 semaines ; écart
  apparié de M0 contre la meilleure méthode naïve.

## Limites connues avant même de mesurer

- **Canton manquant** : simap n'indique pas toujours le canton du lieu
  d'exécution ; le filtre par canton perd ces marchés (46,6 % des 1 937 adjudications
  d'août–septembre 2026 n'ont pas de canton : `CLAIMS.md` SIMAP-1).
- **Noms** : sans IDE, deux entreprises homonymes sont confondues et une même
  entreprise écrite différemment est comptée deux fois (M4 réduit ce risque
  quand l'IDE est connu).
- **Dernière publication seulement** (audit M7) : la recherche simap ne
  renvoie que la publication la plus récente de chaque projet. Les
  adjudications antérieures d'un projet (lots attribués à des dates
  différentes) sont récupérées par `past-publications` pour les projets qui
  ont au moins 3 publications (`simap.complete_past_awards`). Un projet dont
  la dernière publication n'est pas une adjudication (rectification,
  révocation) peut manquer : biais résiduel, plutôt défavorable aux méthodes
  naïves, non mesuré.
- **Historique court** : 15 mois d'historique utilisable, 58 semaines
  évaluées au plus ; les semaines voisines se recouvrent (horizon 8 semaines),
  d'où le bootstrap par blocs.

## Résultat (RÉEL, mesuré le 2026-10-05)

Données : 1 892 adjudications simap de construction en Suisse romande
(dont 17 récupérées par `past-publications`), 731 entreprises lauréates
(après rafraîchissement des fiches collectées avant la correction B1 : voir
ci-dessous).
L'historique réellement disponible commence fin 2024 (moins de 40
adjudications par mois avant février 2025 : la nouvelle plateforme s'est
remplie progressivement). Semaines évaluées : du 2025-10-06 au 2026-08-03
(**44 semaines**, un an d'historique avant la première) ; en moyenne 554
entreprises classables par semaine.

| Méthode | P@20 moyenne | IC 95 % (blocs de 8 semaines) | IC 95 % (blocs de 12) |
|---|---|---|---|
| Hasard (taux de base) | **16,0 %** | 14,6 – 18,2 % | 14,8 – 18,6 % |
| Récence (dernier marché gagné) | 31,0 % | 28,7 – 37,0 % | 29,0 – 37,7 % |
| **Fréquence sur 52 semaines** | **55,0 %** | 48,4 – 68,5 % | 50,7 – 69,7 % |
| M0 marchés (nombre pondéré par l'ancienneté) | 52,7 % | 47,3 – 62,7 % | 49,1 – 63,5 % |

Écart apparié M0 − fréquence : **−2,3 points** (IC 95 % : −8,9 à +1,4).

### Lecture honnête

- **Gagner un marché public est très persistant** : les 20 entreprises qui
  ont le plus gagné l'année passée en regagnent un dans les 8 semaines dans
  55 % des cas, contre 16 % au hasard.
- **Le radar réduit aux seuls marchés (M0) ne bat pas la simple
  fréquence** : sur cette cible, « appeler les habitués des marchés
  publics » suffit. Ce n'est pas une surprise : T0 mesure l'activité
  publique, pas un besoin nouveau.
- **Cela ne dit rien de la valeur pour Flexsis** : la question utile est
  de savoir si un signal (marché, permis, mutation RC) précède une
  **commande** (T2) — souvent chez des entreprises qui ne sont **pas** des
  habituées. Seul l'historique des commandes de Flexsis permet de le mesurer
  (`docs/affaires/demande-donnees-pilote.md`).
- Limites : canton manquant pour près de la moitié des projets (le filtre
  Suisse romande les perd) ; rapprochement par nom sans IDE ; dernière
  publication seulement, complétée par past-publications (biais résiduel).

Reproduire : `proxsis backtest-reel ../data/reel/simap/adjudications_romandie_construction_2024-07_2026-09.jsonl --first-week 2025-10-06 --last-week 2026-08-03 --data-end 2026-09-30 --k 20`.

## Ce que demande l'historique des commandes de Flexsis

| Question | Pourquoi il faut les données Flexsis |
|---|---|
| Le radar trouve-t-il les entreprises **qui commandent** ? (T2, P@10 par agence) | la commande n'est pas publique |
| Combien de **jours d'avance** entre un marché attribué et une commande, par métier ? | idem ; le monde fictif suppose ce délai |
| Quelle **taille de besoin** (nombre de postes) par type de marché ? | idem |
| Les signaux publics apportent-ils quelque chose **au-delà des clients habituels** ? | il faut savoir qui est déjà client et à quelle fréquence il commande |
| Équité des suggestions de candidats sur de **vrais** profils | candidats réels (après AIPD) |

Demande formelle : `docs/affaires/demande-donnees-pilote.md`.


## Cible « surprise » et modèle combiné (RÉEL, demande de Hiba du 2026-10-05)

La fréquence sur 52 semaines est la méthode à battre. Deux mesures de plus,
mêmes données et mêmes semaines (`docs/backtest/reel_t0_surprise_combine.json`) :

- **Premiers gagnants** : sur les 44 semaines, **34,4 %** des lauréats d'une
  fenêtre de 8 semaines n'avaient jamais gagné de marché avant T (2 053 sur
  5 965, une même entreprise pouvant compter dans plusieurs fenêtres). Aucun
  classement fondé sur l'historique des marchés ne peut les trouver : il faut
  d'autres signaux (inscriptions au registre du commerce, permis de
  construire).
- **Pic** : l'entreprise gagne au moins 2 marchés dans les 8 semaines **et**
  au moins le double de son rythme habituel des 52 semaines passées.
- **Modèle combiné** : régression logistique sur la fréquence (52, 26 et 8
  semaines), la récence, M0, les montants, le nombre d'adjudicateurs
  distincts, l'ancienneté et la tendance ; entraînée sur les semaines de
  mars 2025 à T − 8 semaines (cibles entièrement connues à T), réentraînée
  toutes les 4 semaines.

| Cible | Taux de base | Fréquence 52 sem. | M0 marchés | **Combiné** | Combiné − fréquence (IC 95 %) |
|---|---|---|---|---|---|
| T0 (un marché) | 16,0 % | 55,0 % | 52,7 % | 56,0 % | +1,0 point (−4,5 à +4,4) : **non significatif** |
| **Pic** | 3,5 % | 8,1 % | 12,3 % | **12,8 %** | **+4,8 points (+2,0 à +7,5)** |

**Correction du 2026-10-12** (questionnaire de Hiba du 07.10.2026, B10). Le combiné compte les adjudicateurs ;
ceux-ci ont été remasqués le 06.10.2026 (audit B1), après la mesure du 05.10.2026 (T0 55,9 %, +0,9 point ;
pic 12,7 %, +4,7 points). Rejoué sur l'instantané actuel le 07.10.2026 puis le 12.10.2026 :
valeurs ci-dessus (`docs/backtest/reproductibilite.md`). Les conclusions ne changent pas.

**Lecture.** Sur la cible facile (T0), les habitués suffisent et le modèle
n'ajoute rien de mesurable. Sur la cible qui compte pour un consultant (une
entreprise **sort de son rythme habituel**), le modèle combiné trouve environ
1,6 fois plus de pics que la fréquence ; l'essentiel du gain vient déjà de la
pondération par l'ancienneté (M0 seul : 12,3 %).

**Correction du 2026-10-05.** Une première version de ce tableau (combiné
14,2 % sur le pic, +6,1 points) avait été calculée sur des fiches collectées
avant la correction B1 de l'audit (353 adjudicateurs et 31 lauréats masqués à
tort). Après rafraîchissement de ces 378 fiches, les méthodes simples ne
changent pas ; le modèle combiné baisse (variable « adjudicateurs
distincts » désormais juste). C'est encore un indicateur d'activité
publique (marchés), pas une commande ; la relance avec les permis du BO VS
(deuxième famille de signaux) se fera quand ils seront importés.

Reproduire : `proxsis backtest-reel <fichier> --first-week 2025-10-06 --last-week 2026-08-03 --data-end 2026-09-30 --k 20 --etendu --out ../docs/backtest/reel_t0_surprise_combine.json`.
