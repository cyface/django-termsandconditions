"""WSGI File that enables Apache/GUnicorn to run Django"""

# pylint: disable=C0103

import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(os.pardir), os.pardir)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)))))

print (sys.path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'socialprofile_demo.settings')

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()