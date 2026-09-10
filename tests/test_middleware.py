"""Tests for the redirect middleware and its path exclusion rules."""

from django.test import SimpleTestCase, override_settings

from termsandconditions.middleware import is_path_protected
from termsandconditions.models import TermsAndConditions, UserTermsAndConditions

from .factories import TermsTestCase


class MiddlewareRedirectTests(TermsTestCase):
    def test_logged_in_user_is_sent_to_accept_outstanding_terms(self):
        self.client.login(username="user1", password="user1password")
        response = self.client.get("/secure/", follow=True)
        self.assertRedirects(response, "/terms/accept/contrib-terms/?returnTo=/secure/")

    def test_querystring_is_carried_across(self):
        self.client.login(username="user1", password="user1password")
        response = self.client.get("/secure/?foo=bar", follow=True)
        self.assertRedirects(
            response, "/terms/accept/contrib-terms/?returnTo=/secure/%3Ffoo%3Dbar"
        )

    def test_excluded_url_is_not_intercepted(self):
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms2)
        self.client.login(username="user1", password="user1password")

        response = self.client.get("/securetoo/", follow=True)
        self.assertContains(response, "SECOND")

    def test_excluded_prefix_is_not_intercepted(self):
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms2)
        self.client.login(username="user1", password="user1password")

        response = self.client.get("/admin", follow=True)
        self.assertContains(response, "administration")

    def test_anonymous_users_are_left_alone(self):
        response = self.client.get("/", follow=True)
        self.assertEqual(200, response.status_code)

    def test_new_terms_version_redirects_again(self):
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms2)
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms3)
        self.client.login(username="user1", password="user1password")

        self.assertContains(self.client.get("/secure/", follow=True), "secure area")

        TermsAndConditions.objects.create(
            slug="site-terms",
            name="Site Terms",
            text="Site Terms and Conditions 2.5",
            version_number=2.5,
            date_active="2012-02-05T00:00:00+00:00",
        )

        response = self.client.get("/secure/", follow=True)
        self.assertRedirects(response, "/terms/accept/site-terms/?returnTo=/secure/")


class IsPathProtectedTests(SimpleTestCase):
    def test_ordinary_path_is_protected(self):
        self.assertTrue(is_path_protected("/secure/"))

    def test_excluded_prefix(self):
        self.assertFalse(is_path_protected("/admin/auth/user/"))

    def test_excluded_exact_path(self):
        self.assertFalse(is_path_protected("/securetoo/"))

    def test_accept_path_itself(self):
        self.assertFalse(is_path_protected("/terms/accept/site-terms/"))

    @override_settings(TERMS_EXCLUDE_URL_CONTAINS_LIST={"/i18n/"})
    def test_excluded_fragment(self):
        self.assertFalse(is_path_protected("/en/i18n/setlang/"))
        self.assertTrue(is_path_protected("/en/secure/"))

    @override_settings(
        TERMS_EXCLUDE_URL_PREFIX_LIST=set(),
        TERMS_EXCLUDE_URL_LIST=set(),
        ACCEPT_TERMS_PATH="/terms/accept/",
    )
    def test_empty_exclusion_lists_protect_everything_else(self):
        self.assertTrue(is_path_protected("/admin/"))
        self.assertFalse(is_path_protected("/terms/accept/"))
