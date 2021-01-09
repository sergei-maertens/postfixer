#!/bin/sh

set -e

# Wait for the database container
# See: https://docs.docker.com/compose/startup-order/
db_host=${DB_HOST:-db}
db_user=${DB_USER:-postgres}
db_password=${DB_PASSWORD}

until PGPASSWORD=$db_password psql -h "$db_host" -U "$db_user" -c '\q'; do
  >&2 echo "Waiting for database connection..."
  sleep 1
done

>&2 echo "Database is up."

# Apply database migrations
>&2 echo "Apply database migrations"
python src/manage.py migrate

# Start server
>&2 echo "Starting server"
exec uwsgi \
    --http :8000 \
    --module postfixer.wsgi \
    --static-map /static=/app/static \
    --static-map /media=/app/media  \
    --chdir src \
    --processes 4 \
    --threads 1
    # processes & threads are needed for concurrency without nginx sitting inbetween
