-- Proxsis — retours d'appel en un clic (démo « Lundi 8 h à Martigny »).
-- Aucune donnée personnelle : identifiant d'entreprise (public, simap), code de consultant (C1, M1…, jamais un
-- nom), issue de l'appel, semaine. Les formats sont contraints : aucun texte libre ne peut être enregistré.

create extension if not exists pgcrypto;

create table if not exists public.retours_appel (
  id uuid primary key default gen_random_uuid(),
  entreprise_id text not null check (entreprise_id ~ '^ent-[0-9a-f]{10}$'),
  consultant text not null check (consultant ~ '^[A-Z]{1,2}[0-9]{0,3}$'),
  issue text not null check (issue in ('rdv', 'pas_de_besoin', 'a_rappeler')),
  semaine date not null,
  enregistre_le timestamptz not null default now(),
  recu_le timestamptz not null default now()
);

comment on table public.retours_appel is
  'Retours d''appel des consultants (démo). Pas de donnée personnelle : formats contraints, aucun texte libre.';

alter table public.retours_appel enable row level security;

-- L'appli (clé publique « anon ») peut seulement AJOUTER un retour, jamais lire, modifier ni effacer.
create policy "anon insère des retours" on public.retours_appel
  for insert to anon
  with check (enregistre_le <= now() + interval '5 minutes');

-- Les comptes connectés (chef d'agence, direction) lisent les retours pour l'apprentissage et le tableau de bord.
create policy "authentifiés lisent les retours" on public.retours_appel
  for select to authenticated
  using (true);

revoke update, delete on public.retours_appel from anon, authenticated;
