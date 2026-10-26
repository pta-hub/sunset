#!/bin/sh
set -eu

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

python manage.py migrate --noinput
exec python run_tornado.py
