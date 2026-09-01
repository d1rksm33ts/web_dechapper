# Greenfield deployment and migration runbook

This runbook records the isolated greenfield deployment and the production
cutover completed on 2026-09-01.

The application does not publish a host port. Shared containerized Caddy reaches
`web-dechapper:8080` over `yanoa-edge`. The older `127.0.0.1:8003:8000` pattern
in `yanoa_home` is required by host-installed nginx; it is not needed when both
proxy and application are containers on the greenfield network.

## 1. Preview DNS

Create an `A` record:

```text
dechapper.greenfield.yanoa.be -> 185.115.218.135
```

## 2. Repository and secrets

Clone this repository to `/srv/yanoa/repositories/web_dechapper`. Create `/srv/yanoa/secrets/web_dechapper` with mode `0700`. Keep `app.env` at mode `0600`. Give the four Compose secret files owner `ubuntu`, numeric group `10001` (the fixed non-root container group) and mode `0640`:

- `django_secret_key`: newly generated random value;
- `db_password`: newly generated database password;
- `smtp_password`: empty for the first preview, then a rotated SMTP password;
- `turnstile_secret`: a Cloudflare Turnstile secret key. Use Cloudflare's official testing key only while the contact form is disabled, then replace it with the real widget secret before enabling submissions.

Copy `.env.example` to `/srv/yanoa/secrets/web_dechapper/app.env`. The initial preview deliberately uses the console email backend and disables form submission.

## 3. Database

From the repository:

```sh
sudo ./scripts/provision-database.sh
```

This creates only the `dechapper_app` role and `dechapper` database. The shared infrastructure backup job discovers every non-template PostgreSQL database, so this database is automatically included in local and Dropbox backups.

## 4. Application and edge route

Start the app with its protected environment file:

```sh
docker compose --env-file /srv/yanoa/secrets/web_dechapper/app.env up -d --build
```

Add this independent site block to the shared Caddy configuration:

```caddyfile
dechapper.greenfield.yanoa.be {
    encode zstd gzip
    reverse_proxy web-dechapper:8080
}
```

Reload Caddy only after DNS resolves to the greenfield VM.

## 5. Configuration data

Create a least-privilege editor account and enter its password interactively:

```sh
docker exec -it web-dechapper python manage.py createeditor dirk
```

Use `/beheer/` to update the current next-availability date. This dedicated workflow does not require Django administrator access. Migrating only the useful configuration record keeps unrelated monolith data out of this application.

## 6. Contact form

Before enabling the form:

1. Rotate the legacy SMTP credential and store the new value only in `smtp_password`.
2. Create a Cloudflare Turnstile widget in Managed mode for `dechapper.greenfield.yanoa.be`, `dechapper.be`, and `www.dechapper.be`.
3. Store its secret in `turnstile_secret` and set the SMTP variables, `TURNSTILE_SITE_KEY`, `TURNSTILE_REQUIRED=true`, `TURNSTILE_EXPECTED_HOSTNAMES`, `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, and `CONTACT_FORM_ENABLED=true` in `app.env`.
4. Recreate the app and submit a real end-to-end test request.

## 7. Production cutover and legacy decommissioning

The production canonical hostname is `dechapper.be`. `www.dechapper.be`,
`chapper.be`, and `www.chapper.be` redirect permanently to the canonical
hostname while preserving the requested path and query string. All four DNS
records point to `185.115.218.135`, where Caddy manages their TLS certificates.

Before cutover, a final legacy SQLite snapshot was copied to:

```text
/srv/yanoa/backups/legacy/dechapper/dechapper-legacy-pre-cutover-2026-09-01.sqlite3
```

The old host used the shared `yanoa_be` uWSGI monolith, so that service cannot
be stopped until the remaining YaNoa routes have migrated. Only the legacy
De Chapper nginx sites were deactivated. Their symlinks remain recoverable at:

```text
/etc/nginx/decommissioned-sites/2026-09-01-dechapper/
```

The four obsolete Certbot renewal profiles were moved to:

```text
/etc/letsencrypt/renewal-decommissioned/2026-09-01-dechapper/
```

The old code, SQLite database, and certificate material have deliberately not
been deleted. A rollback consists of restoring both nginx symlinks to
`/etc/nginx/sites-enabled/`, running `sudo nginx -t`, reloading nginx, restoring
the renewal profiles if needed, and changing the four DNS records back to
`217.19.239.177`.

Post-decommission verification confirmed that the other old-host applications
remained reachable. An unrelated pre-existing issue was observed: the
certificate currently served for `www.yanoa.be` does not include that hostname;
the canonical `yanoa.be` endpoint remains healthy.
