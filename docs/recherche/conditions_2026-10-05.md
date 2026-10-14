# Conditions d'utilisation et robots.txt — lus le 2026-10-05

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.
>
> **simap.ch, relu le 07.10.2026** : conditions inchangées pour l'API ; passages exacts, version qui fait foi et conformité dans [docs/DONNEES.md](../DONNEES.md#conditions-de-simapch), archive `data/conditions/2026-10-07/`.

Les fichiers `robots.txt` bruts sont archivés dans
[`data/conditions/2026-10-05/`](../../data/conditions/2026-10-05/). Les
conditions générales ont été lues **une fois, à la main** (navigateur), pas
aspirées. Ce document les résume avec mes mots ; il ne remplace pas le texte
officiel.

Règle appliquée par le code (`proxsis.http.PoliteClient`) : robots.txt selon
la RFC 9309 (la règle la plus précise l'emporte ; 4xx = pas de restriction ;
5xx ou injoignable = tout interdit). **Un chemin interdit par robots.txt n'est
jamais appelé**, même si l'exploitant documente une API à cet endroit : voir
la question ouverte en fin de document.

## Décisions par source

| Source | robots.txt pour le chemin utile | CG lues | Verdict d'accès automatisé |
|---|---|---|---|
| simap.ch, API `/api/publications/…` | **autorisé** (seules des pages de l'interface web sont interdites, ex. `/fr/project-detail`) | **oui** : CG API, version du 30.09.2023 | **Oui**, par l'API uniquement, sans compte |
| amtsblattportal.ch (FOSC, BO VS…), `/api/v1/…` | **interdit** (`Disallow: /`) | **oui** : CG du portail (SECO), PDF `/static/agb_fr.pdf` | **Non pour l'instant** : décision de Hiba demandée |
| Zefix PublicREST | **interdit** (`Disallow: /`) et compte obligatoire | non | **Non** : compte gratuit à demander (zefix@bj.admin.ch), voir § Inscriptions |
| ckan.opendata.swiss, `/api/` | **interdit** (`Disallow: /api/`, `Crawl-Delay: 10`) | non | **Non** pour l'API CKAN ; les fichiers hébergés ailleurs restent possibles |
| data.bl.ch, opendata.fr.ch (Opendatasoft), `/api/` et `/explore/dataset/*/download` | **interdits** | non | **Non pour l'instant** (même question) |
| www.web.statistik.zh.ch | `Disallow: /` sauf `/ogd/daten/ressourcen`, `/datenkatalog` | non | Ressources OGD sous `/ogd/daten/ressourcen` : **oui** ; `/ogd/data/…` (créations Zefix ZH) : **non** |
| daten.statistik.zh.ch | pas de robots.txt (404) | non | **Oui** (jeu OGD Baugesuche, désidentifié) |
| api3.geo.admin.ch (RegBL, géocodage) | autorisé | conditions connues par la recherche du 04.10 (fair use 20 req./min) | **Oui**, ≤ 20 req./min |
| www.pxweb.bfs.admin.ch (OFS STAT-TAB) | pas de robots.txt (404) | non relues | **Oui**, débit faible ; licence par tableau à vérifier |
| tsdb-api.kof.ethz.ch | pas de robots.txt (404) | non | **Oui**, débit faible |
| openholidaysapi.org | pas de robots.txt (404) | licence du dépôt lue le 04.10 | **Oui** |
| date.nager.at, `/api/v…` | **interdit** (`Disallow: /api/v`) | non | **Non** : utiliser OpenHolidays |
| api.job-room.ch | API non interdite (seul `/job-search/` l'est) | — | **Non** : accord écrit du SECO requis (règle du projet) |
| api.publicai.co | signaux de contenu (pas d'interdiction de l'API) | conditions Public AI non lues | Appels d'inférence avec clé ; voir `docs/modeles/apertus.md` |

## simap.ch — points des CG API à respecter (version du 30.09.2023)

- **Accès sans compte** permis pour rechercher et lire les publications (ch. 3 et 6).
- **Usage commercial et transmission à des tiers autorisés** (ch. 4).
- **Ne pas modifier le contenu** ; le présenter séparé de nos commentaires ;
  ajouter la mention : « Ceci n'est pas une publication officielle. Les
  données publiées sur la plateforme www.simap.ch font foi. » (ch. 5).
- Publier les déclarations de qualité et les corrections de l'association ;
  diffusion à des tiers **dès 8 h le jour de publication** (ch. 5).
- Faire endosser ces obligations aux utilisateurs de Proxsis (ch. 5).
- Gratuit à ce jour ; un émolument peut être introduit (ch. 7).
- Les CG générales du site exigent un accord écrit pour reproduire le
  contenu **du site** : on n'utilise donc que l'API, jamais les pages web.

**Conséquences pour le produit**
1. L'appli n'affiche jamais un texte simap retouché comme s'il était la
   publication : elle montre nos champs dérivés (entreprise, montant, CPV,
   date), clairement marqués « analyse Proxsis », avec le lien vers la
   publication officielle et la mention obligatoire.
2. Le filtre de données personnelles masque les noms de personnes dans les
   textes que nous **conservons** (traitement interne : page d'annotation,
   extraction). Ces textes masqués ne sont pas montrés aux clients comme
   publications simap.
3. Pas de diffusion avant 8 h le jour de publication.

## amtsblattportal.ch — points des CG (SECO)

- Usage des données autorisé « à des fins personnelles et commerciales »
  (ch. 3.1 et 3.2) ; « Une API est mise à disposition pour la transmission
  des données de publication » (ch. 3.1 al. 2).
- Obligations : respecter la LPD ; appliquer par analogie les durées d'accès
  de l'art. 11 al. 3 OFOSC aux données personnelles ; citer la source
  (« Portail des feuilles officielles » ou « FOSC ») (ch. 3.3).
- **Contradiction** : le robots.txt du même domaine interdit tout
  (`User-agent: * / Disallow: /`).

## Décision de Hiba (2026-10-05, 18:45 UTC environ)

> **Bulletin officiel du Valais et FOSC : collecte À LA MAIN.** Consulter ces
> portails comme des humains est autorisé ; **aucun script ne doit naviguer
> automatiquement sur ces sites** à notre place. simap.ch continue de passer
> par son API, qui est autorisée.

Mise en œuvre : `proxsis.http.MANUAL_ONLY_HOSTS` (amtsblattportal.ch,
www.amtsblattportal.ch, shab.ch, www.shab.ch, bulletin-officiel.vs.ch) bloque
toute requête, même robots.txt (tests) ; ces domaines sont retirés de la
vérification réseau et du test du catalogue ; le connecteur amtsblatt n'est
plus appelé par `proxsis update`. Kit de collecte manuelle :
`docs/annotation/consigne_collecte_manuelle.md`.

La question ci-dessous reste ouverte pour **data.bl.ch, opendata.fr.ch et
l'API CKAN d'opendata.swiss** (non utilisés à ce jour).

## Question ouverte (historique)

> Les CG d'amtsblattportal (SECO) offrent explicitement une API pour la
> réutilisation commerciale, mais son robots.txt interdit tout accès
> automatisé. Même situation, moins nette, pour l'API CKAN d'opendata.swiss et
> les portails Opendatasoft (BL, FR). Le code respecte robots.txt à la
> lettre : ces sources ne sont **pas** interrogées. Options :
> 1. rester strict et écrire à l'exploitant (pour amtsblattportal :
>    SECO, Publications DPPU, adresse dans les CG) pour obtenir un accord
>    écrit d'usage de l'API à débit modéré ;
> 2. décider que les CG, qui offrent l'API, priment sur robots.txt pour le
>    seul chemin `/api/`, à débit modéré, et le consigner dans une ADR.
>
> Sans FOSC ni BO VS, le jeu réel ne contient que des publications simap
> (appels d'offres et adjudications) : pas de registre du commerce ni de
> permis de construire.

## Inscriptions nécessaires (non faites, à décider par Hiba)

| Service | Inscription | Pourquoi |
|---|---|---|
| Zefix PublicREST | identifiants gratuits par e-mail à zefix@bj.admin.ch | toute l'API exige Basic Auth |
| simap.ch | **facultative** : compte « développeur » gratuit | être averti des changements d'API et de CG (ch. 6 et 8) |
| OJP (opentransportdata.swiss) | clé gratuite | temps de trajet (M5) |
| Adzuna | clé + accord écrit d'usage commercial | offres d'emploi agrégées |
| Destatis GENESIS | compte | comparaison Allemagne (priorité 3) |
| Job-Room | accord écrit du SECO | offres d'emploi (cible du backtest) |
