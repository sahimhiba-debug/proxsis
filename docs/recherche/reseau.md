# Vérification du réseau — 2026-10-05

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

**Contexte.** La session du 2026-10-04 tournait dans un environnement cloud
dont le proxy bloquait presque toutes les sources (voir `donnees.md` § 2.1).
La reprise du 2026-10-05 tourne **sur le Mac de Hiba**, sans liste blanche
réseau : les sources sont joignables directement.

**Commande reproductible**

```bash
cd python && . .venv/bin/activate
python -c "from pathlib import Path; from proxsis.netcheck import run; run(Path('../data/reseau/verification_2026-10-05.csv'))"
```

Méthode : un seul `GET https://<domaine>/robots.txt` par domaine, User-Agent
du projet sous son ancien nom (`…/0.1 (prototype de recherche Hack VS 2026)`), délai 10 s. Tout
code HTTP (même 404) signifie que le domaine répond. Les domaines « à ne pas
autoriser » (`donnees.md` § 5.1 : SAD Consult GE, jobs.ch, jobup.ch,
Indeed, LinkedIn, serveur OSRM public) ne sont **pas** contactés
(`proxsis.netcheck.NEVER_CONTACT`, vérifié par un test).

Résultat brut : [`data/reseau/verification_2026-10-05.csv`](../../data/reseau/verification_2026-10-05.csv).

## Résultat (2026-10-05, 17:40 UTC environ)

| | Nombre |
|---|---|
| Domaines testés | 77 |
| Répondent (un code HTTP, quel qu'il soit) | 76 |
| Ne répondent pas | 1 : `datenservice.kof.ethz.ch` |

- `datenservice.kof.ethz.ch` refuse la connexion sur les ports 443 **et** 80
  (`curl: (7) Failed to connect … Could not connect to server`, adresse
  129.132.11.121). Le refus vient du serveur, pas de notre réseau. Le service
  de données KOF semble passé sur `tsdb-api.kof.ethz.ch` (qui répond) : à
  confirmer dans la documentation KOF.
- `public.madd.bfs.admin.ch` répond `403` sur `/robots.txt` : le serveur
  répond, le fichier n'est pas public. À tester sur l'URL d'extrait elle-même.
- La passerelle Public AI (`api.publicai.co`) répond.

## Domaines à ajouter à une liste blanche

**Aucun depuis ce poste.** Si le travail repasse dans un environnement cloud
filtré, la liste à autoriser reste celle de `donnees.md` § 5.1, plus
`api.publicai.co` (passerelle Apertus).

## Ce que ce test ne dit pas

Joignable ne veut pas dire autorisé. Pour chaque source, les conditions
d'utilisation, le robots.txt et les limites de débit sont lus avant tout
appel « métier » : voir le catalogue (`data/catalogue.csv`, colonne
`test_reel_2026_10_05`) et `docs/recherche/conditions_2026-10-05.md`.
