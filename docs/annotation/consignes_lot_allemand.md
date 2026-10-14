# Consignes : annoter le lot allemand sans lire l'allemand

Lot : 50 demandes d'autorisation de construire publiées en allemand au Bulletin officiel du Valais (« Baugesuche »).
Annotateurs : A1 et A2, francophones. Six publications sont annotées par les deux, à l'aveugle. Profil
d'annotation : « bo_de_structure ». À lire avant de commencer, avec le glossaire
`docs/annotation/glossaire_bo_de_fr.md` et le guide général `docs/annotation/guide_annotation.md`.

## En bref

- **Huit champs** : entreprise requérante, une personne physique est mentionnée, commune, date de publication,
  date d'expiration du délai, parcelle mentionnée, coordonnées mentionnées, commentaire.
- On n'annote **ni les métiers, ni le besoin de personnel, ni le montant, ni le début des travaux** (§ 6).
- On **repère** chaque information grâce au code de la ligne et au glossaire. On ne cherche pas à comprendre le
  texte allemand.
- **Aucune traduction automatique**, ni pour comprendre ni pour vérifier (§ 7).
- **Jamais de donnée personnelle** dans le commentaire. On ne cherche jamais à retrouver une valeur masquée.
- En cas de doute : laissez le champ vide et écrivez pourquoi en commentaire, en français.

## 1. Pourquoi ce lot est différent

Décision de Hiba du 06.10.2026 : personne ne lit l'allemand, ni dans l'équipe ni autour. Le lot allemand est donc
annoté **seulement sur les champs lisibles sans comprendre la langue** : noms propres, formes juridiques, communes,
dates, présence d'un champ. Le français et l'allemand sont mesurés séparément. Toute mesure sur ce lot porte la
mention suivante, reprise telle quelle (CLAIMS `BO-LECT-DE`) :

> allemand : mesure partielle (champs structurés) ; métiers non mesurés

La lecture des métiers en allemand sera vérifiée **pendant le pilote, avec des consultants germanophones de
Flexsis**. Ces consultants confirmeront aussi les équivalences du glossaire marquées « à confirmer ».

## 2. Avant de commencer

1. Lisez le guide général (`guide_annotation.md`), puis ces consignes et le glossaire. Gardez le glossaire ouvert
   à côté de la page.
2. Ouvrez **votre** page d'annotation du lot allemand (A1 ou A2), remise par Hiba. Elle reste sur votre poste,
   hors git (actuellement dans `data/manuel/textes/bo_vs_v1/de/pages/`). La page du profil « bo_de_structure »
   porte en tête l'encadré « Lot allemand : seuls les champs structurés sont annotés ; métiers non mesurés » et ne
   montre que les huit champs. Si vous voyez d'autres champs (métiers, montant, besoin), vous n'avez pas la bonne
   page : demandez-la à Hiba.
3. **Refusez la traduction proposée par le navigateur.** Chrome, Edge et Safari proposent « Traduire cette page »
   sur un texte allemand : répondez « Jamais pour cette langue », ou désactivez l'option avant de commencer.
4. Ne regardez ni le travail de l'autre annotateur ni une sortie de modèle.

## 3. Lire une publication

La page affiche le texte **filtré** : les personnes physiques, les adresses, les parcelles et les coordonnées sont
remplacées par `[masqué]`.

- **En tête**, les métadonnées : langue, rubrique et date de publication (« DE · BA-VS05 · AAAA-MM-JJ »).
- **Première ligne**, toujours en français : « Demande d'autorisation de construire — », suivi du titre allemand.
  La commune figure en général à la fin du titre, après la dernière virgule.
- **Lignes suivantes**, sous la forme `code : valeur`. Le code est un nom de champ français sans accent
  (`requerant`, `parcelle`, `expiration`…). Le glossaire (§ 3) donne pour chaque code l'intitulé allemand du PDF
  et l'intitulé français. Une valeur peut contenir plusieurs parties séparées par ` ; ` (par exemple un
  particulier masqué et une société).

Ne cliquez pas sur « voir la publication (Bulletin officiel) ». N'ouvrez jamais le portail ni le PDF officiel
pour compléter un champ : le texte filtré suffit pour les huit champs (même règle que pour le lot français,
notes de travail non publiées). Si une information manque ou est coupée, laissez le champ vide et commentez. Les intitulés
allemands du glossaire servent à relier les codes de la page au formulaire officiel. Ils ne sont pas une
invitation à lire le PDF.

## 4. Champ par champ

Suivez cet ordre : il va du plus mécanique au plus délicat.

### 4.1 Date de publication

- Recopiez la date des **métadonnées** en tête de la publication (« DE · BA-VS05 · AAAA-MM-JJ ») dans le champ
  « Date de publication ». La page ne la remplit pas d'avance.
- Ne prenez jamais une date du texte : ce sont d'autres dates (§ 4.2).

### 4.2 Date d'expiration du délai (« Ablauf der Frist »)

1. Trouvez la ligne `expiration :` (dans le PDF : « Ablauf der Frist »).
2. Elle est écrite `JJ.MM.AAAA` : annotez `AAAA-MM-JJ` (`07.09.2026` → `2026-09-07`). Un jour à un chiffre
   (`6.08.2025`) se lit de la même façon.
3. Ignorez ce qui suit la date (par exemple `21.09.2026 35` → `2026-09-21`). Ce reste vient sans doute de la mise en
   page du PDF.
4. Contrôle : la date tombe en général **31 jours** après la date de publication, parfois un peu moins (20 à
   30 jours ; voir `link_to_index` dans `gazette_pdf.py`). Si l'écart sort de cette plage, annotez quand même la
   date de la ligne `expiration` et écrivez « écart inhabituel » en commentaire.
5. Le paragraphe `moyen_de_droit` contient parfois « bis 7. September 2026 », c'est-à-dire « jusqu'au … ». C'est
   la même date : elle peut servir de confirmation. Les mois en toutes lettres figurent dans le glossaire (§ 8).
6. Une date précédée de « vom » (« du »), dans le titre, la zone ou le paragraphe, renvoie à une **autre**
   décision ou publication. On ne l'annote pas.
7. Pas de ligne `expiration`, ou pas de date lisible : laissez vide et commentez.

### 4.3 Commune

1. Lisez la **fin de la première ligne**, après la dernière virgule. C'est la commune du projet.
2. Confirmez avec la ligne `point_de_contact` (« Kontaktstelle »). Elle commence le plus souvent par
   « Gemeinde X », « Einwohnergemeinde X », « Stadtgemeinde X », « Gemeindeverwaltung X » ou
   « Bauverwaltung Gemeinde X ». X est la commune. Vous pouvez aussi confirmer avec « an die Gemeinde X » dans le
   paragraphe `moyen_de_droit`.
3. **Commission cantonale (KBK).** Si le point de contact est masqué ou si le paragraphe mentionne la « KBK »
   (en français : CCC, adresse à Sion), le dossier est traité par le canton. La commune du projet reste celle de la
   fin du titre. N'écrivez pas « Sion ».
4. Écrivez le **nom officiel**, sans NPA ni canton : « Stalden (VS) » s'écrit « Stalden ». Ne le francisez
   jamais : « Visp », pas « Viège » (glossaire, § 9).
5. **Nom coupé en fin de ligne**, par exemple « Gampel- Bratsch » : supprimez l'espace et gardez le trait d'union
   (« Gampel-Bratsch »). Si la partie qui suit commence par une **minuscule** (« Holz- bau »), supprimez le trait
   d'union et l'espace (« Holzbau »). La même règle vaut pour les raisons sociales.
6. **Communes à double nom.** Pour une commune du Haut-Valais, le texte allemand donne le nom officiel :
   recopiez-le. Si un texte allemand nomme une commune romande sous sa forme allemande (« Sitten », « Siders »),
   écrivez le nom officiel (« Sion », « Sierre ») et commentez « écrit en allemand ».
7. Fin du titre et point de contact différents : prenez la fin du titre et commentez « point de contact : autre
   commune ». Si le titre ne se termine pas par une commune du glossaire ni du répertoire (par exemple « mehrere
   Gemeinden », plusieurs communes), prenez la première commune citée ensuite et commentez.

### 4.4 Entreprise requérante

Ne regardez que la ou les lignes `requerant :` (« Gesuchsteller », « Gesuchstellende Partei »). Ne prenez jamais
le propriétaire, l'auteur des plans ni le bureau d'architectes à la place du requérant.

| Ce que vous voyez dans `requerant` | Entreprise requérante | Personne physique |
|---|---|---|
| Aucune ligne `requerant` | vide ; commentaire « pas de requérant indiqué » | selon les autres rôles (§ 4.5) |
| Seulement `[masqué]` | vide (particulier) | oui |
| Un nom terminé par une forme juridique (AG, GmbH, SA, Sàrl, KG, Genossenschaft…) | le nom **exactement** tel qu'écrit, forme juridique comprise | selon les autres rôles |
| `[masqué] ; Beispiel Bau AG` (particulier et société) | la **première personne morale** citée : `Beispiel Bau AG` | oui |
| Un organisme public : Gemeinde X, Einwohnergemeinde X, Burgergemeinde X, Stadtgemeinde X, Kanton Wallis, Dienststelle …, Bundesamt …, Pfarrei … | le nom tel qu'écrit (personne morale, comme dans le guide général) ; commentaire « organisme public » | selon les autres rôles |
| Une association, une fondation ou une coopérative : Verein …, Stiftung …, Genossenschaft …, Alpgenossenschaft … | le nom tel qu'écrit ; commentaire « association », « fondation » ou « coopérative » | selon les autres rôles |
| Un organisme dont une partie du nom est masquée (`Verein [masqué]`) | tel qu'affiché, `[masqué]` compris ; commentaire « nom partiellement masqué » | selon les autres rôles |
| Plusieurs lignes `requerant` | la première personne morale, dans l'ordre d'affichage | oui si l'une est `[masqué]` |

Règles d'écriture :

- **Ne traduisez rien** : « AG » reste « AG », « Gemeinde Naters » reste « Gemeinde Naters ». Gardez les
  trémas (ä, ö, ü), les majuscules et la ponctuation tels qu'ils sont affichés.
- Ne recopiez ni adresse ni NPA qui suivraient le nom.
- **Ce que vous ne devez jamais voir.** Une communauté privée (Erbengemeinschaft, Stockwerkeigentümergemeinschaft
  ou StWEG, Einfache Gesellschaft, Familie…) ou un nom de personne non masqué (« Herr … », un prénom suivi d'un
  nom, sans forme juridique) ne devrait pas apparaître. Si c'est le cas : laissez l'entreprise vide, cochez
  « personne physique », commentez « mention privée non masquée, à signaler », **sans recopier le nom**, et
  prévenez Hiba en ne donnant que l'identifiant de la publication.

### 4.5 Une personne physique est mentionnée (oui / non)

- **Oui** si au moins une ligne de rôle contient `[masqué]` : `requerant`, `proprietaire`, `auteur_plans`,
  `auteur_plans_entreprise`, `maitre_ouvrage` ou `autres_parties`. Le filtre masque tout ce qui, dans un rôle,
  n'est pas une organisation. C'est souvent le cas de l'auteur des plans (« Planverfasser »), qui est une
  personne.
- **Non** si aucune ligne de rôle ne contient `[masqué]`.
- Un `[masqué]` hors des lignes de rôle **ne compte pas**. Dans `parcelle` et `coordonnees`, ce sont des numéros.
  Dans le titre, la zone, le point de contact ou le paragraphe `moyen_de_droit`, il cache le plus souvent un
  numéro d'article, une adresse ou un mot rare, et on ne peut pas savoir lequel sans lire l'allemand. Pour que
  deux annotateurs arrivent au même résultat, ce lot précise ainsi la règle « en cas de doute : cochée » du guide
  général : seules les lignes de rôle décident.

### 4.6 Parcelle mentionnée (oui / non)

- **Oui** s'il existe une ligne `parcelle :` (« Parzelle »), **même si sa valeur est masquée** : c'est le cas
  normal.
- Oui aussi si le titre mentionne une parcelle (« Parzelle », « Parz. », « Grundstück »), même sans ligne
  `parcelle`.
- Non s'il n'y a ni ligne `parcelle` ni mention dans le titre. Une ligne `parcelle :` vide compte comme « non » et
  se commente « ligne parcelle vide ».
- On annote la **présence**, jamais la valeur. On ne lève pas le masque.

### 4.7 Coordonnées mentionnées (oui / non)

- **Oui** s'il existe une ligne `coordonnees :` (« Koordinaten »). Sa valeur est toujours `[masqué]`.
- Non sinon. Une ligne vide compte comme « non » et se commente.
- Là aussi, on annote la présence, jamais la valeur.

### 4.8 Commentaire

- En français, court : la raison d'un doute, d'un champ vide ou d'un cas limite. Vous pouvez citer un code de
  champ ou un mot du glossaire (« KBK », « Abänderungsgesuch »).
- **Jamais** de nom de particulier, d'adresse, de numéro de parcelle, de coordonnées, de numéro de téléphone ou
  d'e-mail. Pas non plus de valeur lue dans le PDF officiel ni de contenu masqué deviné.
- Ne recopiez pas de phrase allemande et n'écrivez pas de traduction.

## 5. Cas limites

| Situation | Que faire |
|---|---|
| Une société et un particulier sont requérants | La société dans « entreprise requérante » ; personne physique : oui. |
| La commune, la bourgeoisie, le canton ou un office fédéral est requérant | Nom tel qu'écrit (« Gemeinde X », « Burgergemeinde X ») ; commentaire « organisme public ». |
| Le requérant est `[masqué]` | Entreprise vide ; personne physique : oui. Ne cherchez pas qui c'est. |
| Le requérant est une société, le propriétaire `[masqué]` | La société ; personne physique : oui (le propriétaire est un rôle). |
| La commune a un double nom FR/DE | Nom officiel (glossaire, § 9) ; jamais la forme française d'une commune du Haut-Valais. |
| Commune ou nom coupé (« Brig- Glis ») | Recollez selon § 4.3, point 5. |
| La KBK traite le dossier | Commune de la fin du titre ; ni « Sion » ni « KBK ». |
| Le titre contient « Abänderungsgesuch » (demande de modification, à confirmer) | On annote de la même façon ; commentaire « demande de modification » si utile. |
| Le paragraphe dit que la publication en remplace une autre (« ersetzt … vom … », à confirmer) | On annote cette publication-ci ; la date après « vom » ne s'annote pas. |
| La date d'expiration est suivie d'un nombre | Seulement `JJ.MM.AAAA`. |
| Le texte porte « Es gibt keine Übersetzung » ou n'a que le titre | Ne devrait pas arriver dans ce lot : remplissez ce qui est lisible et commentez « contenu incomplet ». |
| Une société porte une forme française dans un texte allemand (« … SA ») | Telle qu'écrite. |
| Un mot ou un nom contient « ß » | Tel qu'écrit (citation originale) ; ne le corrigez pas en « ss ». |

## 6. Ce qu'on n'annote pas, et pourquoi

| Champ exclu | Pourquoi |
|---|---|
| **Métiers** | Pour savoir quels métiers un chantier fera travailler, il faut comprendre la description du projet (titre et objet), donc lire l'allemand. Une estimation au jugé, ou faite avec une traduction automatique, donnerait une référence qui mesure le traducteur et non la lecture. Les métiers sont **non mesurés** en allemand, puis vérifiés pendant le pilote avec des consultants germanophones de Flexsis. |
| **Besoin de personnel temporaire** | C'est un jugement métier fondé sur la même description : même raison. |
| **Montant** | Le formulaire du Bulletin officiel n'a pas de champ « coût ». Aucune des 808 publications complètes du corpus (277 en allemand, 531 en français) n'indique de montant. Un montant glissé dans le titre demanderait de lire l'allemand. |
| **Début des travaux** | Le formulaire n'a pas non plus de champ « début des travaux », et aucune des 808 publications n'en mentionne. Une mention éventuelle se trouverait dans le texte allemand. |

Ces champs restent donc hors de la référence allemande. Aucun résultat ne doit les présenter comme mesurés en
allemand : la mention est « allemand : mesure partielle (champs structurés) ; métiers non mesurés ».

## 7. Rappels

- **Aucune traduction automatique** : pas de DeepL, de Google Traduction, de traduction du navigateur ni
  d'assistant conversationnel. Il y a deux raisons. D'abord, la référence doit rester indépendante des outils
  qu'elle sert à évaluer. Ensuite, copier un texte dans un service externe le fait sortir de votre poste.
- **Données personnelles** : le texte est filtré, mais un oubli reste possible. Ne recopiez jamais un nom de
  particulier, ni dans un champ ni dans un commentaire. Signalez l'oubli à Hiba avec l'identifiant de la
  publication seulement.
- **Parcelles et coordonnées** : on annote leur présence, jamais leur valeur. On ne lève pas le masque.
- **Indépendance** : les six publications en double servent à mesurer l'accord entre vous. Ne vous concertez pas
  avant l'arbitrage.
- **Fin du travail** : exportez votre fichier (bouton « Exporter ») et remettez-le à Hiba par un canal privé. La
  comparaison des deux annotateurs puis l'arbitrage suivent le protocole du guide général. La référence est gelée
  avant toute mesure.

## 8. Exemples annotés (textes fictifs)

**Exemple 1 : société et particulier.** Métadonnées : « DE · BA-VS05 · 2026-08-14 ».

```text
Demande d'autorisation de construire — Neubau Einstellhalle, Naters
titre_projet : Neubau Einstellhalle
numero_econstruction : 0a1b2c3d
requerant : [masqué] ; Beispiel Holzbau AG
proprietaire : [masqué]
auteur_plans : [masqué]
auteur_plans_entreprise : Muster Architektur GmbH
parcelle : [masqué] Nr [masqué] Im [masqué] genannt [masqué]
coordonnees : [masqué]
zone : Wohnzone W2
moyen_de_droit : Allfällige Einsprachen … sind innert dreissig Tagen … an die Gemeinde Naters zu richten.
point_de_contact : Gemeinde Naters [masqué]
delai :
expiration : 14.09.2026
```

Annotation : entreprise requérante `Beispiel Holzbau AG` (et non `Muster Architektur GmbH`, qui est l'auteur des
plans) · personne physique **oui** · commune `Naters` · date de publication `2026-08-14` · expiration
`2026-09-14` (31 jours plus tard) · parcelle **oui** · coordonnées **oui** · commentaire vide.

**Exemple 2 : organisme requérant, dossier cantonal.** Métadonnées : « DE · BA-VS05 · 2026-09-04 ».

```text
Demande d'autorisation de construire — Sanierung Alphütte, Obergoms
titre_projet : Sanierung Alphütte
requerant : Alpgenossenschaft Beispielalp
proprietaire : Gemeinde Obergoms
auteur_plans_entreprise : Beispiel Planung AG
parcelle : [masqué] Nr [masqué]
coordonnees : [masqué]
zone : Landwirtschaftszone
moyen_de_droit : … bei der KBK … 1951 Sion … innerhalb von 30 Tagen …
point_de_contact : [masqué] 1950 [masqué]
expiration : 05.10.2026
```

Annotation : entreprise requérante `Alpgenossenschaft Beispielalp` (coopérative, recopiée telle quelle) ·
personne physique **non** (aucune ligne de rôle masquée ; les masques de `parcelle`, `coordonnees` et
`point_de_contact` ne comptent pas, § 4.5) · commune `Obergoms` (fin du titre ; pas « Sion ») · date de
publication `2026-09-04` · expiration `2026-10-05` · parcelle **oui** · coordonnées **oui** · commentaire
« coopérative ; dossier KBK ».
