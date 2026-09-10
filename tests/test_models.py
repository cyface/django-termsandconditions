"""Tests for the TermsAndConditions and UserTermsAndConditions models."""

from django.db import IntegrityError, transaction
from django.test import override_settings

from termsandconditions.models import TermsAndConditions, UserTermsAndConditions

from .factories import TermsTestCase


class TermsAndConditionsModelTests(TermsTestCase):
    def test_get_active_terms_list(self):
        active_list = TermsAndConditions.get_active_terms_list()
        self.assertEqual(2, len(active_list))
        self.assertQuerySetEqual(active_list, [self.terms3, self.terms2])

    def test_get_active_terms_ids(self):
        self.assertEqual([3, 2], TermsAndConditions.get_active_terms_ids())

    def test_get_active_picks_latest_past_version(self):
        self.assertEqual(
            2.0, TermsAndConditions.get_active(slug="site-terms").version_number
        )
        # contrib-terms 2.0 is dated in the future, so 1.5 stays active.
        self.assertEqual(
            1.5, TermsAndConditions.get_active(slug="contrib-terms").version_number
        )

    def test_get_active_defaults_to_configured_slug(self):
        self.assertEqual(self.terms2, TermsAndConditions.get_active())

    @override_settings(DEFAULT_TERMS_SLUG="contrib-terms")
    def test_get_active_honours_overridden_default_slug(self):
        self.assertEqual(self.terms3, TermsAndConditions.get_active())

    def test_slug_defaults_to_the_configured_value(self):
        terms = TermsAndConditions.objects.create(name="Unslugged", version_number=1.0)
        self.assertEqual("site-terms", terms.slug)

    @override_settings(DEFAULT_TERMS_SLUG="house-rules")
    def test_slug_default_follows_the_setting_at_creation_time(self):
        terms = TermsAndConditions.objects.create(name="Unslugged", version_number=1.0)
        self.assertEqual("house-rules", terms.slug)

    def test_str(self):
        self.assertEqual("site-terms-2.00", str(self.terms2))
        self.assertEqual("contrib-terms-1.50", str(self.terms3))

    def test_get_absolute_url(self):
        self.terms2.refresh_from_db()
        self.assertEqual("/terms/view/site-terms/2.00/", self.terms2.get_absolute_url())

    def test_acceptance_is_recorded_against_the_user(self):
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms1)
        UserTermsAndConditions.objects.create(user=self.user2, terms=self.terms3)

        self.assertEqual(1.0, self.user1.userterms.get().terms.version_number)
        self.assertEqual(1.5, self.user2.userterms.get().terms.version_number)
        self.assertEqual("user1", self.terms1.users.all()[0].get_username())

    def test_user_terms_str(self):
        user_terms = UserTermsAndConditions.objects.create(
            user=self.user1, terms=self.terms2
        )
        user_terms.refresh_from_db()
        self.assertEqual("user1:site-terms-2.00", str(user_terms))

    def test_a_user_cannot_accept_the_same_terms_twice(self):
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms2)
        with self.assertRaises(IntegrityError), transaction.atomic():
            UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms2)


class NotAgreedToTests(TermsTestCase):
    def test_lists_everything_the_user_has_not_accepted(self):
        active_list = TermsAndConditions.get_active_terms_not_agreed_to(self.user1)
        self.assertEqual(2, len(active_list))
        self.assertQuerySetEqual(active_list, [self.terms3, self.terms2])

    def test_accepted_terms_drop_off_the_list(self):
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms3)
        self.assertQuerySetEqual(
            TermsAndConditions.get_active_terms_not_agreed_to(self.user1),
            [self.terms2],
        )

    def test_anonymous_users_are_shown_every_active_terms(self):
        from django.contrib.auth.models import AnonymousUser

        self.assertQuerySetEqual(
            TermsAndConditions.get_active_terms_not_agreed_to(AnonymousUser()),
            [self.terms3, self.terms2],
        )

    def test_user_with_skip_permission_is_excluded(self):
        self.assertEqual(
            [], TermsAndConditions.get_active_terms_not_agreed_to(self.user3)
        )

    def test_superuser_is_not_implicitly_excluded(self):
        active_list = TermsAndConditions.get_active_terms_not_agreed_to(self.su)
        self.assertQuerySetEqual(active_list, [self.terms3, self.terms2])

    def test_superuser_cannot_skip_via_the_permission(self):
        # has_perm() is True for every permission when is_superuser.
        self.su.user_permissions.add(self.skip_perm)
        active_list = TermsAndConditions.get_active_terms_not_agreed_to(self.su)
        self.assertQuerySetEqual(active_list, [self.terms3, self.terms2])

    @override_settings(TERMS_EXCLUDE_SUPERUSERS=True)
    def test_superuser_excluded_by_setting(self):
        self.assertEqual([], TermsAndConditions.get_active_terms_not_agreed_to(self.su))

    @override_settings(TERMS_EXCLUDE_USERS_WITH_PERM=None)
    def test_skip_permission_ignored_when_setting_is_unset(self):
        active_list = TermsAndConditions.get_active_terms_not_agreed_to(self.user3)
        self.assertQuerySetEqual(active_list, [self.terms3, self.terms2])


class CacheInvalidationTests(TermsTestCase):
    def test_new_terms_version_invalidates_the_active_terms(self):
        self.assertEqual(
            2.0, TermsAndConditions.get_active("site-terms").version_number
        )

        TermsAndConditions.objects.create(
            slug="site-terms",
            name="Site Terms",
            text="Site Terms and Conditions 2.5",
            version_number=2.5,
            date_active="2012-02-05T00:00:00+00:00",
        )

        self.assertEqual(
            2.5, TermsAndConditions.get_active("site-terms").version_number
        )

    def test_accepting_terms_invalidates_the_user_cache(self):
        self.assertEqual(
            2, len(TermsAndConditions.get_active_terms_not_agreed_to(self.user1))
        )

        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms3)

        self.assertEqual(
            1, len(TermsAndConditions.get_active_terms_not_agreed_to(self.user1))
        )

    def test_deleting_an_acceptance_invalidates_the_user_cache(self):
        acceptance = UserTermsAndConditions.objects.create(
            user=self.user1, terms=self.terms3
        )
        self.assertEqual(
            1, len(TermsAndConditions.get_active_terms_not_agreed_to(self.user1))
        )

        acceptance.delete()

        self.assertEqual(
            2, len(TermsAndConditions.get_active_terms_not_agreed_to(self.user1))
        )
