"""ASGI entry point for the demo project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "termsandconditions_demo.settings")

application = get_asgi_application()
