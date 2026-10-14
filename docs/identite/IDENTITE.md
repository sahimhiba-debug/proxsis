# Proxsis · identité visuelle dans l'univers Flexsis

Fiche du 07.10.2026 · **Prototype · concept non officiel**. Flexsis n'est ni client ni partenaire de Proxsis.

En une phrase : blanc dominant, noir `#121212` pour les moments de décision, et un seul orange `#E6530F` qui ne marque que ce qui compte.

## Contenu du dossier

| Dossier | Contenu |
|---|---|
| `prototype/proxsis-identite.html` | La présentation de 48 s (ordinateur et téléphone), les trois vues de référence et la fiche. Un seul fichier, à ouvrir dans un navigateur. |
| `logo/` | Quatre versions du logo, en SVG et en PNG transparents (2400 et 600 px de large). |

## Couleurs

| Rôle | Valeur | Usage |
|---|---|---|
| Orange | `#E6530F` | Sélection, décision, date de rappel, prochaine action. Grande diagonale du décor. Raccords. |
| Noir | `#121212` | Textes, scènes sombres. |
| Blanc | `#FFFFFF` | Fond dominant, face des étiquettes. |
| Gris texte | `#5C5C5C` | Informations secondaires sur blanc. |
| Gris clair | `#F4F4F4` | Puces neutres, surfaces calmes. |
| Trait | `#E3E3E3` | Séparations fines. |
| Texte secondaire sur noir | `rgba(255, 255, 255, 0.72)` | Sous-titres et mentions dans les scènes sombres. |

Contrastes mesurés :

| Combinaison | Contraste | Usage autorisé |
|---|---|---|
| Orange sur blanc | 3,7:1 | Titres de 24 px et plus, ou gras de 19 px et plus. En dessous de ces tailles, le texte reste noir ou gris foncé et l'orange devient une marque (la petite diagonale). |
| Blanc sur orange | 3,7:1 | Pastilles en gras de 19 px et plus. |
| Orange sur noir | 5,1:1 | Libre. |
| Gris `#5C5C5C` sur blanc | 6,7:1 | Libre. |

## Polices

**Sora** pour les grands titres. Un poids léger (300) avec un mot fort (600), souvent en orange : « Vous **décidez.** ». Les très grands titres sont légèrement resserrés (−0,035 em).

**Urbanist** pour les informations, les étiquettes, les boutons et les mentions, en poids 500 à 700. Les chiffres sont à chasse fixe (`font-variant-numeric: tabular-nums`) pour que les dates et les montants se comparent d'un coup d'œil.

Les deux polices sont sous SIL Open Font License 1.1. Pour Urbanist : Copyright 2021 The Urbanist Project Authors (https://github.com/coreyhu/Urbanist). Le fichier `polices/OFL-Urbanist.txt` accompagne les fichiers de police.

Chargement local :
- Urbanist : `polices/urbanist-latin.woff2` et `polices/urbanist-latin-ext.woff2`.
- Sora n'était pas disponible dans mon espace de travail. Le prototype la charge donc depuis Google Fonts. Dans l'application, elle doit être auto-hébergée (paquet `@fontsource/sora` ou téléchargement Google Fonts), avec son fichier OFL.

Écriture :
- Dates suisses : `05.10.2026`. Heures : `08:03`. Montants : `CHF 750'969`.
- Espace fine insécable avant « ? », « ! » et « : ». Guillemets « ».
- Allemand : ä, ö, ü et ß sont couverts (« Dienststelle für Mobilität »).

## Logo

L'écriture est exactement **Proxsis** : un P majuscule, puis des minuscules.

Dessin :
- Il est construit à partir des contours d'Urbanist instanciés en graisse 820, avec une approche resserrée (−55 unités). On obtient ainsi la densité et la géométrie franche du lettrage Flexsis.
- Le point du « i » devient une petite diagonale orange, un parallélogramme incliné de 0,2. C'est la signature que l'on retrouve sur les étiquettes et dans le décor.

Ce que le logo ne reprend volontairement pas : la construction du « x » de Flexsis et sa partie orange. Elles appartiennent au logo Flexsis, et les recopier ferait de Proxsis une imitation de leur marque. Le logo Proxsis est de la même famille, sans être une copie.

Versions :

| Fichier | Usage |
|---|---|
| `proxsis-logo-noir-orange` | Sur fond clair. |
| `proxsis-logo-blanc-orange` | Sur fond noir. |
| `proxsis-logo-mono-noir` | Monochrome, sur fond clair. |
| `proxsis-logo-mono-blanc` | Monochrome, sur fond sombre. |

Taille et espace :
- Le logo est lisible dès 72 px de large, soit environ 16 px de haut. En dessous, écrire « Proxsis » en Urbanist gras.
- Laisser tout autour un espace au moins égal à la hauteur du « x ».

Animation : le point du « i » (suite 8, § 4 ; environ 2,2 s) :
1. Les lettres montent depuis la ligne de base, l'une après l'autre (décalage de 35 ms, 0,42 s chacune) ; le « i » arrive
   sans son point.
2. Iris entre, petite (sa tête fait 2,1 fois le point), et frappe juste à l'endroit du point : toc, une petite onde
   orange.
3. Quand elle se relève, la diagonale orange est posée, avec un léger rebond (« tampon » ; l'autre façon gardée :
   « chute », le point tombe de la tête). Elle s'efface, et plus rien ne bouge.
4. Sans mouvement : le logo complet, le point déjà posé, pas d'Iris. Code : `apps/web/src/iris/logo.js`.

## La mascotte : Iris, le marteau du bisse (12.10.2026)

Choisie par Hiba le 12.10.2026 ; elle remplace l'ancienne Iris (la sphère noire, notes de travail non publiées). Tout est dans `mascotte/MASCOTTE.md`, qui fait foi.

- **Son corps** : une tête en mélèze patiné, une visière de verre gris, deux yeux ovales lumineux ; un long manche qui
  pivote sur un chevalet ; une roue à aubes orange `#E6530F` dans un court bisse ; une planche blanche où elle frappe.
  Jamais de bras ni de jambes, rien dans les mains.
- **Un seul orange** : la roue, le point (la petite diagonale de Proxsis) et l'onde. Le reste est bois, verre, blanc et
  gris. Le bois reste à Iris : l'interface garde ses étiquettes blanches à fine coque graphite.
- **Son nom**, pour trois raisons : dans les légendes grecques, Iris est la messagère des dieux (CLAIMS
  EXT-IRIS-MESSAGERE) ; « Iris met les points sur les i » ; le nom se dit pareil en français, en allemand et en anglais.
- **Son histoire** : sur les bisses du Valais, une roue mue par l'eau faisait battre un marteau ; tant qu'il frappait, le
  gardien savait que l'eau coulait (CLAIMS EXT-BISSE-MARTEAU). Iris reprend ce geste : quand un fait mérite un appel,
  toc, elle pose le point.

Ses tailles :

| Taille | Quand | Images |
|---|---|---|
| En grand, la scène complète (roue, bisse, planche) | Le film et la présentation vidéo (branches `video/`) ; plus dans l'application | `mascotte/calques/` |
| En petit, debout sur son manche, tournée vers l'information | Le guide de la visite, un coin d'écran | `mascotte/petite/` (`IrisPetite.tsx`) |
| L'icône : la tête de face | L'onglet, l'écran d'accueil, le manifeste ; lisible à 32 px | `mascotte/petite/icones/` |

Ses gestes :

| Geste | Comment |
|---|---|
| Elle veille | La roue tourne, les yeux sont calmes et clignent de temps en temps. |
| Regarder une information | Elle tourne les yeux vers la carte. |
| Attirer l'attention (« Repéré ») | Toc, et le point se pose sur la carte, avec un léger rebond. |
| Accompagner un choix | Ses yeux deviennent contents quand le consultant choisit. |
| Retrouver un rappel | Le point est déjà posé sur l'étiquette « Rappel du jour ». |
| Une source se tait | Le silence : l'eau et la roue s'arrêtent, ses yeux deviennent inquiets, et elle le dit. |

Règles :
- Elle se pose pendant la lecture et laisse la place aux informations ; petite et dans un coin, sauf quand c'est son
  moment.
- Elle ne choisit jamais : elle prévient et pose le point ; le consultant décide.
- Le son : le toc à chaque coup, au contact exact, toujours sous la voix ; l'eau très basse, seulement quand elle est en
  grand. Dans la visite, le son ne part qu'après un premier geste, et un bouton le coupe.
- Ni drapeau ni armoiries du Valais, ni croix suisse ; pas de Cervin, de vache ni de bouquetin.

## Les étiquettes

Elles gardent la matière de l'interface (le bois reste à Iris) :
- une fine coque graphite ;
- une face blanche satinée ;
- des angles arrondis ;
- une petite épaisseur visible ;
- des reflets doux sur les bords ;
- une ombre légère.

Le texte est posé sur la zone opaque. Les reflets ne passent que sur les bords.

Trois formats de la même famille :

| Format | Contenu |
|---|---|
| Petite étiquette | Une date, une source ou un statut : « Publication · 12.08.2026 », « À vérifier », « Rappel · 12.10.2026 ». Elle peut s'accrocher en onglet au bord d'une carte, à moitié dessus. |
| Carte d'entreprise | Le nom d'abord, puis la commune, puis une information courte et sourcée. Le statut est une pastille arrondie : à droite sur ordinateur, dessous au téléphone. |
| Carte de question | Une seule question, beaucoup d'espace autour, et la mention « Fondée sur le seul fait publié. ». |

Décisions :
- Les pastilles de décision sont des boutons arrondis : À appeler · À vérifier · Revoir le… · Écarter. La décision choisie se remplit d'orange.
- La carte choisie reçoit un bord orange et la petite diagonale du logo en haut à droite.
- Le lundi suivant, elle revient avec la même marque : « Revient : À appeler ».

## Fonds, scènes et raccords

| Scènes | Moments | Décor |
|---|---|---|
| Claires | L'ouverture, les signaux, le dossier, la fin. | Blanc dominant, lumière douce, légère profondeur. Une grande diagonale orange entre par un bord et ne touche jamais les textes. |
| Sombres (`#121212`) | L'apparition du choix (« Vous décidez. »), le lundi suivant (« Pas à zéro. »), la grande question (le guide, « Une question ? »). | La diagonale reste dans un coin. Les cartes blanches et l'orange ressortent. |

Les raccords :
- Une seule bande orange en diagonale traverse l'image en 0,9 s. Elle la couvre entièrement à l'instant où la scène change.
- Elle ne sert que trois fois : vers le choix, vers le lundi suivant, et pour revenir à la marque à la fin.
- Pendant la lecture, le décor ne bouge pas.

## Mouvement

- Une seule action principale à la fois, puis un vrai temps de lecture.
- Chaque arrêt sur image doit rester beau et compréhensible.

Trois moments sont particulièrement soignés :
1. **L'ouverture** : le logo, la mascotte et « Votre premier appel ? ».
2. **La publication qui devient un dossier** : la date et la source restent visibles ; le fait publié, ce qui reste à vérifier et la question occupent des espaces distincts.
3. **Le lundi suivant** :
   - la carte choisie revient avec sa marque ;
   - le rappel garde sa date ;
   - la prochaine action est visible ;
   - une nouvelle entreprise rejoint la liste.

## Téléphone

- Le format est 1080 × 1920, avec sa propre mise en page : les cartes passent les unes sous les autres, en pleine largeur, et les textes sont plus grands.
- Le dossier s'affiche en trois pages : le fait publié, ce qui reste à vérifier, puis la question.
- La liste du lundi suivant se resserre (01, 02, ···, 10), et le rappel s'accroche en onglet à la carte 01.
- Le prototype passe au format téléphone sous 700 px de large. Un bouton permet de choisir le format.

## Informations

- Seuls des textes et des chiffres validés sont utilisés. Chaque date, montant, entreprise et source correspond aux fichiers du dépôt.
- Les exemples fictifs sont signalés : « Démonstration · personnes et suites fictives · décisions : exemple préparé · données arrêtées le 30.09.2026. »
- Une publication donne une raison de préparer un appel. Elle ne confirme pas à elle seule un besoin de personnel.
- La mention « Prototype · concept non officiel » est toujours visible.
- Avec les données simap, elle est complétée par : « Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi. »
- La présentation ne montre que les fonctions réellement disponibles.
