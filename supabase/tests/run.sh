#!/usr/bin/env bash
# Tests des migrations Supabase sur un PostgreSQL local JETABLE (créé puis détruit dans un dossier temporaire).
# Reproduit les rôles et les privilèges par défaut de Supabase (supabase_stub.sql). Ne touche à aucune base existante.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bin="${PG_BIN:-}"
if [ -z "$bin" ]; then
  if command -v initdb >/dev/null 2>&1; then bin="$(dirname "$(command -v initdb)")"
  elif [ -x /Applications/Postgres.app/Contents/Versions/latest/bin/initdb ]; then bin=/Applications/Postgres.app/Contents/Versions/latest/bin
  else echo "NON TESTÉ : PostgreSQL introuvable (initdb). Installer Postgres.app ou définir PG_BIN." >&2; exit 2; fi
fi
tmp="$(mktemp -d)"
cleanup() { "$bin/pg_ctl" -D "$tmp/data" -m immediate stop >/dev/null 2>&1 || true; rm -rf "$tmp"; }
trap cleanup EXIT
"$bin/initdb" -D "$tmp/data" -U postgres --auth=trust >/dev/null
"$bin/pg_ctl" -D "$tmp/data" -o "-k $tmp -c listen_addresses='' -p 54329" -l "$tmp/log" -w start >/dev/null
psql=("$bin/psql" -h "$tmp" -p 54329 -U postgres -d postgres -q -v ON_ERROR_STOP=1)
"${psql[@]}" -f "$here/supabase_stub.sql"
for m in "$here"/../migrations/*.sql; do "${psql[@]}" -f "$m"; done
"${psql[@]}" -At -f "$here/retours_appel.test.sql"
