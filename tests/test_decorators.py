"""Tests for the terms_required view decorator."""

from termsandconditions.models import UserTermsAndConditions

from .factories import TermsTestCase


class TermsRequiredTests(TermsTestCase):
    def test_anonymous_user_hits_the_login_redirect_first(self):
        response = self.client.get("/termsrequired/", follow=True)
        self.assertRedirects(response, "/accounts/login/?next=/termsrequired/")

    def test_logged_in_user_is_sent_to_accept_terms(self):
        self.client.login(username="user1", password="user1password")
        response = self.client.get("/termsrequired/", follow=True)
        self.assertRedirects(response, "/terms/accept/?returnTo=/termsrequired/")

    def test_view_runs_once_every_terms_is_accepted(self):
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms2)
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms3)
        self.client.login(username="user1", password="user1password")

        response = self.client.get("/termsrequired/", follow=True)
        self.assertContains(response, "Acceptance Required")
