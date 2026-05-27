#!/bin/sh
set -e

echo "Waiting for postgres..."
until python -c "import psycopg2; psycopg2.connect(host='$POSTGRES_HOST', port='$POSTGRES_PORT', dbname='$POSTGRES_DB', user='$POSTGRES_USER', password='$POSTGRES_PASSWORD')" 2>/dev/null; do
  sleep 1
done
echo "Postgres ready."

if [ "$1" = "web" ]; then
  python manage.py migrate --noinput
  exec python manage.py runserver 0.0.0.0:8000

elif [ "$1" = "celery" ]; then
  exec celery -A judgeFit worker -l info

elif [ "$1" = "celery-beat" ]; then
  exec celery -A judgeFit beat -l info

else
  exec "$@"
fi
