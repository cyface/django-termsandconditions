"""Local Django Settings, Copy This File As settings_local.py and Make Local Changes"""

from .settings import *

# Local Overrides Here
# Local DB settings. (Postgres)
DATABASES = {
    #    'default': {
    #        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #        'NAME': 'termsandconditions',
    #        'USER': 'termsandconditions',
    #        'PASSWORD': '',
    #        'HOST': '127.0.0.1',
    #        'PORT': '', # Set to empty string for default.
    #        'SUPPORTS_TRANSACTIONS': 'true',
    #    },
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": PROJECT_ROOT + "/termsandconditions.db",
        "SUPPORTS_TRANSACTIONS": "false",
    }
}

# Cache Settings
CACHES = {
    "default": {
        "BACKEND": "dummy:///",
        "LOCATION": "",
        "OPTIONS": {"PASSWORD": ""},
    },
}
CACHE_MIDDLEWARE_SECONDS = 30
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_KEY_PREFIX = "tc"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "12345"

# Email Settings
EMAIL_HOST = "a real smtp server"
EMAIL_HOST_USER = "your_mailbox_username"
EMAIL_HOST_PASSWORD = "your_mailbox_password"
DEFAULT_FROM_EMAIL = "a real email address"
SERVER_EMAIL = "a real email address"
