"""Django settings for the termsandconditions demo project.

This is a demo, not a production template.  Copy
``settings_local_template.py`` to ``settings_local.py`` for local overrides;
that file is gitignored.
"""

import logging
import os
from pathlib import Path

# The demo project package directory.
BASE_DIR = Path(__file__).resolve().parent

DEBUG = True
INTERNAL_IPS = ["127.0.0.1"]
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Demo-only key. Never reuse this in a deployed site.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-demo-key-do-not-use-in-production"
)

ROOT_URLCONF = "termsandconditions_demo.urls"
WSGI_APPLICATION = "termsandconditions_demo.wsgi.application"
ASGI_APPLICATION = "termsandconditions_demo.asgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "termsandconditions",
]

# Ordered as Django documents it. UpdateCacheMiddleware really does belong
# above SecurityMiddleware; the terms redirect goes after AuthenticationMiddleware
# because it reads request.user.
MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "termsandconditions.middleware.TermsAndConditionsRedirectMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": DEBUG,
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]

if os.environ.get("TERMS_DATABASE", "sqlite") == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "termsandconditions",
            "USER": "termsandconditions",
            "PASSWORD": "",
            "HOST": "127.0.0.1",
            "PORT": "",
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "termsandconditions.db",
        },
    }

# Static and media files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticroot"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediaroot"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Cache settings
CACHE_MIDDLEWARE_SECONDS = 30
CACHE_MIDDLEWARE_KEY_PREFIX = "tc"

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Denver"
USE_I18N = False
USE_TZ = True

# Email settings. The console backend keeps the demo from needing an SMTP host.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "termsandconditions@example.com"
SERVER_EMAIL = "termsandconditions@example.com"

LOGIN_REDIRECT_URL = "/"

# termsandconditions settings
DEFAULT_TERMS_SLUG = "site-terms"
ACCEPT_TERMS_PATH = "/terms/accept/"
TERMS_EXCLUDE_URL_PREFIX_LIST = {"/admin", "/terms"}
# The app defaults to just {"/"}: which of a project's own paths have to stay
# reachable to someone with terms outstanding is a project decision. Logout is
# the one every project needs, at whatever URL it mounted django.contrib.auth.
TERMS_EXCLUDE_URL_LIST = {"/", "/termsrequired/", "/accounts/logout/", "/securetoo/"}
# Useful with i18n, where a language code can be prepended to your URLs.
TERMS_EXCLUDE_URL_CONTAINS_LIST = set()
TERMS_CACHE_SECONDS = 30
TERMS_EXCLUDE_USERS_WITH_PERM = "auth.can_skip_t&c"
TERMS_IP_HEADER_NAME = "REMOTE_ADDR"
TERMS_STORE_IP_ADDRESS = True

# Route Python warnings (deprecations included) through the logging config.
logging.captureWarnings(True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "py.warnings": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["mail_admins", "console"],
            "level": "ERROR",
            "propagate": True,
        },
        "termsandconditions": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
