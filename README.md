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

## Verification

```sh
make check
make test
make compose-test
```

See [current-production-analysis.md](docs/current-production-analysis.md) for the audited legacy situation and [migration-runbook.md](docs/migration-runbook.md) for the isolated greenfield deployment.

