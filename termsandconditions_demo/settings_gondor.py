import os
import urlparse

from .settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

FACEBOOK_APP_ID              = '295912813778057'
FACEBOOK_API_SECRET          = 'bb0c4233c822875650962953aad4c40e'

if "GONDOR_DATABASE_URL" in os.environ:
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["GONDOR_DATABASE_URL"])
    DATABASES = {
        "default": {
            "ENGINE": {
                "postgres": "django.db.backends.postgresql_psycopg2"
            }[url.scheme],
            "NAME": url.path[1:],
            "USER": url.username,
            "PASSWORD": url.password,
            "HOST": url.hostname,
            "PORT": url.port
        }
    }

if "GONDOR_REDIS_URL" in os.environ:
    urlparse.uses_netloc.append("redis")
    url = urlparse.urlparse(os.environ["GONDOR_REDIS_URL"])
    GONDOR_REDIS_HOST = url.hostname
    GONDOR_REDIS_PORT = url.port
    GONDOR_REDIS_PASSWORD = url.password

SITE_ID = 1 # set this to match your Sites setup

MEDIA_ROOT = os.path.join(os.environ["GONDOR_DATA_DIR"], "site_media", "mediaroot")
STATIC_ROOT = os.path.join(os.environ["GONDOR_DATA_DIR"], "site_media", "staticroot")

MEDIA_URL = "/assets/media/" # make sure this maps inside of a static_urls URL
STATIC_URL = "/assets/static/" # make sure this maps inside of a static_urls URL

FILE_UPLOAD_PERMISSIONS = 0640