# ADR-0001 — Architecture : moteur Python + produit Next.js, démo hors ligne

- Statut : accepté — 2026-10-04 — couloir plateforme

## Contexte
Le cahier des charges impose la pile de l'équipe gagnante du Hack VS (Next.js 16, React 19, TypeScript,
Tailwind 4, shadcn/ui, Supabase) avec des services Python derrière, la parité IA (faux fournisseur) et une
démo qui marche hors ligne et en ligne.

## Décision
- **Moteur** : paquet Python `proxsis` (connecteurs, schéma, modèles, backtest), sans service obligatoire.
- **Produit** : Next.js dans `apps/web`. Deux modes : *démo* (données FICTIVES exportées par
  `proxsis export-demo` en JSON statique, aucun réseau) et *connecté* (Supabase : auth, PostgreSQL avec RLS).
- **API Python optionnelle** (FastAPI) pour les calculs à la demande ; l'appli fonctionne sans elle.
- **Données** : chaque ligne porte sa provenance ; double date `event_date` / `available_at`.

## Alternatives
Tout en TypeScript (pas d'écosystème ML mûr) ; tout en Python (contraire à la pile imposée) ;
démo uniquement en ligne (contraire au cahier des charges).

## Conséquences
Deux langages, contrat de données versionné entre eux (`apps/web/src/data/demo/*.json`). La démo hors
ligne est garantie par construction.
