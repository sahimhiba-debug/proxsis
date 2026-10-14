# Proxsis, l'application web

Next.js 16 (App Router), React 19, Tailwind 4, Motion. Deux identités dans la même application : l'outil du
consultant (`src/futur/`, `/[lang]/semaine/…`) et la visite guidée « Votre prochain lundi » (`src/visite/`, avec ce
qu'elle reprend de l'ancienne présentation dans `src/presentation/` ; `/[lang]/presentation/`). Toutes les données sont des fichiers JSON du dépôt (`src/data/`), validés par des schémas et
figés à la construction : aucune page n'appelle de service extérieur. Vue d'ensemble :
[../../docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md).

## Commandes

Node 22 (`.nvmrc`), dépendances à version exacte (`npm ci`).

| Commande | Rôle |
|---|---|
| `npm run dev` | développement, http://localhost:3000 |
| `npm run lint`, `npm run typecheck`, `npm test` | ESLint, TypeScript strict, tests unitaires (vitest) |
| `npm run build` | version servie (en-têtes de sécurité de `next.config.ts`) |
| `npm run build:static` | copie statique dans `out/`, pour la démonstration sans réseau |
| `npm run e2e:prepare && npx playwright test` | bout en bout : en ligne (port 3211), hors ligne (`out/` sur le port 4310, toute requête externe bloquée), en allemand |
| `npm run visuel:temps` | 68 captures de référence comparées au pixel, à J, J+2, J+30 et J+90 (après `npm run build:static`) |
| `npm run knip`, `npm run cycles` | code mort, imports circulaires (aucun des deux attendu ; à lancer à la main, pas en CI) |
| `node scripts/budget.mjs <url>` | budget de performance au téléphone (`perf-budget.json`) sur une version servie |

## Où sont les choses

| Dossier | Contenu |
|---|---|
| `src/app/` | les routes ; `fonts.css` déclare les polices, servies depuis `public/fonts` (SIL OFL, licences jointes) |
| `src/futur/`, `src/futur/futur.css` | composants et style de l'outil du consultant |
| `src/visite/` | la visite : état et étapes, scènes, textes FR/DE (`copy.ts`, `pages.ts`, `notes.ts`) |
| `src/presentation/` | ce que la visite reprend de l'ancienne présentation : « Choisissez une date », le dossier de preuves, le cadre (`direction.css`, `ui.tsx`), leurs textes FR/DE (`copy.ts`, `copy_c.ts`), la démo au téléphone (`phone/`) |
| `src/i18n/dictionaries.ts` | textes FR/DE de l'outil (même clés dans les deux langues, vérifié par les tests) |
| `src/lib/` | lecture des données (`data.ts`), schémas (`schema.ts`), types, formats, carnet |
| `src/data/` | les fichiers exportés par le moteur Python (ne pas les modifier à la main) |
| `e2e/` | tests de bout en bout ; `e2e/visuel/` : captures de référence (macOS) |

Les retours d'appel restent sur l'appareil (le carnet). La table `retours_appel` (`../../supabase/migrations`) est
prête pour le pilote, mais aucune page ne l'appelle aujourd'hui.
