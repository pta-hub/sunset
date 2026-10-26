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
