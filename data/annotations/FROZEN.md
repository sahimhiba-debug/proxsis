# Jeux de test gelés

| Fichier | SHA-256 | Gelé le | Contenu |
|---|---|---|---|
| `data/annotations/bo_vs_v1/tirage_fr_gele.jsonl` | `1c5545231d3b455c8c97390ba5edeb4fa1ce86ab7c8e31817bcde539701566d3` | 2026-10-06, **avant** toute mesure ; regelé avant toute annotation | RÉEL — Bulletin officiel du Valais, 100 demandes d'autorisation de construire en français tirées au hasard (graine 20261006) parmi 531 importées des PDF. **Mêmes 100 identifiants** que le premier gel (`ab02314e…`) ; seules les empreintes des textes changent, car les textes sont refiltrés (filtre renforcé après les audits de la semaine 2 et de la reconstruction : notes de travail non publiées, verdict v3 « remplaçable »). Aucune annotation faite entre-temps. Textes hors git |
| `data/annotations/bo_vs_v1/tirage_de_gele.jsonl` | `c35cc0e3e9593a642a05171282915d6f2124fb0a33a329f6d7f3d4113d399411` | 2026-10-06, **avant** toute mesure | RÉEL — Bulletin officiel du Valais, 50 demandes d'autorisation de construire en allemand tirées au hasard (graine 20261006) parmi 277 au contenu complet (exports « Individuelle Zusammenstellung »), répartition A1/A2 avec 6 doubles dans `bo_vs_v1/de/repartition.json`. Textes de la reconstruction v3 (même audit). **Annotation non lancée** : lecture allemande des annotateurs à confirmer par Hiba. Textes hors git |
| `extraction_v1.jsonl` | `c40a6c45ab58a2db87b334974dfca3e2d8be2d4d23c51b775408732e9b542cd6` | 2026-10-04, **avant** tout essai d'extraction (règles ou LLM) | 36 publications FICTIVES rédigées à la main (12 permis, 12 adjudications, 12 registre du commerce ; 18 FR, 18 DE), annotées selon `docs/annotation/guide_extraction.md` |

> **Monde fictif : prouve que le code fonctionne, pas sa performance réelle.**
>
> **Le jeu v1 a été écrit ET annoté par l'agent de développement (Claude)**,
> qui a aussi écrit les règles d'extraction et le générateur du jeu de
> développement. Les mêmes tournures se retrouvent donc des deux côtés : les
> scores mesurés sur v1 (ex. 92 % à 100 % d'exactitude par champ pour les
> règles) sont **optimistes** et ne disent rien de la performance sur de
> vraies publications. Ils servent seulement à vérifier que la chaîne de
> mesure fonctionne.

Règles :
- Un jeu gelé ne se modifie plus. Une correction donne une nouvelle version (`extraction_v2.jsonl`) avec sa date ; les résultats de v1 restent publiés.
- Le test `python/tests/test_frozen_sets.py` vérifie l'empreinte.
- Le jeu de référence est le **jeu réel v2** (`data/annotations/reel_v2/`) : 150 publications réelles FR/DE, annotées par l'équipe (double annotation, accord inter-annotateurs), **gelé avant toute mesure**. Tant qu'il n'est pas annoté et gelé, aucun score « réel » n'existe.
