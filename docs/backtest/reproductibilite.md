# Reproductibilité des mesures réelles — vérification du 07.10.2026

Question : les chiffres de CLAIMS.md du **premier test** (REEL-T0 : simap, Suisse romande, vingt entreprises par
semaine, 44 semaines) et de la **mesure du bâtiment** (REEL-SPEC-BAT : entreprises valaisannes, dix par semaine,
57 lundis) se retrouvent-ils à l'identique ? Avec quel environnement ont-ils été calculés ?

## En bref

| Mesure (CLAIMS) | Environnement d'origine reconstitué | Verrou actuel (`python/uv.lock`) avant correctif | Verrou actuel après correctif (`489eba7`) |
|---|---|---|---|
| REEL-T0 : hasard 16,0 %, récence 31,0 %, fréquence 55,0 %, sélection « M0 marchés » 52,7 %, écart −2,3 points (IC −8,9 à +1,4) | **identique** (`reel_t0.json`, 0 écart) | **identique** | **identique** |
| REEL-SPEC-BAT, REEL-SPEC-PIC, REEL-SURPRISE, REEL-SPEC-AUTRES (`specialites_v1.json`) | **identique** (0 écart) | **différent pour le seul modèle combiné** (détail ci-dessous) | **identique** |
| « Choisissez une date » (`lundis.json`, PRES-DATE-1) | identique à l'octet | identique à l'octet | identique à l'octet |
| REEL-T0-COMB, REEL-T0-PIC (`reel_t0_surprise_combine.json`) | **différent** | différent | différent (= environnement d'origine) |
| M4-1, FICTIF (`m4_resultats_v1.json`) ; M3-1, M5-*, M6-1 | M4-1 identique ; les autres identiques | **M4-1 différent** (rappel 0,907 au lieu de 0,725) ; les autres identiques | correctif proposé, non appliqué (§ 3) |

Le premier test se reproduit : **52,7 % et 55,0 %**, aux mêmes décimales, dans les deux environnements. L'écart
du combiné de REEL-SPEC-BAT (66,8 % → 67,0 %) venait de pandas et disparaît avec un correctif d'une ligne. Seules
REEL-T0-COMB et REEL-T0-PIC ne se reproduisent pas : elles ont été mesurées le 05.10.2026 sur des données
**modifiées depuis** (remasquage des adjudicateurs du 06.10.2026), pas à cause de l'environnement. Dans le monde
FICTIF, M4-1 dépend aussi de pandas, mais là c'est le chiffre publié qui porte le défaut (§ 3).

## 1. L'environnement d'origine

Aucun fichier de verrouillage n'existait avant `5c26bda` (07.10.2026) ; `pyproject.toml` donnait des plages
(`>=`). L'environnement se lit dans le `.venv` partagé et dans le cache de uv :

- `python/.venv` créé le **05.10.2026 à 19:34** (`pyvenv.cfg` : uv 0.11.17, CPython 3.12.13) ; tous ses paquets
  datent de 19:34, sauf pypdf (19:44), pandas-stubs et types-pytz (20:04), et **pandas, lifelines, pytz, tzdata et
  proxsis, réinstallés le 06.10.2026 à 22:02** (le sous-agent auditeur, `uv run`, registre des questions du
  06.10 20:40).
- Cache de uv (`~/.cache/uv/wheels-v6/pypi/`) : la seule roue pandas cp312 arm64 téléchargée avant le 06.10 est
  **pandas 3.0.6** (05.10.2026, 19:34:23) ; la roue **lifelines 0.30.0** date de la même minute ; pandas 2.3.3,
  lifelines 0.30.3, pytz 2026.5 et tzdata 2026.5 ont été téléchargées le 06.10.2026 à 22:02.
- Pourquoi ce changement : lifelines 0.30.3 exige `pandas<3.0` ; la résolution du 05.10 (`uv pip install`) avait
  pris pandas 3.0.6 et donc lifelines 0.30.0 ; celle du 06.10 (`uv run`, verrou universel) a préféré lifelines
  0.30.3 et redescendu pandas à 2.3.3.
- Les calculs d'origine ont tous eu lieu entre ces deux dates : REEL-T0 (`8871cf7` 21:53 et `e47bca0` 22:14, le
  05.10), `specialites_v1.json` (`fe8915b` 09:42 et `bb769f1` 10:59, le 06.10).

Liste exacte (60 paquets) : [`environnement_calcul_origine.txt`](environnement_calcul_origine.txt). Différences
avec le verrou actuel : pandas 3.0.6 (au lieu de 2.3.3), lifelines 0.30.0 (au lieu de 0.30.3), ni pytz ni tzdata.

La note d'état du 05.10 (notes de travail) (« numpy 2.3, pandas 2.3.3 ») ne décrit pas le `.venv` : numpy y est en 2.5.3
depuis 19:34, et le seul pandas 2.3.3 du Mac était alors celui d'Anaconda (`/opt/anaconda3`, avec numpy 2.5.0 et
scikit-learn 1.7.2).

## 2. Recréer l'environnement et rejouer

Hors du dépôt, sans réseau (roues du cache de uv), depuis la racine du dépôt :

```sh
uv venv /tmp/venv-origine --python 3.12.13
uv pip install --offline --no-deps --python /tmp/venv-origine/bin/python \
  -r docs/backtest/environnement_calcul_origine.txt
```

Commandes rejouées dans chaque environnement (depuis `python/`, `PYTHONPATH=src`, sans les variables
`PUBLICAI_API_KEY`, `PUBLICAI_BASE_URL`, `PROXSIS_LLM_PROVIDER`, `DYLD_FALLBACK_LIBRARY_PATH=/opt/anaconda3/lib`,
sorties hors du dépôt), sur l'instantané `data/reel/` dont les empreintes sont celles de `data/reel.sha256`
(vérifiées : 8 fichiers OK) :

```sh
python -m proxsis.cli backtest-reel ../data/reel/simap/adjudications_romandie_construction_2024-07_2026-09.jsonl \
  --first-week 2025-10-06 --last-week 2026-08-03 --data-end 2026-09-30 --k 20 --out <sortie>/reel_t0.json
python -m proxsis.cli backtest-reel <même fichier> --first-week 2025-10-06 --last-week 2026-08-03 \
  --data-end 2026-09-30 --k 20 --etendu --out <sortie>/reel_t0_surprise_combine.json
python -m proxsis.cli backtest-specialites --fichiers \
  ../data/reel/simap/adjudications_romandie_construction_2024-07_2026-09.jsonl \
  ../data/reel/simap/adjudications_emetteur_vs_construction_2024-07_2026-09.jsonl --out <sortie>/specialites_v1.json
python -m proxsis.cli lundis-presentation --out <sortie>/lundis.json
```

Comparaison : tous les champs des JSON, sauf le chemin des fichiers lus et la date `mesure_le`.

## 3. Résultats

**REEL-T0** (`reel_t0.json`) : 0 écart dans les deux environnements, avec le code d'aujourd'hui. Hasard 16,0 %
(taux de base 15,98 %), récence 31,0 %, fréquence 52 semaines 55,0 % (IC 95 % 48,4 à 68,5), M0 marchés 52,7 %
(IC 47,3 à 62,7), M0 − fréquence −2,3 points (IC −8,9 à +1,4) ; 1 892 adjudications, 731 entreprises, 44 semaines.
Ces quatre règles ne lisent pas l'adjudicateur ; elles ne dépendent ni de pandas ni du remasquage.

**`specialites_v1.json`** : 0 écart dans l'environnement d'origine. Dans le verrou actuel, avant correctif, le seul
modèle combiné change (le hasard, la récence et la fréquence sont identiques) :

| Ligne CLAIMS | Publié (= environnement d'origine) | Verrou actuel avant correctif |
|---|---|---|
| REEL-SPEC-BAT, combiné | 66,8 % ; combiné − fréquence +0,0 point (IC −2,6 à +2,5) | 67,0 % ; +0,2 point (IC −2,1 à +2,3) |
| REEL-SPEC-PIC, combiné | 14,6 % ; +2,1 points (IC −4,4 à +7,9) | 14,2 % ; +1,8 point (IC −4,6 à +7,4) |
| REEL-SURPRISE, 3 surprises retenues | 42,1 % | 41,5 % |
| REEL-SPEC-AUTRES, Technique, combiné | 20,7 % | 20,5 % |

**Cause, établie** : la variable « nombre d'adjudicateurs distincts en 52 semaines » (`n_auth_52s`) était calculée
avec `astype(str)` (`real_backtest.snapshot`). pandas 3 garde un adjudicateur absent comme valeur manquante (non
comptée) ; pandas 2.3.3 le change en texte « None » ou « nan », compté comme un adjudicateur de plus. Démonstration
dans les deux environnements : `pd.Series(['Commune A', None, nan, 'Commune A']).astype(str).nunique()` vaut 1 avec
pandas 3.0.6 et 3 avec pandas 2.3.3. Seul le modèle combiné (régression logistique) lit cette variable.

**Correctif** (`489eba7`) : l'adjudicateur absent n'est pas compté, quelle que soit la version de pandas (la règle
du calcul d'origine, et celle que disait déjà le commentaire du code). Résultat : `specialites_v1.json` se reproduit
à l'identique **dans les deux environnements** ; test unitaire (il échoue avec l'ancien code sous pandas 2.3.3 et
passe sous pandas 3.0.6) et test de reproduction de la mesure Bâtiment
(`tests/test_reproducibility.py`, quand `data/reel/` est présent ; environ 35 s).

**REEL-T0-COMB et REEL-T0-PIC** (`reel_t0_surprise_combine.json`, `e47bca0`, 05.10.2026 22:14) : ne se
reproduisent dans **aucun** environnement, même avec le code de `e47bca0`. Les fichiers simap de `data/reel/` ont été
réécrits le 06.10.2026 à 10:22 par le remasquage des adjudicateurs (audit de semaine 1, B1 : « 67 adjudicateurs
masqués sur 2 967 fiches de travaux », note d'état de 08:23 UTC) ; le combiné, qui compte les adjudicateurs, en
dépend ; la mesure du bâtiment a été refaite après (`bb769f1`, 10:59), pas celle-ci. Sur l'instantané actuel, avec
le correctif, les deux environnements donnent le même résultat :

| Ligne CLAIMS | Publié (05.10.2026, données d'avant le remasquage) | Instantané actuel, deux environnements |
|---|---|---|
| REEL-T0-COMB | combiné 55,9 % ; +0,9 point (IC −4,7 à +4,3) | combiné 56,0 % ; +1,0 point (IC −4,5 à +4,4) |
| REEL-T0-PIC | combiné 12,7 % ; +4,7 points (IC +1,9 à +7,5) | combiné 12,8 % ; +4,8 points (IC +2,0 à +7,5) |
| REEL-T0-NOUVEAUX | 34,4 % (2 053 sur 5 965) | identique |

Conclusions inchangées : l'écart combiné − fréquence n'est pas établi sur T0 ; il l'est sur le « pic ».

**M4-1 (monde FICTIF), autre dépendance à pandas, en sens inverse.** `proxsis rapports-modeles` redonne
`m3_resultats_regles_v1.json`, `m5_audit_equite_v3.json` et `m6_resultats_v1.json` à l'identique dans les deux
environnements, et `m4_resultats_v1.json` seulement dans l'environnement d'origine. Dans le verrou actuel : M4 flou
auto rappel 0,907 et F1 0,946 (publié : 0,725 et 0,837), précision inchangée (0,989) ; base nom exact rappel 0,735
(publié : 0,588). Cause : dans `models/m4_entity_resolution.benchmark`, une mention d'entreprise inconnue a
`truth = None` ; pandas 3 la lit comme valeur manquante (NaN), et `r.truth is not None` devient vrai : chaque
entreprise inconnue non reliée compte comme une entreprise manquée. Le chiffre publié (calculé avec pandas 3.0.6)
porte donc ce défaut ; pandas 2.3.3 donne le calcul voulu par le code. Correctif proposé (non appliqué : il change
un chiffre publié) : `truth = r.truth if isinstance(r.truth, str) else None`, puis `truth` à la place de `r.truth`
dans les trois tests de la boucle ; vérifié dans les deux environnements, il donne partout les valeurs du verrou
actuel (M4 flou auto : précision 0,989, rappel 0,907, F1 0,946 ; avec la revue acceptée : 0,845, 0,950, 0,895 ;
base nom exact : 0,983, 0,735, 0,841).

**Le reste des mesures réelles** (mêmes contrôles, deux environnements) : `apercu_simap.json`,
`phasage_reel_v1.json`, `m4_reel_v1.json` et `m4_paires_douteuses_v1.csv`, `semaine1_v1.json` et
`semaine1_detail_v1.json` : identiques ; les fichiers de l'application (`tests/test_reproducibility.py` : export de
démonstration, carte, histoires, lundis, territoire, lundi suivant) : identiques à l'octet. Suite Python complète
(`pytest -m "not network"`) : 691 tests réussis dans chacun des deux environnements ; un seul échec, dû au lien
symbolique `data/reel` de la copie de travail (`test_cli_defaults`, réussi sans ce lien).

## 4. Le verrou : proposition

**Garder le verrou actuel** (`python/uv.lock`, pandas 2.3.3, lifelines 0.30.3) **avec le correctif `489eba7`**, et
ne pas revenir à pandas 3.0.6 :

- avec le correctif, les deux environnements donnent les mêmes chiffres sur tout ce qui a été rejoué ; aucun
  chiffre publié de REEL-T0 ni de REEL-SPEC-* ne change ;
- le verrou actuel est celui qui a passé tous les contrôles du 07.10 (mypy strict, CI, fichiers de l'application à
  l'octet) ; revenir à pandas 3.0.6 imposerait lifelines 0.30.0 (lifelines 0.30.3 exige pandas < 3) et un nouveau
  passage de tous les contrôles ;
- pandas 3 change le type des chaînes ; ce passage doit rester une mise à jour volontaire, avec ses tests (ADR-0014).

Conséquences sur CLAIMS.md :

- REEL-T0, REEL-SPEC-BAT, REEL-SPEC-PIC, REEL-SURPRISE, REEL-SPEC-AUTRES, REEL-SPEC-NOUVEAUX, PRES-DATE-1 :
  **aucune** ; ajouter dans la colonne « Statut » de REEL-SPEC-BAT : « rejoué à l'identique le 07.10.2026 dans le
  verrou actuel (correctif du compte des adjudicateurs, `docs/backtest/reproductibilite.md`) ». Non rejouées : REEL-M6
  (`m6-reel` appelle le réseau), NET-1, CAT-1, SIMAP-1 et SIMAP-2 (mesures en ligne, datées).
- REEL-T0-COMB et REEL-T0-PIC : correction datée (indépendante du verrou), valeurs ci-dessus ; régénérer
  `docs/backtest/reel_t0_surprise_combine.json` et `docs/backtest/backtest_reel.md` (§ cible « pic ») avec la
  commande `--etendu`. Ces deux lignes ne sont affichées ni dans la visite ni dans l'application.
- M4-1 (FICTIF, « mécanique seulement ») : appliquer le correctif du benchmark M4 ci-dessus, régénérer
  `docs/modeles/m4_resultats_v1.json` (`proxsis rapports-modeles`) et corriger la ligne avec une note datée :
  « précision 0,989 ; rappel 0,907 ; F1 0,946 (base nom exact : rappel 0,735) — corrigé le 07.10.2026 : les
  entreprises inconnues étaient comptées comme manquées (pandas 3) ; première version : rappel 0,725, F1 0,837, base
  0,588 ». Sans ce correctif, le verrou actuel donne déjà ces valeurs, l'environnement d'origine les anciennes.
- Clore dans le registre des questions (notes de travail) la ligne du 07.10 09:44 (« REEL-SPEC-BAT ne se reproduit plus exactement ») et
  celle du 06.10 20:40 (`uv.lock`).

Si Hiba préfère revenir à l'environnement d'origine : remplacer `pandas==2.3.3` par `pandas==3.0.6` et
`lifelines==0.30.3` par `lifelines==0.30.0` dans `[tool.uv] constraint-dependencies`, retirer pytz et tzdata,
`uv lock`, puis tous les contrôles ; aucune ligne de CLAIMS ne change non plus (mêmes résultats, vérifiés ici).
