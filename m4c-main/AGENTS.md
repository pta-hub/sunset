# M4C project notes

This directory contains the Django project. Run management commands from here:

```sh
python manage.py test
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

The application uses server-rendered templates, vanilla JavaScript, and the
bundled county and ward datasets. Member accounts use Django authentication and
do not require contact verification. Volunteer API requests are validated and
persisted as `VolunteerRegistration` records.

Keep production secrets in environment variables. Production requires
`DJANGO_SECRET_KEY`; configure allowed hosts, PostgreSQL, and SMTP in the
deployment environment as documented in `README.md`.

## Base44 sandbox preview

`docker-compose.base44.yml` (repo root of this directory) runs the bind-mounted
source with `python manage.py runserver 0.0.0.0:8000` on host port 3000, installs
`requirements.txt` and applies migrations at start. No external credentials are
needed to boot: `DJANGO_DEBUG=true` makes Django generate a throwaway secret key
(sessions reset per restart), `ALLOWED_HOSTS` becomes `*`, and email falls back to
the console backend. SQLite lives at `db.sqlite3` (gitignored).

The sandbox proxy forwards the public preview origin on form POSTs, so Compose sets
`DJANGO_CSRF_TRUSTED_ORIGINS=https://3000-${BASE44_PUBLIC_HOST_SUFFIX}` through the
app's existing env setting. Without it, register/login/password-reset/volunteer POSTs
fail with "CSRF verification failed". `BASE44_PREVIEW_MODE` is passed through for the
platform; the app ignores it today.

Verification: `curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/` should
return 200, and these render real titles: `/`, `/leadership/`, `/comrades/`,
`/counties/`, `/counties/mombasa/`, `/login/`, `/register/`, `/password-reset/`.
`POST /api/volunteers` (JSON + `X-CSRFToken`) returns 201. Member registration signs
the account in immediately, so browser flows create real users — delete test
accounts and volunteer records afterwards.
