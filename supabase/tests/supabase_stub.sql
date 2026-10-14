-- Reproduction minimale de Supabase pour tester les migrations sur un PostgreSQL local jetable :
-- rôles de l'API, fonction auth.uid() et privilèges PAR DÉFAUT accordés par Supabase sur le schéma public
-- (tout, à anon et authenticated : c'est ce que les migrations doivent reprendre).
create role anon nologin;
create role authenticated nologin;
create schema auth;
create function auth.uid() returns uuid language sql stable as
  $$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
grant usage on schema public, auth to anon, authenticated;
grant execute on function auth.uid() to anon, authenticated;
alter default privileges in schema public grant all on tables to anon, authenticated;
