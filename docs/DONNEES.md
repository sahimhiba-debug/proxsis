# Données

Ce que Proxsis lit, d'où cela vient, sous quelles conditions, comment les données personnelles sont écartées, et ce
qui est réel ou fictif. Les conditions de chaque source, lues le 05.10.2026, sont dans
[docs/recherche/conditions_2026-10-05.md](recherche/conditions_2026-10-05.md) (robots.txt archivés dans
`data/conditions/`) ; celles de simap.ch, relues le 07.10.2026, sont citées ci-dessous
([§ Conditions de simap.ch](#conditions-de-simapch), archive `data/conditions/2026-10-07/`).

## Sources

| Source | Ce qu'on en tire | Accès | Règle |
|---|---|---|---|
| **simap.ch** (marchés publics) | adjudications de construction : entreprise lauréate, adjudicateur, date, titre, montant publié | API officielle seulement (`connectors/simap.py`), débit limité | la mention obligatoire « Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi. » accompagne toute donnée simap, à l'écran et dans les fichiers (test `e2e/mentions.spec.ts`) |
| **Bulletin officiel du Valais** (demandes d'autorisation de construire) | quelle entreprise a quel rôle dans quel projet | **consultation humaine uniquement** : une personne télécharge les exports PDF et XML ; aucun script n'appelle le portail (`proxsis.http.MANUAL_ONLY_HOSTS` le bloque) | filtre des personnes avant toute écriture (ci-dessous) |
| **swisstopo** (données ouvertes) | localités et codes postaux ; contours des communes (carte de la présentation) | fichiers OGD, copie versionnée dans le dépôt | attribution « © swisstopo » |
| **geo.admin.ch** | géocodage, registre des bâtiments | API, ≤ 20 requêtes par minute | — |

Les sources qui demandent une inscription (Zefix, par exemple) ne sont pas utilisées sans l'accord de Hiba ; les
portails dont le robots.txt interdit l'accès automatisé ne sont pas appelés.

## Conditions de simap.ch

Relues le 07.10.2026 sur les pages publiques https://www.simap.ch/de/about/legal et /fr/about/legal (versions,
empreintes et méthode : `data/conditions/2026-10-07/INDEX.md`). Proxsis utilise l'API **sans compte** : ce sont les
« AGB der Nutzung des Application Programming Interfaces (API) von simap.ch » (ci-dessous « AGB API ») qui
s'appliquent, et, pour ce qu'elles ne règlent pas, les AGB générales de www.simap.ch (AGB API, ch. 2).

- **Version** : les AGB API n'ont pas changé depuis la lecture du 05.10.2026 ; dernière modification le 13.11.2023.
  La « version du 30.09.2023 » notée jusqu'ici est le titre de la page française ; la page allemande titre
  « Version vom 29.09.2009 », avec les mêmes modifications (30.03.2017, 13.11.2023). Les AGB générales ont été
  modifiées le **01.07.2026** (rédaction, chapitres supprimés, protection des données).
- **La version allemande fait foi** : « Im Fall von Widersprüchen zwischen den verschiedenen Sprachfassungen der
  vorliegenden AGB ist die deutsche Version massgebend. » (AGB API, ch. 13, al. 2). Chaque passage est donc cité en
  allemand, puis en français.

### Les quatre points annoncés par une autre IA, vérifiés dans le texte

**1. Transmission à des tiers dès 8 h le jour de la publication : confirmé.** AGB API, ch. 5, al. 2, dernière
phrase :

> « Die simap-Daten dürfen Dritten ab 8:00 Uhr des Erscheinungstages bekannt gegeben werden. »
>
> « Les données simap.ch peuvent être communiquées à des tiers dès 8 h 00 le jour de leur publication. »

L'heure est celle de Zurich : « Den Nutzenden ist zudem bewusst, dass sämtliche erfassten und dargestellten
Uhrzeiten der Zeitzone «Europe/Zurich» entsprechen. » (AGB générales, ch. 4.1, al. 2).

**2. Contenu publié séparé visuellement des commentaires : confirmé, avec deux règles de plus** (ne rien modifier ;
ne jamais donner l'apparence d'une publication officielle). AGB API, ch. 5, al. 2, phrases 1 à 3 :

> « Die simap-Daten dürfen inhaltlich nicht verändert werden und müssen so dargestellt werden, dass sie sich optisch
> deutlich von Kommentaren oder ähnlichen Zusätzen unterscheiden. Sie sind mit folgendem Hinweis zu versehen: «Dies
> ist keine amtliche Veröffentlichung. Massgebend sind die auf der Plattform www.simap.ch veröffentlichten Daten.»
> Weder in der Werbung noch auf der Verpackung, dem Datenträger oder dem elektronischen Medium darf der Eindruck
> erweckt werden, es handle sich um eine amtliche Veröffentlichung. »
>
> « Le contenu des données simap.ch ne doit pas être modifié et elles doivent être présentées de sorte à,
> visuellement, se distinguer clairement des commentaires ou adjonctions analogues. Elles doivent être assorties de la
> remarque suivante: «Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch
> font foi.» Ni la publicité, ni le conditionnement, ni le support de données ou le support électronique ne doivent
> donner l'impression qu'il s'agit d'une publication officielle. »

**3. Diffusion des corrections : confirmé, et aussi les déclarations de simap sur la qualité des données.** AGB API,
ch. 5, al. 2, phrase 4 :

> « Zudem hat der API-Benutzer die Pflicht, Angaben, welche der Verein zur Qualität der gelieferten Daten macht, zu
> veröffentlichen sowie allfällige Berichtigungen von simap-Daten zu publizieren. »
>
> « L'utilisateur de l'API simap.ch a en outre l'obligation de publier les déclarations de l'association sur la
> qualité des données, tout comme les corrections éventuelles de données simap.ch. »

**4. Règles propres aux pièces jointes : pas dans les AGB API ; les AGB générales règlent les documents d'appel
d'offres.** Les documents d'appel d'offres ne s'obtiennent par l'API qu'authentifié comme soumissionnaire
(« Authentifizierung als Anbieter: Bezug von Ausschreibungsunterlagen », AGB API, ch. 6) ; sans compte, Proxsis ne
les lit pas. S'il les lisait un jour :

> « Wer Ausschreibungsunterlagen herunterlädt, verpflichtet sich dadurch gegenüber der Auftraggebenden und den an
> den Ausschreibungsunterlagen Berechtigten, allfällige Bedingungen oder Einschränkungen der Weiterverwendung der
> Ausschreibungsunterlagen einzuhalten, die in den Ausschreibungsunterlagen angebracht sind, oder die sich aus dem
> Urheberrecht oder der anderen Gesetzgebung ergeben. » (AGB générales, ch. 9.1, al. 3)
>
> « Quiconque télécharge des documents d'appel d'offres s'engage ainsi, vis-à-vis des adjudicateurs et des ayants
> droit des documents d'appel d'offres, à respecter les éventuelles conditions ou limitations quant à la
> réutilisation des documents d'appel d'offres telles qu'elles figurent dans les documents d'appel d'offres ou
> découlent du droit d'auteur ou d'une autre législation. »

Les adjudicateurs doivent y mentionner ces restrictions (AGB générales, ch. 4.5, al. 2). Et simap peut retirer de
l'accès des données particulièrement sensibles : « Der Verein behält sich das Recht vor, im Einzelfall besonders
sensible Daten vom Bezug auszunehmen. » (AGB API, ch. 4, al. 1).

### Autres obligations du même texte

- **Usage commercial et transmission permis** : « API-Benutzer können Publikationsdaten für kommerzielle Zwecke
  beziehen und an Dritte weitergeben. » (AGB API, ch. 4, al. 1 ; FR : « Les utilisateurs de l'API simap.ch peuvent
  obtenir des données de publication à des fins commerciales et les transmettre à des tiers. »).
- **Obligations transmises aux utilisateurs de Proxsis** : « Der API-Benutzer muss die Verpflichtungen der
  vorliegenden AGB und den Allgemeinen Nutzungsbedingungen auf sämtliche Personen überbinden, denen er Zugang zu den
  simap-Daten verschafft. Er muss sicherstellen, dass nur Befugte und über die Einschränkungen der Datennutzung
  informierte Personen Zugang zu den simap-Daten erhalten. » (AGB API, ch. 5, al. 3 ; la phrase suivante demande
  de surveiller le respect de ces conditions, et de signaler sans délai tout usage abusif à l'association simap.ch).
- **Contenu du site** : reproduire, publier ou « relier » (« Verknüpfung (insbesondere Integration in eine Website
  oder ins Intranet) ») le contenu de www.simap.ch demande l'accord écrit de simap (AGB générales, ch. 9.1, al. 2).
  Proxsis ne reprend que des données de l'API (permises par le ch. 4 des AGB API) et ne lit aucune page du site ;
  ses liens simples vers la page publique de chaque publication restent **à faire confirmer par simap** (le terme
  « Verknüpfung » vise surtout l'intégration).
- **Changements des conditions** : annoncés à l'avance aux seuls développeurs inscrits (AGB API, ch. 6, dernier
  alinéa, et ch. 8) ; l'inscription est gratuite et facultative, **à décider par Hiba** (elle n'a pas été faite).

### Conformité de Proxsis au 07.10.2026

| Règle | Aujourd'hui | À faire |
|---|---|---|
| Mention obligatoire | sur chaque écran et dans chaque fichier qui montre une donnée simap (test `e2e/mentions.spec.ts`) | — |
| Dès 8 h le jour de publication | la rubrique « Chaque matin, en direct de simap » (suite 10 du 13.10.2026 ; « Cette semaine » avant) ne montre jamais une publication du jour de la lecture : lue chaque jour ouvrable dès 6 h, elle montre la veille, et le lundi la semaine écoulée (lundi à dimanche) ; la plus récente a passé 8 h depuis au moins 22 h ; le contrôle refuse toute date ≥ le jour de lecture (`live_week.check_live`) ; la mise à jour quotidienne lit elle aussi jusqu'à la veille (`proxsis update`) ; les données figées s'arrêtent au 30.09.2026 | écrire la règle dans le contrôle de la rubrique (aucune date ≥ le lundi de mise à jour) et la tester |
| Ne rien modifier | titres cités dans leur langue d'origine, sans traduction ; lauréat non nommé s'il n'est pas certainement une entreprise (rien n'est réécrit) | montants publiés arrondis au franc dans les dossiers guidés (CHF 1 574 663.35 affiché CHF 1 574 663) : afficher le montant exact sur la publication, l'arrondi seulement dans notre lecture ; un champ masqué par notre filtre n'est jamais montré comme publié (le remplacer par « non repris ici, voir la publication officielle ») |
| Séparation visuelle | publication sur papier ivoire, notre lecture à côté ; rubrique de la semaine à part et datée | la mention sur le papier ivoire lui-même, pour qu'il ne passe pas pour une publication officielle |
| Corrections et déclarations de qualité | suivies dans la rubrique (révocations et interruptions de la période ; une adjudication marquée « corrected » par simap passe en rectification : « correction » n'est pas un filtre de recherche de simap, HTTP 400 E0025, vérifié le 13.10.2026) ; avis des données figées rectifiés dans `corrections.json` | voir les notes de travail (non publiées) (rubrique : lire chaque lundi les rectifications et révocations de la semaine pour les avis affichés ; données figées : signaler la correction sans changer les chiffres) ; chercher si simap publie des déclarations de qualité des données |
| Obligations transmises | — | conditions d'utilisation de Proxsis pour les utilisateurs de Flexsis (pilote) reprenant ces obligations |

## Données personnelles

On cible des entreprises, jamais des particuliers. Le filtre est appliqué **avant tout enregistrement** :

- `proxsis.pii` à l'ingestion de chaque enregistrement (rubriques faillites, poursuites, successions et état civil
  exclues ; adjudicateur ou lauréat qui ressemble à une personne masqué) ;
- `proxsis.gazette_filter` pour le Bulletin officiel : chaque partie d'un rôle est classée ; seules les entreprises
  (forme juridique) et les collectivités sont gardées, tout le reste est masqué (`[masqué]`) dans le rôle, le titre et
  le texte ; parcelles et coordonnées aussi ; un dernier balayage arrête l'import si un marqueur de personne survit ;
- chaque export vers l'application repasse le même balayage, et un test le refait sur **tous** les fichiers de
  données que git suit (énumérés, pas listés à la main : `python/tests/test_public_data_sweep.py`) ;
- la section « Chaque matin, en direct de simap », publiée chaque jour ouvrable sans relecture, ne nomme un lauréat
  que s'il est certainement une entreprise (IDE ou forme juridique).

Les textes bruts collectés à la main restent hors de git (`data/manuel/textes/`) ; le dépôt ne garde que des index,
des empreintes et des résultats filtrés. Chaque ligne porte sa provenance (`source`, `url`, `retrieved_at`, `license`).

## Réel et fictif

| Réel | Fictif, marqué `fictif: true` et « Fictif » à l'écran |
|---|---|
| entreprises, marchés publics, demandes d'autorisation, communes | consultants, intérimaires, missions, chiffres d'agence, candidats |

Les besoins de personnel sont des **estimations** (phases d'un chantier, hypothèses écrites dans
`proxsis.phasing`), à confirmer avec l'entreprise : jamais présentés comme des postes réels. Les mesures publiées
(backtests sur données réelles) renvoient chacune à une ligne de [CLAIMS.md](../CLAIMS.md) et à la commande qui la
reproduit.

## Fichiers

| Dossier | Contenu | Dans git |
|---|---|---|
| `apps/web/src/data/demo/` | les onze fichiers lus par l'outil du consultant (`proxsis export-demo`) | oui, validés par des schémas (`src/lib/schema.ts`) |
| `apps/web/src/data/presentation/` | carte, dossiers guidés, les lundis de « Choisissez une date » (`lundis.json`, `proxsis lundis-presentation`, ligne CLAIMS PRES-DATE-1), les trois histoires datées du dossier de preuves, le territoire de la visite (`territoire.json`, `proxsis territoire-presentation` : par commune, siège ici ou marché ici, seulement les entreprises dont le dossier passe tous les contrôles), contours des communes | oui, validés par des schémas |
| `apps/web/src/data/direct/matin.json` | « Chaque matin, en direct de simap » (`semaine.json` jusqu'au 13.10.2026), réécrit chaque jour ouvrable par la tâche automatique si tout passe (`proxsis matin-en-direct`, ADR-0016) | oui |
| `apps/web/src/data/presentation/matins.json` | la même section, figée, pour chaque lundi de « Choisissez une date » : seulement ce qui était publié avant ce lundi (`proxsis matins-presentation`) | oui |
| `apps/web/src/data/sources/carte.json` | la carte des sources : les lignes de `data/catalogue.csv` comptées par groupe (`proxsis carte-sources`, CLAIMS SOURCES-1) | oui |
| `data/terrain/` | la liste gelée du lundi 05.10.2026 et ses feuilles FR/DE à valider par les consultants | oui |
| `data/manuel/import_pdf/` | import filtré du Bulletin officiel (publications, rapport) | oui |
| `data/annotations/` | jeux de test gelés (identifiants et empreintes, sans texte) | oui |
| `data/fictif/` | les 300 candidats fictifs | oui |
| `data/referentiels/` | localités du Valais (swisstopo) | oui |
| `data/reel/` | adjudications simap **filtrées**, séries et référentiels publics : l'instantané qui reproduit à l'octet près les fichiers de `apps/web/src/data/` (`python/tests/test_reproducibility.py`) | **non** ; ses empreintes, oui (`data/reel.sha256`, `shasum -a 256 -c data/reel.sha256`) ; une nouvelle collecte donnerait d'autres données |
| `data/manuel/textes/` | textes filtrés de la collecte manuelle | **non** |

Une date de démonstration unique, le lundi de la liste (05.10.2026) : aucun écran ne lit l'horloge de l'ordinateur.
