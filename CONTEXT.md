# CONTEXT.md — contexte et glossaire du métier

> Les affirmations factuelles sur Flexsis, Interiman et le Hack VS sont
> vérifiées (ou non) dans `docs/recherche/contexte.md`. Ce fichier ne
> contient que le vocabulaire et le cadre du projet.

## Le problème en une phrase

Un consultant d'agence de placement gagne une commande quand il appelle la
bonne entreprise **avant** qu'elle ait publié son besoin (ou appelé un
concurrent). Proxsis lit des signaux publics (marchés attribués,
permis de construire, mutations au registre du commerce, offres d'emploi
publiques) pour dire chaque semaine : **qui appeler, pour quel métier,
quand, avec quels candidats, et pourquoi**.

## Glossaire (FR / DE)

| Terme (FR) | Terme (DE) | Définition dans Proxsis |
|---|---|---|
| Location de services / travail temporaire | Personalverleih / Temporärarbeit | L'agence emploie le travailleur et le met à disposition d'une entreprise cliente (entreprise locataire). Soumis à autorisation (LSE). |
| Placement fixe | Feste Stellenvermittlung | L'agence met en relation ; le candidat est engagé directement par le client. |
| Consultant | Berater/in | Personne de l'agence qui prospecte les clients et place les candidats. Utilisateur principal. |
| Chef d'agence | Filialleiter/in | Responsable d'une agence ; voit les listes de son agence. |
| Groupe | Gruppe | Direction multi-marques (Interiman) ; voit toutes les agences. |
| Entreprise cliente / prospect | Kundenunternehmen / Prospect | Personne morale ciblée. **Jamais** une personne physique. |
| Commande | Auftrag | Demande de personnel d'un client à l'agence. |
| Mission | Einsatz | Affectation d'un travailleur temporaire chez un client. |
| Candidat | Kandidat/in | Personne cherchant un emploi, inscrite à l'agence. **Données FICTIVES** dans ce dépôt. |
| IDE / UID | UID | Numéro d'identification des entreprises (CHE-123.456.789), clé de rapprochement. |
| Registre du commerce, FOSC | Handelsregister, SHAB | Feuille officielle suisse du commerce : publications des créations et mutations d'entreprises. |
| Feuille officielle cantonale | Amtsblatt | Publications officielles d'un canton (ex. Bulletin officiel du Valais) : mises à l'enquête, etc. Portail commun : amtsblattportal.ch. |
| Mise à l'enquête publique | Öffentliche Auflage / Baupublikation | Publication d'une demande de permis de construire. |
| Permis de construire | Baubewilligung | Autorisation de bâtir ; signal de demande future (chantier, puis exploitation). |
| simap.ch | simap.ch | Plateforme officielle des marchés publics (Confédération, cantons, communes). |
| Appel d'offres | Ausschreibung | Publication d'un marché à attribuer. |
| Adjudication / marché attribué | Zuschlag | Décision d'attribution à une entreprise : signal fort pour cette entreprise. |
| CFC | BKP | Code des frais de construction (classification des travaux du bâtiment, CRB). |
| CPV | CPV | Vocabulaire commun des marchés publics (UE), utilisé par simap. |
| CN / LMV | LMV | Convention nationale du secteur principal de la construction. |
| Obligation d'annonce | Stellenmeldepflicht | Pour les genres de profession au taux de chômage ≥ seuil légal, les postes vacants doivent être annoncés à l'ORP ; priorité de 5 jours ouvrables aux demandeurs inscrits. L'outil le rappelle, ne le contourne jamais. |
| ORP | RAV | Office régional de placement. |
| Signal | Signal | Événement public daté et sourcé, rattaché à une entreprise (ou à une région) : adjudication, permis, mutation RC, offre d'emploi. |
| Famille de signaux | Signalfamilie | Regroupement : `marche_attribue`, `permis_construire`, `mutation_rc`, `offre_emploi`, `macro`. |
| Alerte | Alarm | Proposition d'appel pour une entreprise une semaine donnée, avec niveau (rouge / orange / jaune), raisons et sources. |
| Besoin estimé | Geschätzter Bedarf | Nombre estimé de personnes par métier et par semaine, avec intervalle et niveau de confiance. Toujours une estimation, jamais un fait. |
| Métier | Beruf | Catégorie de poste (maçon, manœuvre, électricien, opérateur de production, horloger, cariste, agent de logistique, opérateur pharma…), codée CH-ISCO-19 si possible. |
| Vu à la date T | Stand per T | Reconstitution de ce qui était connu à la date T, sans aucune information postérieure (`available_at <= T`). |
| Cible (vérité terrain) | Zielgrösse | Événement futur mesurable avec des données publiques, ex. « l'entreprise publie une offre dans le bâtiment dans les 8 semaines ». |
| P@20 | P@20 | Précision dans les 20 premières alertes : part des 20 alertes du haut de liste pour lesquelles la cible s'est réalisée. |
| Jours d'avance | Vorlauf in Tagen | Délai entre l'alerte et la réalisation de la cible (ex. publication de l'offre). |
| Backtest | Backtest | Rejeu de la méthode sur le passé, semaine après semaine, « vu à la date T ». |
| FICTIF | FIKTIV | Marque obligatoire de toute donnée inventée (clients, candidats, missions, commandes, monde de démo). |

## Les acteurs

- **Flexsis** : agence de placement (temporaire et fixe), filiale
  d'Interiman Group. Secteurs : industrie, construction, horlogerie,
  logistique, pharma. Suisse romande ; Suisse alémanique depuis la reprise
  des agences Tempro (affirmé dans le cahier des charges ; statut de
  vérification dans `docs/recherche/contexte.md`).
- **Interiman Group** : groupe RH multi-marques (affirmé : « premier groupe
  RH de Suisse, plus de 70 sites, une dizaine de sociétés » — voir
  `docs/recherche/contexte.md`).
- **Hack VS 2026** : défi « anticiper les besoins en personnel » posé par
  Flexsis ; Proxsis en est une réalisation indépendante.

## Les langues

L'interface, les e-mails générés et l'extraction des publications
fonctionnent en **français et en allemand**. Les publications alémaniques
utilisent `Zuschlag`, `Baugesuch`, `Baupublikation`, `Handelsregister`,
`Neueintragung`, `Mutation`, `Zweigniederlassung`.
