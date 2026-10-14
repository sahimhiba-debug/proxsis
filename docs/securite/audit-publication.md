# Audit avant publication du dépôt `proxsis` (14.10.2026)

Ce que contient ce dépôt, d'où il vient et ce qui a été contrôlé avant son premier envoi sur GitHub. Ce rapport ne
recopie aucun contenu sensible : seulement des chemins, des outils et des comptes.

## Origine

- Contenu : la branche de production du dépôt de travail (privé), commit `1c34520` du 14.10.2026, exportée par
  `git archive`, c'est-à-dire **sans historique**. Le seul commit de ce dépôt contient déjà toutes les corrections
  ci-dessous : aucune version antérieure n'est dans son historique.
- Retiré :
  - `archives/` (766 fichiers : briefs, notes, relectures, audits d'étape, captures de revue). Le code ne le citait que
    dans des commentaires, et les tests n'en dépendaient pas. Les renvois sont devenus « notes de travail (non
    publiées) ».
  - `docs/presentation-en.jpg`, la vignette d'une vidéo publiée comme release de l'ancien dépôt.
  - Les consignes pour agents de code (`CLAUDE.md` à la racine, `apps/web/CLAUDE.md`, `apps/web/AGENTS.md`). Leurs
    règles sont reprises dans `CONTRIBUTING.md` ; les deux fichiers que `next dev` réécrit quand un agent le lance
    sont ignorés par git.
  - Toute mention du dépôt d'une autre équipe du hackathon et de son auteur : section de `docs/recherche/contexte.md`
    et ses références, citations dans `docs/recherche/donnees.md` et `data/catalogue.csv` (25 lignes), ADR, en-tête
    de `models/m0_rules.py`, `CONTEXT.md`, `PRODUCT.md`, `DESIGN.md`, README. La règle « compter les familles, pas les
    signaux » reste, comme un choix du projet (ADR 0004).
  - Les noms de deux personnes du groupe Interiman (`docs/recherche/contexte.md`), dont une adresse d'article qui en
    contenait un.
- Renommé : le moteur prend le nom du produit, `proxsis` (dossier `python/src/proxsis/`, commande `proxsis`, variables
  `PROXSIS_*`, User-Agent `Proxsis/0.1`, trousseau macOS `proxsis-publicai`, clés de préférences `proxsis.*`) ;
  `docs/identite-flexsis/` devient `docs/identite/`.

## Informations dont la seule source était le README retiré

Quand une autre source les appuyait déjà, seule la citation est partie. Sinon, l'information est marquée « non
vérifié » ; la pagination simap par `lastItem` est rattachée à notre connecteur (`connectors/simap.py`), qui la
vérifie. Dans `data/catalogue.csv`, trois lignes n'avaient pas d'autre source de documentation
(`amtsblatt_vs_grands_projets`, `amtsblatt_vs_emplois_publics`, `ofs_hesta`) : leur colonne `source_documentation`
dit « non vérifié » et renvoie au test réel de la même ligne.

## Contrôles

| Contrôle | Outil | Résultat |
|---|---|---|
| Ancien nom du projet, nom et prénom de l'auteur tiers (toute casse) | recherche dans le contenu et dans les noms des fichiers suivis | aucun résultat (voir la note ci-dessous) |
| Secrets dans les fichiers | gitleaks 8.30.1 (`detect --no-git`, puis `protect --staged`) | aucun |
| Secrets dans les fichiers et l'historique | `scripts/securite/audit.sh` | aucun |
| Failles des dépendances livrées | `npm audit --omit=dev` ; pip-audit 2.10.1 | aucune ; aucune |
| Failles des outils de développement | `npm audit` | 1 faille à la racine (`braces`, élevée, [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)), atteinte par les outils de lint (`eslint-config-next`, `knip`), rien de livré ; Dependabot proposera la mise à jour |
| Noms de particuliers dans les données publiées | `python/tests/test_public_data_sweep.py` (chaque JSON et chaque page HTML suivis) | aucun |
| Chemins d'un poste de travail (`/Users/`, `/private/tmp`, copies de travail) | recherche dans tout l'arbre | aucun |
| Adresses e-mail | recherche dans tout l'arbre | adresses publiques d'administrations et exemples fictifs seulement |
| Nom du compte Runway | recherche dans tout l'arbre | aucun (seuls les identifiants des tâches, sans compte) |
| Liens LinkedIn | recherche dans tout l'arbre | pages d'organisations seulement, aucun profil de personne |
| Workflows | actionlint 1.7.12 | aucune remarque |
| Contrôles du projet | `make check` (Node 22.23.3, Python 3.12.13) | voir le message du commit |

**Note sur la recherche.** Le filtre des données personnelles (`proxsis/pii.py`) doit reconnaître le prénom courant qui
s'écrit comme « mathieu » avec deux « t » : il y est écrit en deux morceaux, pour que le dépôt n'en contienne aucune
occurrence littérale, et le filtre le reconnaît toujours. Les deux tests qui empêchent l'ancien nom de reparaître à
l'écran le cherchent par un motif (`flex[\s-]?radar`), pas par le mot lui-même.

## Laissé en place, à décider

- Deux dirigeants d'autres entreprises (un éditeur de logiciel, une place de marché américaine) sont nommés dans le
  titre et l'adresse de communiqués publics cités comme sources (`docs/recherche/marche.md`, S21b ;
  `docs/recherche/international.md`, I4).
- Les documents de recherche qui disent avoir été rédigés par un assistant d'IA le disent toujours (honnêteté sur
  leur origine) ; `.mcp.json` (outils de test du navigateur pour un agent de code) reste à la racine.
- Licence : tous droits réservés tant qu'aucune licence n'est choisie.
- Images et sons de la mascotte générés avec Runway (`docs/identite/mascotte/`, `apps/web/public/iris/`) : la
  diffusion publique dépend des conditions du service Runway, à vérifier avant de rendre le dépôt public.
