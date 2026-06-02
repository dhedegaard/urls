# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A minimal Django app that maps short keywords to URLs, supporting HTTP 302 redirects and optional server-side proxying of responses. Authentication is required to manage redirects; unauthenticated users can only see/use keywords marked `public`.

## Dependencies

Dependencies are managed with [uv](https://docs.astral.sh/uv/) via `pyproject.toml` and locked in `uv.lock`. Python is pinned to `==3.14.*` (also the `python:3.14` base image and pyright's `pythonVersion`); ruff targets `py314`.

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

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run pyright .
```

## Architecture

The entire app lives in the `urls/` package (which is also the Django project package — `urls.settings`, `urls.urls`, `urls.wsgi`).

**Model:** `Url` in `urls/models.py` — `keyword` is the primary key (text), `url` is the redirect target, `proxy` controls server-side fetch vs. 302, `public` controls visibility in the list view (unauthenticated users only see public entries in the list, but the redirector itself does not check `public` — any keyword works if you know it).

**Request flow:** `urls/urls.py` routes all paths. A catch-all `(?P<keyword>.+)` at the bottom hits `views.redirector`, which either proxies (fetches and returns content via `requests.get()` with a 15-second timeout) or 302-redirects. Paths like `create`, `logout`, `<keyword>/delete/`, `<keyword>/edit/` are matched before the catch-all.

**Named URL patterns:** `list`, `create`, `edit`, `delete`, `redirector`, `urls_login`, `urls_logout`. The login/logout names use the `urls_` prefix to avoid clashing with Django's built-in auth URL names.

**Form validation:** `UrlForm.clean()` in `urls/forms.py` resolves the keyword as a URL path and rejects it if it matches any non-`redirector` named URL — this prevents keywords from shadowing internal routes. A `slugify` checkbox on the form auto-converts the keyword to a slug before saving.

**Edit behavior:** The `create` view doubles as edit (routed at `<keyword>/edit/`). If the keyword itself is renamed during an edit, the old `Url` record is deleted after the new one is saved.

**Tests:** All tests are in `ViewsTestCase` in `urls/tests.py`. Both proxy tests mock `urls.views.requests` (the whole module) — the success test stubs a minimal response, the failure test sets a `ConnectionError` side effect.

## Configuration

- **Database:** SQLite (`urls.db`) by default; set `DATABASE_URL` env var for PostgreSQL (production).
- **Debug mode:** `DEBUG=True` unless `PRODUCTION` env var is set.
- **Secret key:** Read from `SECRET_KEY` env var; falls back to a hardcoded dev default.
- **ALLOWED_HOSTS:** Defaults to localhost + dhedegaard.dk domains; override with comma-separated `ALLOWED_HOSTS` env var.
- **Port:** Set `PORT` env var to control the gunicorn port (used in docker-compose).

## Deployment

The Dockerfile runs ruff, pyright, tests, and `collectstatic` at build time, then `migrate` + `gunicorn` at startup. CI (GitHub Actions) builds and pushes to `ghcr.io` on pushes to `master`.
