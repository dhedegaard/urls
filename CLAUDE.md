# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A minimal Django app that maps short keywords to URLs, supporting HTTP 302 redirects and optional server-side proxying of responses. Authentication is required to manage redirects; unauthenticated users can only see/use keywords marked `public`.

## Dependencies

Dependencies are managed with [uv](https://docs.astral.sh/uv/) via `pyproject.toml` and locked in `uv.lock`.

## Commands

```bash
# Run tests
uv run manage.py test

# Run tests with coverage
uv run coverage run manage.py test && uv run coverage report

# Run dev server (uses SQLite by default)
uv run manage.py runserver

# Apply migrations
uv run manage.py migrate

# Run a single test
uv run manage.py test urls.tests.ViewsTestCase.test_list
```

## Architecture

The entire app lives in the `urls/` package (which is also the Django project package — `urls.settings`, `urls.urls`, `urls.wsgi`).

**Model:** `Url` in `urls/models.py` — `keyword` is the primary key (text), `url` is the redirect target, `proxy` controls server-side fetch vs. 302, `public` controls unauthenticated visibility.

**Request flow:** `urls/urls.py` routes all paths. A catch-all `(?P<keyword>.+)` at the bottom hits `views.redirector`, which either proxies (fetches and returns content) or 302-redirects. Paths like `create`, `logout`, `<keyword>/delete/`, `<keyword>/edit/` are matched before the catch-all.

**Form validation:** `UrlForm.clean()` in `urls/forms.py` resolves the keyword as a URL path and rejects it if it matches any non-`redirector` named URL — this prevents keywords from shadowing internal routes.

## Configuration

- **Database:** SQLite (`urls.db`) by default; set `DATABASE_URL` env var for PostgreSQL (production).
- **Debug mode:** `DEBUG=True` unless `PRODUCTION` env var is set.
- **ALLOWED_HOSTS:** Defaults to localhost + dhedegaard.dk domains; override with comma-separated `ALLOWED_HOSTS` env var.

## Deployment

The Dockerfile runs tests and `collectstatic` at build time, then `migrate` + `gunicorn` at startup. CI (GitHub Actions) builds and pushes to `ghcr.io` on pushes to `master`.
