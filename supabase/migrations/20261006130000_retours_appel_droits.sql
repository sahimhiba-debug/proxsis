-- Proxsis — droits de retours_appel resserrés (audit semaine 2, M4).
-- 1. Supabase accorde par défaut TOUT sur les tables du schéma public à anon et authenticated (y compris TRUNCATE,
--    qui ignore la RLS) : on retire tout, puis on rend seulement ce qui sert.
-- 2. La clé publique (anon) ajoute un retour et ne choisit que les 4 colonnes utiles : ni identifiant, ni dates.
-- 3. Lecture réservée aux comptes inscrits dans lecteurs_retours (liste blanche gérée par l'administrateur) : un compte
--    créé librement ne lit rien. À fermer aussi : les inscriptions libres (Authentication → Sign In / Providers).
-- 4. Codes de consultant du type M1 (jamais d'initiales), semaine = un lundi entre 2026 et 2030, un même retour une
--    seule fois. La limite de débit (fonction Edge) reste à faire avant tout usage réel.

revoke all on table public.retours_appel from anon, authenticated;
grant insert (entreprise_id, consultant, issue, semaine) on public.retours_appel to anon;
grant select on public.retours_appel to authenticated;

alter table public.retours_appel drop constraint if exists retours_appel_consultant_check;
alter table public.retours_appel
  add constraint consultant_code check (consultant ~ '^[A-Z][0-9]{1,3}$'),
  add constraint semaine_lundi check (semaine between date '2026-01-05' and date '2030-12-30'
                                      and extract(isodow from semaine) = 1),
  add constraint un_retour_par_issue unique (entreprise_id, consultant, semaine, issue);

drop policy if exists "anon insère des retours" on public.retours_appel;
create policy "anon insère des retours" on public.retours_appel for insert to anon with check (true);

create table if not exists public.lecteurs_retours (
  user_id uuid primary key
);
comment on table public.lecteurs_retours is 'Comptes autorisés à lire les retours d''appel (gérée par l''administrateur).';
alter table public.lecteurs_retours enable row level security;
revoke all on table public.lecteurs_retours from anon, authenticated;

-- contrôle d'appartenance dans un schéma non exposé par l'API, exécuté avec les droits du propriétaire
create schema if not exists private;
revoke all on schema private from public;
grant usage on schema private to authenticated;
create or replace function private.est_lecteur_retours() returns boolean
  language sql stable security definer set search_path = '' as
  $$ select exists (select 1 from public.lecteurs_retours l where l.user_id = auth.uid()) $$;
revoke all on function private.est_lecteur_retours() from public;
grant execute on function private.est_lecteur_retours() to authenticated;

drop policy if exists "authentifiés lisent les retours" on public.retours_appel;
create policy "lecteurs autorisés lisent les retours" on public.retours_appel for select to authenticated
  using (private.est_lecteur_retours());
