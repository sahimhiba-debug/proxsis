# proxsis, le moteur Python de Proxsis

Lit les sources autorisées, filtre les données personnelles avant toute écriture, calcule la liste d'appels et les
mesures, exporte les fichiers lus par l'application (`apps/web/src/data/`). Vue d'ensemble :
[../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) ; sources et filtre : [../docs/DONNEES.md](../docs/DONNEES.md).

## Environnement

```bash
uv sync --frozen --extra dev     # Python 3.12.13 et les versions exactes du verrou (uv.lock)
. .venv/bin/activate
```

Sur macOS, LightGBM a besoin d'OpenMP : `brew install libomp` (le `Makefile` le trouve là, ou dans Anaconda).
Changer une version : la modifier dans `[tool.uv] constraint-dependencies` de `pyproject.toml`, lancer `uv lock`, puis
tous les contrôles (`make check` à la racine) avant de commiter les deux fichiers. Rien ne se met à jour tout seul.

## Contrôles

```bash
ruff check src tests && mypy && pytest -q -m "not network"    # ou : make py-check, à la racine
```

## Commandes

`proxsis --help` liste les 42 commandes (analyseur dans `cli.py`, une fonction par commande dans
`proxsis/commands/`). Les plus courantes :

| Commande | Rôle |
|---|---|
| `proxsis export-demo` | fichiers de la démonstration pour l'application (`apps/web/src/data/demo/`), balayage des données personnelles avant écriture |
| `proxsis export-presentation`, `proxsis histoires-presentation` | données de la présentation (carte, trois histoires de l'acte 4) |
| `proxsis matin-en-direct` | « Chaque matin, en direct de simap » (le lundi la semaine écoulée, du mardi au vendredi la veille), lancé chaque jour ouvrable par la CI une fois la mise en route décidée (ADR-0016) ; `--jour` rejoue un jour, `--rejeu` lit un fichier filtré au lieu de l'API |
| `proxsis matins-presentation` | la même section, figée, pour chaque lundi de « Choisissez une date » |
| `proxsis carte-sources` | la carte des sources : `data/catalogue.csv` compté par groupe (CLAIMS SOURCES-1) |
| `proxsis backtest --seed 42 [--quick]` | banc d'essai sur le monde fictif (`docs/backtest/`) |
| `proxsis import-bo-pdf` | import des exports du Bulletin officiel téléchargés par une personne (`make bo-import`) |

Les commandes qui appellent Public AI lisent leur clé dans l'environnement ou le trousseau macOS (simap n'en demande
pas) ; aucune clé n'est écrite dans un fichier ni dans les journaux. Sans clé, tout fonctionne avec le faux fournisseur.
