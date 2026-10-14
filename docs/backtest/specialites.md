# Backtest réel par spécialité d'agence : classement et détecteur de surprises (livrable 2.7)

Données **RÉELLES** : 2 508 adjudications de travaux simap (Suisse romande et adjudicateurs
valaisans, juillet 2024 à septembre 2026). *Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi.*

Commandes : `proxsis backtest-specialites` → `docs/backtest/specialites_v1.json` (bootstrap par blocs de
8 semaines, 2 000 tirages, graine 0) ; ce document : `proxsis docs-semaine1`. Mesuré le 2026-10-06.

## Protocole

- Chaque lundi T de 2025-07-07 à 2026-08-03 (**57 semaines**), on classe les
  entreprises **valaisannes à la date T** : canton le plus fréquent de leurs lots publiés **avant T** (même
  définition que la liste d'appels ; audit m1). Seul ce qui était publié avant T est utilisé.
- On regarde les **10 premières** (P@10) sur deux cibles : **T0** (au moins un nouveau marché de la spécialité dans les
  8 semaines) et **pic** (au moins deux marchés dans les 8 semaines et le double du rythme habituel).
- Classements : hasard (espérance exacte = taux de base), récence, **fréquence sur 52 semaines**, M0, **modèle
  combiné** (régression logistique, apprise sur les semaines dont l'issue était connue avant T).
- Règle fixée **avant** la mesure : le combiné n'est retenu que si la borne basse de l'IC 95 % de (combiné −
  fréquence) sur T0 est positive ; sinon, fréquence puis récence.

## Résultats sur T0

| Spécialité | Entreprises classées (moyenne) | Hasard | Récence | Fréquence 52 sem. (IC 95 %) | Combiné | Combiné − fréquence (IC 95 %, points) | Ordre retenu |
|---|---|---|---|---|---|---|---|
| Bâtiment | 146,9 | 20,7 % | 35,8 % | **66,8 %** (64,0 à 70,4) | 66,8 % | +0,0 (−2,6 à +2,5) | frequence |
| Électricité | 12,3 | 18,3 % | 20,0 % | **19,6 %** (14,4 à 27,4) | 19,8 % | +0,2 (−1,1 à +1,6) | frequence |
| Technique du bâtiment | 25,5 | 13,9 % | 19,6 % | **22,8 %** (16,5 à 31,8) | 20,7 % | −2,1 (−4,9 à +0,5) | frequence |

## Résultats sur « pic »

| Spécialité | Hasard | Fréquence | M0 | Combiné | Combiné − fréquence (IC 95 %, points) |
|---|---|---|---|---|---|
| Bâtiment | 4,8 % | 12,5 % | 11,4 % | 14,6 % | +2,1 (−4,4 à +7,9) |
| Électricité | 4,1 % | 4,7 % | 4,7 % | 4,6 % | −0,2 (−0,5 à +0,0) |
| Technique du bâtiment | 3,2 % | 6,0 % | 3,5 % | 3,3 % | −2,6 (−5,1 à −0,5) |

## Détecteur de surprises, là où l'appli le montre : hors des 10 premières (audit M2)

Taux de réussite sur T0 des entreprises signalées **hors du top 10 par fréquence**, et des **3 surprises retenues**
chaque semaine (signalées hors top 10, triées par le score « pic »). Les signalements ne sont pas indépendants
(une entreprise peut l'être plusieurs semaines de suite) : taux descriptifs.

| Spécialité | « Activité qui bondit » hors top 10 | Réussite T0 | « Nouveau venu » hors top 10 | Réussite T0 | Base hors top 10 | Surprises retenues | Réussite T0 |
|---|---|---|---|---|---|---|---|
| Bâtiment | 298 | 38,3 % | 627 | 9,9 % | 17,3 % | 171 | 42,1 % |
| Électricité | 0 | — | 0 | — | 19,3 % | 0 | — |
| Technique du bâtiment | 0 | — | 120 | 14,2 % | 7,9 % | 97 | 11,3 % |

## Ce qu'on en conclut (honnêtement)

1. **Bâtiment** : les dix entreprises valaisannes les plus fréquentes gagnent un nouveau marché dans les 8 semaines
   dans **66,8 %** des cas, contre 20,7 % au hasard :
   un fort indicateur d'**activité**. Le combiné ne fait pas mieux (+0,0
   point) : la liste reste ordonnée par fréquence puis récence (ADR-0013).
2. **« Activité qui bondit »**, hors des dix premières : **38,3 %** de réussite contre
   17,3 % (2,2 fois la base). Le drapeau mérite sa section « à surveiller ».
3. **« Nouveau venu »** : 9,9 % hors top 10. Il **ne prédit pas** un nouveau marché ; l'appli le dit
   dans la raison même (« indice de prospection »).
4. **Électricité et Technique** : trop peu d'entreprises valaisannes (12,3
   et 25,5 classées en moyenne). En
   Électricité, le top 10 couvre la quasi-totalité de la population : P@10 ≈ taux de base **par construction**
   (audit m2). La liste publique y est un appoint, pas un moteur.
5. **35 % des lauréats** d'une fenêtre de 8 semaines (toutes entreprises de la
   spécialité, Valais ou non, fenêtres glissantes qui se chevauchent) n'avaient jamais gagné de marché de la
   spécialité avant : aucun classement fondé sur l'historique des marchés ne peut les voir venir.

## Ce qui exige l'historique des commandes de Flexsis

Le backtest mesure une **activité publique** (un nouveau marché gagné). Il ne mesure pas la commande de personnel
temporaire, la part du besoin confiée à des temporaires, le délai entre adjudication et commande, ni le taux appel →
rendez-vous → mission. La demande de données est prête : `docs/affaires/demande-donnees-pilote.md`. En attendant,
la première vérité terrain viendra des consultants (`proxsis integrer-validation`).
