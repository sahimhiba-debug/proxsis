# Glossaire allemand → français : demandes d'autorisation de construire du Bulletin officiel du Valais

Ce glossaire est destiné aux annotateurs francophones du lot allemand (A1, A2). Il se lit avec les consignes
`docs/annotation/consignes_lot_allemand.md` (R4, 2026-10-06, à relire).

**Ce glossaire ne traduit pas les publications.** Il aide à **repérer** où se trouve une information dans une
publication allemande : un intitulé, une forme juridique, un organisme, une commune ou une date. Aucune
équivalence ne vient d'une traduction automatique. Chaque ligne indique sa source. Une équivalence sans source
parallèle sûre porte la mention **à confirmer** : elle sera vérifiée pendant le pilote avec des consultants
germanophones de Flexsis. Elle ne change pas l'annotation.

Orthographe : on suit l'allemand de Suisse, avec « ss » et jamais « ß » (Strasse, dreissig). Une citation
originale reste telle qu'elle est imprimée. Sept publications du corpus écrivent par exemple « dreißig ».

## Sources

| Code | Source |
|---|---|
| **[L]** | Lecteur des PDF, `python/src/proxsis/gazette_pdf.py`, constantes `LABELS`, `HEADERS`, `DE_HEADER`, `NO_TRANSLATION` et `NO_TRANSLATION_DE`. Le lecteur rattache l'intitulé allemand et l'intitulé français au **même champ**, car le portail publie le même formulaire dans les deux langues, à la même place. |
| **[G]** | Gabarits mis en regard : le paragraphe « Rechtsmittel / Einsichtnahme » des publications allemandes et le paragraphe « Moyen de droit / Consultation » des publications françaises. On y trouve la même phrase à la même position, avec la même adresse postale ou les mêmes horaires. Ces textes filtrés viennent de la reconstruction v3 et restent hors git. Ce glossaire n'en reprend que des comptes. |
| **[B]** | Nom bilingue imprimé tel quel dans une publication réelle du Bulletin officiel. |
| **[D]** | Droit fédéral, publié officiellement en français et en allemand. Le glossaire cite le titre ou l'article de la loi : Code des obligations (CO, RS 220), Code civil (CC, RS 210), loi sur l'aménagement du territoire (LAT, RS 700), ordonnance sur l'organisation du gouvernement et de l'administration (OLOGA, RS 172.010.1, annexe 1). |
| **[F]** | Filtre de confidentialité et reconnaissance des entreprises : `python/src/proxsis/gazette_filter.py`, `python/src/proxsis/entities.py` et `python/src/proxsis/pii.py`. Le terme allemand et le terme français y figurent dans la même expression ou la même catégorie. |
| **[R]** | Répertoire officiel des localités de swisstopo, copié dans `data/referentiels/localites_vs.csv`. |
| **[A]** | Guide d'annotation existant, `docs/annotation/guide_annotation.md`. |

La colonne « Corpus DE » donne le nombre de publications où le terme ou le champ apparaît. Elle compte les
277 publications allemandes complètes de la reconstruction v3. Ce sont des comptes seulement, sans aucun contenu.
Les chiffres du lot gelé de 50 publications ne sont pas donnés, pour ne pas orienter l'annotation.

## 1. Ce que montre la page d'annotation

- La **première ligne** est toujours en français : « Demande d'autorisation de construire — », suivi du titre
  allemand. En général, le titre se termine par la commune, placée après la dernière virgule.
- Les lignes suivantes commencent par un **code** (par exemple `requerant :`) et non par l'intitulé allemand.
  L'intitulé allemand ne figure que dans le PDF officiel. Le tableau 3 donne les trois formes.
- La date de publication figure dans les métadonnées en tête de la publication, par exemple
  « DE · BA-VS05 · AAAA-MM-JJ ». Elle n'apparaît pas dans le texte.

## 2. En-tête et mentions du portail

| Allemand (PDF) | Français (PDF) | Dans la page | Source |
|---|---|---|---|
| Gesuch für Baubewilligung · Gesuch für Baubewilligungen · Baugesuch | Demande d'autorisation de construire | Première ligne, toujours en français | [L] `HEADERS`, `DE_HEADER` |
| Es gibt keine Übersetzung für diese Publikation. | Il n'existe pas de traduction pour cette publication. | N'apparaît pas : le lot ne contient que des publications complètes | [L] `NO_TRANSLATION_DE`, `NO_TRANSLATION` ; tests du lecteur |
| Abänderungsgesuch (zum bewilligten Baugesuch) | Modification du projet autorisé : **à confirmer** | Dans le titre (6 dans le corpus DE) | Aucun parallèle sûr. Des titres français portent « Modification du projet autorisé » (17 publications du corpus FR). |

## 3. Intitulés des champs

| Allemand (PDF) | Français (PDF) | Code dans la page | Sert à annoter | Corpus DE | Source |
|---|---|---|---|---|---|
| Titel des Bauprojekts | Titre du projet de construction | `titre_projet` | rien (titre en allemand) | 277 | [L] |
| Nummer für die Konsultation eConstruction | Numéro pour consultation eConstruction | `numero_econstruction` | rien | 251 | [L] |
| Gesuchsteller · Gesuchstellende Partei | Requérant(e) · Requérant | `requerant` | **entreprise requérante** ; personne physique | 272 | [L] |
| Grundeigentümer · Eigentümer | Propriétaire | `proprietaire` | personne physique | 273 | [L] |
| Planverfasser · Projektverfasser | Auteur(e) de plans · Auteur du projet | `auteur_plans` | personne physique | 264 | [L] |
| Planverfasser - Firma | Auteur(e) de plans - Entreprise | `auteur_plans_entreprise` | personne physique (si masqué) ; jamais le requérant | 136 | [L] |
| Bauherrschaft · Bauherr | Maître d'ouvrage · Maître de l'ouvrage | `maitre_ouvrage` | personne physique | 3 | [L] |
| Parzelle | Parcelle | `parcelle` | **parcelle mentionnée** (la valeur est masquée) | 276 | [L] |
| Koordinaten | Coordonnées | `coordonnees` | **coordonnées mentionnées** (la valeur est masquée) | 277 | [L] |
| Nutzungszone · Zone | Affectation(s) de la (des) zone(s) · Zone | `zone` | rien | 276 | [L] |
| Ausnahmebewilligung/en | Dérogation(s) | `derogations` | rien ; le « /en » final reste parfois collé à la valeur | 11 | [L] |
| Rechtsmittel / Einsichtnahme | Moyen de droit / Consultation | `moyen_de_droit` | commune et date, pour confirmation (voir § 7) | 277 | [L] |
| Kontaktstelle | Point de contact | `point_de_contact` | commune, pour confirmation | 277 | [L] |
| Auflagefrist | Délai de mise à disposition | `delai` | rien (presque toujours vide) | 251 | [L] |
| Ablauf der Frist | Expiration du délai | `expiration` | **date d'expiration du délai** | 277 | [L] |

Variantes des mots de rôle, au féminin ou au collectif : Gesuchstellerin, Grundeigentümerin,
Grundeigentümerschaft, Projektverfasserin, Planverfasserin. Elles ont le même rôle que la forme de base. Source :
[F] `pii.py`, qui les liste avec « Requérant », « Propriétaire » et « Auteur du projet ».

## 4. Formes juridiques (recopiées telles qu'écrites, jamais traduites)

| Allemand | Abréviation | Français | Corpus DE | Source |
|---|---|---|---|---|
| Aktiengesellschaft | AG | société anonyme, SA | 109 | [D] CO art. 620 ; [F] `entities.py` |
| Gesellschaft mit beschränkter Haftung | GmbH | société à responsabilité limitée, Sàrl | 41 | [D] CO art. 772 ; [F] `entities.py` |
| Genossenschaft | — | société coopérative | 3 | [D] CO art. 828 ; [F] `entities.py` (genossenschaft, coopérative) |
| Kommanditgesellschaft | KG | société en commandite | 0 | [D] CO art. 594 ; [F] `entities.py` (KG) |
| Kollektivgesellschaft | — | société en nom collectif, SNC | 0 | [D] CO art. 552 |
| Stiftung | — | fondation | 2 | [D] CC art. 80 ; [F] `entities.py` (stiftung, fondation : même code) |
| Verein | — | association | 1 | [D] CC art. 60 ; [F] `entities.py` (verein, association : même code) |
| in Gründung | — | en formation | 0 | [F] `entities.py` (même expression) |
| in Liquidation | — | en liquidation | 0 | [F] `entities.py` (même expression) |

Une société d'une publication allemande peut porter une forme française (« SA » : 5 publications du corpus DE).
On la recopie telle qu'elle est écrite. On n'écrit jamais « SA » à la place de « AG », ni l'inverse.

## 5. Organismes publics et collectivités (conservés par le filtre)

Le filtre garde ces noms. S'ils sont requérants, on les recopie tels qu'ils sont écrits : ce sont des personnes
morales ([A]).

| Allemand | Français | Corpus DE | Source |
|---|---|---|---|
| Gemeinde (X) | commune (« Commune de X ») | 251, en tête du point de contact | [L] même champ (Kontaktstelle / Point de contact) : « Gemeinde X » ↔ « Commune de X » ; [F] `commune_of` retire l'un comme l'autre et garde le nom de la commune |
| Einwohnergemeinde | la commune (politique) ; terme juridique français exact : **à confirmer** | 22 | [F] `commune_of`, `_PUBLIC_START` |
| Stadtgemeinde · Stadt | la commune (ville), « Ville de X » ; terme exact : **à confirmer** | 15 | [F] `commune_of` traite « Stadtgemeinde », « Stadt » et « Ville de » de la même façon |
| Munizipalgemeinde | commune municipale : **à confirmer** | 0 | [F] `commune_of` |
| Gemeindeverwaltung | administration communale | 208 | [G] « bei der Gemeindeverwaltung » ↔ « auprès de l'administration communale » |
| Bauverwaltung (Gemeinde X) | service communal des constructions : **à confirmer** | 19 | Aucun parallèle exact. Le paragraphe français dit parfois « service des constructions ». |
| Burgergemeinde | bourgeoisie | 5 | [F] `_PUBLIC_START` ; tests du lecteur : « Bourgeoisie de Sion » et « Burgergemeinde Brig » sont tous deux des organismes publics |
| Pfarrei | paroisse | 1 | [F] `_PUBLIC_START` (paroisse, pfarrei) |
| Kirchgemeinde | paroisse (commune ecclésiastique) : **à confirmer** | 0 | [F] `_PUBLIC_START` |
| Kanton Wallis | Canton du Valais | 3 | [B] point de contact bilingue : « Canton du Valais - Service de l'agriculture, Kanton Wallis - Dienststelle für Landwirtschaft » |
| Staat Wallis | Etat du Valais : **à confirmer** (absent du corpus) | 0 | [F] `_PUBLIC_START` |
| Dienststelle (für …) | Service (de …), service cantonal | 0 (5 publications françaises portent le nom bilingue) | [B] même nom bilingue |
| Bundesamt (für …) | Office fédéral (de …) | 1 | [D] OLOGA, annexe 1 : liste officielle des unités en français et en allemand ; [F] `_PUBLIC_START` |
| KBK | CCC, commission cantonale des constructions | 25 | [G] même phrase, même adresse postale à Sion (1951), mêmes horaires. Forme développée « Kantonale Baukommission » : **à confirmer** (absente du corpus) |
| Alpgenossenschaft | consortage d'alpage : **à confirmer** | 0 | [F] `_ASSOCIATION_START` (consortage, geteilschaft, alpgenossenschaft) |
| Geteilschaft | consortage : **à confirmer** | 0 | [F] `_ASSOCIATION_START` |
| Zweckverband | association intercommunale : **à confirmer** | 0 | [F] `_PUBLIC_START` (association intercommunale, zweckverband) |

## 6. Communautés privées et marqueurs de personnes (masqués par le filtre)

Le filtre remplace ces mentions par `[masqué]` avant tout enregistrement. Elles ne figurent donc pas dans la page.
Une communauté privée compte comme **personne physique**. Ce n'est jamais une entreprise.

| Allemand | Français | Source |
|---|---|---|
| Erbengemeinschaft | hoirie, communauté héréditaire | [D] CC art. 602 ; [F] `_PRIVATE_COLLECTIVE` (hoirie, erbengemeinschaft) |
| Stockwerkeigentum · Stockwerkeigentümergemeinschaft (abréviation « StWEG » : **à confirmer**) | propriété par étages (PPE), communauté des propriétaires d'étages | [D] CC art. 712a ; [F] `_PRIVATE_COLLECTIVE` (ppe, copropriété, stockwerkeigent…) |
| Einfache Gesellschaft | société simple | [D] CO art. 530 ; [F] `_PRIVATE_COLLECTIVE` |
| Familienstiftung | fondation de famille | [D] CC art. 335 ; [F] `_PRIVATE_COLLECTIVE` |
| Familie · Fam. | famille | [F] `_PRIVATE_COLLECTIVE` |
| Wohnsitz | domicile | [F] `_ROLE_START`, `_ADDRESSEE` (Domicile, Wohnsitz) |
| vertreten durch | représenté par | [F] `_SEP` |
| zuhanden · z. Hd. | à l'attention de | [F] `_SEP`, `_ADDRESSEE` |
| Herr · Frau | Monsieur · Madame | [F] `_ADDRESSEE` |
| Vertreter · Vertreterin | représentant · représentante | [F] `pii.py` |
| Architekt | architecte | [F] `_ROLE_START` |

## 7. Paragraphe « Rechtsmittel / Einsichtnahme » (rien à annoter, sauf pour confirmer)

Ce paragraphe est un texte type. Il ne sert qu'à confirmer la commune et la date d'expiration. Un `[masqué]` à
l'intérieur cache le plus souvent un numéro d'article ou une adresse.

| Allemand | Français | Corpus DE | Source |
|---|---|---|---|
| Einsprache(n) | opposition(s) | 267 | [G] |
| Rechtsverwahrung(en) | réserve(s) de droit (privé) | 41 | [G] « Einsprachen/Rechtsverwahrungen » ↔ « oppositions / réserves de droit privé » |
| Amtsblatt · im digitalen Amtsblatt (amtsblatt.vs.ch) · eBO | Bulletin officiel (eBO) | 125 | [G] |
| innert dreissig Tagen · innerhalb von 30 Tagen | dans un délai de 30 jours | 222 · 37 | [G] |
| nach Veröffentlichung · ab dem Datum der Veröffentlichung | à partir de la date de la publication | 67 · 25 | [G] |
| an die Gemeinde X zu richten | à adresser à la commune X | 203 | [G] (« à l'Administration communale, CP …, NPA commune ») |
| Postfach | case postale (CP) | 28 | [G] |
| werktags · Uhr | les jours ouvrables · h | 25 | [G] |
| Gesuchsdossier · eingesehen werden | dossier · être consulté | 25 · 201 | [G] |
| BauG | LC, loi cantonale sur les constructions | 173 | [G] « aux articles … LC » ↔ « in den Artikeln … BauG » |
| RPG (Art. 24 RPG) | LAT (art. 24 LAT) | 5 | [D] LAT, RS 700 |

## 8. Dates

| Forme allemande | Lecture | Source |
|---|---|---|
| `Ablauf der Frist: 07.09.2026` | jour.mois.année → annoter `2026-09-07` | [L] le lecteur lit de la même façon « Ablauf der Frist » et « Expiration du délai : 07.11.2026 » |
| `6.08.2025` (jour sur un chiffre) | `2025-08-06` | corpus DE : 1 date sur 287 |
| `7. September 2026` | jour, point, mois en toutes lettres, année → `2026-09-07` | corpus DE : la date qui suit « bis » est la même que celle de la ligne `expiration` de la publication (10 publications) |
| bis … | jusqu'au … (fin du délai) | même source que la ligne précédente |
| vom … | du … : date d'une **autre** décision ou publication, à ne pas annoter | [A] « journal n° … du … » ↔ « Tagesregister Nr. … vom … » |

| Mois | N° | Français | Source |
|---|---|---|---|
| Januar | 01 | janvier | nom usuel, absent du corpus (période août-septembre) |
| Februar | 02 | février | idem |
| März | 03 | mars | idem |
| April | 04 | avril | idem |
| Mai | 05 | mai | idem |
| Juni | 06 | juin | idem |
| Juli | 07 | juillet | idem |
| August | 08 | août | idem (en chiffres seulement dans le corpus) |
| September | 09 | septembre | corpus DE : « 7. September 2026 » ↔ `07.09.2026`, dans la même publication |
| Oktober | 10 | octobre | corpus DE : « 5. Oktober 2026 » ↔ `05.10.2026`, dans la même publication |
| November | 11 | novembre | nom usuel, absent du corpus |
| Dezember | 12 | décembre | idem |

## 9. Communes à double nom

Règle : on écrit le **nom officiel** (répertoire [R]), sans NPA ni canton (« Stalden (VS) » → « Stalden »). Pour
les communes du Haut-Valais, c'est le nom imprimé dans la publication allemande. On ne le francise jamais.

| Nom officiel [R] | Forme allemande | Forme française usuelle |
|---|---|---|
| Brig-Glis | Brig-Glis | Brigue-Glis |
| Visp | Visp | Viège |
| Leuk | Leuk | Loèche |
| Leukerbad | Leukerbad | Loèche-les-Bains |
| Raron | Raron | Rarogne |
| Salgesch | Salgesch | Salquenen |
| Varen | Varen | Varone |
| St. Niklaus | St. Niklaus | Saint-Nicolas |
| Turtmann-Unterems | Turtmann-Unterems | Tourtemagne pour Turtmann ; nom français de la commune fusionnée : **à confirmer** |
| Goms | Goms | Conches (la vallée) ; nom français de la commune : **à confirmer** |
| Sion | Sitten | Sion |
| Sierre | Siders | Sierre |
| Martigny | Martinach | Martigny |

Le nom officiel vient de [R]. Les formes françaises des communes du Haut-Valais et les formes allemandes des
communes romandes sont des noms d'usage courant : aucune source du dépôt ne les donne. Elles servent seulement à
reconnaître une commune. On ne les écrit pas dans l'annotation.
