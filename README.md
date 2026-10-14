# Proxsis

https://github.com/user-attachments/assets/0f778b6b-f9fd-4ea1-a147-d537d9beca8d

<p align="center"><b>The presentation in English</b> · 3 min 33</p>

https://github.com/user-attachments/assets/101c6ba2-2f92-4e98-bbf3-996130958f95

<p align="center"><b>La présentation en français</b> · 3 min 22<br>
<sub>Voix de synthèse : ElevenLabs. Musique, images et mascotte Iris : générées avec Runway.</sub></p>

[![CI](https://github.com/sahimhiba-debug/proxsis/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/sahimhiba-debug/proxsis/actions/workflows/ci.yml)
[![Démo en ligne](https://img.shields.io/badge/d%C3%A9mo-proxsis.vercel.app-df5a17)](https://proxsis.vercel.app/)
![Langues](https://img.shields.io/badge/langues-fran%C3%A7ais%20%C2%B7%20English%20%C2%B7%20Deutsch-4d4b47)

**La prochaine entreprise à appeler.** · *The next company to call.* · *Das nächste Unternehmen, das Sie anrufen.*

Prototype · concept non officiel. Flexsis n'est ni cliente ni partenaire de Proxsis.

Proxsis prépare le lundi matin d'un consultant d'une agence de travail temporaire en Valais : la liste des entreprises à
appeler cette semaine, chacune avec un fait publié et vérifiable (un marché public attribué sur simap.ch, une demande
d'autorisation de construire du Bulletin officiel), la phrase à dire au téléphone et ce qui reste à vérifier. Le
consultant décide : il garde, reporte ou écarte. Les entreprises et les marchés sont réels ; les consultants, les
intérimaires et les chiffres d'agence de la démonstration sont fictifs et marqués comme tels.

> **In English.** Proxsis prepares a temp-agency consultant's Monday in Valais, Switzerland: the companies to call this
> week, each with a published, verifiable fact (a public contract awarded on simap.ch, a building permit application in
> the cantonal gazette), what to say on the phone and what remains to be checked. The consultant decides. Unofficial
> prototype; the interface is in French and German, the video presentation in English and French.
>
> **Auf Deutsch.** Proxsis bereitet den Montag einer Beraterin oder eines Beraters eines Temporärbüros im Wallis vor:
> die Unternehmen, die diese Woche anzurufen sind, jedes mit einer veröffentlichten, überprüfbaren Tatsache (ein auf
> simap.ch vergebener öffentlicher Auftrag, ein Baugesuch im Amtsblatt des Kantons Wallis), mit dem, was am Telefon zu
> sagen ist, und dem, was noch zu prüfen ist. Die Beraterin oder der Berater entscheidet. Prototyp · inoffizielles
> Konzept; die Oberfläche ist auf Französisch und Deutsch, die Videopräsentation auf Englisch und Französisch.

## Essayer

<img src="docs/qr-proxsis.svg" alt="QR code de proxsis.vercel.app" width="160" align="right">

**[proxsis.vercel.app](https://proxsis.vercel.app/)** : en français et en allemand, sur téléphone et sur ordinateur. La
racine ouvre la langue du navigateur ; `/fr/presentation/` est la visite guidée, `/fr/semaine/M1/` l'outil du consultant
(`/de/…` en allemand). Le site peut s'ajouter à l'écran d'accueil du téléphone.

<br clear="right">

## Lancer en local

Versions exactes, celles que la CI vérifie : **Node.js 22** (`apps/web/.nvmrc`), **[uv](https://docs.astral.sh/uv/)**
qui installe lui-même **Python 3.12.13** et les paquets exacts du verrou (`python/uv.lock`) ; sur macOS, `brew install
libomp` pour LightGBM ; PostgreSQL pour les tests de la base (sans lui : `make py-check web-check`).

```bash
make install   # moteur Python (python/.venv) et application web (npm ci)
make dev       # l'application sur http://localhost:3000
```

## Architecture

Deux parties qui ne se parlent que par des fichiers. Le moteur Python lit les sources officielles, filtre les données
personnelles **avant** toute écriture, mesure et exporte. L'application Next.js lit ces fichiers, figés à la
construction, et ne fait aucun appel extérieur. Détails : [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

| Dossier | Contenu |
|---|---|
| `apps/web/` | l'application (Next.js, React, Tailwind) : l'outil du consultant, la visite guidée, « Sources et mesures » |
| `apps/annotation/` | la page d'annotation des publications, générée par `proxsis page-annotation` |
| `python/` | le moteur `proxsis` : sources, filtre des données personnelles, modèles, backtests, exports |
| `data/` | données publiques suivies (catalogue des sources, conditions, terrain, annotations) et monde fictif |
| `supabase/` | la table des retours d'appel, prête pour le pilote (aucune page ne l'appelle aujourd'hui) |
| `scripts/` | contrôle quotidien de la production, registre des mesures, sécurité, images de la mascotte, captures, copie hors ligne |
| `docs/` | documentation du produit ([index](docs/README.md)) |

## Tests

| Commande | Ce qu'elle vérifie |
|---|---|
| `make check` | ruff, mypy strict et pytest ; lint, typage, tests unitaires et construction du web ; migrations et droits de la base |
| `cd apps/web && npm run e2e:prepare && npx playwright test` | la démonstration dans Chrome, en ligne et hors ligne, en français et en allemand : accessibilité, mentions obligatoires, aucune requête hors du site, téléphone |
| `cd apps/web && npm run build:static && npm run moteurs` | Chrome, WebKit (Safari, iPhone, iPad) et Firefox aux tailles des appareils, aucun texte coupé (`MOTEURS=chrome` si WebKit et Firefox ne sont pas installés) |
| `scripts/securite/audit.sh` | failles connues des dépendances, secrets (fichiers et historique), licences ; à lancer à la main |

La CI (`.github/workflows/ci.yml`) lance les trois premières, en cinq jobs (python, web, e2e, moteurs, base), à chaque
push sur `main` et à chaque pull request. Ce que couvre chaque suite : [docs/TESTS.md](docs/TESTS.md).

## Données et règles

- **Sources** : publications officielles seulement (simap.ch, Bulletin officiel du Valais), lues selon leurs conditions
  d'utilisation et leur `robots.txt`, avec leur mention obligatoire ; ni portails d'emploi privés, ni réseaux sociaux.
  Les accès demandés (SECO, Zefix, Job-Room, registre des bâtiments) sont dans [docs/demandes/](docs/demandes/).
- **Données personnelles** : Proxsis cible des entreprises, jamais des particuliers. Le filtre `proxsis.pii` écarte
  les rubriques sur les personnes et masque les noms de particuliers avant toute écriture ; un test balaie chaque
  fichier JSON et chaque page HTML du dépôt. L'outil propose, le consultant décide, et chaque proposition montre sa logique.
- **Fictif** : tout ce qui est client, candidat, mission ou commande est fictif, marqué `fictif: true` et signalé à
  l'écran. Aucune donnée de Flexsis n'est utilisée.

Détails : [docs/DONNEES.md](docs/DONNEES.md).

## Mesures

Chaque chiffre affiché renvoie à une ligne de [CLAIMS.md](CLAIMS.md), avec la commande qui le refait et sa limite. La
mesure principale : sur 57 lundis passés, dans les huit semaines, 66,8 % des entreprises de la liste ont remporté un
nouveau marché public, contre 20,7 % prises au hasard (`REEL-SPEC-BAT`). Un marché remporté n'est pas une commande.
L'application les montre sur la page « Sources et mesures ».

## Feuille de route

Aujourd'hui, un prototype en ligne ; ensuite, cinq étapes sans aucune durée, chacune ouverte seulement par des
résultats mesurés et l'accord de Flexsis : [docs/FEUILLE-DE-ROUTE.md](docs/FEUILLE-DE-ROUTE.md) (aussi sur le site :
`/fr/presentation/feuille-de-route/`).

## Production

Le site est publié par Vercel (`apps/web`, branche `main`) ; chaque pull request a sa prévisualisation. Mise en place
et passage d'un projet Vercel existant sur ce dépôt : [docs/deploiement_vercel_supabase.md](docs/deploiement_vercel_supabase.md).

Trois tâches planifiées, **à l'arrêt tant que leur variable de dépôt ne vaut pas `actif`** (*Settings → Secrets and
variables → Actions → Variables*) :

| Workflow | Ce qu'il fait | Variable |
|---|---|---|
| `chaque-matin-en-direct.yml` | lit simap chaque jour ouvrable et ne publie que si tous les tests passent | `CHAQUE_MATIN_EN_DIRECT` |
| `mise-a-jour-quotidienne.yml` | met à jour les sources publiques du Valais (tables filtrées seulement) | `MISE_A_JOUR_QUOTIDIENNE` |
| `production-quotidienne.yml` | contrôle chaque jour les adresses publiques (`scripts/production/controle.mjs`) | `CONTROLE_PRODUCTION` |

## Contribuer

Installation, règles du projet (test rouge d'abord, chaque chiffre dans `CLAIMS.md`, provenance des données, français
et allemand) et style des commits : [CONTRIBUTING.md](CONTRIBUTING.md). Signaler une faille : [SECURITY.md](SECURITY.md). Code de conduite :
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Journal des changements : [CHANGELOG.md](CHANGELOG.md).

## Licence et attributions

Tous droits réservés : aucune licence ouverte n'est accordée pour l'instant. Les données, polices et images de tiers
gardent leur licence et leur mention : [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) (dont « Source : simap.ch »,
« © swisstopo » et le Bulletin officiel du Valais).

## Origine

Né du défi « anticiper les besoins en personnel » posé par Flexsis au Hack VS 2026. Réalisation indépendante : Flexsis
n'a ni commandé ni approuvé ce prototype.
