"""Tests for the remove_old_version_acceptance management command."""

from io import StringIO

from django.core.management import call_command

from termsandconditions.models import UserTermsAndConditions

from .factories import TermsTestCase


class RemoveOldVersionAcceptanceTests(TermsTestCase):
    def test_acceptance_of_superseded_versions_is_removed(self):
        # site-terms 1.0 is superseded by 2.0, which is the active version.
        stale = UserTermsAndConditions.objects.create(
            user=self.user1, terms=self.terms1
        )
        current = UserTermsAndConditions.objects.create(
            user=self.user2, terms=self.terms2
        )

        call_command("remove_old_version_acceptance", stdout=StringIO())

        self.assertFalse(UserTermsAndConditions.objects.filter(pk=stale.pk).exists())
        self.assertTrue(UserTermsAndConditions.objects.filter(pk=current.pk).exists())

    def test_acceptance_of_other_slugs_is_untouched(self):
        contrib = UserTermsAndConditions.objects.create(
            user=self.user1, terms=self.terms3
        )

        call_command("remove_old_version_acceptance", stdout=StringIO())

        self.assertTrue(UserTermsAndConditions.objects.filter(pk=contrib.pk).exists())

    def test_reports_what_it_removed(self):
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms1)
        out = StringIO()

        call_command("remove_old_version_acceptance", stdout=out)

        self.assertIn(
            "Removed 1 old acceptance record(s) for site-terms.", out.getvalue()
        )
