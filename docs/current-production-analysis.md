# Current Dechapper production analysis

Analysis date: 1 September 2026. This inventory was performed read-only.

## Current architecture

- `dechapper.be` is not an independent application. It is a Django module inside the shared `/home/yanoa/yanoa_be` monolith on the current `yanoa.be` VM.
- nginx terminates HTTPS and proxies to a host uWSGI service on `127.0.0.1:9191`.
- Production runs Ubuntu 22.04, Python 3.10 and Django 5.0.
- The application shares one SQLite database with the other YaNoa applications.
- `chapper.be` and `www.chapper.be` redirect to `https://dechapper.be`; `www.dechapper.be` redirects to the apex domain.
- The Dechapper data consists of one active configuration row: the next available date and the text for the confirmation email. The obsolete availability table is empty.
- Contact submissions are sent by email and are not persisted by the application.
- Relevant Dechapper code and templates are small. Most of the monolith's static footprint is unrelated legacy UI code.

## Risks found

- Application and data ownership are coupled to unrelated sites.
- The deployed Django branch is no longer supported.
- SMTP and reCAPTCHA credentials are embedded in legacy source code.
- Email errors can expose implementation details to visitors.
- Host validation is overly permissive.
- The frontend ships old Bootstrap, jQuery, animation and gallery dependencies for a simple brochure site.
- The shared root filesystem has little free space, partly due to unrelated legacy assets and operational files.

No credential from the legacy source has been copied. Rotate the existing SMTP and reCAPTCHA credentials before production cutover.

## Target boundary

`web_dechapper` is now an independent deployment unit with:

- its own Django application and image;
- its own PostgreSQL role and database on the shared database service;
- its own secrets directory;
- only `yanoa-edge` and `yanoa-data` network access;
- no published host port;
- database health checking and stdout logging;
- a custom dependency-free public frontend;
- no storage volume, because the application has no uploads or persistent files.

