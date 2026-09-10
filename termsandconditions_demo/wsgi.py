"""WSGI entry point for the demo project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "termsandconditions_demo.settings")

application = get_wsgi_application()
