# Collecte manuelle — Bulletin officiel du Valais et FOSC

Décision de Hiba (2026-10-05) : ces portails sont consultés **par des
personnes**, jamais par un script (`proxsis.http.MANUAL_ONLY_HOSTS` bloque
toute requête, même robots.txt). Consigne : `docs/annotation/consigne_collecte_manuelle.md`.

| Dossier | Contenu | Dans git ? |
|---|---|---|
| `textes/` | textes **filtrés** (noms de particuliers masqués avant l'enregistrement), pages d'annotation et d'arbitrage, jeu gelé avec textes | **non** (`.gitignore`) |
| `index/<initiales>.jsonl` | lien, date, langue, source, rubrique, empreinte SHA-256 du texte filtré | oui |
| `annotation/` | répartition (double annotation), accord, liste des désaccords, référence gelée sans texte | créé par la première session d'annotation (aucune pour l'instant) |

Commandes (depuis `python/`) : `proxsis collecte-manuelle`,
`proxsis etat-collecte`, `proxsis plan-collecte`,
`proxsis repartir-annotation --annotateurs AA,BB,…`,
`proxsis accord-manuel <exports…>`, `proxsis geler-manuel <exports…> --arbitrage <fichier>`.

## Import des PDF « Composition individuelle » (2026-10-06)

Les PDF exportés du portail (demandes d'autorisation de construire, BA-VS05) et l'index XML « bulk-export » du
même portail s'importent sans copier-coller :

```bash
make bo-import                    # import FR puis DE, tirages et gel, répartition A1/A2, projets radar
```

**Reconstruction propre** (après un changement du filtre) : jamais en fusion avec d'anciennes sorties. Écrire dans des
dossiers vides, faire auditer, puis remplacer les fichiers livrés :

```bash
make bo-import BO_PUBLIC=../data/manuel/textes/reconstruction_X/public BO_PRIVE=../data/manuel/textes/reconstruction_X/bo_vs_pdf BO_ANNOT=../data/manuel/textes/reconstruction_X/annotations BO_PAGES=../data/manuel/textes/reconstruction_X/bo_vs_v1 BO_RADAR_MD=../data/manuel/textes/reconstruction_X/radar/projets_bo_vs.md
```

- Lecture **en mémoire** ; filtre des personnes physiques **avant** toute écriture (rôles, titres, texte ;
  parcelles et coordonnées masquées). Public : `import_pdf/` (index sans texte, rapport, projets). Privé, hors git :
  `textes/bo_vs_pdf/` (textes filtrés, items d'annotation) et `textes/bo_vs_v1/` (pages d'annotation).
- Rapport : `import_pdf/RAPPORT_IMPORT.md` (lues, doublons, acceptées, rejetées avec leur raison, par commune, par
  semaine, par langue, masquages à vérifier).

### Export allemand (à faire par Hiba)

Les publications allemandes n'ont que leur titre dans une composition française (« contenu allemand à importer »).
1. Sur le portail, passer l'interface en allemand et exporter les mêmes périodes en « Composition individuelle ».
2. Avant l'import, sonder un fichier (mots du gabarit seulement, aucun contenu lisible) :
   `.venv/bin/python -m proxsis.cli sonder-pdf <dossier des exports>/<fichier_allemand>.pdf` — les libellés allemands
   (Gesuchsteller, Grundeigentümer, Projektverfasser…) seront ajoutés au lecteur d'après ce squelette.
3. Lancer `import-bo-pdf` sur les PDF allemands avec le même index : les entrées « titre seul » sont remplacées par
   leur contenu complet, le reste n'est pas touché ; puis `tirage-bo --langue de --n 50`.
