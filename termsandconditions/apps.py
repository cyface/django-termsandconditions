"""Django Apps Config"""

# pylint: disable=C1001,E0202,W0613

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import logging

LOGGER = logging.getLogger(name="termsandconditions")


class TermsAndConditionsConfig(AppConfig):
    """App config for TermsandConditions"""

    name = "termsandconditions"
    verbose_name = _("Terms and Conditions")

    def ready(self):
        import termsandconditions.signals
