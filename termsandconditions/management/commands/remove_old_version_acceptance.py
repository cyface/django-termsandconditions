"""Prune acceptance records for superseded versions of each set of terms."""

import logging

from django.core.management import BaseCommand

from termsandconditions.models import TermsAndConditions, UserTermsAndConditions

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Removes evidence of acceptance of previous terms and conditions versions."

    def handle(self, *args, **options) -> None:
        for terms in TermsAndConditions.get_active_terms_list():
            old_accepts = UserTermsAndConditions.objects.filter(
                terms__slug=terms.slug
            ).exclude(terms__pk=terms.pk)
            LOGGER.debug("About to delete these old terms accepts: %s", old_accepts)
            deleted, _ = old_accepts.delete()
            self.stdout.write(
                f"Removed {deleted} old acceptance record(s) for {terms.slug}."
            )
