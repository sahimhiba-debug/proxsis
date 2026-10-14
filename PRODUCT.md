# PRODUCT.md — ce que Proxsis fait, pour qui, et comment on sait que ça marche

<!-- impeccable:product-schema 1 -->

Fiche produit confirmée par Hiba le 06.10.2026 (utilisateurs, position face à Flexsis, promesse). L'identité visuelle
est dans `DESIGN.md`, le glossaire dans `CONTEXT.md`, les chiffres dans `CLAIMS.md`.

## Platform

web

## Users

Deux publics, dans cet ordre :

| Public | Situation | Ce qu'il fait avec Proxsis |
|---|---|---|
| **Consultant** d'une agence Flexsis (Valais) | Le lundi matin, sur son téléphone ou à son poste, avant que le téléphone sonne | Lit sa liste d'appels, ouvre le dossier d'une entreprise, prépare l'appel, choisit les candidats, note la suite de l'appel en un geste. **Il décide ; l'outil explique.** |
| **Directeur d'agences**, non technique | Une rencontre en salle : présentation projetée, menée à la main, sans minuterie | Reconnaît son territoire et ses entreprises, comprend chaque transformation, conteste les propositions, et repart avec une **décision de pilote** qu'il sait expliquer ; il retrouve sa synthèse sur son propre téléphone. |

Chef d'agence et groupe (répartition, tableaux de bord) : plus tard, **hors du périmètre actuel**. Les écrans
`/agence` existent comme prototypes, sans priorité.

## Product Purpose

**Promesse.** Chaque lundi, chaque consultant reçoit **sa liste d'appels classée** : quelle entreprise appeler, pour
quel métier, quand, avec quels candidats, et **pourquoi** (information publiée, datée et sourcée).

**Pourquoi.** Né du défi « anticiper les besoins en personnel » posé par Flexsis au Hack VS 2026 (voir
`docs/recherche/contexte.md`). La question qui porte la rencontre : « Lundi prochain, qui appelez-vous avant que le
téléphone sonne ? »

**Ce que veut dire réussir.**
- Pour la rencontre : le directeur décide un pilote et sait l'expliquer.
- Pour le produit : le pilote (`docs/affaires/pilote.md`) mesure si cette information aide les consultants à préparer
  les bons appels, et à quel coût. Si le gain n'est pas suffisant, c'est une raison claire de s'arrêter.

## Positioning

Proxsis ne promet pas de **prédire** les besoins. Il donne au consultant une **information vérifiable** : marchés
publics adjugés (simap), demandes d'autorisation de construire (Bulletin officiel du Valais). Chaque élément porte sa
source, sa date et la raison pour laquelle il mène à un appel. Son utilité reste **à mesurer pendant le pilote** ; elle
n'est pas annoncée comme acquise.

Le premier test réel n'a pas fait mieux qu'une règle simple (`CLAIMS.md`, ligne REEL-T0). Cette règle simple reste donc
la référence, et ce résultat est dit, pas caché.

**Statut.** Réalisation indépendante, proposée à Flexsis **sans accord ni partenariat**. Flexsis n'est ni client ni
partenaire, et n'a pas approuvé le prototype. L'application porte la mention « Prototype, concept non officiel ».

## Operating Context

- **Le lundi du consultant.** Liste « Ma semaine » → dossier d'entreprise → « Préparer l'appel » (guide et e-mail en
  français ou en allemand) → retour d'appel en un geste (rendez-vous, à rappeler, pas de besoin, mauvais contact, déjà
  servi). Agences Flexsis vérifiées en Valais : Sion, Monthey, Martigny.
- **La rencontre avec le directeur.** `/[lang]/presentation` : « Votre prochain lundi », sept actes, avance à la main
  (flèches), sans film ni minuterie. Elle rejoue un lundi passé (lundi 5 octobre 2026), nommé comme un rejeu. Notes du
  présentateur dans `/[lang]/presentation/notes`. Synthèse retrouvée sur le téléphone du directeur (QR et adresse
  courte), et page A4 imprimée. Les trois synthèses (écran, téléphone, A4) viennent des mêmes décisions.
- **Projection.** Salle de réunion, projecteur : lisibilité de loin, au fond de la salle. Formats vérifiés : 1920 × 1080,
  1280 × 720, téléphone 390 × 844.
- **Hors ligne et en ligne.** La démo se rejoue depuis le cache, réseau coupé. La version en ligne attend les accès
  Vercel et Supabase (tâche H1).
- **Langues.** Français et allemand de Suisse (« ss », jamais « ß »). Allemand : mesure partielle (champs structurés),
  métiers non mesurés.

## Capabilities and Constraints

### Écrans de l'application consultant (`/[lang]/…`)

1. **Ma semaine** : liste d'appels classée (niveau d'alerte, métier, fenêtre de besoin, confiance, raison principale).
2. **Carte** (radar) : entreprises et signaux de la semaine.
3. **Fiche entreprise** : chronologie des signaux avec leurs sources, besoin à confirmer par métier et par période,
   explication du classement.
4. **Préparer l'appel** : guide d'entretien et e-mail FR/DE ; chaque affirmation renvoie à sa source.
5. **Candidats suggérés** : critères stricts et proximité de compétences, raisons affichées ; le consultant choisit
   (**candidats fictifs**).
6. **Retour d'appel** en un geste.
7. Écrans secondaires : agence, mesures, conformité (obligation d'annonce), redéploiement, calculateur.

### Ce que l'outil ne fait pas

- Il ne décide pas à la place du consultant (nLPD art. 21) : chaque proposition affiche sa logique.
- Il cible des entreprises, **jamais des particuliers**. Le filtre `proxsis.pii` est obligatoire à l'ingestion, et
  aucun nom de propriétaire privé n'est stocké.
- Il ne contourne pas l'obligation d'annonce : il la rappelle quand un métier y est **probablement** soumis.
- Il n'aspire ni les portails d'emploi privés, ni les réseaux sociaux, ni les dossiers eConstruction. Les sources
  suspendues (Amtsblattportal, Zefix, RegBL…) ne sont pas reprises tant que leur autorisation documentée manque.
- Il ne présente aucune entreprise réelle comme ayant demandé le personnel d'un scénario inventé.

### Mentions, au niveau de l'information

« Entreprise réelle » · « Information publiée » · « Besoin à confirmer » · « Candidat fictif » / « Mission fictive » /
« Situation illustrative » · « Hypothèse ». Elles s'appliquent à l'élément concerné, jamais en bloc à un dossier réel.

### Comment on mesure

- Backtest hebdomadaire « vu à la date T », sans fuite (`available_at <= T`), comparé au hasard, à la récence et à la
  fréquence ; P@20, rappel, jours d'avance, calibration, couverture par région et par langue, intervalles de confiance.
- Monde **FICTIF** (`proxsis world --seed 42`) : il valide la mécanique, pas la valeur commerciale.
- Premier test **réel** (REEL-T0) : nouveau marché public dans les 8 semaines. Il ne mesure ni les recrutements ni les
  commandes Flexsis.
- Un modèle complexe n'est gardé que s'il bat le simple, et chaque choix a son ADR dans `docs/adr/`.

### Pile technique

- Web : Next.js 16, React 19, TypeScript, Tailwind CSS 4, shadcn/ui, Motion ; Supabase (auth, PostgreSQL + RLS).
- Moteur : paquet Python `proxsis` (connecteurs, schéma, modèles, backtest).
- IA : interface `LLMProvider` ; `FakeLLM` par défaut (tout marche avec lui) ; Apertus (Public AI, compatible OpenAI)
  en option, sans résultat établi sur le lot réel annoté.

## Brand Commitments

- Nom : **Proxsis** (depuis le 07.10.2026 : le produit n'est pas un radar d'alertes, c'est le lundi matin du consultant ; « Proxsis » évoque la proximité et la prochaine entreprise à appeler, et se dit pareil en français, en allemand et en anglais). Signature : « La prochaine entreprise à appeler. » Présentation : **« Votre prochain lundi »**.
- Mention obligatoire de l'application : « Prototype, concept non officiel ».
- Ni le logo ni les photos de Flexsis ne sont repris : l'application est « dans l'esprit de Flexsis », sans copie
  (`DESIGN.md` § 1.6).
- Voix : des mots simples pour un directeur non technique, sans jargon. Vocabulaire contrôlé
  (`apps/web/src/presentation/vocabulary.ts`). Sources toujours citées par leur nom (« simap.ch », « Bulletin officiel
  du Valais », « © swisstopo »).
- Réponse fixée à « Alors pourquoi vous écouter ? », mot pour mot : « Parce que nous pouvons vous montrer le travail que le
  consultant pourrait faire avec ces informations, puis le comparer à sa pratique actuelle. Nous n'avons pas encore
  démontré le gain chez vous. Si le pilote n'en montre pas suffisamment, nous aurons une raison claire de nous arrêter. »

## Evidence on Hand

- `CLAIMS.md` : registre de tous les chiffres publics, chacun relié à une commande reproductible. Premier test réel
  REEL-T0 : 1 892 adjudications, 731 entreprises, 44 semaines ; hasard 16,0 %, récence 31,0 %, fréquence 55,0 %,
  radar 52,7 %.
- Données publiques : adjudications simap (accès officiel), exports manuels autorisés du Bulletin officiel du Valais
  (jeu gelé, `FROZEN.md`), contours des communes (swissBOUNDARIES3D 2026-01, © swisstopo).
- Dix entreprises réelles proposées, **en attente de validation par les consultants**
  (support de validation dans les notes de travail, non publiées). Trois dossiers guidés au plus ; le premier est Société de Travaux Publics,
  Joseph Carron SA (CLAIMS PRES-CARRON-1).
- **Absences à ne jamais combler par de l'invention** : aucune donnée interne de Flexsis (clients, candidats, missions,
  commandes, qui sont donc tous fictifs) ; aucun client, aucun témoignage, aucun gain mesuré ; statut de client Flexsis
  des entreprises réelles inconnu ; aucune annotation humaine terminée ; aucun déploiement public.

## Product Principles

1. **Le consultant décide, l'outil explique.** Chaque proposition montre sa raison et sa source.
2. **Vérifiable avant d'être impressionnant.** Chaque information porte sa source et sa date, et chaque chiffre a sa
   ligne dans `CLAIMS.md`. En cas de doute : « inconnu ».
3. **Des entreprises, jamais des particuliers.**
4. **Le simple d'abord.** La règle simple reste la référence tant qu'un modèle ne la bat pas sans fuite ; l'utilité
   se mesure pendant le pilote, elle ne s'annonce pas.
5. **Le résultat défavorable s'explique.** Un test qui ne montre pas de supériorité est dit en mots simples, avec ce
   que le pilote doit vérifier.

## Accessibility & Inclusion

- Lisibilité de loin, en projection : noms, dates, preuves, statuts et résultats lisibles depuis le fond de la salle.
  Tout texte utile ≥ 4,5:1.
- Version sans mouvement complète (`prefers-reduced-motion`) ; aucune information portée par le seul mouvement.
- Français et allemand complets sur chaque écran (aucun français sur une page allemande).
- Contrôle axe dans les tests de parcours ; navigation au clavier (flèches) dans la présentation.
