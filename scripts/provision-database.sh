#!/bin/sh
set -eu

DB_NAME=${DB_NAME:-dechapper}
DB_USER=${DB_USER:-dechapper_app}
PASSWORD_FILE=${PASSWORD_FILE:-/srv/yanoa/secrets/web_dechapper/db_password}
POSTGRES_CONTAINER=${POSTGRES_CONTAINER:-yanoa-postgres}

if [ ! -r "$PASSWORD_FILE" ]; then
  echo "Cannot read $PASSWORD_FILE" >&2
  exit 1
fi

DB_PASSWORD=$(cat "$PASSWORD_FILE")
ADMIN_USER=$(docker exec "$POSTGRES_CONTAINER" cat /run/secrets/postgres_admin_user)
docker exec -i "$POSTGRES_CONTAINER" psql -v ON_ERROR_STOP=1 --username "$ADMIN_USER" --dbname postgres \
  --set=db_name="$DB_NAME" --set=db_user="$DB_USER" --set=db_password="$DB_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'db_user', :'db_password')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'db_user') \gexec
SELECT format('ALTER ROLE %I PASSWORD %L', :'db_user', :'db_password') \gexec
SELECT format('CREATE DATABASE %I OWNER %I', :'db_name', :'db_user')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = :'db_name') \gexec
SELECT format('REVOKE ALL ON DATABASE %I FROM PUBLIC', :'db_name') \gexec
SQL

echo "Database $DB_NAME and role $DB_USER are ready."
