"""Django Apps Config"""

# pylint: disable=C1001,E0202,W0613

from django.apps import AppConfig
import logging

LOGGER = logging.getLogger(name='termsandconditions')


class TermsAndConditionsConfig(AppConfig):
    """App config for TermsandConditions"""
    name = 'termsandconditions'
    verbose_name = "Terms and Conditions"

    def ready(self):
        import termsandconditions.signals
