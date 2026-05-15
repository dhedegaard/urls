from __future__ import annotations
import os
from typing import Dict, cast

ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEBUG: bool = "PRODUCTION" not in os.environ
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ADMINS = (("Dennis Hedegaard", "dennis@dhedegaard.dk"),)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "urls.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "localhost",
    }
}

if "DATABASE_URL" in os.environ and os.environ["DATABASE_URL"]:
    import dj_database_url

    DATABASES["default"] = cast(
        Dict[str, str],
        dj_database_url.config(
            default=os.environ["DATABASE_URL"],
            conn_max_age=600,
            ssl_require=True,
        ),
    )

ALLOWED_HOSTS: list[str] = (
    os.environ["ALLOWED_HOSTS"].split(",")
    if "ALLOWED_HOSTS" in os.environ
    else [
        "127.0.0.1",
        "u.neo2k.dk",
        "urls.neo2k.dk",
        "u.dhedegaard.dk",
        "urls.dhedegaard.dk",
        "localhost",
    ]
)

TIME_ZONE = "Europe/Copenhagen"
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True

STATIC_ROOT = os.path.join(ROOT, "staticfiles/")
STATIC_URL = "/static/"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

SECRET_KEY = "jw-_tia*(q^e^pb^5n7q492sxpm%k*xg!0ya7uuh$%htpd7*7g"

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

ROOT_URLCONF = "urls.urls"
WSGI_APPLICATION = "urls.wsgi.application"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "urls",
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

TEST_RUNNER = "django.test.runner.DiscoverRunner"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]
