# Movement for Change

Movement for Change (M4C) is a Django website for peacebuilding, community
participation, and county and campus leadership in Kenya. The application is
in [`m4c-main`](m4c-main/); its detailed setup and configuration guide is in
[`m4c-main/README.md`](m4c-main/README.md).

## Run locally

```sh
cd m4c-main
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Publish on Render

Configure the Render web service with:

- Root directory: `m4c-main`
- Build command: `pip install -r requirements.txt`
- Start command: `sh start.sh`
- Environment: `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and a persistent PostgreSQL `DATABASE_URL`
- Deploy branch: `freeze-development-requirements` or the branch configured for the service

Push the commit to the service's deploy branch. If automatic deploys are
disabled, open the service in the Render dashboard and select **Manual Deploy**
then **Deploy latest commit**. Wait for the deploy to finish, confirm the
deployed commit matches the pushed commit, and check `/leadership/` on the live
site. The startup script collects static files before starting the app so
regional leader portraits are served by WhiteNoise.
