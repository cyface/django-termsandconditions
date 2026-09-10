"""Tests for the redirect middleware and its path exclusion rules."""

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from asgiref.sync import iscoroutinefunction

from termsandconditions import middleware as middleware_module
from termsandconditions.middleware import (
    TermsAndConditionsRedirectMiddleware,
    is_path_protected,
)
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

    @override_settings(TERMS_EXCLUDE_URL_PREFIX_LIST="/admin")
    def test_a_prefix_setting_written_as_a_string_still_gates_the_site(self):
        # Iterating "/admin" yields single characters, and every path starts
        # with "/", so this used to exclude every URL on the site.
        self.assertFalse(is_path_protected("/admin/auth/user/"))
        self.assertTrue(is_path_protected("/secure/"))

    @override_settings(TERMS_EXCLUDE_URL_LIST="/secure/")
    def test_an_exact_path_setting_written_as_a_string_is_honoured(self):
        self.assertFalse(is_path_protected("/secure/"))
        self.assertTrue(is_path_protected("/other/"))

    @override_settings(TERMS_EXCLUDE_URL_CONTAINS_LIST="/i18n/")
    def test_a_fragment_setting_written_as_a_string_is_honoured(self):
        self.assertFalse(is_path_protected("/en/i18n/setlang/"))
        self.assertTrue(is_path_protected("/en/secure/"))


class MiddlewareModuleTests(SimpleTestCase):
    def test_accept_terms_path_is_still_importable_from_here(self):
        # It was a module-level constant before 3.0 and is imported from this
        # module downstream.
        from termsandconditions.middleware import ACCEPT_TERMS_PATH

        self.assertEqual("/terms/accept/", ACCEPT_TERMS_PATH)

    @override_settings(ACCEPT_TERMS_PATH="/elsewhere/")
    def test_the_re_export_is_resolved_on_access(self):
        self.assertEqual("/elsewhere/", middleware_module.ACCEPT_TERMS_PATH)

    def test_an_unknown_module_attribute_still_raises(self):
        with self.assertRaises(AttributeError):
            _ = middleware_module.NOT_A_REAL_NAME


class AsyncMiddlewareTests(TermsTestCase):
    """The middleware must not force an ASGI stack back onto the thread pool."""

    def test_it_declares_both_capabilities(self):
        self.assertTrue(TermsAndConditionsRedirectMiddleware.sync_capable)
        self.assertTrue(TermsAndConditionsRedirectMiddleware.async_capable)

    def test_an_async_get_response_yields_a_coroutine_middleware(self):
        async def get_response(request):
            return HttpResponse("ok")

        self.assertTrue(
            iscoroutinefunction(TermsAndConditionsRedirectMiddleware(get_response))
        )

    async def test_outstanding_terms_redirect_on_the_async_path(self):
        async def get_response(request):
            return HttpResponse("view ran")

        middleware = TermsAndConditionsRedirectMiddleware(get_response)
        request = RequestFactory().get("/secure/")
        request.user = self.user1

        response = await middleware(request)

        self.assertEqual(302, response.status_code)
        self.assertIn("/terms/accept/", response["Location"])

    async def test_the_view_runs_on_the_async_path_when_nothing_is_outstanding(self):
        async def get_response(request):
            return HttpResponse("view ran")

        middleware = TermsAndConditionsRedirectMiddleware(get_response)
        request = RequestFactory().get("/secure/")
        request.user = self.user3  # holds the skip permission

        response = await middleware(request)

        self.assertEqual(b"view ran", response.content)
