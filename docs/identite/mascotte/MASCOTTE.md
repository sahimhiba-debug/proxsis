# Iris, le marteau du bisse — la nouvelle mascotte (12.10.2026)

Choisie par Hiba le 12.10.2026. Elle remplace l'ancienne Iris (la sphère noire). L'ancienne reste archivée, jamais
supprimée, et n'est remplacée partout qu'une fois la nouvelle version validée par Hiba.

## En une phrase

Iris est un petit marteau de bisse : une tête en mélèze patiné, avec une visière de verre et deux yeux lumineux, au bout
d'un long manche. Une roue à aubes orange, dans l'eau, la soulève. Quand un fait mérite un appel, elle frappe une
planche blanche : **toc**. Et elle pose le point.

## L'histoire, à dire simplement

- Sur les bisses du Valais, une roue tournée par l'eau soulevait un petit marteau. Tant qu'il frappait, le garde savait
  de loin que l'eau coulait (le bisse d'Ayent, 1442). Les bisses font partie de l'irrigation traditionnelle, inscrite en
  2023 au patrimoine culturel immatériel de l'UNESCO.
- Iris reprend ce geste pour les agences : sa roue tourne tant que l'information coule. Quand un fait mérite un appel,
  toc.
- Sa devise : « Iris met les points sur les i. » Le point du « i » de Proxsis est la petite diagonale orange. Et
  « Iris » a deux i.
- Son silence parle aussi : si la roue s'arrête, une source ne coule plus. Comme le garde du bisse, on va voir.

## Son corps : ce qui ne change jamais

- **La tête** : un bloc de mélèze patiné, aux arêtes arrondies, avec de fines fentes et un petit tenon rond sur le
  dessus.
- **Le visage** : une visière de verre gris, plus large que haute. Deux yeux ovales blancs et lumineux, côte à côte.
  Tout passe par les yeux : pas de bouche.
- **Le manche** : long, en bois patiné. Il pivote sur un petit chevalet en A.
- **La roue** : une roue à aubes orange `#E6530F`, dans un court bisse de bois à l'eau claire.
- **La planche** : blanche, posée en travers du bisse. C'est là qu'elle frappe.
- **Le point** : la petite diagonale orange de Proxsis, `polygon(0 100%, 82% 100%, 100% 0, 18% 0)`.
- **Debout**, pour une icône ou un coin d'écran : la tête sur son manche planté droit (voir `images/vues.jpg`).
- Jamais de bras ni de jambes, jamais rien dans les mains. Elle *est* le marteau.

## Ses gestes

1. **Elle veille.** La roue tourne. Les yeux sont ovales et calmes.
2. **Elle vise.** Un point orange arrive avec l'eau. Ses yeux le suivent et se plissent un peu.
3. **Toc.** Le point monte avec la roue et soulève le manche. La tête retombe sur la planche : le son du toc, une onde
   orange sur l'eau, les yeux en arcs (contente). Le point se pose sur l'étiquette de la semaine.
4. **Le silence.** L'eau s'arrête, la roue s'arrête, le marteau se tait. Les yeux deviennent inquiets, et Iris dit
   qu'une source ne coule plus.
- **Le lundi** : dix coups, dix points, dix entreprises à appeler.

## Le son

- `sons/toc.mp3` : le toc original de Runway (1,48 s), un coup de maillet sur une planche de mélèze, avec un filet
  d'eau derrière.
- `sons/toc-court.mp3` : le même, coupé juste sur l'attaque (0,78 s). C'est lui qu'on joue au moment exact où la tête
  touche la planche.
- `sons/eau.mp3` : l'eau du bisse et la roue, en boucle de 10 s. Toujours très bas, sous la voix.
- Aucune musique sans l'accord de Hiba.

## Les fichiers

| Fichier | Ce que c'est | Tâche Runway |
|---|---|---|
| `images/portrait.jpg` | La référence choisie par Hiba (« le 2ᵉ exemple ») : le portrait en studio | `5f4ca776-d1a9-4708-bb31-1352d802d844` |
| — | L'autre portrait, presque identique | `18730402-0698-409b-9b1d-b515d2f85bd9` |
| `bisse.jpg` (notes de travail) | Iris sur un bisse du Valais, dans les mélèzes d'automne | `3d9bcaf2-0ed3-44a2-a73d-77e86bfe20f4` |
| `toc.jpg` (notes de travail) | Le moment du toc : yeux contents, point posé, onde orange | `88dd24bf-63e8-463c-be40-09fc66d77afd` |
| `images/vues.jpg` | De face, de trois quarts, de profil, de dos (recadrée) | `c2a86371-cceb-4add-8f2a-1cdba41e4029` |
| `expressions.jpg` (notes de travail) | Elle veille, elle vise, c'est posé, elle s'inquiète (recadrée) | `c0267111-8f20-48d2-8787-9412e1fa36bf` |
| `sons/toc.mp3` | Le toc | `880c584c-2269-4bea-86ad-508f0f66ba3c` |
| `sons/eau.mp3` | L'eau du bisse, en boucle | `e1daf199-a000-48e9-8b34-227da59c3a45` |

- Les originaux sont aussi dans la bibliothèque Runway de Hiba. Les études (`bisse.jpg`, `toc.jpg`, `expressions.jpg`,
  `planche.html`, `modele-mouvement-3d.html`) sont dans les notes de travail (non publiées).
- `planche.html` (notes de travail) : la planche de la mascotte, à ouvrir dans un navigateur. Elle montre tout ce qui précède.
- `modele-mouvement-3d.html` (notes de travail) : un modèle en 3D, fait en code, qui montre seulement **l'ordre et le rythme** des gestes
  (la roue, le point qui monte, le manche qui se lève, le toc, le point posé sur l'étiquette). **Son rendu n'est pas
  l'image de la mascotte** : Hiba ne l'a pas aimé, ne le réutilise pas tel quel.

## Pour garder la même Iris dans Runway

- Passe toujours `portrait.jpg` (ou la tâche `5f4ca776…`) en image de référence, et redis la description du corps
  ci-dessus, mot pour mot.
- Évite les mots « character », « 3D animation film » et « film still » dans les consignes : Runway a refusé deux
  consignes de ce genre (contrôle « CHARACTER »). « Product photography » et « photorealistic photograph » passent bien.
- Une première vidéo faite le 12.10.2026 (10 s, 360 crédits) partait de l'ancienne image, celle du petit robot en bois
  avec des bras. Il y prenait un marteau dans les mains, ce qui est faux. Pars toujours de `portrait.jpg` ou de
  `bisse.jpg`, et écris : « the mascot is the hammer itself, it has no arms and holds nothing ».

## Règles d'usage

- Une seule pièce : la tête, le manche et la roue (et la planche).
- Un seul orange : la roue, le point, l'onde. Le reste est bois, verre, blanc et gris.
- Ni drapeau ni armoiries du Valais (réservés au canton, loi sur la protection des armoiries, art. 8), ni croix suisse.
  Pas de Cervin, pas de vache, pas de bouquetin.
- Iris ne décide jamais : elle prévient et pose le point. Le consultant décide.
- Elle garde son nom et se présente ainsi : « Je suis Iris, l'assistante de Proxsis. »
- Au générique : « Voix de synthèse (ElevenLabs) » et « Images de la mascotte : Runway ».

## Vérification des faits (13.10.2026, suite 8 § 6)

Recherche documentaire faite pour CLAIMS (lignes EXT-BISSE-MARTEAU, EXT-BISSE-AYENT, EXT-UNESCO-IRRIGATION) :
- **Confirmé en général** : sur les grands bisses, une roue mue par l'eau faisait battre un « marteau avertisseur » ; tant
  qu'il frappait, le gardien savait que l'eau coulait ; on l'appelait « le marteau du bisse ».
- **Non confirmé** : un marteau attesté précisément au bisse d'Ayent, et l'année 1442 (les sources disent 1442, 1448 ou
  « milieu du XVe siècle »). Dans les textes de Proxsis, on dit donc « sur les bisses du Valais » et, pour Ayent,
  « construit au milieu du XVe siècle », sans année. La phrase de l'histoire ci-dessus et de `planche.html`
  (« le bisse d'Ayent, 1442 ») est gardée telle quelle, mais n'est plus reprise ailleurs.
- **Confirmé** : l'irrigation traditionnelle, inscrite le 6 décembre 2023 au patrimoine culturel immatériel de l'UNESCO,
  avec sept pays ; la part suisse comprend les consortages du Valais (dont Ayent) et les prairies irriguées de
  l'Oberaargau.
