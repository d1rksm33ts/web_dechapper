# Greenfield deployment and migration runbook

This runbook creates an isolated preview. It does not alter current production or DNS for `dechapper.be`.

## 1. Preview DNS

Create an `A` record:

```text
dechapper.greenfield.yanoa.be -> 185.115.218.135
```

## 2. Repository and secrets

Clone this repository to `/srv/yanoa/repositories/web_dechapper`. Create `/srv/yanoa/secrets/web_dechapper` with mode `0700` and four files with mode `0600`:

- `django_secret_key`: newly generated random value;
- `db_password`: newly generated database password;
- `smtp_password`: empty for the first preview, then a rotated SMTP password;
- `recaptcha_secret`: empty for the first preview, then a key authorized for the preview and production hostnames.

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

Create a Django administrator and add the current next-availability date and confirmation text through `/admin/`. This is preferable to copying the shared SQLite database: the one useful record is intentionally migrated, while all unrelated monolith data stays behind.

## 6. Contact form

Before enabling the form:

1. Rotate the legacy SMTP credential and store the new value only in `smtp_password`.
2. Create or update reCAPTCHA keys to include both the preview and final domains.
3. Set the SMTP variables, site key, `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, `RECAPTCHA_REQUIRED=true`, and `CONTACT_FORM_ENABLED=true` in `app.env`.
4. Recreate the app and submit a real end-to-end test request.

## 7. Cutover (later phase)

Only after acceptance: reduce DNS TTL, take a final backup, update the three production hostnames in Caddy and Django settings, switch DNS, verify redirects/TLS/forms, and retain the old service for a rollback window.

