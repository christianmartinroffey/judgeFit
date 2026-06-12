#!/bin/sh
set -e

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
