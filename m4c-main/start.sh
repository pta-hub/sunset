#!/bin/sh
set -eu

if [ -f ".env" ]; then
  set -a
  . ./.env
  set +a
fi

export DJANGO_DEBUG="${DJANGO_DEBUG:-false}"

if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
  if [ "$DJANGO_DEBUG" != "true" ]; then
    echo "DJANGO_SECRET_KEY must be configured for production." >&2
    exit 1
  fi
  secret_file=".django_secret_key"
  if [ ! -s "$secret_file" ]; then
    umask 077
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" > "$secret_file"
  fi
  DJANGO_SECRET_KEY="$(cat "$secret_file")"
  export DJANGO_SECRET_KEY
fi

python manage.py collectstatic --noinput
python manage.py migrate --noinput

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}${DJANGO_SUPERUSER_EMAIL:-}${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  if [ -z "${DJANGO_SUPERUSER_USERNAME:-}" ] || \
     [ -z "${DJANGO_SUPERUSER_EMAIL:-}" ] || \
     [ -z "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo "DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD must all be configured." >&2
    exit 1
  fi

  superuser_exists="$(
    python manage.py shell --verbosity 0 -c 'import os; from django.contrib.auth import get_user_model; print("yes" if get_user_model().objects.filter(username=os.environ["DJANGO_SUPERUSER_USERNAME"], is_superuser=True).exists() else "no")'
  )"
  if [ "$superuser_exists" = "no" ]; then
    python manage.py createsuperuser --noinput
  elif [ "$superuser_exists" = "yes" ]; then
    echo "Configured Django superuser already exists; skipping creation."
  else
    echo "Could not determine whether the configured Django superuser exists." >&2
    exit 1
  fi
fi

exec gunicorn m4c.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers 2 \
  --timeout 60
