# ADR-0012 — M5 : plafonner l'effet de l'expérience (équité selon l'âge)

- Statut : **proposé** — à valider par Hiba, puis par Flexsis et son juriste avant tout pilote. **Tant qu'il n'est pas accepté, le code garde le comportement v1 (15 ans).**
- Date : 2026-10-05 ; **révisé le même jour après l'audit** (notes de travail non publiées, M4 et M5)
- Couloir : évaluation (session Mac)
- Complète : ADR-0008

> **Monde fictif : prouve que le code fonctionne, pas sa performance réelle.**
> Les candidats sont FICTIFS ; leur répartition par âge, expérience et
> disponibilité vient d'hypothèses du générateur. Les chiffres ci-dessous
> disent comment le score réagit, pas ce qui se passerait avec les vrais
> candidats de Flexsis.

## Contexte

L'audit v1 (ADR-0008) donnait un ratio de sélection par classe d'âge de
**0,82**, proche du seuil d'alerte de 0,8 (règle des 4/5, utilisée comme
signal, pas comme test juridique). Deux constats du 2026-10-05 :

1. **Ce 0,82 ne se reproduisait pas** : la graine du tirage des 300 besoins
   n'avait pas été consignée. Un seul tirage ne suffit pas : d'un tirage à
   l'autre, le ratio varie de plusieurs centièmes. L'audit est désormais
   répété sur **20 tirages consignés** (`proxsis rapports-modeles`,
   `docs/modeles/m5_audit_equite_v2.json`).
2. **L'écart d'âge a deux causes**, mesurées sur les candidats éligibles :
   - l'**expérience**, très liée à l'âge (rapport de corrélation η = 0,59),
     pénalise les **18–29 ans** ;
   - la **disponibilité** (date à laquelle le candidat peut commencer)
     pénalise un peu les **55 ans et plus** dans ce tirage de 700 candidats
     fictifs. Ce n'est **pas** voulu par le générateur, qui tire la
     disponibilité indépendamment de l'âge : c'est un **hasard du tirage**
     (95 candidats de 55 ans et plus). Mesure versée au rapport v3 :

| Classe d'âge | Candidats | Jours avant disponibilité (moyenne) | Disponibles sous 14 jours |
|---|---|---|---|
| 18-29 | 233 | 19,0 | 50,2 % |
| 30-44 | 236 | 20,9 | 48,7 % |
| 45-54 | 136 | 21,0 | 45,6 % |
| 55+ | 95 | 21,4 | 45,3 % |


## Mesures, 1re partie : tirages de sélection (graines 0–19, 300 besoins, top-5, candidats FICTIFS)

| Variante | Ratio âge moyen | min – max (20 tirages) | Tirages < 0,8 | Groupe le moins sélectionné (taux moyen) | Ratio genre | Ratio nationalité | Expérience moyenne du top-5 (ans) | Top-5 identique à v1 |
|---|---|---|---|---|---|---|---|---|
| plafond 15 ans (v1) | 0,840 | 0,771 – 0,884 | 2/20 | 18-29 (0,654) | 0,980 | 0,896 | 10,0 | 100 % |
| plafond 10 ans (1re proposition, retirée) | 0,856 | 0,809 – 0,902 | 0/20 | 18-29 (0,664) | 0,975 | 0,894 | 9,8 | 98,7 % |
| **plafond 5 ans (proposé)** | **0,867** | 0,794 – 0,920 | 1/20 | 55+ (0,658) | 0,977 | 0,895 | 9,7 | 97,8 % |
| plafond 3 ans | 0,860 | 0,778 – 0,937 | 3/20 | 55+ (0,644) | 0,980 | 0,903 | 9,7 | 97,3 % |
| plafond 1 an (expérience quasi binaire) | 0,840 | 0,767 – 0,927 | 5/20 | 55+ (0,625) | 0,971 | 0,944 | 9,4 | 95,5 % |
| sans expérience (poids 0) | 0,810 | 0,720 – 0,879 | 7/20 | 55+ (0,612) | 0,944 | 0,939 | 9,2 | 94,9 % |

« Top-5 identique à v1 » : part des 5 candidats proposés qui restent les
mêmes qu'avec v1, sur un tirage séparé de 300 besoins (graine 1000). La
proximité de métier et la distance des candidats proposés ne bougent pas
(0,86 et 19 km environ dans toutes les variantes).

## Mesures, 2e partie : confirmation hors échantillon (graines 100–199)

La première version de cette ADR choisissait 10 ans parce que c'était la
seule variante sans tirage sous 0,8 **sur les 20 tirages qui avaient servi à
choisir**. L'audit a montré que ce critère ne tenait pas sur d'autres
graines. On sépare donc désormais : choisir sur les graines 0–19,
**rapporter** sur 100 autres tirages (`docs/modeles/m5_audit_equite_v3.json`).

| Variante | Ratio âge moyen | min – max | Tirages < 0,8 (IC 95 %) | Groupe le moins sélectionné (taux moyen) |
|---|---|---|---|---|
| plafond 15 ans (v1) | 0,834 | 0,760 – 0,916 | 18 % (12 – 27 %) | 18-29 (0,641) |
| plafond 10 ans | 0,845 | 0,762 – 0,928 | 15 % (9 – 23 %) | 18-29 (0,649) |
| plafond 5 ans | 0,862 | 0,742 – 0,960 | 10 % (6 – 17 %) | 55+ (0,659) |

Intervalle de confiance de la part de tirages sous 0,8 : méthode de Wilson.

## Décision proposée (révisée)

Plafonner l'effet de l'expérience à **5 ans** (paramètre `exp_cap_years=5`
de `CandidateMatcher`) : au-delà de 5 ans, l'expérience n'augmente plus le
score.

- Critère de choix, fixé avant de regarder la confirmation : le **ratio
  moyen** sur les tirages de sélection (plus stable que « aucun tirage sous
  0,8 », qui dépend de quelques tirages). 5 ans a le meilleur ratio moyen
  (0,867), et le reste sur la confirmation (0,862 contre 0,845 pour 10 ans et
  0,834 pour v1).
- Sur la confirmation, la part de tirages sous 0,8 baisse de 18 % (v1) à
  10 %, mais **les intervalles se recouvrent** (12–27 % contre 6–17 %) : le
  gain est probable, pas démontré.
- Changement visible pour le consultant : 97,8 % des suggestions inchangées ;
  expérience moyenne proposée 9,7 ans au lieu de 10,0.
- **Aucun plafond n'élimine le risque** : même à 5 ans, environ 1 tirage sur
  10 reste sous 0,8 dans ce monde fictif.

## Le compromis, honnêtement

- **Le gain est modeste** : +0,028 sur le ratio moyen hors échantillon
  (0,834 → 0,862) ; les intervalles se recouvrent.
- **Supprimer l'expérience aggrave l'équité selon l'âge** (0,810, 7 tirages
  sur 20 sous le seuil) : l'avantage bascule vers d'autres critères qui
  défavorisent les plus âgés (disponibilité). « Ne pas utiliser un attribut »
  ne suffit pas ; il faut mesurer.
- **On ne connaît pas le coût réel** : on ne sait pas si un candidat de 25
  ans d'expérience réussit mieux sa mission qu'un candidat de 10 ans. Seul
  l'historique des missions (pilote, `docs/affaires/demande-donnees-pilote.md`)
  permet de le mesurer.
- **À 5 ans, le groupe le moins sélectionné devient les 55 ans et plus**,
  surtout à cause de la disponibilité (45,3 % disponibles sous 14 jours
  contre 50,2 % pour les 18–29 ans dans ce tirage). La disponibilité est un
  critère légitime (le besoin commence à une date), mais son poids (0,10)
  devra être revu avec les vraies données.
- Le consultant voit toujours les raisons de chaque suggestion et décide
  (nLPD art. 21) ; aucune suggestion n'est automatique.

## Alternatives considérées

- Garder 15 ans (v1) : 18 % des tirages sous 0,8 hors échantillon.
- 10 ans (première version de cette ADR) : 15 % ; choisi sur un critère qui
  ne tenait pas hors échantillon.
- Retirer l'expérience : pire (voir ci-dessus).
- Re-pondérer par groupe d'âge (« quotas ») : écarté ; cela ferait lire l'âge
  par l'appariement, ce que l'ADR-0008 interdit.

## Conséquences

- Relancer l'audit (20 tirages) sur les **vrais** candidats avant tout
  pilote, avec AIPD ; revenir sur ce choix si le ratio réel est sous 0,8 ou
  si l'historique des missions montre que l'expérience au-delà de 10 ans
  prédit nettement la réussite.
- Commande : `proxsis rapports-modeles` (une dizaine de minutes sur un portable) ;
  le rapport v2 (sélection seule) se reproduit à l'identique, le v3 ajoute
  la confirmation et la disponibilité par âge.

## Mesures liées

`CLAIMS.md` : lignes M5-1 à M5-6.
