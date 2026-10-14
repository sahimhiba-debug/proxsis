# Déploiement : Vercel (appli) et Supabase (retours d'appel)

> Aujourd'hui, seule l'appli est en ligne (Vercel). La table Supabase des retours d'appel est prête pour le pilote ;
> aucune page ne l'appelle (le carnet garde les retours sur l'appareil).

Préparé le 2026-10-06 ; l'appli est en ligne depuis le 07.10.2026 sur `proxsis.vercel.app`, publique (avec son QR code),
les pages en `noindex, nofollow`. **Rien ne va en production sans l'accord de Hiba.** Les deux services ne reçoivent aucune donnée personnelle : l'appli ne
contient que des entreprises et des marchés publics (simap.ch, Bulletin officiel filtré) et des données FICTIVES
étiquetées ; Supabase ne stocke que des retours d'appel au format contraint (identifiant d'entreprise, code de
consultant, issue, semaine).

## Ce que l'appli exige

| Élément | Valeur |
|---|---|
| Dossier | `apps/web` (Next.js 16, React 19, Tailwind 4) |
| Build | `npm run build` (pages statiques pré-rendues, 445 pages) |
| Données | `apps/web/src/data/demo/*.json`, produites par `proxsis export-demo` et commitées |
| Variables publiques | aucune aujourd'hui ; pour le pilote, `NEXT_PUBLIC_SUPABASE_URL` et `NEXT_PUBLIC_SUPABASE_ANON_KEY` (l'adresse ouvre aussi la politique de contenu vers Supabase) |
| Apertus | **pas au déploiement** : les e-mails sont rédigés à l'export (`PUBLICAI_API_KEY` dans l'environnement de `proxsis export-demo`), contrôlés phrase par phrase, puis commités |

## 1. Supabase

1. Créer un projet (organisation de Hiba). Région : la plus proche disponible ; Zurich si l'offre la propose, sinon
   Francfort — à vérifier dans la console au moment de la création.
2. Depuis la racine du dépôt :

   ```bash
   npx supabase login
   npx supabase link --project-ref <ref du projet>
   npx supabase db push
   ```

   Les migrations `supabase/migrations/` créent la table `retours_appel` et fixent ses droits (audit semaine 2, M4) :
   - la clé publique (`anon`) peut **seulement ajouter** un retour, avec 4 colonnes (entreprise, code consultant du
     type M1, issue, semaine) ; ni identifiant ni date forgés, un même retour une seule fois ;
   - personne ne modifie, n'efface ni ne vide la table depuis l'appli ;
   - seuls les comptes inscrits dans `lecteurs_retours` lisent les retours : un compte créé librement ne lit rien.
3. Dans *Authentication → Sign In / Providers* : **fermer les inscriptions libres**. Ajouter les comptes lecteurs
   (chef d'agence, direction) à la main : `insert into public.lecteurs_retours (user_id) values ('<uuid du compte>');`
   depuis l'éditeur SQL. **Reste à faire avant un usage réel** : une limite de débit (fonction Edge) contre l'ajout
   en masse avec la clé publique.
3 bis. Vérifier les droits : `./supabase/tests/run.sh` (ou `make db-test`) joue les migrations et 18 cas de droits sur
   un PostgreSQL local **jetable** qui reproduit les rôles et privilèges par défaut de Supabase (Postgres.app ou
   `PG_BIN`) ; il ne touche à aucune base existante.
4. Récupérer, dans *Project Settings → API* : l'URL du projet et la clé `anon` (publique). **Ne jamais** utiliser
   la clé `service_role` dans l'appli.

## 2. Vercel

1. *Add New → Project*, importer le dépôt GitHub `sahimhiba-debug/proxsis` (branche `main`).
   Pour passer un projet Vercel existant sur ce dépôt : *Settings → Git → Connected Git Repository*, déconnecter
   l'ancien dépôt, connecter `sahimhiba-debug/proxsis`, *Production Branch* : `main` ; l'adresse ne change pas.
2. *Root Directory* : `apps/web`. *Framework* : Next.js (détecté). *Build Command* : `npm run build`.
   *Install Command* : `npm ci`.
3. *Environment Variables* : aucune aujourd'hui ; pour le pilote, `NEXT_PUBLIC_SUPABASE_URL` et
   `NEXT_PUBLIC_SUPABASE_ANON_KEY` (Production et Preview).
4. *Deployment Protection* : la production est publique (le QR code y mène) ; les prévisualisations des branches restent
   protégées par compte Vercel. Les pages ne sont pas indexées (`noindex, nofollow`).
5. Déployer, puis contrôler les adresses publiques : `node scripts/production/controle.mjs` (pages, mentions,
   en-têtes de sécurité, même version partout ; liste des adresses dans `scripts/production/domaines.json`).

## 3. Version hors ligne (instantané statique)

Pour le cas où le réseau tombe pendant la réunion :

```bash
scripts/copie-hors-ligne.sh     # dossier daté et versionné, essayé avant livraison, à copier sur une clé USB
```

Il s'ouvre en trois lignes (son `LISEZMOI.txt`) : un petit serveur local, puis `http://localhost:8000/fr/presentation/`.
Tout s'affiche hors ligne, carte comprise (contours des communes embarqués) ; les retours d'appel sont gardés sur
l'appareil. Le test `--project hors-ligne` rejoue la démo dans ces conditions, toutes les requêtes externes bloquées.

## 4. Ce qu'il faut de Hiba

- **Vercel** : une invitation dans l'équipe (rôle *Member*) ou un jeton de déploiement à durée limitée.
- **Supabase** : une invitation dans l'organisation (rôle *Developer*) ou la référence du projet et un jeton d'accès
  personnel à durée limitée. Les jetons ne seront jamais écrits dans un fichier ni dans les journaux.

## 5. Check-list après déploiement

- [ ] `/fr/` et `/de/` s'ouvrent ; le bandeau FICTIF et la mention simap sont visibles.
- [ ] Pour le pilote seulement (quand une page appellera la table) : un retour d'appel apparaît dans `retours_appel`
  (console Supabase), sans aucun texte libre.
- [ ] Le test de bout en bout passe contre l'URL de production.
- [ ] La version hors ligne est copiée sur la machine de démo et testée sans Wi-Fi.
