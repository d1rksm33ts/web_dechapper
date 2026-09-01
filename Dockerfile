FROM python:3.14.7-slim-trixie@sha256:656d12e70054d5fda18a045e2494c96701e9792dd1445f95b3d038df954f57e9 AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.14.7-slim-trixie@sha256:656d12e70054d5fda18a045e2494c96701e9792dd1445f95b3d038df954f57e9

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PATH="/opt/venv/bin:$PATH"
WORKDIR /app
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app . .
RUN DJANGO_SECRET_KEY=build-only DJANGO_SECURE_COOKIES=false python manage.py collectstatic --noinput && chmod +x /app/entrypoint.sh
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--workers=2", "--threads=4", "--timeout=45", "--no-control-socket", "--access-logfile=-", "--error-logfile=-", "dechapper_project.wsgi:application"]
