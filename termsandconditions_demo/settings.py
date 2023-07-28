"""
Django Settings File

INSTRUCTIONS
SAVE A COPY OF THIS FILE IN THIS DIRECTORY WITH THE NAME local_settings.py
MAKE YOUR LOCAL SETTINGS CHANGES IN THAT FILE AND DO NOT CHECK IT IN
CHANGES TO THIS FILE SHOULD BE TO ADD/REMOVE SETTINGS THAT NEED TO BE
MADE LOCALLY BY ALL INSTALLATIONS

local_settings.py, once created, should never be checked into source control
It is ignored by default by .gitignore, so if you don't mess with that, you should be fine.
"""
import os
import logging

# Set the root path of the project so it's not hard coded
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
# IP Addresses that should be treated as internal/debug users
INTERNAL_IPS = ("127.0.0.1",)
ALLOWED_HOSTS = ("localhost", "127.0.0.1")

# Cache Settings
CACHE_MIDDLEWARE_SECONDS = 30
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_KEY_PREFIX = "tc"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory that holds media.
# Note that as of Django 1.3 - media is for uploaded files only.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "mediaroot")

# Staticfiles Config
STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticroot")
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(PROJECT_ROOT, "static")]

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"

# DB settings
if os.environ.get("TERMS_DATABASE", "sqlite") == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "termsandconditions",
            "USER": "termsandconditions",
            "PASSWORD": "",
            "HOST": "127.0.0.1",
            "PORT": "",  # Set to empty string for default.
            "SUPPORTS_TRANSACTIONS": "true",
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(PROJECT_ROOT, "termsandconditions.db"),
            "SUPPORTS_TRANSACTIONS": "false",
        }
    }

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "termsandconditions_demo.wsgi.application"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "America/Denver"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Make this unique, and don't share it with anybody.
SECRET_KEY = "zv$+w7juz@(g!^53o0ai1uF82)=jkz9my_r=3)fglrj5t8l$2#"

# Default Auto Field Class
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Email Settings
EMAIL_HOST = "a real smtp server"
EMAIL_HOST_USER = "your_mailbox_username"
EMAIL_HOST_PASSWORD = "your_mailbox_password"
DEFAULT_FROM_EMAIL = "a real email address"
SERVER_EMAIL = "a real email address"

""" Django settings for the project. """

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS_LIST = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

# List of callables that add their data to each template

# List of directories to find templates in
TEMPLATE_DIRS_LIST = [os.path.join(PROJECT_ROOT, "templates")]

# Whether Template Debug is enabled
TEMPLATE_DEBUG_SETTING = DEBUG

# Needed to configure Django 1.8+
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATE_DIRS_LIST,
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ),
            "debug": TEMPLATE_DEBUG_SETTING,
            "loaders": TEMPLATE_LOADERS_LIST,
        },
    },
]

# For use Django 1.10+
MIDDLEWARE = (
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "termsandconditions.middleware.TermsAndConditionsRedirectMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
)

ROOT_URLCONF = "termsandconditions_demo.urls"

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "termsandconditions",
)

# Custom Variables Below Here #######

LOGIN_REDIRECT_URL = "/"

# Terms & Conditions (termsandconditions) Settings #######
DEFAULT_TERMS_SLUG = "site-terms"
ACCEPT_TERMS_PATH = "/terms/accept/"
TERMS_EXCLUDE_URL_PREFIX_LIST = {"/admin", "/terms"}
TERMS_EXCLUDE_URL_LIST = {"/", "/termsrequired/", "/accounts/logout/", "/securetoo/"}
TERMS_EXCLUDE_URL_CONTAINS_LIST = (
    {}
)  # Useful if you are using internationalization and your URLs could change per language
TERMS_CACHE_SECONDS = 30
TERMS_EXCLUDE_USERS_WITH_PERM = "auth.can_skip_t&c"
TERMS_IP_HEADER_NAME = "REMOTE_ADDR"
TERMS_STORE_IP_ADDRESS = True

# LOGGING ######
# Catch Python warnings (e.g. deprecation warnings) into the logger
try:
    logging.captureWarnings(True)
except AttributeError:  # python 2.6 does not do this  # pragma: nocover
    pass

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
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
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
