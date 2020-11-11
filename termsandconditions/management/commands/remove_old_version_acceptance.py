"""
Management command to remove all UserTermsAndConditions objects from the database except the latest for each terms.
"""
import logging
from django.core.management import BaseCommand
from termsandconditions.models import TermsAndConditions, UserTermsAndConditions
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Removes evidence of acceptance of previous terms and conditions versions."

    def handle(self, *args, **options):
        active_terms = TermsAndConditions.get_active_terms_list()
        for term in active_terms:
            old_accepts = UserTermsAndConditions.objects.filter(terms__slug=term.slug).exclude(terms__pk=term.pk)
            logger.debug(f"About to delete these old terms accepts: {old_accepts}")
            old_accepts.delete()

