# Journal des changements

Les changements visibles et les garanties ajoutées, par étape. Le détail de chaque changement est dans son message de
commit ; les décisions sont dans `docs/adr/` et dans les notes de travail (non publiées).

## 0.1.0 — Dépôt `proxsis` (14.10.2026)

- **Nouveau dépôt, historique neuf** : le contenu de la version en ligne au 14.10.2026, sans l'historique de travail.
  Les notes de travail (briefs, relectures, audits d'étape, captures de revue) ne sont pas publiées.
- **Un seul nom, Proxsis** : le moteur Python devient le paquet `proxsis` (commande `proxsis`, variables
  `PROXSIS_*`, User-Agent `Proxsis/0.1`, trousseau macOS `proxsis-publicai`) ; les clés de préférences du navigateur
  passent à `proxsis.*`.
- **Rangement** : `docs/identite-flexsis/` devient `docs/identite/` ; les noms de deux personnes du groupe Interiman
  retirés de `docs/recherche/contexte.md` ; les passages sur le dépôt d'une autre équipe du hackathon retirés, et
  les informations qui n'avaient que lui pour source marquées « non vérifié » ; les consignes pour agents de code
  (`CLAUDE.md`, `AGENTS.md`) hors du dépôt, leurs règles reprises dans `CONTRIBUTING.md`.
- **Les présentations vidéo en tête du README** : l'anglaise (3 min 33), puis la française (3 min 22), lues dans la
  page ; copies de 9,3 Mo en 960 × 540 des originaux 1080p, sans coupe.
- **Dépôt soigné** : README (badges, résumés en anglais et en allemand, contribution, licence, origine), `CONTRIBUTING.md`,
  `SECURITY.md`, `CODE_OF_CONDUCT.md`, `THIRD_PARTY_NOTICES.md`, modèles d'issue et de pull request, `CODEOWNERS`,
  Dependabot, `.editorconfig`, `.gitattributes`.
- **CI** : droits en lecture seule par défaut, exécutions dépassées annulées, actions épinglées par empreinte, durée
  limitée par job ; les trois tâches planifiées restent à l'arrêt tant que leur variable de dépôt ne vaut pas `actif`.

## Nouvelle version — branche `design/nouvelle-version` (07 au 14.10.2026)

- **La visite guidée** remplace l'ancienne présentation par étapes ; « Chaque matin » et la carte des sources ; les
  quatre demandes d'accès ; la mascotte Iris.
- **La feuille de route** (`docs/FEUILLE-DE-ROUTE.md`, `/[lang]/presentation/feuille-de-route/`), sans aucune durée,
  reliée à la fin de la visite et à « Pour votre direction » ; allemand à relire.
- **Rangement** : les notes de travail rangées à part, hors du dépôt public ;
  retrait du code mort (ancienne présentation par étapes, retours d'appel non branchés, son de l'eau jamais joué, scripts
  de la vidéo et de la revue) et de quatre dépendances Python inutilisées ; plus aucun chemin vers un poste de travail dans les fichiers (l'historique Git en garde).

## Non publié — branche `design/futurisme-suisse` (06 et 07.10.2026)

Mission « finir, auditer, blinder ». La production (dépôt de travail, `09aad3a`) n'a pas
bougé : elle attend l'accord de Hiba.

### Produit (phase 1)

- **Proxsis** remplace Proxsis partout (application, présentation, icônes, exports) ; signature « La prochaine
  entreprise à appeler. » ; mention « Prototype · concept non officiel » sur chaque écran.
- **Application** entièrement dans le cadre « futurisme suisse » : Ma semaine (avec « Fins de mission à replacer » et
  « Cette semaine, en direct de simap »), dossier d'entreprise, Préparer l'appel, Candidats, Carte (contours communaux
  embarqués, sans tuiles), Fin de mission, Conformité, Agence, Retour sur investissement, Sources et mesures.
- **Présentation « Votre prochain lundi »** : sept actes, 24 étapes, trois histoires datées (acte 4), calculateur et
  pilote (actes 5 et 6), feuille « Votre point de départ » et sa page imprimable A4 (acte 7) ; démo au téléphone
  pilotée (l'application réelle dans un téléphone) ; notes du présentateur.
- Deux passes de critique de design (notes de travail, non publiées), chaque constat
  corrigé ou reporté avec sa raison.

### Audit et nettoyage (phase 2)

- Code mort retiré (boîte à outils shadcn inutilisée, ancien rendu de la présentation, ancien cadre, thème CSS,
  images du gabarit) ; zéro import circulaire ; `cli.py` (1 277 lignes) découpé en `proxsis/commands/` ; filtre des
  données personnelles du Bulletin officiel isolé dans `gazette_filter.py`.
- Typage strict : mypy `--strict` sur tout le moteur ; plus de double cast qui cachait des écarts de type ; toutes les
  données lues par les écrans validées par des schémas (zod), y compris la section réécrite chaque lundi.
- Textes : chaque texte d'interface existe en français et en allemand, dans les fichiers de traduction.
- Erreurs : le stockage local abîmé (séance, retours d'appel, rôle) est relu champ par champ sans planter.
- Accessibilité : 0 violation axe, tous niveaux, sur toutes les pages et les 24 étapes, FR et DE, téléphone et
  ordinateur ; démo au téléphone utilisable au clavier ; l'acte 3 ne passe plus sous la navigation au téléphone.
- Tests des règles du projet : mentions obligatoires, aucune donnée de particulier dans ce que le dépôt publie, aucune
  requête hors du site (`docs/TESTS.md`).
- Sécurité : en-têtes du site servi (politique de contenu), audit reproductible des dépendances, des secrets et des
  licences (`scripts/securite/audit.sh`).

### Blindage (phase 3)

- Versions exactes : Node 22, Python 3.12.13, un verrou par langage, installé tel quel partout ; aucune mise à jour
  automatique (ADR-0014).
- Rien ne dépend de l'horloge ni du réseau à l'exécution ; polices servies par le site ; 60 captures identiques à J,
  J+2, J+30 et J+90 (ADR-0015).
- CI : tests de bout en bout à chaque push ; contrôle quotidien des adresses de production (actif après la fusion).
- Copie hors ligne versionnée pour clé USB (`scripts/copie-hors-ligne.sh`).

### Documentation (phases 4 et 5)

- README (installer, lancer, tester, durées mesurées), `docs/ARCHITECTURE.md`, `docs/DONNEES.md`, `docs/TESTS.md`,
  ADR-0014 et ADR-0015, README de l'application et du moteur.
