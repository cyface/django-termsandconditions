"""App config for the termsandconditions app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TermsAndConditionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "termsandconditions"
    verbose_name = _("Terms and Conditions")

    def ready(self) -> None:
        from . import signals  # noqa: F401  (registers the receivers)
