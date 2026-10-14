# Module de conformité : CCT Location de services, obligation d'annonce, CH-ISCO-19, phases SIA et CFC

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

Date de consultation de toutes les sources : **2026-10-05**.

## Méthode, accès et limites

- Toutes les sources citées ont été **ouvertes** directement (« page ouverte »), une à une, à faible débit. Aucun compte, aucun formulaire. **Aucun appel à Job-Room** ni à une API qui demande une inscription.
- Pour lire les textes, ces fichiers officiels ont été téléchargés **hors du dépôt**, dans le dossier temporaire de la session :
  - le PDF de la CCT LS et son commentaire ;
  - l'arrêté du Conseil fédéral du 11.12.2025 ;
  - la directive LSE SPE ;
  - la liste SECO 2026 (PDF et XLSX) ;
  - la nomenclature CH-ISCO-19 (XLSX FR et DE) ;
  - les extraits gratuits SIA et CRB.

  **Aucun fichier n'a été ajouté au dépôt.** Les tailles indiquées « mesurées » viennent de ce téléchargement, pas de la page.
- Fedlex : les textes de loi ont été lus sur `www.fedlex.admin.ch/filestore/…`, que le robots.txt de ce domaine autorise. Le domaine `fedlex.data.admin.ch` interdit `/filestore/*`. On n'y a utilisé que le point SPARQL public, pour trouver l'adresse de la dernière version consolidée.
- Les extraits de textes légaux sont cités mot pour mot quand la formulation compte. Les lois et ordonnances ne sont pas protégées par le droit d'auteur (art. 5 al. 1 let. a LDA, [L6]). Les autres citations font moins de 15 mots.
- robots.txt vérifiés le 2026-10-05 :

| Site | robots.txt | Utilisation |
|---|---|---|
| www.tempservice.ch | interdit `/webEdition/`, `/cgi-bin/`, `/inc/`, `/tools/` | pages et `/docs/` autorisés |
| www.seco.admin.ch | `Disallow:` vide | autorisé |
| www.arbeit.swiss | `Disallow:` vide | autorisé (voir les conditions au § c) |
| www.fedlex.admin.ch | `Allow: /`, interdit seulement les URL `?print=` | autorisé |
| fedlex.data.admin.ch | interdit `/filestore/*` | seul `/sparqlendpoint` est utilisé |
| www.bfs.admin.ch, dam-api.bfs.admin.ch | pas de robots.txt (page 404) | aucune restriction déclarée |
| shop.sia.ch | interdit des dossiers techniques (`/DownloadSRD/`, `/JS/`…) | pages produit et sommaire gratuit autorisés |
| www.crb.ch / webshop.crb.ch | interdit `/neos/` ; `/api/*` et admin | pages publiques autorisées |

---

## a. CCT Location de services (CCT LS) : salaires minimaux 2026

### Version en vigueur

- **Texte** : CCT Location de services **2024-2027**. La brochure PDF de tempservice.ch est datée du **11 décembre 2025** [T1] (DE : [T2]).
- **Extension (DFO)** :
  - arrêté du Conseil fédéral, modification du **11.12.2025** (FF 2025 3547), en vigueur du **1.1.2026 au 31.12.2027** [T4] ;
  - il étend **l'art. 20 al. 1 et 5** (salaires minimaux 2026) ;
  - la page SECO des CCT étendues donne la CCT LS « valable jusqu'au 31.12.2027 », pour toute la Suisse [T5].
- **Champ** :
  - entreprises titulaires d'une autorisation fédérale ou cantonale (LSE) dont la location de services est l'**activité principale** (art. 2 al. 1) ;
  - sont exclus les travailleurs dont le salaire dépasse le gain maximal assuré SUVA (art. 2 al. 2) [T1].

### Catégories et salaires minimaux 2026 (art. 20 al. 1 et 5, texte étendu [T4], identique à [T1])

Montants soumis à l'AVS. Le salaire mensuel est versé 13 fois.

| Catégorie (FR / DE) | Par an | Par mois (×13) | Par heure |
|---|---|---|---|
| Employés sans formation professionnelle / Ungelernte | 50 277 | 3 867.45 | 21.22 |
| … au Tessin | 44 834 | 3 448.80 | 18.92 |
| … dans une région de hauts salaires | 53 050 | 4 080.75 | 22.39 |
| … Genève | 53 780 | 4 136.90 | 22.70 |
| **Employés spécialisés / Angelernte** (88 % des « avec formation ») | 53 920 | 4 147.70 | 22.76 |
| … au Tessin | 50 106.80 | 3 854.36 | 21.15 |
| … dans une région de hauts salaires | 57 580 | 4 429.25 | 24.30 |
| Employés avec formation professionnelle / Gelernte | 61 273 | 4 713.29 | 25.86 |
| … au Tessin | 56 940 | 4 379.96 | 24.03 |
| … dans une région de hauts salaires | 65 432 | 5 033.24 | 27.62 |

Autres règles de l'art. 20 [T1] :

- **Al. 2** : indexation automatique au 1er janvier, sur la prévision de renchérissement du SECO de septembre, si la DFO est accordée.
- **Al. 3** : les régions de hauts salaires sont l'agglomération de Berne, l'arc lémanique, BS, BL, ZH et GE. Les communes de Berne et de l'arc lémanique sont listées par NPA à l'annexe 3.
  - **Valais** : aucun NPA valaisan (19xx ou 39xx) ne figure à l'annexe 3. La liste de l'arc lémanique s'arrête à 1844, Villeneuve VD. Celle de Berne ne contient que des NPA 30xx et 31xx. Le Valais relève donc des montants **standard**. C'est une déduction de lecture, à confirmer sur tempdata.
- **Al. 4** : est « **avec formation professionnelle** » (Gelernte) la personne qui a :
  - un CFC de la branche ;
  - **ou** une formation professionnelle de base achevée d'au moins trois ans, appropriée à l'activité ;
  - **ou** une AFP avec au moins trois ans de pratique dans l'activité à exercer.
- **Al. 6** : pour un jeune qui vient de terminer son apprentissage, le minimum « avec formation » peut baisser de 10 % pendant la première année.
- **Al. 7** : un an compte 52,07 semaines à 42 heures, soit **2187 heures**.
- **Al. 8** : un salaire minimum cantonal ou communal s'applique s'il est plus élevé. Le texte de 2026 ne cite que NE et GE en note. Un salaire minimum cantonal valaisan n'a **pas été vérifié**.
- **Art. 19** : l'employeur classe le travailleur dans une classe de salaire et l'écrit dans le contrat. Il peut corriger ce classement **une fois** pendant le temps d'essai.

### La règle « quatre ans de pratique et 1 000 heures par an »

- **Article** : **art. 20 al. 5 CCT LS**, étendu par l'arrêté du 11.12.2025 [T4][T1]. Texte exact :

  > « Sont considérés comme employés spécialisés les travailleurs qui bénéficient de quatre années au minimum de pratique professionnelle dans l'activité à exercer, et pour laquelle il existe une formation professionnelle. Le travailleur doit avoir effectué au moins 1000 heures de travail par année civile. »

- DE [T2] : « Als angelernt gelten Arbeitnehmende mit mindestens vier Jahren Berufspraxis in der auszuübenden Tätigkeit, für die es eine Berufsbildung gibt. Der Arbeitnehmende muss dabei pro Kalenderjahr mindestens 1'000 Arbeitsstunden absolviert haben. »
- **Correction** : cette règle ne fait **pas** passer en catégorie « qualifié » (avec formation professionnelle). Elle crée la catégorie **« employé spécialisé »** (DE : **Angelernte**). Son minimum vaut **88 %** de celui des employés avec formation, soit 22.76 CHF/h en 2026 hors Tessin et hors hauts salaires.
- **Trois conditions cumulatives** :
  1. au moins 4 ans de pratique **dans l'activité à exercer** ;
  2. il existe une formation professionnelle (CFC/AFP) pour cette activité ;
  3. au moins 1 000 heures de travail **par année civile**.
- **Point ouvert** : le texte ne dit pas si les 1 000 heures sont exigées pour **chacune** des quatre années. Le commentaire officiel (version du 12.04.2019) [T3] reprend le texte sans le préciser. Interprétation **à faire valider** par tempcontrol ou le service juridique de swissstaffing.
- **Diplômes étrangers** (commentaire [T3]) :
  - professions réglementées : c'est le SEFRI ou l'autorité cantonale qui juge ;
  - autres professions : la CPSLS reprend les critères du SEFRI, avec équivalence si la formation étrangère dure au moins autant que la formation suisse.

### Priorité des CCT étendues de l'entreprise locataire (bâtiment)

- **Loi** : **art. 20 al. 1 LSE** [L3]. Si l'entreprise locataire est soumise à une CCT étendue, le bailleur doit appliquer au travailleur ses dispositions sur le **salaire et la durée du travail**.
  - Les contributions obligatoires à la formation continue et aux frais d'exécution s'appliquent aussi, au prorata.
  - **Al. 3** : un régime de **retraite anticipée** étendu doit aussi être respecté.
- **CCT LS, art. 3 al. 1** [T1] : la CCT LS « reprend, à l'exclusion de ses propres dispositions », les règles de salaire et de temps de travail des CCT étendues de l'entreprise locataire, et celles des CCT non étendues listées à l'annexe 1.
  - **Al. 2** : l'IJM, la LPP et les contributions ne sont pas reprises si les solutions de la CCT LS sont au moins équivalentes.
  - L'annexe 1 de 2026 ne contient **aucune CCT valaisanne** [T4].
- **Conséquence** : pour un maçon placé dans une entreprise soumise à la **CN**, ce sont les salaires minimaux et la durée du travail de la **CN** qui s'appliquent, pas l'art. 20 CCT LS.
- **CCT étendues utiles pour le bâtiment en Valais**, d'après les pages SECO du 2026-10-05 [T5][T6] :

| CCT étendue | Champ territorial | Valable jusqu'au | Remarque |
|---|---|---|---|
| **CN pour le secteur principal de la construction en Suisse** | toute la Suisse (exclusions partielles GE, VD) | 31.12.2031 | arrêté du 04.11.2025 en vigueur le 01.12.2025 ; modification du 05.03.2026 en vigueur le 01.04.2026 |
| CCT pour la retraite anticipée, secteur principal (CCT RA) | toute la Suisse **sauf VS** | 31.12.2034 | en VS : RETABAT (ci-dessous) |
| **CCT du second-œuvre romand** | FR, JU, Jura bernois, NE, **VS**, VD, GE | 31.12.2028 | modification du 11.12.2025 en vigueur le 01.01.2026 |
| CCRA (retraite anticipée, second œuvre romand) | BS, BL, FR, JU, JB, NE, **VS**, VD, GE, TI | 31.12.2028 | — |
| VS : CCT des entreprises de carrelage du canton du Valais | VS | 31.12.2026 | — |
| VS : CCT de la construction métallique du canton du Valais | VS | 31.05.2030 | — |
| VS : CCT des métiers de l'électricité du canton du Valais | VS | 31.05.2027 | la CCT nationale de l'électricité **exclut VS** |
| VS : CCT des métiers de la technique du bâtiment du canton du Valais | VS | 31.05.2030 | la CCT nationale des techniques du bâtiment **exclut VS** |
| VS : RETABAT (retraite anticipée, construction et carrelage) | VS | 31.12.2028 | — |
| VS : RETAVAL (préretraite) | VS | 31.12.2027 | champ des branches **non vérifié** |

- **CCT nationales étendues qui excluent le Valais** [T5] :
  - techniques du bâtiment (exclut GE, VD, VS) ;
  - électricité (exclut GE, VS) ;
  - enveloppe des édifices (exclut BS, BL, GE, VD, VS) ;
  - Holzbau (exclut les cantons romands, dont VS) ;
  - isolation (exclut GE, VD, VS) ;
  - revêtements de sol (exclut VS, entre autres).
- **Non vérifié ici** : les classes et montants de salaire de la CN et des CCT valaisannes. Ils sont à lire dans les arrêtés liés depuis [T5][T6], ou dans **tempdata**. tempservice présente tempdata comme la base de référence pour connaître les conditions minimales par profil professionnel : http://tempdata.ch/ (non consultée).
- Le rattachement d'un métier à une CCT dépend de l'**entreprise locataire**, pas seulement du métier. Le module doit donc demander « CCT de l'entreprise de mission » au lieu de la déduire du code ISCO.

---

## b. Obligation d'annoncer les postes vacants (Stellenmeldepflicht)

### Base légale (textes ouverts sur Fedlex)

- **Correction** : la base légale n'est **pas** l'art. 21a LSE. C'est **l'art. 21a LEI**, la loi sur les étrangers et l'intégration (RS 142.20) [L1].
  - Al. 3 : obligation d'annoncer et accès restreint pour une période limitée.
  - Al. 4 : envoi de dossiers par le SPE ; l'employeur convoque les candidats dont le profil correspond.
  - Al. 5 : exception quand le poste est pourvu par un demandeur d'emploi inscrit.
  - Al. 6 : autres exceptions et listes périodiques.
  - Al. 7 : droit de proposition des cantons.
- **Ordonnance** : **OSE**, RS 823.111 [L2], art. **53a** (valeur seuil), **53b** (annonce et restriction), **53c** (dossiers et retour), **53d** (exceptions), **53e** (cantons), **53f** (liste annuelle par le DEFR). Version consolidée au 01.08.2024, la plus récente avant le 2026-10-05.
- **Liste 2026** : **ordonnance du DEFR du 27 novembre 2025** (RS 823.111.3), en vigueur du **1.1.2026 au 31.12.2026** [L4].
- **Sanctions** (art. 117a LEI [L1]) :
  - amende jusqu'à **40 000 CHF** si l'obligation d'annoncer (art. 21a al. 3) ou de convoquer (art. 21a al. 4) est violée intentionnellement ;
  - jusqu'à **20 000 CHF** par négligence.
- **Directive d'application** du SECO, qui lie les organes d'exécution : « Directive LSE SPE », partie B, état au 01.07.2025 [S3]. Une version plus récente n'est **pas vérifiée**.

### Seuil

- **Art. 53a al. 1 OSE** : l'obligation vise les genres de profession (nomenclature suisse des professions) dont le **taux de chômage national** atteint ou dépasse **5 %**.
- La moyenne porte sur le **4e trimestre de l'année précédente et les trois premiers trimestres de l'année en cours**. Pour la liste 2026 : T4 2024 à T3 2025 [L2][S1].
- **Al. 2** : taux = chômeurs inscrits aux ORP / personnes actives (statistique SECO).

### Restriction de l'information (5 jours ouvrés)

- **Art. 53b al. 5 OSE** : l'employeur peut publier ailleurs « au plus tôt cinq jours ouvrés après la publication sur la plateforme du service public de l'emploi ».
- **Al. 6** : pendant ces cinq jours ouvrables, seuls les demandeurs d'emploi inscrits et les collaborateurs du SPE ont accès à l'annonce [L2].
- **Départ du délai** :
  - il commence le **premier jour ouvrable qui suit la mise en ligne** dans la partie protégée de la plateforme du SPE (directive B16) ;
  - l'accusé de réception **ne déclenche pas** le délai (B13) ;
  - samedis, dimanches et jours fériés nationaux, cantonaux et régionaux ne comptent pas (B17) ;
  - exemple officiel : mise en ligne le lundi 5.7.2021 ; délai du 6 au 12.7 ; publication libre dès le mardi 13.7 [S3].
- **Attestation** (art. 53b al. 4 OSE) : nom et adresse de l'employeur, **numéro de l'annonce**, **date à partir de laquelle** le poste peut être publié librement [L2].
- **Contenu obligatoire de l'annonce** (art. 53b al. 2 OSE) :
  - profession ;
  - activité et exigences ;
  - lieu ;
  - taux d'occupation ;
  - date d'entrée ;
  - durée déterminée ou indéterminée ;
  - adresse ;
  - nom de l'employeur ;
  - pour un **bailleur de services**, **nom de l'entreprise locataire** (let. i) [L2].
- **ORP compétent** : en location de services, celui du **siège de l'entreprise locataire** (directive B14) [S3].

### Délai de l'ORP (3 jours ouvrables)

- **Art. 53c al. 1 OSE** : « Dans les trois jours ouvrables à compter de la réception de l'annonce complète », le SPE transmet des dossiers pertinents ou dit qu'il n'en a pas [L2].
- La directive (B19) fait partir ces 3 jours de la **publication** sur la plateforme. Les deux formulations diffèrent un peu. Ce retour **ne raccourcit pas** les 5 jours [S3].
- **Art. 53c al. 2** : l'employeur indique au SPE :
  - quels candidats il juge appropriés et lesquels il a convoqués ;
  - s'il a engagé l'un d'eux ;
  - si le poste reste vacant.

  Il n'a pas à justifier ses choix (B23) [L2][S3].

### Ce qui concerne directement une agence de location de services

| Règle | Texte | Source |
|---|---|---|
| L'agence mandatée annonce **à la place** de l'employeur, avec toutes les obligations. Elle respecte aussi les 5 jours ouvrables. Les candidats de **sa propre base non inscrits au SPE** ne peuvent être contactés et engagés **qu'après** le délai. | Directive B8 | [S3] |
| Si plusieurs agences sont mandatées pour le même poste, **toutes** respectent l'obligation. | B9 | [S3] |
| Le bailleur de services est l'employeur. Une mission dans une nouvelle entreprise locataire n'est **pas** couverte par l'exception « personnel interne ». | Art. 53d al. 2 OSE ; B36 | [L2][S3] |
| Si l'entreprise locataire engage le travailleur loué, c'est un **nouvel engagement** à annoncer. | B36 | [S3] |
| Seul un poste **concret** dont le recrutement a commencé peut être annoncé. Un poste encore en planification ne le peut pas. | B7 | [S3] |
| Le SPE ne peut pas utiliser les noms d'entreprises locataires reçus par ce biais à des fins de concurrence. | B36 | [S3] |

### Exceptions (art. 21a al. 5 LEI ; art. 53d OSE)

| Exception | Vaut pour une agence de location de services ? | Source |
|---|---|---|
| Poste pourvu par une personne **inscrite au SPE (ORP) comme demandeur d'emploi** | **Oui**. Attention : « inscrit chez Flexsis » ne suffit pas, il faut être inscrit à l'ORP. Sinon B8 s'applique : attendre la fin du délai. | Art. 21a al. 5 LEI ; B27, B8 |
| Personne déjà employée depuis au moins **6 mois** dans l'entreprise ou le groupe, ou apprenti gardé après son apprentissage (let. a) | **Non** : art. 53d **al. 2** l'exclut pour les bailleurs de services | Art. 53d al. 1 let. a et al. 2 OSE |
| Rapport de travail de **14 jours civils au plus** (let. b) | **Oui**. Des missions successives de la même personne **pour le même profil** comptent comme une prolongation : dès que le total dépasse 14 jours civils, l'annonce est due. Pour des profils différents, pas d'annonce. | Art. 53d al. 1 let. b OSE ; B33 |
| Conjoint, partenaire enregistré ou parent (ligne directe, ou jusqu'au 1er degré en ligne collatérale) de la personne autorisée à signer (let. c) | En principe oui, mais rarement utile. Frères et sœurs = 2e degré, donc annonce due (B35). | Art. 53d al. 1 let. c OSE ; B34–B35 |

Sources : [L1][L2][S3].

Pour le produit, deux règles fermes :

1. Ne jamais proposer de découper une mission pour rester sous 14 jours.
2. Ne jamais publier ni contacter les candidats de la base non inscrits à l'ORP avant la date de publication libre indiquée sur l'attestation.

C'est le sens de B8 et B33 [S3].

---

## c. Liste 2026 des genres de profession soumis à l'obligation d'annonce

### Documents officiels

| Document | URL exacte | Format | Date | Taille |
|---|---|---|---|---|
| **Ordonnance du DEFR du 27.11.2025** (RS 823.111.3), texte légal | https://www.fedlex.admin.ch/eli/cc/2025/800/fr (HTML lu : https://www.fedlex.admin.ch/filestore/fedlex.data.admin.ch/eli/cc/2025/800/20260101/fr/html/fedlex-data-admin-ch-eli-cc-2025-800-20260101-fr-html.html) | HTML / PDF | 27.11.2025, état au 1.1.2026 | — |
| Liste SECO FR (`liste_meldepflichtige_berufsarten_2026_fr.pdf`), liée depuis la page « Obligation d'annoncer… et Check-Up pour 2026 » | https://www.arbeit.swiss/api/media/fileservice/sdweb-docs-prod-arbeitswiss-files/files/2026/05/26/239dbc64-d9d6-4b43-98a2-d3464f5d670e.pdf | PDF, 2 pages | affichée « 01.12.2025 » | non affichée ; mesurée 142 523 octets |
| Même liste, 2e copie (`Genres_profession_obligation_annonce_2026.pdf`), liée depuis la page générale | https://www.arbeit.swiss/api/media/fileservice/sdweb-docs-prod-arbeitswiss-files/files/2026/07/13/591833ce-f2fc-43f0-91bc-cc28c656eab1.pdf | PDF | non affichée | mesurée 169 583 octets (même texte) |
| Liste SECO DE (`liste_meldepflichtige_berufsarten_2026_de.pdf`) | https://www.arbeit.swiss/api/media/fileservice/sdweb-docs-prod-arbeitswiss-files/files/2026/05/26/a9e5c639-5421-4452-bd6a-09e8ae91e0fb.pdf | PDF, 2 pages | affichée « 01.12.2025 » | mesurée 138 599 octets |
| **Liste avec désignations** (`excel_meldepflicht_2026.xlsx`, FR/DE/IT) | https://www.arbeit.swiss/api/media/fileservice/sdweb-docs-prod-arbeitswiss-files/files/2026/06/10/753eab53-1b0d-44e4-93da-4a617650f637.xlsx | **XLSX** | aucune date affichée ; la cellule d'en-tête porte le 01.11.2025 | mesurée 36 785 octets |

- **Pages** : FR https://www.arbeit.swiss/fr/obligation-dannoncer ; DE https://www.arbeit.swiss/de/arbeitgebende/stellenmeldepflicht-2026 ; page générale https://www.arbeit.swiss/fr/employeurs/obligation-dannoncer-les-postes-vacants [S1][S2].
- **Ce que disent les pages** [S1] :
  - la liste est mise à jour chaque année au dernier trimestre et vaut du 1er janvier au 31 décembre suivant ;
  - pour 2026, deux genres s'ajoutent : agents d'entretien (5,3 %) et cuisiniers (5,3 %) ;
  - le genre le plus peuplé reste celui des **manœuvres du bâtiment** (88 187 actifs) ;
  - la part des actifs concernés passe de 6,5 % en 2025 à **10,8 %** en 2026 ;
  - une désignation ne donne qu'une **première indication**. L'**ORP** tranche selon les activités réelles du poste.
- **Pas de CSV** publié. La page n'a pas été vérifiée sur opendata.swiss.
- **Liste 2027** : le DEFR la fixe au 4e trimestre (art. 53f OSE [L2]). Elle n'était **pas trouvée** au 2026-10-05.

### Colonnes

- **PDF** (lu dans le fichier, la page ne les décrit pas) : `CH-ISCO-19` | `Genres de profession` | `Chômeurs` | `Actifs occupés` | `Taux de chômage`. Même structure dans l'ordonnance [L4].
- **XLSX**, feuille « Meldepflichtige Berufsarten », 10 colonnes (lues dans le fichier) :
  - `BERUFSART_NR / GENRE DE PROFESSION_NR / GENERE DI PROFESSIONE_NR` (code CH-ISCO-19 à 5 chiffres) ;
  - `BERUFSART_DE`, `GENRE DE PROFESSION_FR`, `GENERE DI PROFESSIONE_IT` ;
  - `BEZEICHNUNG_M_DE`, `DESIGNATION_M_FR`, `DENOMINAZIONE_M_IT` ;
  - `BEZEICHNUNG_W_DE`, `DESIGNATION_F_FR`, `DENOMINAZIONE_F_IT`.

  On y trouve **134 lignes** de désignations et **44 codes distincts**.
- **Piège pour le module** : l'ordonnance groupe certains codes, et le XLSX ne les détaille **pas tous**. Exemples :
  - « **90 ; 93 sans 93120** » vise aussi 90000, 93100, 93110, 93310 à 93340. Le XLSX ne donne que 93130, 93131, 93132, 93210, 93290 et 93330.
  - « 71240 ; 71241 » : le XLSX ne donne que 71241.
  - « 4225–4229 » : seulement 42260.
  - « 94 » : seulement 94110, 94121 et 94122.
  - « 962 » : seulement 96210 et 96230.
  - « 1221 » : 12211 et 12212.

  La règle d'appartenance doit donc partir des **préfixes de l'ordonnance**. Le XLSX ne sert qu'aux libellés.
- **Nomenclature** : CH-ISCO-19, codes à 5 chiffres (genres de profession). Certaines lignes sont agrégées à 2, 3 ou 4 chiffres.

### Lignes 2026 utiles pour le bâtiment et l'industrie (ordonnance [L4])

| Code | Genre | Taux de chômage |
|---|---|---|
| 71140 | Constructeurs en béton armé, maçons ragréeurs et assimilés | 10,4 % |
| 71190 | Métiers qualifiés du bâtiment non classés ailleurs | 7,0 % |
| 71230 | Plâtriers, constructeurs à sec | 10,0 % |
| 71240 ; 71241 | Monteurs en isolation ; isoleurs, enveloppe des bâtiments | 7,0 % |
| 71310 | Peintres en bâtiment et poseurs de papiers peints | 5,3 % |
| 72120 | Soudeurs et oxycoupeurs | 5,1 % |
| 72240 | Meuleurs, polisseurs et affûteurs | 7,5 % |
| 83440 | Conducteurs de chariots élévateurs | 7,2 % |
| 90 ; 93 sans 93120 | Professions élémentaires sip ; manœuvres des mines, du bâtiment (hors génie civil), des industries manufacturières et des transports | 13,5 % |

### Liste complète des codes et préfixes de l'ordonnance 2026 (lue sur Fedlex le 2026-10-06)

Ajout de l'audit de semaine 1 (m8) : tous les codes CH-ISCO-19 de l'ordonnance du DEFR du 27.11.2025, tels que codés dans `proxsis.compliance.SUBJECT_PREFIXES_2026` :

1221 ; 21130 ; 21310 ; 21330 ; 21660 ; 24331 ; 24332 ; 26310 ; 26320 ; 26330 ; 26550 ; 33320 ; 4222 ; 4223 ; 42240 ; 4225 à 4229 ; 51200 ; 51311 ; 51313 ; 71140 ; 71190 ; 71230 ; 71240 ; 71241 ; 71310 ; 72120 ; 72240 ; 73112 ; 81570 ; 83440 ; 90 ; 93 sans 93120 ; 91120 ; 92110 ; 92140 ; 94 ; 962.

Source : https://www.fedlex.admin.ch/eli/cc/2025/800/fr (version HTML du 1.1.2026, tableau de l'annexe).

### Conditions d'utilisation

- **robots.txt d'arbeit.swiss** : `User-Agent: *` / `Disallow:` vide. Tout est autorisé.
- **« Informations juridiques » d'arbeit.swiss** [S4] :
  - télécharger ne transfère aucun droit ;
  - la **reproduction** d'éléments du site demande une **autorisation écrite préalable** ;
  - l'intégration de pages dans un autre site demande aussi une autorisation, mais un simple lien n'en demande pas.
- **Ordonnance du DEFR** : c'est un acte officiel, **non protégé** par le droit d'auteur (art. 5 al. 1 let. a LDA [L6]).
- **Question pour Hiba** : stocker le **XLSX de désignations** du SECO dans le dépôt demande-t-il cette autorisation ? Recommandation : construire la table des codes à partir de l'ordonnance, citer le XLSX par lien, et demander l'accord du SECO avant de redistribuer le fichier.

---

## d. CH-ISCO-19 (OFS)

### Source officielle

- **Page** : https://www.bfs.admin.ch/bfs/fr/home/statistiques/travail-remuneration/nomenclatures/ch-isco-19.html. Le contenu se charge en JavaScript ; les liens ont été retrouvés par l'API publique DAM de l'OFS.
- **Fiche signalétique** (PDF, 90 011 octets) : https://dam-api.bfs.admin.ch/hub/api/dam/assets/23530787/master [B1]. Ce qu'elle dit :
  - CH-ISCO-19 reprend les **4 premiers niveaux** de la CITP-08 (ISCO-08) et ajoute un **5e niveau suisse**, les « genres » ;
  - la structure a **cinq positions** : grand groupe (1 chiffre), sous-grand groupe (2), sous-groupe (3), groupe de base (4), genre (5) ;
  - le 5e niveau peut être révisé **tous les 3 ans** (première fois au 01.01.2022) ;
  - elle remplace la NSP2000.
- **Fichier téléchargeable**, version actuelle : « Nomenclature suisse des professions CH-ISCO-19 — Intitulés de profession, titres des catégories et clé d'attribution » [B2].

| | FR | DE |
|---|---|---|
| Page de l'asset | https://www.bfs.admin.ch/asset/fr/36037208 | https://www.bfs.admin.ch/asset/de/36037209 |
| Lien direct | https://dam-api.bfs.admin.ch/hub/api/dam/assets/36037208/master | https://dam-api.bfs.admin.ch/hub/api/dam/assets/36037209/master |
| Format, taille (métadonnées OFS) | XLSX, 3 189 791 octets | XLSX, 3 169 788 octets |
| Publication | 04.07.2025 | 04.07.2025 |
| N° de commande | do-f-00.07-ch-isco-19-04 | — |
| Licence | **OPEN-BY**, « Open use – Must provide the source » | idem |

- **Anciennes versions (2022)** :
  - nomenclature seule, asset 23530848 (XLSX, 80 787 octets) ;
  - « Zuweisungsschlüssel », asset 23530845 (XLSX, 3 368 201 octets).
- **Un code à 8 chiffres ?** Oui, mais il ne désigne pas la même chose que le genre.
  - Le fichier 36037208 a une feuille `HCL_CH_ISCO_19_PROF_1_2_2` : 23 209 lignes, 30 colonnes.
  - Colonnes : niveaux 1 à 4, `DV_CH_ISCO_19_TYP` (**genre à 5 chiffres**), `Code` (**intitulé de profession à 8 chiffres**, par exemple 23101001 = Maçon), `Name_fr` (forme masculine | forme féminine).
  - Indicateurs : `ACTIVE`, `AVAM`, `DUPLICATE_F/M`, `GENDER_F/M`, `LEARNED_OR_PRACTICED`, `REDUCED_LIST_F/M`.
  - On y trouve 548 genres distincts et 22 937 intitulés actifs.
  - La liste SECO utilise les **genres à 5 chiffres**. Le code à 8 chiffres sert à rattacher un intitulé de poste à son genre.

### Codes probables pour les métiers demandés

Lecture du fichier FR et DE 36037208/36037209 : intitulé actif, de préférence marqué `REDUCED_LIST`, plus la variante CFC quand elle existe. « Soumis 2026 » se lit sur l'ordonnance [L4]. Le code reste « probable » : il dépend du poste réel, et l'ORP tranche.

| Métier | Intitulé CH-ISCO-19 retenu (code 8 chiffres) FR / DE | Genre (5 chiffres) FR / DE | Soumis 2026 ? |
|---|---|---|---|
| Maçon | 23101001 Maçon / Maurer | **71121** Maçons (sauf poêliers-fumistes) / Maurer und verwandte Berufe (ohne Ofenbau) | Non |
| Manœuvre de chantier (bâtiment) | 51103450 Manoeuvre, bâtiment / Allrounder, Hochbau | **93130** Manœuvres du bâtiment, sip / Hilfsarbeiter im Hochbau, onA | **Oui** |
| Manœuvre (gros œuvre) | 51103510 Ouvrier de la construction, secteur principal / Bauarbeiter, Bauhauptgewerbe | **93131** Manœuvres du bâtiment, domaine principal de la construction / Hilfsarbeiter im Hochbau, Bauhauptgewerbe | **Oui** |
| Manœuvre (second œuvre) | 51103511 Ouvrier de la construction, second œuvre / Bauarbeiter, Ausbaugewerbe | **93132** Manœuvres du bâtiment, second œuvre / Hilfsarbeiter im Hochbau, Ausbaugewerbe | **Oui** |
| Manœuvre (génie civil) | 51103316 Manoeuvre, génie civil / Allrounder, Tiefbau | **93120** Manœuvres de chantier de travaux publics / Hilfsarbeiter im Tiefbau | **Non** (exclu : « sans 93120 ») |
| Charpentier | 23103003 Charpentier / Zimmermann | **71151** Charpentiers / Zimmerleute | Non |
| Menuisier | 26105004 Menuisier / Schreiner | **71152** Menuisiers du bâtiment / Schreiner | Non |
| Plâtrier-peintre | 23203020 Plâtrier-peintre / Gipser und Maler | **71310** Peintres en bâtiment et poseurs de papiers peints / Maler und verwandte Berufe | **Oui** |
| (Plâtrier seul) | 23203018 Plâtrier / Gipser ; 23203037 Plâtrier constructeur à sec CFC / Gipser-Trockenbauer EFZ | **71230** Plâtriers, constructeurs à sec / Gipser, Trockenbauer | **Oui** |
| Peintre | 23204001 Peintre en bâtiments / Baumaler ; 23204056 Peintre CFC / Maler EFZ | **71310** (idem) | **Oui** |
| Carreleur | 23201036 Carreleur / Plattenleger ; 23201070 Carreleur CFC / Plattenleger EFZ | **71220** Poseurs de revêtements de sol et carreleurs / Boden- und Fliesenleger | Non |
| Électricien de montage | 23210056 Électricien de montage / Montage-Elektriker ; 23210068 … CFC / … EFZ | **74110** Électriciens du bâtiment et assimilés / Bauelektriker und verwandte Berufe | Non |
| Installateur-électricien | 23210042 Installateur-électricien / Elektroinstallateur ; 23210067 … CFC / … EFZ | **74110** (idem) | Non |
| Monteur sanitaire | 23211015 Monteur sanitaire / Sanitärmonteur ; 23211046 Installateur sanitaire CFC / Sanitärinstallateur EFZ | **71263** Installateurs sanitaires / Sanitärinstallateure | Non |
| Monteur en chauffage | 23205011 Monteur en chauffage / Heizungsmonteur ; 23205072 Installateur en chauffage CFC / Heizungsinstallateur EFZ | **71261** Installateurs de chauffage / Heizungsinstallateure | Non |
| Ferblantier | 23206002 Ferblantier / Spengler ; 23206027 Ferblantier CFC / Spengler EFZ | **71262** Ferblantiers / Bauspengler | Non |
| Couvreur | 23202001 Couvreur / Dachdecker | **71210** Couvreurs et zingueurs / Dachdecker | Non |
| Poseur de sols | 23201003 Poseur de revêtements de sols / Bodenleger | **71220** (idem carreleur) | Non |
| Serrurier / constructeur métallique | 25306002 Serrurier-constructeur (bâtiment) / Metallbauschlosser ; 25306034 Constructeur métallique CFC / Metallbauer EFZ | **72140** Charpentiers métalliers et monteurs de charpentes métalliques / Baumetallverformer und Metallbauer | Non |
| Grutier | 29503001 Grutier / Kranführer ; 29502033 Grutier dans la construction / Baukranführer | **83431** Conducteurs de grues, d'engins de levage divers et de matériels similaires (sans remontées mécaniques) / Kranführer, Aufzugmaschinisten und Bediener verwandter Hebeeinrichtungen (ohne Seilbahn) | Non |
| Machiniste (chantier) | 29502002 Machiniste de la construction / Baumaschinist ; 29502029 Conducteur de machines de chantier / Baumaschinenführer | **83422** Conducteurs de machines de chantier qualifiés / Führer von Erdbewegungs- und verwandten Maschinen, Baumaschinen | Non (variante routes : 83421, non soumise) |
| Soudeur | 25301015 Soudeur / Schweisser | **72120** Soudeurs et oxycoupeurs / Schweisser und Brennschneider | **Oui** |
| Mécanicien de production | 51102674 Mécanicien de production / Produktionsmechaniker ; 25401062 … CFC / … EFZ | **72001** Polymécaniciens et mécaniciens de production / Polymechaniker und Produktionsmechaniker | Non |
| Opérateur de machines | 51102342 Opérateur de machines automatisées / Anlagenführer ; 29507063 … CFC / Anlagenführer EFZ | **81000** Conducteurs de machines et d'installations fixes, sip / Bediener stationärer Anlagen und Maschinen, onA | Non. **À confirmer** : il existe des genres par industrie (81210, 81310…), et seul 81570 est soumis. |
| Logisticien | 51103508 Logisticien / Logistiker ; 33206092 Logisticien CFC / Logistiker EFZ | **43200** Employés d'approvisionnement, d'ordonnancement et des transports, sip / Bürokräfte im Bereich Materialwirtschaft und Transport…, onA | Non. **À confirmer** : un poste de manutention relève de **93330**, soumis ; un cariste de **83440**, soumis. |
| Polymécanicien | 25403028 Polymécanicien / Polymechaniker ; 25403032 … CFC / … EFZ | **72001** (idem) | Non |
| Automaticien | 51102659 Automaticien / Automatiker ; 25506064 … CFC / … EFZ | **74120** Mécaniciens et ajusteurs d'appareils électriques / Automatiker und verwandte Berufe | Non |

Règle pratique : dans le bâtiment, l'obligation 2026 touche surtout :
- les **manœuvres** (sauf génie civil) ;
- les **plâtriers** et les **peintres** ;
- les **soudeurs** ;
- les **coffreurs et ferrailleurs** (71140) ;
- les **échafaudeurs** (71190) ;
- les **étancheurs et façadiers** (71241).

---

## e. Références publiques pour le phasage : SIA 112, SIA 102, CFC (CRB)

### SIA 112:2014 « Modèle : Étude et conduite de projet » (DE : « Modell Bauplanung »)

- **Fiche produit** [A1] : SN 509 112, valable depuis le **01.11.2014**, 28 pages, **payante** (110 CHF, papier ou téléchargement).
- **Gratuit** : le **sommaire** (PDF, 5 pages, 44 619 octets).
  - FR : https://shop.sia.ch/a4658acf-50f9-4b19-9f5e-981a0a9b3abc/F/DownloadAnhang
  - DE : https://shop.sia.ch/bfe9decc-d1eb-4d73-8834-8e4c55cbc06d/D/DownloadAnhang

  Il donne la liste des phases et phases partielles ci-dessous [A2][A3].
- La SIA 112 décrit le **déroulement par phases**. Les mandats d'architectes et d'ingénieurs relèvent des règlements SIA 102, 103, 104, 105 et 108 (note préliminaire, [A2]).

| Phase | Phase partielle FR | Phase partielle DE |
|---|---|---|
| **1** Définition des objectifs / Strategische Planung | 11 Énoncé des besoins, approche méthodologique | 11 Bedürfnisformulierung, Lösungsstrategien |
| **2** Études préliminaires / Vorstudien | 21 Définition du projet de construction, étude de faisabilité ; 22 Procédure de choix de mandataires | 21 Definition des Bauvorhabens, Machbarkeitsstudie ; 22 Auswahlverfahren |
| **3** Étude du projet / Projektierung | 31 Avant-projet ; 32 Projet de l'ouvrage ; 33 Procédure de demande d'autorisation / dossier de mise à l'enquête | 31 Vorprojekt ; 32 Bauprojekt ; 33 Bewilligungsverfahren / Auflageprojekt |
| **4** Appel d'offres / Ausschreibung | 41 Appels d'offres, comparaison des offres, propositions d'adjudication | 41 Ausschreibung, Offertvergleich, Vergabe |
| **5** Réalisation / Realisierung | 51 Projet d'exécution ; 52 Exécution de l'ouvrage ; 53 Mise en service, achèvement | 51 Ausführungsprojekt ; 52 Ausführung ; 53 Inbetriebnahme, Abschluss |
| **6** Exploitation / Bewirtschaftung | 61 Fonctionnement ; 62 Surveillance / contrôle / entretien ; 63 Maintenance | 61 Betrieb ; 62 Überwachung / Überprüfung / Wartung ; 63 Instandhaltung |

Lien avec les signaux de Proxsis (interprétation, à valider) :
- une **mise à l'enquête** correspond à la phase partielle **33** ;
- une **adjudication** correspond à la fin de **41** ;
- le besoin de main-d'œuvre sur chantier arrive en **52**.

### SIA 102:2020 « Règlement concernant les prestations et honoraires des architectes »

- **Fiche produit** [A4] : SN 508 102, valable depuis le **01.01.2020**, 44 pages, **payante** (180 CHF).
- Un sommaire gratuit existe aussi sur la fiche produit, mais il n'a pas été lu.
- La répartition des prestations ou des honoraires par phase n'est **pas publique gratuitement** : **non vérifiée**.

### CFC (Code des frais de construction, DE : BKP), CRB, SN 506 500, édition 2017

- **Page CRB** [K1] : https://www.crb.ch/fr/normes-standards/codes-des-couts-de-construction/code-des-frais-de-construction-cfc-1
  - le CFC est une subdivision des coûts **orientée exécution**, par catégories de travaux (entrepreneurs, peintres, électriciens…) ;
  - il compte **quatre niveaux** : groupe principal, groupe, sous-groupe, catégorie ;
  - selon le CRB, le code à quatre chiffres correspond à peu près aux chapitres du CAN.
- **Norme payante** : brochure A4 de 82 pages, **132 CHF**, avec un glossaire en quatre langues [K4].
- **Gratuits** :
  - « Aperçu du CFC » (1 page, 29 212 octets) : https://www.crb.ch/_Resources/Persistent/3/a/1/1/3a1142c4fbb4acd81573f48a774d449032c5bad9/Einblick_BKP_fr.pdf [K2] ;
  - « Extrait de la norme CFC » (8 pages, 296 441 octets) : https://www.crb.ch/_Resources/Persistent/9/1/c/c/91ccc767e1dc5287ccd954463028ffb289a9103f/Auszug_BKP2017_fr.pdf [K3].
- **Structure publique**, d'après l'extrait [K3] :
  - codes : groupe principal à **1 chiffre**, groupe à **2 chiffres**, sous-groupe à **3 chiffres**, catégorie à **4 chiffres** avec un point après le 3e (ex. 211.0) ;
  - **groupes principaux** : 0 Terrain · 1 Travaux préparatoires · **2 Bâtiment** · 3 Équipements d'exploitation · 4 Aménagements extérieurs · 5 Frais secondaires · 6, 7, 8 Réserve · 9 Ameublement et décoration ;
  - exemples de groupes et sous-groupes publics ([K2]) : **20 Excavation** (201 Fouilles en pleine masse) ; **21 Gros œuvre 1** (211 Travaux de l'entreprise de maçonnerie, 211.0 Installations de chantier, 211.1 Échafaudages).
- **Groupes 22 à 29** : la liste n'est pas dans les extraits gratuits. Elle se trouve dans l'« Aperçu des 1er et 2e niveaux », p. 82 de la norme payante. **À vérifier** avant de s'en servir pour faire correspondre corps de métier et phase.
- **eCCC-Bât** (SN 506 511, édition 2020, 171 CHF) : code des coûts **par éléments**, complémentaire du CFC. Exemple public : C « Gros œuvre » → C01 « Fondation, radiers » → C01.01 [K5].

---

## Sources

Toutes consultées et ouvertes le 2026-10-05.

**CCT Location de services**
- [T1] tempservice, CCT Location de services 2024-2027, texte FR (11.12.2025) : https://www.tempservice.ch/docs/fr/tempservice/GAV_PVL_2024-2027_frz_ohne_Leerseiten.pdf ; liste des documents : https://www.tempservice.ch/fr/documents/download.php
- [T2] Idem, texte DE : https://www.tempservice.ch/docs/de/tempservice/GAV_PVL_2024-2027_dt_ohne_Leerseiten.pdf
- [T3] tempservice, Commentaire CCT Location de services (12.04.2019) : https://www.tempservice.ch/docs/fr/tempservice/GAV_Personalverleih_Kommentar_FR.pdf ; page entreprises (tempdata, contributions) : https://www.tempservice.ch/fr/tempservice/pour-les-entreprises-de-location-de-services.php
- [T4] SECO, arrêté du Conseil fédéral étendant la CCT de la location de services, modification du 11.12.2025 (FF 2025 3547) : https://www.seco.admin.ch/dam/fr/sd-web/n6upUXXDGNUr/personalverleih_aend_11_12_2025_fr.pdf
- [T5] SECO, CCT étendues de la Confédération : https://www.seco.admin.ch/fr/convention-collectives-de-travail-confederation
- [T6] SECO, CCT étendues du canton du Valais : https://www.seco.admin.ch/fr/conventions-collectives-de-travail-valais

**Lois (Fedlex)**
- [L1] LEI, RS 142.20, art. 21a et 117a (version du 12.06.2026) : https://www.fedlex.admin.ch/eli/cc/2007/758/fr
- [L2] OSE, RS 823.111, art. 53a à 53f (version du 01.08.2024) : https://www.fedlex.admin.ch/eli/cc/1991/408_408_408/fr
- [L3] LSE, RS 823.11, art. 19 et 20 (version du 01.01.2026) : https://www.fedlex.admin.ch/eli/cc/1991/392_392_392/fr
- [L4] Ordonnance du DEFR du 27.11.2025 sur la soumission de genres de profession à l'obligation d'annoncer les postes vacants pendant l'année 2026, RS 823.111.3 : https://www.fedlex.admin.ch/eli/cc/2025/800/fr
- [L6] LDA, RS 231.1, art. 5 : https://www.fedlex.admin.ch/eli/cc/1993/1798_1798_1798/fr

**SECO / travail.swiss**
- [S1] arbeit.swiss, « Obligation d'annoncer les postes vacants et Check-Up pour 2026 » : https://www.arbeit.swiss/fr/obligation-dannoncer (EN : https://www.arbeit.swiss/en/employers/job-registration-requirement-and-check-up-for-2026)
- [S2] arbeit.swiss, page générale « Obligation d'annoncer les postes vacants » : https://www.arbeit.swiss/fr/employeurs/obligation-dannoncer-les-postes-vacants
- [S3] SECO, Directive LSE SPE (Bulletin LSE SPE), partie B, état au 01.07.2025 : https://www.arbeit.swiss/api/media/fileservice/sdweb-docs-prod-arbeitswiss-files/files/2026/05/25/57fbe29d-7261-4347-8aed-bfff96a54f66.pdf
- [S4] arbeit.swiss, Informations juridiques : https://www.arbeit.swiss/fr/informations-juridiques

**OFS**
- [B1] OFS, fiche signalétique CH-ISCO-19 : https://dam-api.bfs.admin.ch/hub/api/dam/assets/23530787/master
- [B2] OFS, Nomenclature suisse des professions CH-ISCO-19 (intitulés, catégories, clé d'attribution), FR : https://www.bfs.admin.ch/asset/fr/36037208 ; DE : https://www.bfs.admin.ch/asset/de/36037209 ; métadonnées : https://dam-api.bfs.admin.ch/hub/api/dam/assets/36037208

**SIA**
- [A1] SIA-Shop, SIA 112/2014 F : https://shop.sia.ch/normenwerk/architekt/sia%20112/f/2014/F/Product (DE : https://shop.sia.ch/normenwerk/architekt/sia%20112/d/2014/D/Product)
- [A2] SIA 112:2014, sommaire FR (gratuit) : https://shop.sia.ch/a4658acf-50f9-4b19-9f5e-981a0a9b3abc/F/DownloadAnhang
- [A3] SIA 112:2014, sommaire DE (gratuit) : https://shop.sia.ch/bfe9decc-d1eb-4d73-8834-8e4c55cbc06d/D/DownloadAnhang
- [A4] SIA-Shop, SIA 102/2020 F : https://shop.sia.ch/normenwerk/architekt/sia%20102/f/2020/F/Product

**CRB**
- [K1] CRB, Code des frais de construction CFC : https://www.crb.ch/fr/normes-standards/codes-des-couts-de-construction/code-des-frais-de-construction-cfc-1
- [K2] CRB, Aperçu du CFC (PDF) : https://www.crb.ch/_Resources/Persistent/3/a/1/1/3a1142c4fbb4acd81573f48a774d449032c5bad9/Einblick_BKP_fr.pdf
- [K3] CRB, Extrait de la norme CFC 2017 (PDF) : https://www.crb.ch/_Resources/Persistent/9/1/c/c/91ccc767e1dc5287ccd954463028ffb289a9103f/Auszug_BKP2017_fr.pdf
- [K4] CRB webshop (prix CFC et eCCC) : https://webshop.crb.ch/fr/node/papierform-baukostenplan-26
- [K5] CRB, eCCC-Bât : https://www.crb.ch/fr/normes-standards/codes-des-couts-de-construction/code-des-couts-de-construction-batiment-eccc-bat-1
