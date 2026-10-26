# Movement for Change (M4C)

M4C is a Django website for peacebuilding, community participation, and the
movement's county and campus structures in Kenya.

## Local setup

Run these commands from `m4c-main`:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

The default local database is SQLite. The homepage, leadership, Comrades, and
county directory pages are available immediately; the interactive map uses
the bundled county and ward GeoJSON data.

To serve through Tornado instead, configure a secret and start the app:

```sh
export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
python run_tornado.py
```

Tornado listens on `0.0.0.0:8000` by default. Set `HOST` or `PORT` to change
the bind address. `sh start.sh` applies migrations and launches Tornado. For a
local start without a configured key, set `DJANGO_DEBUG=true`; the script then
stores a generated key in the ignored `.django_secret_key` file.

## Configuration

- `DJANGO_SECRET_KEY`: required when `DJANGO_DEBUG=false`; keep it in the
  hosting provider's secret store.
- `DJANGO_DEBUG`: defaults to `true` for local development and `false` on
  Render. Keep it disabled in production.
- `DJANGO_ALLOWED_HOSTS`: optional comma-separated hostnames. Render's
  `RENDER_EXTERNAL_HOSTNAME` is used when available.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: optional comma-separated HTTPS origins for
  additional deployment domains.
- `DATABASE_URL`: optional PostgreSQL URL. Without it, Django uses local
  SQLite. Configure a persistent PostgreSQL database in production.
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`,
  `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL`: SMTP settings for password
  reset messages. Without SMTP configuration, Django uses its console email
  backend for local development.

The default sender is `Movement for Change
<noreply@movementforchange.co.ke>`. In production, authorize the sender domain
with the SMTP provider and configure SPF and DKIM. Password reset responses
do not disclose whether an account exists.

## Volunteer registrations and member accounts

Member registration creates a Django account and signs the member in
immediately; email and phone verification are not required. Members can sign
in using their username or email, view `/profile/`, and reset passwords from
`/password-reset/`.

The CSRF-protected `POST /api/volunteers` endpoint accepts JSON using either
camelCase (`fullName`, `phoneNumber`) or snake_case (`full_name`,
`phone_number`) names. Successful submissions are stored and return HTTP 201
with a registration ID. Django admins can manage member profiles and volunteer
registrations at `/admin/`.

## Deployment

For Render, set the service root directory to `m4c-main`, configure
`DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and a persistent PostgreSQL
`DATABASE_URL`, and use `pip install -r requirements.txt` as the build command.
Use `sh start.sh` as the start command. The start script runs migrations before
serving. Render's forwarded HTTPS scheme is trusted for CSRF handling.

`docker-compose.base44.yml` provides a local Python 3.12 development container
on host port 3000 and runs Django's auto-reloading development server.

Run the test suite with:

```sh
python manage.py test
```
