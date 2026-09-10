"""Tests for the accept, view, print and email views."""

import re

from django.core import mail
from django.test import override_settings
from django.utils import timezone

from termsandconditions.models import TermsAndConditions, UserTermsAndConditions

from .factories import TermsTestCase


def rendered_form_fields(html: str) -> dict[str, str]:
    """The name/value pairs a browser would submit from the first form in ``html``."""
    return dict(re.findall(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', html))


class AcceptTermsViewTests(TermsTestCase):
    def test_get_lists_outstanding_terms(self):
        self.client.login(username="user1", password="user1password")
        response = self.client.get("/terms/accept/", follow=True)
        self.assertContains(response, "Accept")

    def test_posting_records_acceptance_and_redirects(self):
        self.client.login(username="user1", password="user1password")
        response = self.client.post(
            "/terms/accept/",
            {"terms": self.terms2.pk, "returnTo": "/secure/"},
            follow=True,
        )
        # site-terms accepted, so the middleware now asks for contrib-terms.
        self.assertContains(response, "Contributor")
        self.assertTrue(
            UserTermsAndConditions.objects.filter(
                user=self.user1, terms=self.terms2
            ).exists()
        )

    def test_accepting_the_last_outstanding_terms_reaches_the_target(self):
        self.client.login(username="user1", password="user1password")
        self.client.post(
            "/terms/accept/", {"terms": self.terms2.pk, "returnTo": "/secure/"}
        )
        response = self.client.post(
            "/terms/accept/",
            {"terms": self.terms3.pk, "returnTo": "/secure/"},
            follow=True,
        )
        self.assertContains(response, "Secure")

    def test_get_specific_version(self):
        self.client.login(username="user1", password="user1password")
        response = self.client.get("/terms/accept/contrib-terms/1.5/", follow=True)
        self.assertContains(response, "Contributor Terms and Conditions 1.5")

    def test_unknown_version_is_a_404(self):
        response = self.client.get("/terms/accept/contrib-terms/99.0/")
        self.assertEqual(404, response.status_code)

    def test_anonymous_post_is_sent_home(self):
        response = self.client.post(
            "/terms/accept/", {"terms": self.terms2.pk}, follow=True
        )
        self.assertContains(response, "Home")
        self.assertFalse(UserTermsAndConditions.objects.exists())

    def test_non_numeric_terms_id_is_ignored(self):
        self.client.login(username="user1", password="user1password")
        response = self.client.post(
            "/terms/accept/", {"terms": "not-a-pk", "returnTo": "/secure/"}
        )
        self.assertEqual(302, response.status_code)
        self.assertFalse(UserTermsAndConditions.objects.exists())

    def test_unknown_slug_renders_the_empty_state(self):
        self.client.login(username="user1", password="user1password")
        response = self.client.get("/terms/accept/no-such-terms/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "No terms defined.")

    def test_a_version_that_is_not_active_yet_cannot_be_pre_accepted(self):
        # terms4 is contrib-terms 2.0, dated 2100. Recording acceptance of it
        # now would mean the user was never asked once it went live.
        self.client.login(username="user1", password="user1password")

        self.client.post(
            "/terms/accept/", {"terms": self.terms4.pk, "returnTo": "/secure/"}
        )

        self.assertFalse(UserTermsAndConditions.objects.exists())

    def test_a_pre_accept_attempt_does_not_survive_the_version_going_live(self):
        self.client.login(username="user1", password="user1password")
        self.client.post(
            "/terms/accept/", {"terms": self.terms4.pk, "returnTo": "/secure/"}
        )

        self.terms4.date_active = timezone.now()
        self.terms4.save()

        outstanding = TermsAndConditions.get_active_terms_not_agreed_to(self.user1)
        self.assertIn(self.terms4, outstanding)

    def test_a_version_that_is_not_active_yet_is_not_offered(self):
        # The page must not render an Accept button the POST would refuse.
        self.client.login(username="user1", password="user1password")
        response = self.client.get("/terms/accept/contrib-terms/2.0/")
        self.assertEqual(404, response.status_code)

    def test_a_superseded_version_is_not_offered(self):
        self.client.login(username="user1", password="user1password")
        response = self.client.get("/terms/accept/site-terms/1.0/")
        self.assertEqual(404, response.status_code)

    def test_a_superseded_version_can_still_be_viewed_and_printed(self):
        # Only accepting is narrowed to what is in force.
        for url in ("/terms/view/site-terms/1.0/", "/terms/print/site-terms/1.0/"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, self.terms1.text)

    def test_a_superseded_version_cannot_be_accepted(self):
        # terms1 is site-terms 1.0, replaced by terms2 at 2.0.
        self.client.login(username="user1", password="user1password")

        self.client.post(
            "/terms/accept/", {"terms": self.terms1.pk, "returnTo": "/secure/"}
        )

        self.assertFalse(UserTermsAndConditions.objects.exists())

    def test_the_rendered_form_can_be_submitted_as_a_browser_would(self):
        self.client.login(username="user1", password="user1password")
        response = self.client.get("/terms/accept/site-terms/")

        fields = rendered_form_fields(response.content.decode())
        self.client.post("/terms/accept/", fields)

        self.assertTrue(
            UserTermsAndConditions.objects.filter(
                user=self.user1, terms=self.terms2
            ).exists()
        )

    def test_accepting_the_same_terms_twice_is_harmless(self):
        self.client.login(username="user1", password="user1password")
        for _ in range(2):
            self.client.post(
                "/terms/accept/", {"terms": self.terms2.pk, "returnTo": "/secure/"}
            )
        self.assertEqual(
            1,
            UserTermsAndConditions.objects.filter(
                user=self.user1, terms=self.terms2
            ).count(),
        )


class AcceptRedirectTargetTests(TermsTestCase):
    def _post_accept(self, return_to):
        # contrib-terms out of the way first, so accepting site-terms leaves
        # nothing outstanding and the middleware lets the target render.
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms3)
        self.client.login(username="user1", password="user1password")
        return self.client.post(
            "/terms/accept/",
            {"terms": self.terms2.pk, "returnTo": return_to},
            follow=True,
        )

    def test_safe_target_is_honoured(self):
        self.assertRedirects(self._post_accept("/secure/"), "/secure/")

    def test_absolute_url_is_rejected(self):
        self.assertRedirects(self._post_accept("http://attacker/"), "/")

    def test_scheme_relative_url_is_rejected(self):
        self.assertRedirects(self._post_accept("//attacker.com"), "/")

    def test_triple_slash_url_is_rejected(self):
        self.assertRedirects(self._post_accept("///attacker.com"), "/")

    def test_quadruple_slash_url_is_rejected(self):
        self.assertRedirects(self._post_accept("////attacker.com"), "/")


class IpAddressTests(TermsTestCase):
    def test_ip_address_is_stored_by_default(self):
        self.client.login(username="user1", password="user1password")
        self.client.post(
            "/terms/accept/", {"terms": self.terms2.pk, "returnTo": "/secure/"}
        )
        user_terms = UserTermsAndConditions.objects.get()
        self.assertEqual(self.user1, user_terms.user)
        self.assertEqual(self.terms2, user_terms.terms)
        self.assertEqual("127.0.0.1", user_terms.ip_address)

    def test_proxy_chain_keeps_the_client_address(self):
        self.client.login(username="user1", password="user1password")
        self.client.post(
            "/terms/accept/",
            {"terms": self.terms2.pk, "returnTo": "/secure/"},
            REMOTE_ADDR="1.2.3.4, 5.6.7.8",
        )
        self.assertEqual("1.2.3.4", UserTermsAndConditions.objects.get().ip_address)

    @override_settings(TERMS_STORE_IP_ADDRESS=False)
    def test_ip_address_can_be_disabled(self):
        self.client.login(username="user1", password="user1password")
        self.client.post(
            "/terms/accept/", {"terms": self.terms2.pk, "returnTo": "/secure/"}
        )
        self.assertIsNone(UserTermsAndConditions.objects.get().ip_address)

    @override_settings(TERMS_IP_HEADER_NAME="HTTP_X_MISSING_HEADER")
    def test_missing_ip_header_does_not_error(self):
        self.client.login(username="user1", password="user1password")
        self.client.post(
            "/terms/accept/", {"terms": self.terms2.pk, "returnTo": "/secure/"}
        )
        self.assertIsNone(UserTermsAndConditions.objects.get().ip_address)


class TermsViewTests(TermsTestCase):
    def test_anonymous_sees_every_active_terms(self):
        response = self.client.get("/terms/", follow=True)
        for terms in TermsAndConditions.get_active_terms_list():
            self.assertContains(response, terms.name)
            self.assertContains(response, terms.text)
        self.assertContains(response, "Terms and Conditions")

    def test_anonymous_can_view_by_slug_and_version(self):
        response = self.client.get(self.terms2.get_absolute_url(), follow=True)
        self.assertContains(response, self.terms2.name)
        self.assertContains(response, self.terms2.text)

    def test_logged_in_user_sees_only_outstanding_terms(self):
        self.client.login(username="user1", password="user1password")
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms3)

        response = self.client.get("/terms/", follow=True)
        self.assertContains(response, self.terms2.text)
        self.assertNotContains(response, self.terms3.name)
        self.assertContains(response, "Sign Out")

    def test_active_terms_page(self):
        response = self.client.get("/terms/active/", follow=True)
        self.assertContains(response, self.terms2.text)
        self.assertContains(response, self.terms3.text)

    def test_print_page(self):
        response = self.client.get("/terms/print/site-terms/2.0/", follow=True)
        self.assertContains(response, self.terms2.text)

    def test_unknown_slug_renders_the_empty_state(self):
        response = self.client.get("/terms/view/no-such-terms/", follow=True)
        self.assertContains(response, "No terms defined.")

    def test_unknown_version_is_a_404(self):
        response = self.client.get("/terms/view/site-terms/99.0/")
        self.assertEqual(404, response.status_code)


class EmailTermsViewTests(TermsTestCase):
    def test_form_renders(self):
        response = self.client.get("/terms/email/", follow=True)
        self.assertContains(response, "Email")

    def test_valid_address_sends_the_terms(self):
        response = self.client.post(
            "/terms/email/",
            {
                "email_address": "foo@foo.com",
                "email_subject": "Terms Email",
                "terms": self.terms2.pk,
                "returnTo": "/",
            },
            follow=True,
        )
        self.assertEqual(1, len(mail.outbox))
        self.assertIn(self.terms2.text, mail.outbox[0].body)
        self.assertContains(response, "Sent")

    def test_the_rendered_form_can_be_submitted_as_a_browser_would(self):
        # The hidden terms input used to carry a Python repr, so every real
        # submission failed validation and no mail was ever sent.
        for url in ("/terms/email/", "/terms/email/site-terms/2.0/"):
            with self.subTest(url=url):
                mail.outbox.clear()
                fields = rendered_form_fields(self.client.get(url).content.decode())
                fields["email_address"] = "foo@foo.com"

                self.client.post("/terms/email/", fields, follow=True)

                self.assertEqual(1, len(mail.outbox))
                self.assertIn(self.terms2.text, mail.outbox[0].body)

    def test_a_superseded_version_can_still_be_emailed(self):
        # Sending a copy grants nothing, so the specific-version URL keeps
        # working for versions that are no longer in force.
        fields = rendered_form_fields(
            self.client.get("/terms/email/site-terms/1.0/").content.decode()
        )
        fields["email_address"] = "foo@foo.com"

        self.client.post("/terms/email/", fields)

        self.assertEqual(1, len(mail.outbox))
        self.assertIn(self.terms1.text, mail.outbox[0].body)

    def test_the_subject_line_names_the_terms(self):
        response = self.client.get("/terms/email/site-terms/2.0/")
        self.assertContains(response, "You Requested: Site Terms")

    def test_emailing_without_a_slug_sends_every_outstanding_terms(self):
        self.client.post(
            "/terms/email/",
            {
                "email_address": "foo@foo.com",
                "email_subject": "Terms Email",
                "terms": [self.terms2.pk, self.terms3.pk],
                "returnTo": "/",
            },
        )
        self.assertEqual(1, len(mail.outbox))
        self.assertIn(self.terms2.text, mail.outbox[0].body)
        self.assertIn(self.terms3.text, mail.outbox[0].body)

    def test_invalid_address_is_reported(self):
        response = self.client.post(
            "/terms/email/",
            {
                "email_address": "INVALID EMAIL ADDRESS",
                "email_subject": "Terms Email",
                "terms": self.terms2.pk,
                "returnTo": "/",
            },
            follow=True,
        )
        self.assertEqual(0, len(mail.outbox))
        self.assertContains(response, "Invalid")
