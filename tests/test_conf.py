"""Tests for the app settings wrapper."""

from django.test import SimpleTestCase, override_settings

from termsandconditions.conf import DEFAULTS, app_settings


class AppSettingsTests(SimpleTestCase):
    def test_falls_back_to_the_documented_default(self):
        # The demo project does not define TERMS_BASE_TEMPLATE.
        self.assertEqual("base.html", app_settings.TERMS_BASE_TEMPLATE)

    @override_settings(TERMS_CACHE_SECONDS=99)
    def test_project_settings_win(self):
        self.assertEqual(99, app_settings.TERMS_CACHE_SECONDS)

    def test_settings_are_read_at_access_time(self):
        with override_settings(DEFAULT_TERMS_SLUG="first"):
            self.assertEqual("first", app_settings.DEFAULT_TERMS_SLUG)
        with override_settings(DEFAULT_TERMS_SLUG="second"):
            self.assertEqual("second", app_settings.DEFAULT_TERMS_SLUG)

    def test_unknown_setting_raises(self):
        with self.assertRaises(AttributeError):
            _ = app_settings.NOT_A_REAL_SETTING

    def test_dir_lists_every_known_setting(self):
        self.assertEqual(sorted(DEFAULTS), dir(app_settings))
