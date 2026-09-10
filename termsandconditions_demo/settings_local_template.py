"""Local settings. Copy to settings_local.py and edit; that file is gitignored."""

from .settings import *

# Point at Postgres instead of the bundled SQLite file.
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "termsandconditions",
#         "USER": "termsandconditions",
#         "PASSWORD": "",
#         "HOST": "127.0.0.1",
#         "PORT": "",
#     },
# }

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "termsandconditions",
    },
}

SECRET_KEY = "django-insecure-local-development-key"

# Real SMTP settings, if you want to exercise the email-terms view for real.
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.example.com"
# EMAIL_HOST_USER = "your_mailbox_username"
# EMAIL_HOST_PASSWORD = "your_mailbox_password"
# DEFAULT_FROM_EMAIL = "terms@example.com"
# SERVER_EMAIL = "terms@example.com"
