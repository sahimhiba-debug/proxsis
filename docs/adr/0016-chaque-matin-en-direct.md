# ADR-0016 — « Chaque matin, en direct de simap » : une lecture chaque jour ouvrable, la veille, mise en route par Hiba

- Statut : proposé (en attente de l'audit et de l'accord de Hiba pour la mise en route en production)
- Date : 2026-10-13
- Couloir : produit et plateforme

## Contexte
La suite 10 (13.10.2026, § 2) demande qu'on voie que Proxsis veille chaque matin : la section « Cette semaine, en direct
de simap » (lue le lundi seulement, `lundi-en-direct.yml`, jamais lancée : la fusion en production date du 12.10.2026
au soir) devient « Chaque matin, en direct de simap ». Les règles de simap restent celles du lundi : jamais une
publication du jour même, le filtre des données personnelles avant tout enregistrement, rien n'est publié si un contrôle
échoue. La liste du lundi ne change pas pendant la semaine ; « depuis hier » montre des faits, pas un score.

En préparant la lecture quotidienne, trois défauts de la lecture du lundi sont apparus (essais du 13.10.2026) :
1. la recherche des rectifications demandait le type « correction », que simap refuse (HTTP 400, E0025 « Invalid
   parameter » ; le type n'existe pas dans `ProjectSearchPubTypeFilter`, `simap.yaml`) : chaque lundi aurait échoué ;
2. le détail d'une publication appelle « award » une adjudication après appel d'offres (« award_tender » n'est que le
   nom du filtre de recherche) : la section ne gardait que les adjudications de gré à gré (13 sur 25 la semaine du
   21.09.2026, rejouée) ;
3. le planificateur de GitHub démarre souvent avec des heures de retard (la mise à jour quotidienne prévue à 7 h 17 a
   démarré entre 13 h 47 et 15 h 10, du 06.10 au 13.10.2026).

## Décision
- **Ce qui est lu** : chaque jour ouvrable, les adjudications de construction des adjudicateurs valaisans
  (`issuedByOrganizations` = Valais) — le lundi celles publiées du lundi au dimanche de la semaine écoulée, du mardi au
  vendredi celles publiées la veille (`live_week.reading_period`). Rien du jour de la lecture ; le contrôle refuse toute
  date ≥ le jour de lecture et toute période qui n'est pas celle du jour (`check_live`).
- **Fichier** : `apps/web/src/data/direct/matin.json` (schéma 2 : `mode`, `periode`, lauréats avec l'identifiant des
  listes de l'application, pour dire « dans votre liste »), écrit avec `corrections.json` seulement si tout passe.
- **Rectifications** : révocations et interruptions par leur type ; une adjudication marquée « corrected » par la
  recherche de simap passe en rectification (et non comme un nouveau marché).
- **Travail planifié** : `.github/workflows/chaque-matin-en-direct.yml`, trois départs par jour (6 h en été, 6 h en
  hiver, rattrapage) ; la lecture part au premier départ après 6 h à Zurich, jamais deux fois le même jour
  (`morning_gate.py`, bibliothèque standard seulement). Les lectures planifiées ne partent que si la variable du dépôt
  `CHAQUE_MATIN_EN_DIRECT` vaut `actif` : la fusion seule ne met rien en route ; Hiba pose la variable après l'audit.
- **« Choisissez une date »** : la même section, figée, pour chaque lundi au choix (`matins.json`,
  `proxsis matins-presentation`), seulement ce qui était publié avant ce lundi, repliée sous les dix entreprises.
- **Contrôle de la production** : une fois la section publiée, chaque jour ouvrable a sa lecture ; la lecture du jour
  n'est attendue qu'à partir de 16 h (`scripts/production/fraicheur.mjs`).
- **Mise à jour quotidienne** (`proxsis update`) : elle lit désormais jusqu'à la veille à Zurich (même règle).

## Alternatives considérées
Lire « depuis la dernière lecture réussie » plutôt que la veille : couvrirait un jour manqué, mais la section dirait
alors une période variable ; on garde la règle simple de la consigne (la veille), et le contrôle de la production
signale un jour manqué. Un déclencheur externe pour tenir 6 h exactement : un service de plus, avec un secret ; écarté
tant que l'heure exacte n'est pas une promesse (l'écran dit la date de lecture, pas l'heure). Laisser la lecture partir
dès la fusion : écarté, la mise en route attend l'accord de Hiba.

## Conséquences
Un commit par jour ouvrable sur la branche de production (seulement les deux fichiers de la section), donc un
déploiement Vercel par jour. Les tests de l'application tournent avant chaque publication : un titre publié par simap
(« signalisation routière ») ne doit pas les faire échouer (les champs cités de simap sont exclus du contrôle du
vocabulaire). Raison de revenir dessus : un retard du planificateur qui rendrait la section inutile le matin, ou une
réponse aux demandes d'accès (Portail des feuilles officielles) qui permettrait de lire aussi le Bulletin officiel
chaque matin.

## Mesures liées
Aucune : la section montre des faits publiés, sans chiffre mesuré. La carte des sources (même suite) : SOURCES-1.
