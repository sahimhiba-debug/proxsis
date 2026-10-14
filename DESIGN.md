---
name: Proxsis — l'identité Flexsis
description: Depuis le 07.10.2026 (brief « Le design Flexsis, l'écart rattrapé, Apertus branché »), Proxsis porte l'identité visuelle de Flexsis sans son logo — blanc dominant, noir #121212 pour trois moments de décision, un seul orange #E6530F qui ne marque que ce qui compte ; Sora léger pour les énoncés avec un mot fort, Urbanist pour le reste ; étiquettes blanches à fine coque graphite, pastilles arrondies, diagonales orange. La référence est docs/identite/IDENTITE.md. Remplace la direction du 06.10.2026 (graphite, ivoire, cuivre).
colors:
  orange: "#E6530F"
  noir: "#121212"
  blanc: "#FFFFFF"
  gris-texte: "#5C5C5C"
  gris-clair: "#F4F4F4"
  trait: "#E3E3E3"
  trait-controle: "#8A8A8A"
  coque: "#2A2A2A"
  sombre-surface: "#1C1C1C"
  sombre-texte-doux: "rgba(255, 255, 255, 0.72)"
  app-fond: "#121212"
  app-surface: "#171717"
  app-surelevee: "#1C1C1C"
  app-texte: "#FFFFFF"
  app-doux: "#B5B5B5"
typography:
  enonce:
    fontFamily: "Sora"
    fontWeight: 300
    fontSize: "clamp(40px, min(4.2vw, 7.6vh), 84px)"
    letterSpacing: "-0.025em"
  enonce-mot-fort:
    fontFamily: "Sora"
    fontWeight: 600
  narration:
    fontFamily: "Sora"
    fontWeight: 300
    fontSize: "clamp(28px, min(2.6vw, 4.8vh), 52px)"
    lineHeight: 1.14
  texte:
    fontFamily: "Urbanist"
    fontWeight: 500
    fontSize: "clamp(17px, min(1.25vw, 2.3vh), 24px)"
    fontFeature: "tabular-nums"
  etiquette:
    fontFamily: "Urbanist"
    fontWeight: 700
    fontSize: "clamp(14px, min(1.042vw, 1.86vh), 20px)"
  bouton:
    fontFamily: "Urbanist"
    fontWeight: 700
rounded:
  etiquette: "16px"
  petite-etiquette: "10px"
  carte: "12px"
  choix: "14px"
  pastille: "999px"
spacing:
  marge-x: "clamp(16px, 4.2vw, 96px)"
  marge-y: "clamp(12px, 2.6vh, 36px)"
  ecart: "clamp(16px, 2.2vw, 48px)"
components:
  etiquette:
    backgroundColor: "{colors.blanc}"
    textColor: "{colors.noir}"
    rounded: "{rounded.etiquette}"
    border: "3px inset {colors.coque}, épaisseur 3px, ombre 0 16px 32px -14px rgb(0 0 0 / 0.4)"
  petite-etiquette:
    backgroundColor: "{colors.blanc}"
    textColor: "{colors.noir}"
    typography: "{typography.etiquette}"
    rounded: "{rounded.petite-etiquette}"
  carte-choisie:
    border: "6px inset {colors.orange} sous la coque, petite diagonale orange en haut à droite"
  pastille-decision:
    backgroundColor: "{colors.blanc}"
    textColor: "{colors.noir}"
    typography: "{typography.bouton}"
    rounded: "{rounded.pastille}"
  pastille-decision-choisie:
    backgroundColor: "{colors.orange}"
    textColor: "{colors.blanc}"
    note: "blanc sur orange seulement en gras de 19 px et plus"
  statut:
    backgroundColor: "{colors.gris-clair}"
    textColor: "{colors.noir}"
    rounded: "{rounded.pastille}"
    note: "statut marqué : bord orange et diagonale, texte noir"
  bouton:
    backgroundColor: "{colors.noir}"
    textColor: "{colors.blanc}"
    typography: "{typography.bouton}"
    rounded: "{rounded.pastille}"
---

# DESIGN.md — identités visuelles de Proxsis

## Direction en vigueur : l'identité Flexsis (07.10.2026)

> **Historique** : cette direction **remplace la direction du 06.10.2026** (« Votre prochain lundi » : graphite, ivoire,
> un seul accent cuivre, papier ivoire en serif, italiques serif ; § 3) et, pour l'application, les couleurs et la police
> de « futurisme suisse » (§ 4 bis). Décision de Hiba : brief du 07.10.2026 (notes de travail, non publiées), § 0 et § 2.
> Les sections plus bas restent pour l'historique ; en cas de contradiction, cette section l'emporte.

**La référence est `docs/identite/IDENTITE.md`** (couleurs, contrastes, polices, logo, mascotte, étiquettes,
scènes, raccords, téléphone), avec sa référence vivante `docs/identite/prototype/proxsis-identite.html` et les
images des notes de travail (non publiées). En une phrase : blanc dominant, noir `#121212` pour les moments de décision, et
un seul orange `#E6530F` qui ne marque que ce qui compte.

**Couleurs** (jetons dans `apps/web/src/presentation/direction.css`, nommés d'après leur rôle) : orange `#E6530F`
(`--orange` : sélection, décision, date de rappel, prochaine action, grande diagonale, raccords) ; noir `#121212`
(`--texte`, et le fond des trois scènes sombres) ; blanc `#FFFFFF` (`--fond`, la face des étiquettes) ; gris texte
`#5C5C5C` (`--doux`, 6,7:1) ; gris clair `#F4F4F4` (`--surface`) ; trait `#E3E3E3` (`--trait`) ; bord d'un contrôle
`#8A8A8A` (`--trait-fort`, 3,4:1) ; coque des étiquettes `#2A2A2A` (`--coque`).

**L'orange en texte** : seulement à partir de 24 px, ou en gras à partir de 19 px (3,7:1 sur blanc). Plus petit, le
texte reste noir ou gris foncé et l'orange devient **la petite diagonale** à côté (le point du « i » du logo,
`clip-path: polygon(0 100%, 82% 100%, 100% 0, 18% 0)`, jeton `--diag`). Blanc sur orange : seulement en gras de 19 px et
plus (les pastilles de décision). Dans les scènes sombres, l'orange en texte est libre (5,1:1 sur noir).

**Polices**, hébergées par le site, chacune avec sa licence OFL (`apps/web/public/fonts/`) : **Sora** 300 et 600 pour les
énoncés (un poids léger, un mot fort en 600, souvent orange : « Vous **décidez.** ») ; **Urbanist** (fichier variable)
pour les informations, étiquettes, boutons et mentions, de 500 à 700, chiffres à chasse fixe. Plus de Nunito Sans, de
Newsreader ni de JetBrains Mono, plus d'italique. Le premier écran reste sous 1 Mo (`e2e/accueil.spec.ts`).

**Logo** : le mot « Proxsis » dessiné dans la famille d'Urbanist, le point du « i » en diagonale orange
(`apps/web/src/lib/Logo.tsx`, tracés de `docs/identite/logo/`) ; lettres en `currentColor` (noir sur clair, blanc
sur sombre), point toujours orange. Animation d'environ 1 s sur le premier écran (les lettres montent depuis la ligne
de base, 35 ms d'écart, 0,42 s chacune ; la diagonale se pose avec un léger rebond) ; rien ne bouge sans mouvement. Le
logo de Flexsis n'apparaît nulle part. Icône et favicon : deux propositions à Hiba, aucune imposée (§ « Icônes » des
notes de travail, non publiées).

**Scènes et passages** (`apps/web/src/visite/passage.ts`, `identite.css`) : fond blanc dominant, une grande diagonale
orange qui entre par un bord, dans la marge, jamais sous un texte. Noir `#121212` pour **trois moments seulement** :
le directeur décide dans le carnet, le lundi suivant, la grande question « Et la liste, vaut-elle quelque chose ? »
(`data-scene="sombre"`). Pour y entrer en avançant, **une bande orange diagonale** traverse l'image en 0,9 s et la
couvre entièrement à l'instant où l'étape change (trois fois au plus sur un parcours). Rien ne bouge pendant la lecture.
Sans mouvement, un fondu court des couleurs remplace la bande.

**Étiquettes** (`identite.css`) : face blanche, fine coque graphite, angles arrondis, petite épaisseur visible, ombre
légère ; le texte sur la face opaque. Trois formats : la **petite étiquette** (une date, une source, un statut :
« Publication · 12.08.2026 », « Revoir le 12.10.2026 »), qui peut s'accrocher en onglet au bord d'une carte ; la **carte
d'entreprise**, le nom d'abord, puis la commune, le statut en pastille (à droite sur ordinateur, dessous au téléphone) ;
la **carte de question**, une seule question et « Fondée sur le seul fait publié. ». La publication n'est plus sur papier
ivoire : c'est une étiquette blanche à coque graphite.

**Décisions** : des boutons arrondis ; la décision choisie se remplit d'orange ; la carte retenue reçoit un bord orange
et la petite diagonale ; le lundi suivant, elle revient avec la même marque (« Revient : À appeler »), et le rappel garde
sa date. Au téléphone, les cartes s'empilent en pleine largeur.

**Application** (`apps/web/src/futur/futur.css`) : même orange et Urbanist, mise en page inchangée ; elle reste sombre,
sur les noirs de l'identité (`#121212`, `#171717`, `#1C1C1C` : l'orange y garde 4,6 à 5,0:1) ; texte noir sur orange
(5,0:1, ses boutons sont petits) ; documents sur étiquettes blanches à coque graphite.

**Documents** : « Proxsis en une page » et les synthèses prennent la même identité ; les QR restent noirs sur blanc.

**Mascotte** (branche `design/mascotte-visite`) : coque noire satinée, face blanche, détails orange qui ne tournent jamais
au cuivre, au rose ou au jaune ; mêmes étiquettes et fonds que le prototype ; elle se pose pendant la lecture et ne
choisit jamais.


> Tâche D1 (`design-recherche`), 06.10.2026, puis **mise en conformité du 06.10.2026** (tâche E3, chef d'orchestre),
> après le retour de Hiba : « Le design n'est pas celui que j'ai demandé. » L'identité A (§ 3) suit désormais la
> **direction créative** de Hiba et sa **maquette** (notes de travail non publiées, mesures relevées dans le navigateur) ;
> l'écart point par point est dans les notes de travail (non publiées). Statut : identité A appliquée à **trois écrans**
> (ouverture « Lundi », carte du Valais, décision du directeur), **en attente de l'accord de Hiba** avant les autres
> écrans (E4). L'identité B (§ 4) n'a pas changé. L'en-tête YAML suit le format DESIGN.md lu par Impeccable.

Deux identités, une seule grammaire :

| | A. Présentation « Votre prochain lundi » | B. Application consultant |
|---|---|---|
| Où | `/[lang]/presentation`, projection et synthèse sur téléphone | écrans métier (Ma semaine, dossier, source, appel préparé…) et téléphone affiché dans la présentation |
| Ambiance | page éditoriale suisse : graphite, ivoire, **un seul** accent cuivre ; pièces sur papier ivoire en serif ; grands énoncés fins, quelques mots en italique serif ; filets fins, beaucoup d'espace | clair, encre presque noire, un orange de signal ; « dans l'esprit » du site public de Flexsis, sans rien en reprendre |
| Mention permanente | aucune (la présentation est la nôtre) | **« Prototype, concept non officiel »** · DE « Prototyp, inoffizielles Konzept » |
| Partagé | chiffres tabulaires ; même grammaire de mentions ; une courbe et trois durées ; contraste ≥ 4,5:1 pour tout texte utile (police : Nunito Sans et Georgia en A, Inter en B) | idem |

## 0. Principes communs

1. **La projection décide.** Tout texte utile (nom, date, preuve, statut, résultat, mention, commande) atteint au moins
   **4,5:1**, quelle que soit sa taille ; les repères graphiques porteurs de sens atteignent **3:1** (WCAG 1.4.11). Les
   ratios ci-dessous sont **calculés** (luminance relative WCAG 2.x, sRGB), pas estimés. Un projecteur et la lumière
   de la salle réduisent le contraste réel : seule la répétition au fond de la salle valide (brief § 12).
2. **Une information garde son identité quand elle change de forme** (annonce → point sur la carte → dossier → raison
   d'appeler → carte de travail → synthèse). Le nom et la date restent lisibles pendant toute la transformation.
3. **Les mentions qualifient l'information à laquelle elles s'appliquent**, jamais tout un écran (§ 7).
4. **Le logo de Flexsis n'est jamais repris** (aucune autorisation écrite), ni photo, ni code, ni texte. Depuis le
   07.10.2026, à la demande de Hiba, Proxsis porte l'identité visuelle de Flexsis (couleurs, polices de la même famille,
   diagonales : section « Direction en vigueur ») ; le « x » de Flexsis et sa partie orange ne sont pas recopiés. Le reste
   de ce principe tient (version du 06.10.2026 : « ni motif graphique, ni police de marque », remplacée). Flexsis n'est présenté ni comme client, ni comme partenaire, ni comme ayant approuvé le
   prototype.
5. **Aucune photographie de personnes.** Les visuels sont des documents (sources sur papier), la carte, le calendrier
   et les données ; une personne fictive est représentée par des initiales et la mention « Personne fictive ».

## 1. Relevé du site public de Flexsis (www.flexsis.ch, 06.10.2026)

**Méthode.** Chrome piloté par Playwright (`@playwright/test` 1.63, `channel: "chrome"`), script hors dépôt, lecture
seule. `robots.txt` consulté le 06.10.2026 : aucune interdiction (`User-agent: * / Disallow:`), plan du site Yoast.
Neuf chargements : accueil FR et DE, Entreprise, Secteurs d'activités, Construction, Agences de placement,
Actualités, Contact (1440 × 900), puis accueil au format 390 × 844 ; pause de 5 s entre les pages. Bandeau de cookies
laissé sans réponse (rien n'a été accepté). Les valeurs viennent des styles calculés (`getComputedStyle`) et de la
surface couverte par chaque couleur. Les captures prises pour l'analyse contiennent leurs photos et leur logo : elles
restent hors dépôt ; seuls les relevés ci-dessous sont conservés.

Pages : `https://www.flexsis.ch/`, `/de/`, `/entreprise/`, `/secteurs-activites/`, `/secteurs-activites/construction/`,
`/agences-de-placement/`, `/actualites/`, `/contacter-flexsis/`.

### 1.1 Palette relevée

| Couleur | Usage observé | Contraste calculé |
|---|---|---|
| `#121212` | texte courant, boutons pleins (pilule noire), titres de cartes | 18,73:1 sur blanc |
| `#e6530f` | orange de marque : titres de section, mots en gras des titres, bandeaux pleins, grandes diagonales sur les photos, onglet actif, icônes et puces | 3,74:1 sur blanc, 3,46:1 sur `#f6f6f6` (titres grands seulement) ; `#121212` dessus : 5,00:1 ; blanc dessus : 3,74:1 |
| `#ffffff` | fond principal ; texte sur photos et sur fonds sombres | 15,13:1 sur `#262626` |
| `#f6f6f6` | bandes claires alternées, cartes de prestations | — |
| `#262626` | sections sombres, pied de page | orange dessus : 4,04:1 |
| `#323232` à 45 % | voile sombre sur les photos d'en-tête | — |
| `#212121`, `#000000` | bandeau de cookies, bouton de recherche | — |
| `#7f8285` | dates des actualités | 3,86:1 sur blanc |
| `#dee2e6`, `#121212` à 20 % | filets, séparateurs en pointillé | — |

Le site est un WordPress à base Bootstrap 5 (variables `--bs-*` ; l'orange y figure comme `--bs-orange`).

### 1.2 Typographie relevée

- **Sora** (300 léger, 700 gras) pour les titres. Signature : **contraste gras / léger dans un même titre** (une partie
  en 700, la suite en 300). Tailles à 1440 px : h1 54,7 à 67,2 px (interligne 1,2 à 1,3), titres de section 44,8 px,
  sous-titres 35,2 / 22,4 / 19,2 px ; au téléphone, h1 25,7 px et titres de section 38,4 px.
- **Urbanist** (400 à 700) pour l'interface : navigation 19,2 px 600, boutons 18,4 px 600, texte courant 17,6 px 400
  (interligne 1,4), étiquettes 12,8 px 600 en majuscules.
- Roboto (cartes et widgets) et Material Symbols (icônes) chargées en complément.
- Échelle en rem de 16 px multipliés par 0,8 à 4,2 (12,8 → 67,2 px) ; espacements 6,4 / 12,8 / 19,2 / 38,4 / 76,8 /
  102,4 px.

### 1.3 Espacements et formes

- Conteneur de 1320 px (Bootstrap), marges latérales de 60 px à 1440 ; sections de 76,8 à 102,4 px en hauteur de marge ;
  au téléphone 38,4 px vertical et 12 px latéral.
- Boutons **pilule** (rayon 50 px, 14,7 × 18,4 px de marge interne), blancs ou noirs ; recherche par bouton noir
  pleine largeur.
- Cartes à fond gris clair ou blanc, coins faibles, ombre légère ; séparateurs **en pointillé** ; accordéons « + »
  orange.
- Motif : chevron / X dérivé du logo, en grandes diagonales orange posées sur les photos et en filigrane.

### 1.4 Ton des textes

Vouvoiement ; « nous » de l'entreprise ; accroches courtes à jeu de mots (ex. « Notre mission : trouver la vôtre »,
page d'accueil) ; valeurs affichées (proximité, humain, expertise, identité suisse) ; superlatifs de marque et appels à
l'action directs ; site en cinq langues (FR, DE, IT, EN, PT).

### 1.5 Photographies

Photographies réelles et chaleureuses : gros plans de mains au travail (horlogerie, chantier), ouvriers en équipement
de protection (couvreur, soudeur, industrie), bureaux ; photos d'équipes d'agence dans les actualités ; voile sombre et
diagonales orange par-dessus ; une illustration ponctuelle.

### 1.6 Ce que l'application garde, ce qu'elle écarte

| On garde l'esprit | On écarte |
|---|---|
| fond blanc, encre presque noire, **un seul** orange chaud | logo, chevron / X, toute photo du site |
| boutons pilule, noir plein ou contour | Sora et Urbanist (polices de marque, même sous licence libre : pas d'imitation) ; Inter les remplace |
| contraste gras / léger dans les titres (avec Inter 700 / 300) | orange en texte sur fond clair (3,74:1 < 4,5:1) |
| blancs généreux, bandes claires alternées | séparateurs décoratifs en pointillé (le pointillé est réservé au statut, § 7) |
| vouvoiement direct, phrases courtes | superlatifs, promesses, texte posé sur une photo |

## 2. Tendances 2025-2026 (inspiration, jamais copie)

Sources consultées le 06.10.2026.

| Source | Date | Ce qu'on en retient | Décision |
|---|---|---|---|
| Linear, « UI refresh », [linear.app/changelog/2026-03-12-ui-refresh](https://linear.app/changelog/2026-03-12-ui-refresh) | 12.03.2026 | interface plus calme : navigation atténuée, contenu en avant, en-têtes cohérents d'une vue à l'autre | application : la navigation s'efface, le dossier mène ; mêmes en-têtes sur tous les écrans |
| UXMagic, « B2B SaaS UI Design Trends in 2026 », [uxmagic.ai/blog/b2b-saas-ui-design-trends](https://uxmagic.ai/blog/b2b-saas-ui-design-trends) (blog d'éditeur : un signal, pas une étude) | 25.09.2026 | parcours plutôt qu'écrans isolés, minimalisme calme, divulgation progressive, interfaces par rôle | une scène = une idée ; le détail (source, dossier) s'ouvre à la demande |
| Nielsen Norman Group, R. Budiu, « Liquid Glass Is Cracked, and Usability Suffers in iOS 26 », [nngroup.com/articles/liquid-glass](https://www.nngroup.com/articles/liquid-glass/) | 10.10.2025 | la transparence et le texte sur fond chargé nuisent à la lisibilité ; le mouvement gratuit distrait | surfaces opaques, aucun flou ni verre, aucun texte sur photo, aucun mouvement décoratif |
| IBM Carbon, « Motion », [carbondesignsystem.com/elements/motion/overview](https://carbondesignsystem.com/elements/motion/overview/) | mise à jour 12.08.2026 | mouvement « productif » (discret, rapide) et « expressif » (moments marquants) ; durée liée à l'ampleur du déplacement | court et moyen pour le travail ; long réservé aux quatre révélations |
| 9to5Google, Material 3 Expressive, [9to5google.com/2025/05/13/android-16-material-3-expressive-redesign](https://9to5google.com/2025/05/13/android-16-material-3-expressive-redesign/) | 13.05.2025 | mouvement à ressorts, plus vivant | **écarté** pour la projection : le dépassement d'un ressort se lit comme un tremblement à grande échelle ; une courbe sans rebond |
| Chrome for Developers, « What's new in view transitions (2025 update) », [developer.chrome.com/blog/view-transitions-in-2025](https://developer.chrome.com/blog/view-transitions-in-2025) ; web.dev, [same-document view transitions Baseline](https://web.dev/blog/same-document-view-transitions-are-now-baseline-newly-available) | 08.10.2025 ; 16.10.2025 | transitions entre deux états d'un même document, disponibles dans les principaux navigateurs | relier deux états par le même élément ; `stage.css` prévoit des règles `::view-transition`, mais aucune transition de ce type n'est déclenchée dans le code au 06.10.2026 (Motion suffit) |
| Motion, « Layout animations », [motion.dev/docs/react-layout-animations](https://motion.dev/docs/react-layout-animations) | documentation | `layoutId` relie deux éléments qui sont la même information ; animation par transformations | déjà utilisé par `Stage.tsx` (« Lundi », annonce, entreprise) ; règle générale au § 5 |
| W3C, Understanding WCAG 2.2, SC 2.3.3 « Animation from Interactions », [w3.org/WAI/WCAG22/Understanding/animation-from-interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | référence | le mouvement déclenché par l'interaction doit pouvoir être désactivé ; `prefers-reduced-motion` | version sans mouvement obligatoire (§ 5.4) |
| AVIXA, Image System Contrast Ratio (V201.01:2021), [avixa.org/standards/image-system-contrast-ratio](https://www.avixa.org/standards/image-system-contrast-ratio) ; DISCAS (ANSI/INFOCOMM V202.01:2016), [avixa.org/standards/discas-calculators/discas/bdm](https://www.avixa.org/standards/discas-calculators/discas/bdm) | 2021 ; 2016 | le contraste d'une image projetée se mesure dans la salle ; la taille minimale d'un caractère se raisonne en part de la hauteur d'image selon la distance du spectateur le plus éloigné | normes payantes, valeurs non reproduites ici ; tailles exprimées aussi en % de la hauteur d'image (§ 3.2) ; mode projection renforcée ; test humain |

## 3. Identité A — présentation « Votre prochain lundi » (direction du 06.10.2026, remplacée le 07.10.2026)

Sources : direction créative de Hiba (§ 2 « Direction artistique » : univers éditorial suisse, graphite, ivoire, cuivre
pour le dossier retenu, documents sur papier clair, une idée par écran, trois lignes au plus) ; maquette
`proxsis-preview.html` ; brief § 8 et § 12. Code : `apps/web/src/presentation/direction.css` (jetons), `ui.tsx`
(composants), `Frame.tsx` (cadre), `Opening.tsx`, `ValaisMap.tsx`, `Decision.tsx`. Les autres écrans gardent
`stage.css` jusqu'à l'accord de Hiba (E4).

### 3.1 Couleurs

Contrastes calculés (WCAG 2.x) sur `--g`, sauf mention.

| Jeton | Valeur | Usage | Contraste |
|---|---|---|---|
| `--g` | `#151715` | fond (graphite légèrement vert, celui de la maquette) | — |
| `--g-2` | `#1c1f1b` | menu du sommaire (seule surface sur graphite) | — |
| `--ivory` | `#f2f0e7` | énoncés, noms, dates, preuves, statuts, résultats | 15,78:1 |
| `--muted` | `#aeb1a5` | texte secondaire, mentions, sources | 8,27:1 |
| `--muted` projection | `#cfd1c6` | mode projection renforcée | 11,66:1 |
| `--rule` | `#41463c` | filets de 1 px (structure seule, jamais porteur de sens) | 1,86:1 |
| `--rule-strong` | `#636858` | soulignement des champs, contours des communes | 3,13:1 |
| `--copper` | `#f49b67` | **le seul accent** (voir la règle) | 8,35:1 |
| encre sur cuivre | `#24271f` sur `#f49b67` | texte du bouton d'action | 7,03:1 |
| `--paper` | `#eeeadf` | pièces : annonce, source, feuille finale | — |
| `--ink` | `#24271f` | texte sur papier | 12,61:1 sur papier |
| `--ink-muted` | `#5c6152` | en-tête et métadonnées sur papier | 5,32:1 sur papier |
| `--paper-rule` | `#bbbdae` | filet sur papier | — |

**Règle du cuivre (un seul accent).** Il marque : l'heure « 8 h 03. », l'étiquette numérotée de la scène, **l'action
de la scène** (un bouton plein par écran), l'étape courante de la progression, **le choix du directeur** (bordure et
numéro), **les marqueurs** de la carte (marchés attribués) et le chiffre qui leur correspond. Jamais un texte courant,
un intertitre ou un avertissement. **Couleurs d'alerte** : réservées aux vraies alertes (aucune dans ces trois écrans).

**Jamais** : dégradé, lueur, faisceau, verre, flou décoratif, ombre colorée. Une seule ombre, celle du papier
(décalage et flou : `0 22px 44px -22px rgb(0 0 0 / 0.75)`). Rayons : 0 partout (la maquette est à angles vifs).
Seule exception : la lumière du guide de la visite (§ 5.5), qui remplace les traits et les filets reliant deux
éléments ; jamais en décor.

### 3.2 Typographie

- **Sans-serif : Nunito Sans** (SIL OFL 1.1, servie par `next/font`, donc identique sur toutes les machines et hors
  ligne). La maquette utilise Avenir Next, police commerciale absente des PC Windows : Nunito Sans est la plus proche
  des sept polices libres comparées le 06.10 (Figtree, Nunito Sans, Mulish, Albert Sans, Outfit, Urbanist, Plus Jakarta
  Sans), même dessin du « a », du « t » et des chiffres. Énoncés, texte métier, chiffres et sources.
- **Serif : Georgia** (celle de la maquette, présente sur Mac et Windows), Newsreader servie en secours. Seulement :
  **quelques mots en italique** pour l'émotion (« *Vous décidez.* », « *existait déjà.* », « *plus tôt ?* »), le
  **titre des pièces sur papier** et les citations. Dans les textes, ces mots sont marqués `*…*` (composant `Em`).
- **Énoncés en sans-serif fin** comme la maquette ; le message de Hiba parlait d'un « grand serif » : la variable
  `--font-display` bascule les énoncés en serif d'une ligne (question ouverte, notes de travail non publiées).

Tailles à 1920 × 1080 ; chaque taille est bornée par la largeur **et** la hauteur (`min(vw, vh)`), donc la même
composition tient à 1280 × 720.

| Rôle | 1920 × 1080 | Règle | Dessin |
|---|---|---|---|
| Affiche (« Lundi. », « 8 h 03. ») | 180 px | `clamp(64px, min(9.4vw, 16.5vh), 184px)` | 400, approche −0,07 em, interligne 0,96 |
| Énoncé (une idée par écran) | 81 px | `clamp(40px, min(4.2vw, 7.6vh), 84px)` | 400, −0,05 em, 1,04, lignes équilibrées |
| Sous-énoncé (« Quatre personnes. ») | 50 px | `clamp(28px, min(2.6vw, 4.8vh), 52px)` | 450, −0,035 em |
| Chiffre qui se construit | 65 px | `clamp(40px, min(3.4vw, 6.2vh), 68px)` | 400, −0,045 em, chiffres tabulaires |
| Titre d'une pièce (serif) | 34 px | `clamp(22px, min(1.75vw, 3.2vh), 34px)` | Georgia 400, −0,025 em |
| Récit, actions, options, navigation | 28 px | `clamp(19px, min(1.45vw, 2.7vh), 28px)` | 450-550 |
| Texte | 24 px | `clamp(17px, min(1.25vw, 2.3vh), 24px)` | 450 |
| Étiquettes, mentions, sources | 20 px | `clamp(14px, min(1.04vw, 1.86vh), 20px)` | étiquette : capitales, +0,14 em, 500, cuivre |

**Plancher** : rien de ce que lit le public n'est sous **20 px** à 1920 × 1080. La maquette met ses mentions à 11 px :
on garde leur **place** (en bas) et leur **ton** (petites, grises), pas leur taille (brief § 12 : sources lisibles).
**Allemand** : césure automatique pour le récit seulement, jamais pour les raisons sociales, citations et mentions.

**Écarts assumés avec le socle d'Impeccable** (`craft-floor.md`) : il proscrit l'étiquette au-dessus d'un titre et les
numéros de section ; Hiba les demande explicitement (« 03 — VOUS CONNAISSEZ LE MÉTIER ») et le numéro porte une
information (l'acte, sur sept). L'approche de l'affiche (−0,07 em) est celle de la maquette, sous le plancher
d'Impeccable (−0,04 em).

### 3.3 Cadre et mise en page

- **Un même cadre** sur chaque écran : en-tête (« Proxsis », le « + » en cuivre ; à droite « VOTRE PROCHAIN
  LUNDI » et « La semaine que vous choisissez. », la langue, le sommaire), **filet fin** ; la scène ; **filet fin** ;
  navigation **« ← Retour · 03 / 07 · progression en tirets · Continuer → »** en texte seul ; mentions **en bas** (à
  gauche celles de la scène, à droite la date du rejeu).
- **Progression** : un tiret par acte (sept), l'acte courant en cuivre, les actes passés en gris clair, les actes pas
  encore construits en pointillé et inactifs ; un clic mène au début de l'acte. Le compteur annonce aussi l'étape aux
  lecteurs d'écran (« Acte 3 · étape 13 sur 14 »).
- Marges latérales 4,2 vw (80 px à 1920). Deux colonnes : l'énoncé et la preuve à gauche, l'action ou l'image à droite ;
  jamais une grille de cartes. Aucune carte grise remplie : les filets structurent, le papier est la seule surface.
- Écrans de projection peu hauts (≤ 820 px) : la date du rejeu passe dans le sommaire pour laisser la largeur aux
  mentions. Téléphone (≤ 860 px) : une colonne, la page défile, la navigation suit le contenu (rien ne recouvre la
  carte).

### 3.4 Composants (shadcn/ui personnalisé, `ui.tsx`)

- `PButton` : primitive `Button` de base-ui avec variantes `cva`, comme les composants shadcn/ui du projet, stylée par
  `direction.css` : `action` (cuivre plein, **un par scène**, flèche ↗ de lucide), `option` (rangée à filet fin,
  numéro 01-03 à droite, bordure et numéro cuivre quand elle est choisie, `aria-pressed`), `nav` (texte et flèche),
  `quiet` (lien souligné gris), `tool` (en-tête), `paper` (lien sur une pièce).
- `Em` (mots en italique serif), `Counter` (chiffre qui se construit ; valeur exacte annoncée aux lecteurs d'écran).
- Papier (`.d-paper`) : en-tête en capitales grises et date, filet, titre en serif ; l'annonce est inclinée de −0,6°.
- Champ : soulignement seul, cuivre au focus. Focus clavier : contour cuivre 2 px, décalage 4 px. Sélection de texte :
  fond cuivre, encre. Icônes : lucide-react, trait 1,6.

### 3.5 Les trois écrans refaits

1. **Ouverture (acte 1)**, trois gestes sur une même composition : « Lundi. » ; « 8 h 03. » en cuivre ; à droite, sous
   un filet qui se trace, « Quatre personnes. / Pour mercredi. » et « Situation illustrative » ; en bas « Et si cette
   conversation avait commencé *plus tôt ?* » et l'action « Remonter le fil ↗ ».
2. **Carte du Valais (acte 2)** : contours des **122 communes** (swissBOUNDARIES3D 2026-01, © swisstopo, embarqués
   dans `communes_vs.json`, commande `contours-communes`) ; **une semaine par geste** (flèche, action « Semaine
   suivante ↗ » ou un tiret de semaine ; « Toute la période ») ; chaque commune teintée d'ivoire en trois classes selon
   les demandes d'autorisation publiées (1-4, 5-14, 15 et plus) ; marchés attribués en **anneaux cuivre** ; six lieux
   familiers, Martigny (l'agence) en ivoire ; **les chiffres se construisent** (publications sur la carte, communes
   concernées, marchés attribués). À la dernière semaine, l'action devient « Ouvrir un exemple ↗ » et les hors-carte
   s'affichent (818 publications, dont 83 sans commune ; 45 marchés sans lieu). Une commune sans publication reste
   éteinte ; aucun point n'est inventé.
3. **Décision du directeur (acte 3)** : « La piste est là. *Vous décidez.* » ; à gauche l'entreprise réelle et
   l'annonce sur papier (la même pièce qu'à l'acte 2, pour que le public reconnaisse le dossier) ; à droite trois
   rangées « À examiner 01 · Déjà connu 02 · À écarter 03 », la raison courte (facultative), « Ce choix vous suivra
   jusqu'à la dernière scène. », puis « Décision enregistrée sur cet ordinateur ».

## 4. Identité B — application consultant (« dans l'esprit de Flexsis »)

### 4.1 La mention « Prototype, concept non officiel »

- Bandeau **permanent** en haut de chaque écran, non masquable, collant au défilement : fond `--app-dark`, texte blanc
  (15,52:1), 14 px 600, hauteur 36 px ; FR « Prototype, concept non officiel », DE « Prototyp, inoffizielles
  Konzept ». Sur grand écran, il peut ajouter « · données de démonstration » en `--app-on-dark-2` (10,38:1).
- Il remplace le bandeau ambre actuel (`layout.tsx`, `data-testid="demo-banner"`) sans supprimer le sens de celui-ci :
  les données fictives restent signalées par les mentions au niveau de chaque élément (§ 7).
- Dans la présentation, quand le téléphone affiche l'application, le bandeau est visible dans l'écran du téléphone
  **et** une légende à taille de projection l'accompagne (« Application · prototype, concept non officiel », 22 px).
- Le nom « Flexsis » n'apparaît pas dans l'en-tête de l'application.

### 4.2 Couleurs

Contraste sur blanc / sur `--app-surface`.

| Jeton | Valeur | Usage | Blanc | Surface |
|---|---|---|---|---|
| `--app-bg` | `#ffffff` | fond | — | — |
| `--app-surface` | `#f6f5f2` | bandes, cartes (légère chaleur qui fait écho à l'ivoire) | — | — |
| `--app-ink` | `#141414` | texte principal | 18,42:1 | 16,90:1 |
| `--app-ink-2` | `#4d4b47` | texte secondaire | 8,70:1 | 7,98:1 |
| `--app-ink-3` | `#66635e` | dates, métadonnées (plancher du texte) | 5,98:1 | 5,49:1 |
| `--app-line` | `#e3e0da` | séparateurs (structure seule) | — | — |
| `--app-line-strong` | `#8a8781` | contours de champs (non-texte) | 3,58:1 | 3,29:1 |
| `--app-dark` | `#242424` | bandeau prototype, bouton principal, pied de page | blanc dessus 15,52:1 | |
| `--app-on-dark-2` | `#d6d3cc` | texte secondaire sur sombre | 10,38:1 sur sombre | |
| `--app-orange` | `#df5a17` | **signal** : remplissage, icône, onglet actif, contour de focus, points de carte (non-texte) | 3,74:1 | 3,43:1 |
| `--app-orange-ink` | `#b0430f` | orange pour un mot ou un lien ; « Information publiée » | 5,74:1 | 5,27:1 |
| `--app-orange-soft` | `#fbe9dc` | surbrillance (ligne choisie) | encre 15,61:1 · orange texte 4,87:1 · encre-3 5,07:1 | |
| `--app-orange-on-dark` | `#f2a46f` | orange sur fond sombre | 7,62:1 sur sombre | |

Autres paires : encre sur orange signal 4,92:1 (texte sur un remplissage orange : toujours `--app-ink`, jamais blanc,
3,74:1) ; blanc sur orange texte 5,74:1 ; orange signal sur sombre 4,15:1 (non-texte).

L'orange de signal est **voisin, non identique**, de l'orange relevé (`#e6530f`) : l'esprit est reconnaissable, la
marque n'est pas reproduite. Il ne porte jamais de texte sur fond clair.

### 4.3 Typographie

Inter seule (déjà fournie par `next/font` ; aucune police nouvelle). Signature empruntée à l'esprit relevé : un titre
d'écran peut associer un mot en 700 et la suite en 300 (« **Ma semaine** à préparer »), une fois par écran au plus.

| Rôle | Téléphone (390) | Bureau | Graisse | Couleur |
|---|---|---|---|---|
| Titre d'écran | 28 / 34 px | 32 / 38 px | 700 (+ 300) | encre |
| Titre de carte | 20 / 26 px | 20 / 26 px | 600 | encre |
| Texte | 17 / 26 px | 16-17 / 26 px | 400 | encre |
| Secondaire | 15 / 22 px | 15 / 22 px | 400 | encre 2 |
| Métadonnées (plancher) | 14 / 20 px | 14 / 20 px | 500 | encre 3 |
| Mention | 14 / 18 px | 14 / 18 px | 600, bordure 2 px | selon § 7 |
| Bouton | 17 px | 16 px | 600 | |

Chiffres tabulaires pour les dates, comptes et montants (CHF). Formats suisses : dates `jj.mm.aaaa` ; heures « 8 h 03 »
(FR) et « 8.03 Uhr » (DE) ; montants formatés par la langue (`Intl.NumberFormat("fr-CH" | "de-CH")`).

### 4.4 Espacements, formes, profondeur

- Pas de 4 px : 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64.
- Téléphone : marge latérale 16 px, marge interne des cartes 16 px, 12 px entre cartes, 32 px entre sections, aucun
  défilement horizontal. Bureau : conteneur de 960 px, colonne de lecture ≤ 720 px, marges 32 px.
- Rayons : boutons et mentions en pilule (écho aux boutons relevés), cartes 14 px, champs 10 px.
- Profondeur : à plat ; les cartes se distinguent par la teinte `--app-surface`, pas par une ombre. Ombre réservée aux
  éléments superposés (feuille de source, menu).
- Boutons : principal = sombre plein, texte blanc ; secondaire = blanc, contour encre 2 px ; cible ≥ 44 × 44 px.
  Focus : contour `--app-orange` 3 px, décalage 3 px (3,74:1 sur blanc). Onglet actif : filet `--app-orange` 4 px sous
  le libellé, libellé en encre 600.
- Statuts de décision : À examiner = sombre plein, texte blanc ; Déjà connu = surface, contour `--app-line-strong`,
  texte encre ; À écarter = blanc, texte encre 2, « × » devant le mot.

### 4.5 Le téléphone dans la présentation (C2, « démo vivante »)

- Maquette d'iPhone sous licence claire (MIT), habillée selon l'identité A : cadre graphite, filet fin, **sans reflet,
  lueur, faisceau ni dégradé** ; une ombre portée sobre au plus. Écran : l'application réelle (iframe 390 × 844), donc
  l'identité B, claire, posée sur la scène graphite comme une feuille de papier.
- Démo pilotée : à chaque flèche, un indicateur de doigt discret (disque ivoire, liseré graphite) se déplace, touche un
  bouton avec une onde cuivre sans flou, et la vraie page change ; le présentateur peut reprendre la main en cliquant
  dans le téléphone. Sans mouvement : le doigt saute, pas d'onde, la page change aussitôt.
- Hauteur à l'écran ≤ 80 % de l'image : le texte du téléphone n'est pas lisible du fond de la salle ; **l'information
  clé est répétée à côté, à taille de projection**.

## 4 bis. Identité B, nouvelle direction : « futurisme suisse » (06.10.2026 ; couleurs et police remplacées le 07.10.2026)

Brief de Hiba (« Refonte visuelle de l'application — futurisme suisse ») ; brief de forme Impeccable :
notes de travail (non publiées). **Appliquée à deux écrans** : « Ma semaine » et le dossier d'entreprise
(`apps/web/src/app/[lang]/(futur)/`, cadre `layout.tsx`, composants `apps/web/src/futur/`). Les autres pages gardent
l'identité B du § 4 **jusqu'à l'accord de Hiba** ; ensuite, la présentation s'aligne sur cette direction.

- **Couleurs** : trois graphites pour la profondeur — fond `#101210`, surface `#181b17`, surface surélevée `#21251f` ;
  ivoire `#f2f0e7` (16,5 / 15,2 / 13,6:1) ; ivoire atténué `#a7ab9d` (8,0 / 7,4 / 6,6:1) ; **un seul cuivre lumineux**
  `#f59e66` pour l'action et le signal (8,9 / 8,3 / 7,4:1 ; encre sur cuivre 8,6:1). Aucune autre couleur, sauf une
  alerte réelle. Jamais de dégradé ni de lueur.
- **Matière** : filets d'un pixel en ivoire à 9 % et 16 % ; grain fixe très léger (bruit SVG statique, 5 %) ; verre
  dépoli (`blur` 18 à 24 px, fond graphite à 90 %, assez opaque pour l'AA même au-dessus d'une feuille ivoire :
  libellés d'onglets `#c9ccc0` à 8,2:1, cuivre à 6,4:1 dans le pire cas) **seulement** sur la barre d'onglets, l'en-tête
  au défilement, le menu « Démo » et le panneau « Comment cette liste est faite ». Pas d'ombre lourde : une seule ombre
  sous les feuilles de papier.
- **Typographie** : Nunito Sans légère (300) pour les titres, 400 pour le texte ; Georgia italique pour quelques mots ;
  **JetBrains Mono** (SIL OFL 1.1, servie par `next/font`, hors ligne) pour les données : dates, nombres, rangs,
  communes en petites capitales (11 px, +0,12 em) ; chiffres tabulaires. Grille de 4 px.
- **Mouvement (Motion + View Transitions)** : une famille de courbes (`[0.2, 0.7, 0.1, 1]`, 220 / 420 / 700 ms, ressort
  court pour la pression et l'onglet) ; cartes en cascade (45 ms entre deux cartes) ; **la carte devient le dossier** —
  `ViewTransition` de React intégré à Next.js 16, parce que la carte et le dossier sont deux routes (le `layoutId` de
  Motion ne relie que des éléments d'un même arbre) ; nombres qui se construisent ; pouls cuivre sur les marchés de
  moins de 14 jours ; en-tête de hauteur fixe qui se resserre (verre, échelle 0,96, deux seuils) ; indicateur d'onglet
  qui glisse ; chaque bouton réagit à la pression. Mouvement réduit : `MotionConfig reducedMotion="user"`, pouls masqué,
  View Transitions sans animation ; même HTML côté serveur et client.
- **« Ma semaine »** : « Lundi 5 octobre » (affiche), « Martigny · Bâtiment » (petites capitales cuivre), une ligne
  « Démonstration · entreprises réelles, personnes fictives », le lien « Comment cette liste est faite » (panneau
  `<dialog>`, mots simples, lien vers la mesure, sources) ; cartes : « 01 · SAXON », nom d'usage en grand (nom
  juridique complet en libellé accessible et dans le dossier), « pourquoi maintenant » (la raison de l'export, mot pour
  mot, trois lignes au plus), micro-frise des marchés de la spécialité sur 52 semaines (un point par marché, même compte
  que la donnée pour les 68 entreprises), « Préparer l'appel → » et « Dossier ». Aucune étiquette, aucun niveau de
  confiance, aucune estimation. « Nouveaux venus » en une phrase. **Écran large** (≥ 1024 px, décision de Hiba du
  06.10.2026) : à droite de l'en-tête, **« Les signaux de la semaine »**, une mini-carte de la région — limites
  communales swisstopo en filets (seulement les communes du cadre), l'agence en anneau ivoire, un point par commune où
  une entreprise de la semaine a son siège, **en cuivre qui respire** si l'une d'elles a remporté un marché il y a moins
  de 14 jours ; étiquettes posées du côté libre ; légende sans chiffre (le seul chiffre de l'en-tête reste « 10
  entreprises à appeler ») ; rendue côté serveur, sans script. Le taux mesuré (66,8 % contre 20,7 %) **n'est pas en
  vitrine** : il reste dans « Comment cette liste est faite », avec la phrase « Un nouveau marché n'est pas une commande
  de personnel ». Menu « Démo » : rôles en clair (« Consultant·e bâtiment · Martigny », « Chef·fe d'agence · Sion »),
  jamais les codes des consultants fictifs.
- **Dossier** : l'en-tête de la carte ouverte (lieu, nom d'usage, nom juridique, nombre de marchés qui se construit,
  micro-frise, actions), puis « Ce que dit l'annonce » (dernier marché sur papier, source cliquable, autres faits
  publiés), « Ce que ça laisse envisager » (métiers et période à confirmer, lots attendus, liens vers les mesures),
  « Ce qui reste à vérifier » (questions, obligation d'annonce, limites des données), la frise verticale des marchés
  datés, chacun sur sa feuille, et le retour d'appel. Écran large : en-tête fixe à gauche, preuves à droite.
- **Vocabulaire** : aucun code interne visible (les mesures sont reliées par l'adresse `#BESOIN-1`, `#PHAS-2`…) ; ni
  « backtest », ni « indice », ni « pic sur 8 semaines ».
- **Écarts assumés avec le guide Operate d'Impeccable** : cascade au chargement et pouls d'activité, demandés par le
  brief.

## 4 ter. Le nom : Proxsis (07.10.2026, décision de Hiba ; logo dessiné le 07.10.2026, section « Direction en vigueur »)

- **Pourquoi** : le produit n'est pas un radar d'alertes, c'est le lundi matin du consultant. « Proxsis » évoque la
  proximité et la prochaine entreprise à appeler, et se dit de la même façon en français, en allemand et en anglais.
- **Logo** : « Proxsis » en Nunito Sans fine (300), un seul détail cuivre `#f59e66` : le **x** (la prochaine entreprise).
  Jamais seul : toujours avec sa **signature** — FR « La prochaine entreprise à appeler. », DE « Das nächste
  Unternehmen, das Sie anrufen. » (**à relire par un germanophone**), EN « The next company to call. » — et la mention
  **« Prototype · concept non officiel »** (DE « Prototyp · inoffizielles Konzept »), visible juste dessous.
  Composants : `apps/web/src/futur/Brand.tsx` (application), en-tête de `apps/web/src/presentation/Frame.tsx`.
- **Icône** : P ivoire au trait fin sur graphite `#101210`, le x cuivre du nom (ancienne icône, dans l'historique Git ; l'icône actuelle est la tête d'Iris, `apps/web/src/app/icon.png`, PNG 16 à
  512 px, icône Apple, manifeste `manifest.ts`). Aucune image de radar ; rien de la charte de Flexsis (ni logo ni
  couleurs).
- **Ce qui ne change pas** : adresses des pages et domaine de production (QR validé). Un test échoue si l'ancien nom
  apparaît dans un texte visible.
- **Vocabulaire visible** : ni « radar », ni « alerte », ni « signal », ni « niveau » ; on dit liste de la semaine,
  raison d'appeler, fait vérifiable, décision (textes d'interface seulement, jamais les citations de sources).

## 5. Mouvement (commun aux deux identités)

### 5.1 Une courbe, trois durées

Identiques à `apps/web/src/presentation/motion.ts` :

- Courbe : **`cubic-bezier(0.2, 0.7, 0.1, 1)`** (Motion : `[0.2, 0.7, 0.1, 1]`). Démarre vite et se pose
  doucement ; pas de ressort, pas de dépassement.
- **Court, 220 ms** : retour d'un contrôle (survol, pression, choix « À examiner »), apparition d'une mention, fondu de
  la version sans mouvement.
- **Moyen, 420 ms** : un élément change de place ou de taille dans la scène (carte qui s'ouvre, source qui s'ouvre puis
  revient au même endroit, profil qui entre, semaine suivante sur la carte, défilement du téléphone).
- **Long, 700 ms** : transformation qui relie deux états, réservée aux révélations : l'annonce qui devient un point puis
  un dossier, l'information qui se détache de son document pour devenir un appel à préparer, la journée vide qui reçoit
  une mission en tirets, « Lundi » qui devient « Votre prochain lundi », l'entrée du téléphone.
- Délais : un délai vaut **0**, ou **l'une des trois durées** (pour enchaîner un second temps après la fin du premier,
  sans chevauchement), ou **100 ms par élément** pour une suite lue dans l'ordre, trois éléments au plus (comme les
  profils de l'ancienne présentation par étapes). Au-delà de trois, entrée groupée, ou révélation pas à pas par le présentateur (« quelques
  noms à la fois »).
- Sur la carte, les communes d'une même semaine s'allument **ensemble** (durée moyenne) et les marqueurs grandissent
  (durée moyenne) : une cascade suggérerait un ordre dans le temps qui n'existe pas à l'intérieur d'une semaine.
- **Les chiffres se construisent** de leur valeur précédente à la nouvelle en durée longue (`Counter`) ; sans
  mouvement, la valeur s'affiche directement.
- **Ouverture** : « 8 h 03. » monte de 0,18 em en durée longue ; le filet de droite se trace (durée longue) ; la
  demande, puis la mention et la question arrivent en fondu (délais : une durée courte, puis moyenne).
- **Gestes à l'intérieur d'une étape** : la flèche révèle d'abord les gestes de l'étape (les semaines de la carte),
  puis passe à l'étape suivante ; revenir dans une étape la montre complète (`state.ts`, `reveal`).

### 5.2 Relier deux états

- Le même élément (même `layoutId` Motion ou même `view-transition-name`) passe d'une forme à l'autre ; le nom, la date
  et la mention restent visibles pendant le trajet et voyagent avec l'élément.
- Mouvement par transformations (translation, échelle) et opacité ; pas d'animation de largeur ou de hauteur.
- Ampleur proportionnée : aucun volume, point ou mouvement ne suggère plus que le périmètre documenté (brief § 8).

### 5.3 Jamais

Boucle, pulsation, respiration, parallaxe, défilement automatique, minuterie, effet d'apparition sur un texte que le
directeur doit lire pendant que le présentateur parle, flou ou verre, ressort. Seule exception : la mascotte du guide, qui flotte et
cligne dans son coin (§ 5.5).

### 5.4 Interruption et version sans mouvement

- Toute animation est interrompable : « Suivant », « Retour » ou une touche pendant un mouvement mènent directement à
  l'état final de l'étape demandée.
- Version sans mouvement, activée par `prefers-reduced-motion: reduce` **ou** par le bouton « Sans mouvement » de la
  présentation (`MotionConfig reducedMotion="always"`) : aucune translation ni échelle ; changement direct ou fondu de
  220 ms au plus ; même mise en page finale, même hiérarchie, mêmes mentions ; rien ne disparaît avant que le
  présentateur avance.

### 5.5 La lumière et la mascotte du guide (règle de Hiba, 07.10.2026)

Les mots de Hiba : « Les liens passent par la lumière, jamais par un trait. » et « reprends du prototype la visée
(quatre coins qui se referment, étiquettes « REPÉRÉ » et « RAPPEL DU JOUR »), le balayage sur les blocs, lignes et
sections, et le miroitement cuivre dans les lettres des titres. Aucun trait, aucun lavis seul. » Référence : le
prototype de Hiba, version 4 (`video/reference/prototype-mascotte.html` sur la branche du film).

- **La visée** relie ce que le guide regarde : quatre coins de 18 px (trait de 2 px, ivoire sur graphite, encre sur
  papier) partent 30 px plus loin, puis se referment autour de la cible (16 px autour d'un bloc, moins autour d'une
  ligne de liste, pour ne pas mordre sur la voisine), en 0,55 s ; d'une cible à l'autre, ils glissent. Étiquette
  posée sur le bord du cadre : « Repéré » (la ligne choisie), « Rappel du jour » (la décision qui revient). Cibles
  marquées `data-lumiere` : le premier siège de la carte, le fait publié puis la question du dossier, « Revoir le… »
  puis « À revoir aujourd'hui », le compte de « Une date », le seuil.
- **Le balayage** : un éclat de lumière traverse une fois le bloc, la ligne ou la section qui vient d'apparaître
  (0,6 s), jamais en boucle.
- **Le miroitement** : un reflet cuivre traverse une fois les lettres d'un titre (le premier écran, la phrase de chaque
  étape), 0,9 s.
- **Jamais** : un trait ou un filet qui relie deux éléments ; un lavis (fond éclairé) sans visée ni balayage ; une
  lumière en décor, sans cible.
- **La mascotte** (sphère graphite, coutures cuivre, visage de verre ivoire) est le seul objet en relief : petite, dans
  un coin, elle flotte et cligne, suit le pointeur, « parle » quand une phrase arrive et s'écarte quand le visiteur
  décide (sa lumière baisse : elle ne décide jamais). Elle s'arrête hors de l'écran et quand l'onglet est caché ;
  30 images par seconde sur un petit processeur. Un bouton, à côté du mode présentateur, masque le guide et sa
  lumière (choix gardé sur l'appareil).
- **Sans mouvement** : la visée se pose directement, sans balayage ni miroitement ; la mascotte est une image immobile.
  Sans WebGL2 : son image fixe.

## 6. Textes à l'écran

- Vouvoiement, phrases courtes, verbes d'action du consultant (« examiner », « préparer », « vérifier ») ; aucune
  promesse, aucun superlatif.
- Chaque fait porte sa source et sa date ; le rejeu est nommé comme tel (« Rejeu du lundi … »), jamais « ce matin ».
- Vocabulaire interne à éviter dans les textes destinés au directeur : liste du brief § 14 (contrôlée par
  `apps/web/src/presentation/vocabulary.ts`).
- Les citations des sources restent intactes ; une traduction est signalée comme telle ; les raisons sociales ne sont
  pas traduites.

## 7. Mentions

### 7.1 Grammaire

La **forme du contour** porte le statut, le **mot** est toujours écrit (jamais une icône seule), la couleur ne fait
que renforcer.

| Mention (FR) | DE (`copy.ts`) | Contour | Présentation | Application | S'applique à |
|---|---|---|---|---|---|
| Entreprise réelle | Reales Unternehmen | plein | ivoire | encre | l'identité d'une entreprise vérifiée ; le statut de client de Flexsis reste inconnu |
| Information publiée | Veröffentlichte Information | plein | cuivre (cuivre foncé sur papier) | orange texte | un contenu daté et attribué ; **toujours suivie de « source · date »** (ex. simap.ch · jj.mm.aaaa) |
| Besoin à confirmer | Bedarf zu bestätigen | points | ivoire atténué | encre 2 | une interprétation qui demande un contact avec l'entreprise |
| Personne fictive | Fiktive Person | tirets | ivoire | encre 2 | un profil de candidat inventé (le brief dit « Candidat fictif ») |
| Mission fictive | Fiktiver Einsatz | tirets | ivoire | encre 2 | une mission inventée |
| Situation illustrative | Beispielsituation | tirets | ivoire | encre 2 | une mise en situation (ex. la demande urgente de l'acte 1) |
| Hypothèse | Annahme | tirets | ivoire | encre 2 | une valeur du calculateur ou un scénario sans mesure établie |

Scène mixte : une seule mention « Entreprise réelle · personnes et missions fictives » (« Reales Unternehmen · Personen
und Einsätze fiktiv »). La possibilité placée dans le calendrier (« en pointillé » dans le récit) se dessine en tirets
cuivre : elle appartient à la famille des éléments non confirmés.

**Présentation (direction du 06.10.2026)** : plus de pastilles cerclées. La mention s'écrit **en texte**, petit et
gris, au niveau de l'information (« Situation illustrative » sous la demande, « entreprise réelle » à côté du nom) et
la mention de la scène est répétée en bas de l'écran, à gauche (sources et mentions obligatoires mot pour mot). Les
contours (plein, points, tirets) restent la grammaire de l'application (identité B) et des éléments non confirmés
dessinés (la possibilité en pointillé du planning). Taille en projection : 20 px (plancher de l'identité A, § 3.2).

### 7.2 Règles

1. Au niveau de l'information, à côté de l'élément qu'elle qualifie ; jamais en bandeau global (le bandeau
   « Prototype, concept non officiel » qualifie le produit, pas les données).
2. Jamais une mention fictive ou illustrative sur un nom d'entreprise réelle comme si cette entreprise avait demandé du
   personnel ; si la confusion est possible, séparer visuellement l'annonce réelle de l'exercice de placement.
3. Taille : ≥ 20 px en projection (texte, identité A), ≥ 14 px au téléphone ; contraste ≥ 4,5:1 ; bordure 2 px pour
   les mentions à contour de l'application (1,5 px ne distingue plus les points des tirets au téléphone).
4. Une mention reste visible tant que son élément est visible, voyage avec lui pendant une transition et n'est jamais
   la première à disparaître.
5. Une mention longue passe à la ligne entre deux mots ; au téléphone, son rayon devient 14 px pour garder un contour
   lisible sur deux lignes.
6. Les statuts de décision du directeur ne reprennent jamais ces contours (§ 3.4, § 4.4).

## 8. Écarts restants (E4, après l'accord de Hiba)

Les trois écrans de § 3.5 sont faits. Restent, dans la même direction :

| Écran | À faire |
|---|---|
| Annonce (acte 2) | l'annonce sur papier **se détache et devient un appel** (même pièce, `layoutId`), au lieu de deux blocs côte à côte |
| Les dix entreprises (acte 3) | liste à filets fins (nom, commune), les dossiers préparés en action cuivre ; plus de grille de cartes grises |
| Entreprise, raison, appel, personnes, vérifications | deux colonnes, trois lignes de message au plus, la pièce sur papier, « **Ce que le consultant y gagne :** … » en bas ; plus de pastilles cerclées (les mentions vont en bas ou au niveau de l'information, en texte) |
| Mission suivante | la journée vide **reçoit** la mission en pointillé (geste), planning à filets |
| Synthèse (acte 7) | **fait le 07.10.2026** : « Lundi. » devient « Votre prochain lundi. », feuille « Votre point de départ. », page imprimable A4 |
| Notes du présentateur | même cadre et mêmes polices |
| Téléphone | démo vivante (C2) intégrée aux actes 3, 5 et 7 |

## 9. Captures de référence (notes de travail, non publiées)

Planches générées à partir d'HTML local (polices Inter et Newsreader de l'application), rendues par Chrome via
Playwright en projection (1920 × 1080) et au téléphone (390 × 844, pleine page, densité 2). Aucune ne contient d'image,
de logo ou de texte du site de Flexsis ; les contenus d'exemple sont génériques (« Nom de l'entreprise », « jj.mm.aaaa »).

| Fichier | Contenu |
|---|---|
| `01-presentation-palette-{1920,390}.png` | jetons A, contrastes sur graphite et sur papier, projection renforcée, paires interdites |
| `02-presentation-typographie-{1920,390}.png` | échelle de projection à taille réelle ; au téléphone, variante papier de la synthèse |
| `03-application-palette-{1920,390}.png` | jetons B, contrastes, bandeau prototype, boutons, onglet, surbrillance |
| `04-application-typographie-{1920,390}.png` | échelle de l'application et écran type « Ma semaine » au téléphone |
| `05-mentions-{1920,390}.png` | les sept mentions en FR et DE dans les deux identités, mention mixte |
| `06-mouvement-espacements-{1920,390}.png` | courbe, trois durées et leurs usages, règles, échelles d'espacement |
| `07-presentation-existante-projection-renforcee-1920.png` | présentation actuelle, acte 3 étape 7, projection renforcée |
| `08-presentation-existante-telephone-390.png` | même étape au téléphone |
| `maquette/` | la maquette de Hiba capturée par Playwright (`projection-00…05`, `telephone-00…05`) |
| `2026-10-06-avant/` | **avant** : les 14 étapes actuelles, FR et DE, 1920 × 1080, 1280 × 720 et 390 × 844 |
| `2026-10-06-apres/` | **après** : les trois écrans refaits (8 états : Lundi, 8 h 03, demande ; carte vide, semaine 4, complète ; décision, décision prise), FR et DE, mêmes trois formats |
| `2026-10-06-ecart.md` | l'écart point par point (26 points) et l'état des outils |

## 10. Dépendances

- **Nunito Sans** (SIL Open Font License 1.1), servie par `next/font` avec l'application (hors ligne) : seule nouvelle
  ressource. Georgia est une police système (Mac, Windows) ; Newsreader et Inter restent servies par `next/font`.
- Déjà dans le projet : Motion, `@base-ui/react` (primitive des composants shadcn/ui), `class-variance-authority`,
  `lucide-react`.

## 11. Limites et restant à faire

- **Contrôle humain** : lecture depuis le fond de la salle avec le projecteur réel (cuivre délavé, finesse des filets
  et des contours de communes, mentions à 20 px). Non fait.
- **Revue Impeccable** : le lanceur charge le contexte (`impeccable context`) ; la commande `/impeccable critique` n'a
  pas été lancée (pas chargée dans la session de travail) ; revue équivalente faite : socle `craft-floor.md` relu et
  appliqué, contrastes calculés, captures en trois formats et deux langues, e2e et axe verts.
- **Accord de Hiba** sur les trois écrans avant E4 ; deux questions ouvertes (énoncés en serif ou non, police).
