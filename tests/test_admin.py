"""Tests for the admin registrations."""

from django.contrib.admin.sites import AdminSite
from django.forms import Textarea
from django.test import RequestFactory, override_settings

from termsandconditions.admin import (
    TermsAndConditionsAdmin,
    UserTermsAndConditionsAdmin,
)
from termsandconditions.models import TermsAndConditions, UserTermsAndConditions

from .factories import TermsTestCase


class MarkerWidget(Textarea):
    """Stand-in for a third-party rich-text widget."""


class TermsAdminTests(TermsTestCase):
    def setUp(self):
        super().setUp()
        self.admin = TermsAndConditionsAdmin(TermsAndConditions, AdminSite())
        self.request = RequestFactory().get("/admin/")
        self.request.user = self.su

    def _widget_for(self, field_name):
        db_field = TermsAndConditions._meta.get_field(field_name)
        return self.admin.formfield_for_dbfield(db_field, self.request).widget

    def test_text_uses_a_textarea_by_default(self):
        self.assertIsInstance(self._widget_for("text"), Textarea)
        self.assertNotIsInstance(self._widget_for("text"), MarkerWidget)

    @override_settings(TERMS_ADMIN_TEXT_WIDGET="tests.test_admin.MarkerWidget")
    def test_configured_widget_is_used_for_rich_text_fields(self):
        self.assertIsInstance(self._widget_for("text"), MarkerWidget)
        self.assertIsInstance(self._widget_for("info"), MarkerWidget)

    @override_settings(TERMS_ADMIN_TEXT_WIDGET="tests.test_admin.MarkerWidget")
    def test_other_fields_keep_their_default_widget(self):
        self.assertNotIsInstance(self._widget_for("name"), MarkerWidget)


class UserTermsAdminTests(TermsTestCase):
    def test_search_fields_follow_the_configured_user_model(self):
        admin = UserTermsAndConditionsAdmin(UserTermsAndConditions, AdminSite())
        self.assertIn("user__username", admin.get_search_fields(None))
