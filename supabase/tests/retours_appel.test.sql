-- Droits de la table retours_appel (audit semaine 2, M4). SQL simple, joué par supabase/tests/run.sh sur une base
-- jetable qui reproduit les privilèges par défaut de Supabase. Chaque cas lève une erreur s'il n'est pas respecté.
\set ON_ERROR_STOP on

create function pg_temp.expect_error(sql text, code text, what text) returns void language plpgsql as $$
begin
  execute sql;
  raise exception 'ÉCHEC : % (aucune erreur, % attendu)', what, code;
exception when others then
  if sqlstate <> code then
    raise exception 'ÉCHEC : % (erreur %, % attendu : %)', what, sqlstate, code, sqlerrm;
  end if;
end $$;
grant execute on function pg_temp.expect_error(text, text, text) to anon, authenticated;

do $$ begin
  if not (select relrowsecurity from pg_class where relname = 'retours_appel') then
    raise exception 'ÉCHEC : RLS non activée';
  end if;
end $$;

-- anon : ajouter un retour bien formé, rien d'autre
set role anon;
insert into public.retours_appel (entreprise_id, consultant, issue, semaine) values ('ent-0123456789', 'M1', 'rdv', '2026-10-05');
select pg_temp.expect_error($$insert into public.retours_appel (entreprise_id, consultant, issue, semaine) values ('ent-0123456789', 'Jean Dupont', 'rdv', '2026-10-05')$$, '23514', 'un nom à la place du code');
select pg_temp.expect_error($$insert into public.retours_appel (entreprise_id, consultant, issue, semaine) values ('ent-0123456789', 'JD', 'rdv', '2026-10-05')$$, '23514', 'des initiales à la place du code');
select pg_temp.expect_error($$insert into public.retours_appel (entreprise_id, consultant, issue, semaine) values ('ent-0123456789', 'M1', 'texte libre', '2026-10-05')$$, '23514', 'une issue hors liste');
select pg_temp.expect_error($$insert into public.retours_appel (entreprise_id, consultant, issue, semaine) values ('ent-0123456789', 'M1', 'rdv', '2026-10-06')$$, '23514', 'une semaine qui ne commence pas un lundi');
select pg_temp.expect_error($$insert into public.retours_appel (entreprise_id, consultant, issue, semaine) values ('ent-0123456789', 'M1', 'rdv', '9999-12-27')$$, '23514', 'une semaine hors période');
select pg_temp.expect_error($$insert into public.retours_appel (entreprise_id, consultant, issue, semaine, recu_le) values ('ent-0123456789', 'M2', 'rdv', '2026-10-05', '2099-01-01')$$, '42501', 'une date de réception forgée');
select pg_temp.expect_error($$insert into public.retours_appel (entreprise_id, consultant, issue, semaine, enregistre_le) values ('ent-0123456789', 'M2', 'rdv', '2026-10-05', '1900-01-01')$$, '42501', 'une date d''enregistrement forgée');
select pg_temp.expect_error($$insert into public.retours_appel (id, entreprise_id, consultant, issue, semaine) values (gen_random_uuid(), 'ent-0123456789', 'M2', 'rdv', '2026-10-05')$$, '42501', 'un identifiant forgé');
select pg_temp.expect_error($$insert into public.retours_appel (entreprise_id, consultant, issue, semaine) values ('ent-0123456789', 'M1', 'rdv', '2026-10-05')$$, '23505', 'le même retour deux fois');
select pg_temp.expect_error($$select count(*) from public.retours_appel$$, '42501', 'anon lit les retours');
select pg_temp.expect_error($$update public.retours_appel set issue = 'rdv'$$, '42501', 'anon modifie');
select pg_temp.expect_error($$delete from public.retours_appel$$, '42501', 'anon efface');
select pg_temp.expect_error($$truncate public.retours_appel$$, '42501', 'anon vide la table');
reset role;

-- authenticated : un compte inscrit quelconque ne lit rien ; seul un lecteur autorisé lit ; personne n'écrit
set role authenticated;
set request.jwt.claim.sub = '00000000-0000-0000-0000-000000000001';
do $$ begin
  if (select count(*) from public.retours_appel) <> 0 then
    raise exception 'ÉCHEC : un compte inscrit non autorisé lit les retours';
  end if;
end $$;
select pg_temp.expect_error($$insert into public.retours_appel (entreprise_id, consultant, issue, semaine) values ('ent-0123456789', 'S1', 'rdv', '2026-10-05')$$, '42501', 'authenticated ajoute');
select pg_temp.expect_error($$truncate public.retours_appel$$, '42501', 'authenticated vide la table');
select pg_temp.expect_error($$insert into public.lecteurs_retours (user_id) values ('00000000-0000-0000-0000-000000000001')$$, '42501', 'un compte s''ajoute lui-même aux lecteurs');
reset role;
insert into public.lecteurs_retours (user_id) values ('00000000-0000-0000-0000-000000000002');
set role authenticated;
set request.jwt.claim.sub = '00000000-0000-0000-0000-000000000002';
do $$ begin
  if (select count(*) from public.retours_appel) <> 1 then
    raise exception 'ÉCHEC : le lecteur autorisé ne lit pas les retours';
  end if;
end $$;
select pg_temp.expect_error($$update public.retours_appel set issue = 'rdv'$$, '42501', 'le lecteur modifie');
reset role;

select 'retours_appel : tous les cas passent' as resultat;
