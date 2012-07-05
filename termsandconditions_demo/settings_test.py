"""Automated Unit Test Settings File for the Project"""

# pylint: disable=W0401, W0614, E0611, F0401

from settings_main import * #@UnusedWildImport
from settings_local_template import * #@UnusedWildImport

try:
    from socialprofile_demo.settings_test_local import * #@UnusedWildImport
except:
    pass
import tempfile

# Test DB settings. (SQLLite)
DATABASES = {
    'default': {
        'NAME': 'default',
        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': # DO NOT SPECIFY A NAME SO THAT TEST RUNNER WILL USE IN-MEMORY DB
        'SUPPORTS_TRANSACTIONS': 'false',
    }
}

# Test Cache Settings
CACHE_BACKEND = "file://" + tempfile.gettempdir()

INSTALLED_APPS += ('django_nose',)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner' # Should work with Django 1.2.1+