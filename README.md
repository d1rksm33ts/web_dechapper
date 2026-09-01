# web_dechapper

Standalone, containerized website for [dechapper.be](https://dechapper.be). It preserves the public identity and content of the current site while separating it from the legacy YaNoa Django monolith.

## Local development

Python 3.14 is required.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
DJANGO_DEBUG=true DJANGO_SECURE_COOKIES=false python manage.py migrate
DJANGO_DEBUG=true DJANGO_SECURE_COOKIES=false python manage.py runserver
```

Without `DB_HOST`, local development uses SQLite. Production always sets `DB_HOST` and uses the dedicated PostgreSQL database.

## Availability editor

The public **Login** link opens the dedicated editor at `/beheer/`. Authentication is required; the technical Django admin is not part of this workflow. An authenticated editor can select the next available date, save it explicitly, and follow the link back to the public availability section to verify the result.

Create the first editor account from the running application container:

```sh
docker exec -it web-dechapper python manage.py createeditor dirk
```

The contact form is protected by a honeypot and Cloudflare Turnstile with server-side token, action, and hostname validation. Production refuses to enable submissions unless real SMTP and Turnstile credentials are configured; Cloudflare testing keys are accepted only while the production form remains disabled.

## Verification

```sh
make check
make test
make compose-test
```

See [current-production-analysis.md](docs/current-production-analysis.md) for the audited legacy situation and [migration-runbook.md](docs/migration-runbook.md) for the isolated greenfield deployment.
