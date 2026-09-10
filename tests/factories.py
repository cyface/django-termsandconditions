"""Shared fixtures for the test suite."""

from django.contrib.auth.models import ContentType, Permission, User
from django.core.cache import cache
from django.test import TestCase

from termsandconditions.models import TermsAndConditions

SKIP_PERM_CODENAME = "can_skip_t&c"


class TermsTestCase(TestCase):
    """Users and four sets of terms, shared by most tests.

    ``site-terms`` is active at 2.0, ``contrib-terms`` at 1.5 (its 2.0 is
    dated in the future).  ``user3`` holds the skip permission; ``su`` is a
    superuser without it.

    Primary keys are left to the database.  Assigning them here would leave the
    Postgres sequence at 1, so the first ``objects.create()`` in a test that
    does not name an id collides with this fixture data.
    """

    def setUp(self) -> None:
        self.su = User.objects.create_superuser("su", "su@example.com", "superstrong")
        self.user1 = User.objects.create_user(
            "user1", "user1@user1.com", "user1password"
        )
        self.user2 = User.objects.create_user(
            "user2", "user2@user2.com", "user2password"
        )
        self.user3 = User.objects.create_user(
            "user3", "user3@user3.com", "user3password"
        )

        self.terms1 = TermsAndConditions.objects.create(
            slug="site-terms",
            name="Site Terms",
            text="Site Terms and Conditions 1",
            version_number=1.0,
            date_active="2012-01-01T00:00:00+00:00",
        )
        self.terms2 = TermsAndConditions.objects.create(
            slug="site-terms",
            name="Site Terms",
            text="Site Terms and Conditions 2",
            version_number=2.0,
            date_active="2012-01-05T00:00:00+00:00",
        )
        self.terms3 = TermsAndConditions.objects.create(
            slug="contrib-terms",
            name="Contributor Terms",
            text="Contributor Terms and Conditions 1.5",
            version_number=1.5,
            date_active="2012-01-01T00:00:00+00:00",
        )
        self.terms4 = TermsAndConditions.objects.create(
            slug="contrib-terms",
            name="Contributor Terms",
            text="Contributor Terms and Conditions 2",
            version_number=2.0,
            date_active="2100-01-01T00:00:00+00:00",
        )

        content_type = ContentType.objects.get_for_model(User)
        self.skip_perm = Permission.objects.create(
            content_type=content_type,
            name="Can skip T&Cs",
            codename=SKIP_PERM_CODENAME,
        )
        self.user3.user_permissions.add(self.skip_perm)

        cache.clear()

    def tearDown(self) -> None:
        cache.clear()
