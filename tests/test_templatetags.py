"""Tests for the terms_tags template library."""

from django.template import Context, Template
from django.test import RequestFactory

from termsandconditions.models import TermsAndConditions, UserTermsAndConditions
from termsandconditions.templatetags.terms_tags import show_terms_if_not_agreed

from .factories import TermsTestCase


class ShowTermsIfNotAgreedTests(TermsTestCase):
    def _render(self, template_string, path="/test"):
        request = RequestFactory().get(path)
        request.user = self.user1
        return Template(template_string).render(Context({"request": request}))

    def test_modal_is_rendered_when_terms_are_outstanding(self):
        rendered = self._render("{% load terms_tags %}{% show_terms_if_not_agreed %}")
        self.assertIn(TermsAndConditions.get_active().slug, rendered)

    def test_modal_is_hidden_once_every_terms_is_accepted(self):
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms2)
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms3)

        rendered = self._render("{% load terms_tags %}{% show_terms_if_not_agreed %}")
        self.assertNotIn("termsandconditions-modal", rendered)

    def test_field_argument_selects_a_different_meta_key(self):
        request = RequestFactory().get("/test")
        request.user = self.user1
        request.META["HTTP_REFERER"] = "/some-other-page/"

        result = show_terms_if_not_agreed({"request": request}, field="HTTP_REFERER")
        self.assertEqual("/some-other-page/", result["returnTo"])

    def test_protected_url_shows_the_outstanding_terms(self):
        result = show_terms_if_not_agreed(self._context("/test"))
        # Outstanding terms come back ordered by slug.
        self.assertQuerySetEqual(result["not_agreed_terms"], [self.terms3, self.terms2])

    def test_unprotected_url_shows_nothing(self):
        result = show_terms_if_not_agreed(self._context("/"))
        self.assertEqual({"not_agreed_terms": False}, result)

    def _context(self, url):
        request = RequestFactory().get(url)
        request.user = self.user1
        request.META["PATH_INFO"] = url
        return {"request": request}


class AsTemplateFilterTests(TermsTestCase):
    def test_terms_text_is_rendered_as_a_template(self):
        self.terms2.text = "Read the <a href=\"{% url 'tc_view_page' %}\">terms</a>."
        self.terms2.save()

        rendered = Template(
            "{% load terms_tags %}{% include terms.text|as_template %}"
        ).render(Context({"terms": self.terms2}))

        self.assertIn('href="/terms/"', rendered)
