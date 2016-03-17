from django.test import TestCase
from django.utils import timezone
from termsandconditions.models import TermsAndConditions, DEFAULT_TERMS_SLUG


class TermsAndConditionsTestCase(TestCase):

    def setUp(self):
        self.terms_1 = TermsAndConditions.objects.create(
            name='terms_1',
            date_active=timezone.now()
        )
        self.terms_2 = TermsAndConditions.objects.create(
            name='terms_2',
            date_active=None
        )

    def test_termsandconditions_default_slug(self):
        """test if default slug is used"""
        self.assertEqual(self.terms_1.slug, DEFAULT_TERMS_SLUG)

    def test_termsandconditions_get_active(self):
        """test if right terms are active"""
        active = TermsAndConditions.get_active()
        self.assertEqual(active.name, self.terms_1.name)
        self.assertNotEqual(active.name, self.terms_2.name)
