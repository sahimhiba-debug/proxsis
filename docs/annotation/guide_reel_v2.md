# Guide d'annotation — jeu réel v2 (adjudications simap, FR/DE)

**But** : mesurer honnêtement l'extraction (règles et Apertus) sur de **vraies**
publications, annotées par l'équipe, avant toute mesure.

## Le jeu

- **150 adjudications réelles** publiées sur simap.ch du 2026-08-01 au
  2026-09-30 (travaux, services, fournitures) : **75 rédigées en français, 75
  en allemand** (langue de création de la publication).
- Tirage aléatoire reproductible : `proxsis tirage-reel` (graine
  20261005). Cadre, ordre de lecture et raison de chaque rejet :
  `data/annotations/reel_v2/` (`cadre.jsonl`, `tirage_journal.jsonl`,
  `TIRAGE.json`).
- Les textes ont été **filtrés avant tout enregistrement** : personnes de
  contact, téléphones, e-mails et adresses retirés ; un lauréat personne
  physique apparaît comme `[particulier]`, un nom masqué comme `[masqué]`.
- Mention obligatoire (CG API simap.ch) : *Ceci n'est pas une publication
  officielle. Les données publiées sur la plateforme www.simap.ch font foi.*
- **Limite** : faute d'accès autorisé à la FOSC et au Bulletin officiel
  (robots.txt d'amtsblattportal), ce jeu ne contient **ni registre du
  commerce ni permis de construire**. Les scores ne valent que pour les
  adjudications simap.

## Comment annoter

1. Ouvrir `apps/annotation/index.html` dans un navigateur (double-clic ; tout
   reste sur votre poste, rien n'est envoyé).
2. Saisir votre prénom (sert à nommer votre fichier), puis annoter chaque
   publication **sans regarder les annotations des autres** ni aucune sortie
   de modèle.
3. Exporter régulièrement (bouton « Exporter ») : le fichier
   `annotations_<prénom>_<date>.jsonl` se télécharge. Le remettre à Hiba
   (ou le déposer dans `data/annotations/reel_v2/annotations/`).

## Champs

| Champ | Valeur | Règle |
|---|---|---|
| `doc_type` | `adjudication` (pré-rempli) | Corriger seulement si le texte n'est manifestement pas une adjudication. |
| `company_name` | texte ou vide | L'**adjudicataire** (premier lauréat mentionné), avec sa forme juridique, tel qu'écrit. **Vide** si c'est `[particulier]` ou une personne physique. Consortium : le nom du consortium tel qu'écrit. |
| `uid` | `CHE#########` ou vide | Seulement s'il figure dans le texte (rare sur simap). |
| `commune` | texte ou vide | Commune du **lieu d'exécution** ; à défaut, celle de l'adjudicateur. Nom de commune seulement (sans NPA ni canton). |
| `amount_chf` | nombre ou vide | **Prix adjugé** du premier lauréat, en francs (« 1,2 Mio » → 1200000). Vide si non publié. |
| `trades` | cases à cocher | Métiers dont **ce marché fera probablement naître un besoin de personnel** chez le lauréat. Mêmes règles que le guide v1 (CFC/BKP 211 → maçon et manœuvre ; 23 → électricien ; 25 → sanitaire ; 285 → peintre ; routes, conduites → machiniste et manœuvre ; charpente → charpentier). Services intellectuels (études, architecture, informatique) et simples fournitures : **aucun métier**. |
| `private_person` | case | Cochée si le texte mentionne une personne physique (y compris `[particulier]` ou `[masqué]` ; voir les limites en fin de guide). |
| `besoin_temporaire` | oui · non · incertain | **Jugement métier** : ce marché peut-il créer un besoin de personnel **temporaire** dans les secteurs de Flexsis (construction, industrie, horlogerie, logistique, pharma) ? Études, informatique, nettoyage de bureaux… → non. |
| `commentaire` | texte libre | Doute, cas limite. **Jamais** de donnée personnelle. |

## Accord et arbitrage (même protocole que le jeu manuel)

Le guide de référence des champs est `docs/annotation/guide_annotation.md`
(à lire avant de commencer). Depuis `python/` :

1. `proxsis repartir-annotation --items ../data/annotations/reel_v2/a_annoter.jsonl --public ../data/annotations/reel_v2/annotation --prive ../data/annotations/reel_v2/prive --annotateurs AA,BB,CC`
   : chacun reçoit sa page ; **20 publications** sont annotées par deux
   personnes, à l'aveugle.
2. `proxsis accord-manuel <exports…> --items … --public … --prive …` :
   accord champ par champ (kappa pour les catégories ; accord exact pour
   les montants, les dates et les noms) et page d'arbitrage des désaccords.
3. Une troisième personne tranche les désaccords sur la page d'arbitrage.
4. `proxsis geler-manuel <exports…> --arbitrage <fichier> --items … --nom reel_v2`
   gèle la référence et inscrit son empreinte dans `data/annotations/FROZEN.md`
   **avant toute mesure**. Les champs sur lesquels les humains ne
   s'accordent pas sont signalés dans la comparaison des modèles.

## Deux limites à garder en tête (audit du 2026-10-05)

- **`[particulier]`** désigne un lauréat dont le nom ressemble à celui d'une
  personne physique (prénom courant, aucune forme juridique) et que le filtre
  a masqué par prudence. Cochez « personne physique mentionnée » dans ce cas.
- **Le texte affiché est un rendu par Proxsis des champs de l'API simap**
  (étiquettes « Adjudicataire : », « Zuschlagsempfänger : »…), pas la page
  officielle. Ces étiquettes facilitent la tâche des règles : les scores sur
  ce jeu surestiment ce qu'on obtiendrait sur un texte libre.
