# ADR-0007 — M3 : extraction des publications FR/DE — règles d'abord, LLM derrière une interface

- Statut : accepté — 2026-10-04 — couloir modèles / IA

## Décision
- Extracteur à **règles** développé sur un jeu de développement généré, évalué **une seule fois** sur le jeu
  gelé `data/annotations/extraction_v1.jsonl` (empreinte dans `FROZEN.md`, gelé avant tout essai).
- `LLMExtractor` derrière `LLMProvider` : `FakeLLM` par défaut, Apertus via Public AI (API compatible OpenAI,
  sortie structurée JSON Schema, repli appel d'outil). Même post-traitement que les règles (aucun nom de
  particulier ne peut sortir, codes métiers validés).
- Modèle spécialisé (GLiNER, XLM-R) seulement si un LLM est trop coûteux ou lent **et** si le modèle distillé
  s'en approche à quelques points près.

## Résultat mesuré
Règles sur le jeu gelé v1 (FICTIF, rédigé par l'agent) : voir CLAIMS.md. **Apertus non mesuré** : réseau
bloqué et clé absente. Le jeu v1 n'est pas un jeu de référence : l'équipe doit annoter ≥ 200 publications
réelles (`docs/annotation/guide_extraction.md`).

## Conséquences
Le produit fonctionne hors ligne avec les règles ; Apertus se branche par variables d'environnement.
