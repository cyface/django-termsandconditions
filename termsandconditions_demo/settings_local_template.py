"""
Local Django Settings File

INSTRUCTIONS
SAVE A COPY OF THIS FILE IN THIS DIRECTORY WITH THE NAME local_settings.py
MAKE YOUR LOCAL SETTINGS CHANGES IN THAT FILE AND DO NOT CHECK IT IN
CHANGES TO THIS FILE SHOULD BE TO ADD/REMOVE SETTINGS THAT NEED TO BE
MADE LOCALLY BY ALL INSTALLATIONS

local_settings.py, once created, should never be checked into source control
It is ignored by default by .gitignore, so if you don't mess with that, you should be fine.
"""
# pylint: disable=R0801, W0611
import os, logging
from settings_main import MIDDLEWARE_CLASSES, INSTALLED_APPS

# Set the root path of the project so it's not hard coded
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
# IP Addresses that should be treated as internal/debug users
INTERNAL_IPS = ('127.0.0.1',)

# Cache Settings
# CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_BACKEND = 'dummy:///'
CACHE_MIDDLEWARE_SECONDS = 30
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_KEY_PREFIX = 'tc'

# List of Admin users to be emailed by error system
MANAGERS = (
# ('Your Name', 'you@you.com'),
)
ADMINS = MANAGERS

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds media.
# Note that as of Django 1.3 - media is for uploaded files only.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'mediaroot')

#Staticfiles Config
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticroot')
STATIC_URL = '/static/'
STATICFILES_DIRS = [ os.path.join(PROJECT_ROOT, 'static')  ]
TEMPLATE_DIRS = [os.path.join(PROJECT_ROOT, 'templates')]

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Local DB settings. (Postgres)
DATABASES = {
    #    'default': {
    #        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #        'NAME': 'socialprofile',
    #        'USER': 'socialprofile',
    #        'PASSWORD': '',
    #        'HOST': '127.0.0.1',
    #        'PORT': '', # Set to empty string for default.
    #        'SUPPORTS_TRANSACTIONS': 'true',
    #    },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_ROOT + '/socialprofile.db',
        'SUPPORTS_TRANSACTIONS': 'false',
        }
}

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'termsandconditions_demo.wsgi.application'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Denver'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'zv$+w7juz@(g!^53o0ai1uF82)=jkz9my_r=3)fglrj5t8l$2#'

# Email Settings
EMAIL_HOST = 'a real smtp server'
EMAIL_HOST_USER = 'your_mailbox_username'
EMAIL_HOST_PASSWORD = 'your_mailbox_password'
DEFAULT_FROM_EMAIL = 'a real email address'
SERVER_EMAIL = 'a real email address'

### Local add-ons to main inclusion variables
# TEMPLATE_CONTEXT_PROCESSORS +=

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # Leave Enabled for Admin Access
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    )

##### Custom Variables Below Here #######

# Django Socialauth Settings
SOCIAL_AUTH_ENABLED_BACKENDS = ('facebook', 'google-oauth2', 'twitter')

TWITTER_CONSUMER_KEY         = ''
TWITTER_CONSUMER_SECRET      = ''
#Below is localhost facebook key
FACEBOOK_APP_ID              = ''
FACEBOOK_API_SECRET          = ''
FACEBOOK_EXTENDED_PERMISSIONS = ['email',]
GOOGLE_OAUTH2_CLIENT_ID      = 'xxxxxx.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET  = ''
GOOGLE_OAUTH_EXTRA_SCOPE     = ['https://www.googleapis.com/auth/userinfo.profile',] # Note that this extra scope is not the same as the API URL we use

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'termsandconditions.pipeline.user_accept_terms',
)

# Core Authentication Settings
LOGIN_URL          = '/socialprofile/select/'
LOGIN_REDIRECT_URL = '/secure/'
LOGIN_ERROR_URL    = '/socialprofile/select/'

# Terms & Conditions (termsandconditions) Settings
DEFAULT_TERMS_SLUG = 'site-terms'
ACCEPT_TERMS_PATH = '/terms/accept/'
TERMS_EXCLUDE_URL_PREFIX_LIST =  {'/admin/',}
TERMS_EXCLUDE_URL_LIST = {'/', '/terms/required/', '/socialprofile/logout/', '/securetoo/'}
MULTIPLE_ACTIVE_TERMS = True # Multiple kinds of T&Cs active at once (like site-terms, and contributor-terms).

### DEBUG TOOLBAR
#if DEBUG:
#    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
#    INSTALLED_APPS += ('debug_toolbar',)
#
#    DEBUG_TOOLBAR_PANELS = (
#        'debug_toolbar.panels.timer.TimerDebugPanel',
#        'debug_toolbar.panels.headers.HeaderDebugPanel',
#        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
#        'debug_toolbar.panels.template.TemplateDebugPanel',
#        'debug_toolbar.panels.sql.SQLDebugPanel',
#        'debug_toolbar.panels.signals.SignalDebugPanel',
#        'debug_toolbar.panels.logger.LoggingPanel',
#        )
#
#    DEBUG_TOOLBAR_CONFIG = {
#        'INTERCEPT_REDIRECTS': False
#    }

#### LOGGING
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

# Catch Python warnings (e.g. deprecation warnings) into the logger
logging.captureWarnings(True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'py.warnings': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
            },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
            },
        'SocialAuth': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
            },
        'termsandconditions': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
            },
        }
}