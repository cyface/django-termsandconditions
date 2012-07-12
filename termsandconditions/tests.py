"""Unit Tests for the termsandconditions module"""

# pylint: disable=R0904, C0103

from django.test.client import Client
from django.test import TestCase
from django.contrib.auth.models import User
from termsandconditions.models import TermsAndConditions
from termsandconditions.models import UserTermsAndConditions
import logging

LOGGER = logging.getLogger(name='termsandconditions')


class TermsAndConditionsTests(TestCase):
    """Tests Terms and Conditions Module"""

    def setUp(self):
        """Setup for each test"""
        LOGGER.debug('Test Setup')
        self.c = Client()
        self.user1 = User.objects.create_user('user1', 'user1@user1.com', 'user1password')
        self.user2 = User.objects.create_user('user2', 'user2@user2.com', 'user2password')
        self.terms1 = TermsAndConditions.objects.create(slug="site-terms", name="Site Terms",
            text="Site Terms and Conditions 1", version_number=1.0, date_active="2012-01-01")
        self.terms2 = TermsAndConditions.objects.create(slug="site-terms", name="Site Terms",
            text="Site Terms and Conditions 2", version_number=2.0, date_active="2012-01-05")
        self.terms3 = TermsAndConditions.objects.create(slug="contrib-terms", name="Contributor Terms",
            text="Contributor Terms and Conditions 1.5", version_number=1.5, date_active="2012-01-01")
        self.terms4 = TermsAndConditions.objects.create(slug="contrib-terms", name="Contributor Terms",
            text="Contributor Terms and Conditions 2", version_number=2.0, date_active="2100-01-01")

    def tearDown(self):
        """Teardown for each test"""
        LOGGER.debug('Test TearDown')
        User.objects.all().delete()
        TermsAndConditions.objects.all().delete()
        UserTermsAndConditions.objects.all().delete()

    def test_get_active_list(self):
        """Test get list of active T&Cs"""
        active_list = TermsAndConditions.get_active_list()
        LOGGER.debug('Active Terms: ' + str(active_list))
        self.assertEqual(2, len(active_list))

    def test_terms_and_conditions_models(self):
        """Various tests of the TermsAndConditions Module"""

        # Testing Direct Assignment of Acceptance
        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms1)
        UserTermsAndConditions.objects.create(user=self.user2, terms=self.terms3)

        self.assertEquals(1.0, self.user1.userterms.get().terms.version_number)
        self.assertEquals(1.5, self.user2.userterms.get().terms.version_number)

        self.assertEquals('user1', self.terms1.users.all()[0].username)

        # Testing the get_active static method of TermsAndConditions
        self.assertEquals(2.0, TermsAndConditions.get_active(slug='site-terms').version_number)
        self.assertEquals(1.5, TermsAndConditions.get_active(slug='contrib-terms').version_number)

        # Testing the agreed_to_latest static method of TermsAndConditions
        self.assertEquals(False, TermsAndConditions.agreed_to_latest(user=self.user1, slug='site-terms'))
        self.assertEquals(True, TermsAndConditions.agreed_to_latest(user=self.user2, slug='contrib-terms'))

        # Testing the unicode method of TermsAndConditions
        self.assertEquals('site-terms-2.00', str(TermsAndConditions.get_active(slug='site-terms')))
        self.assertEquals('contrib-terms-1.50', str(TermsAndConditions.get_active(slug='contrib-terms')))

    def test_middleware_redirect(self):
        """Validate that a user is redirected to the terms accept page if they are logged in, and decorator is on method"""

        UserTermsAndConditions.objects.all().delete()

        LOGGER.debug('Test user1 login for middleware')
        login_response = self.c.login(username='user1', password='user1password')
        self.assertTrue(login_response)

        LOGGER.debug('Test /secure/ after login')
        logged_in_response = self.c.get('/secure/', follow=True)
        self.assertRedirects(logged_in_response, "http://testserver/terms/accept/site-terms?returnTo=/secure/")

    def test_terms_required_redirect(self):
        """Validate that a user is redirected to the terms accept page if they are logged in, and decorator is on method"""

        LOGGER.debug('Test /termsrequired/ pre login')
        not_logged_in_response = self.c.get('/termsrequired/', follow=True)
        self.assertRedirects(not_logged_in_response, "http://testserver/accounts/login/?next=/termsrequired/")

        LOGGER.debug('Test user1 login')
        login_response = self.c.login(username='user1', password='user1password')
        self.assertTrue(login_response)

        LOGGER.debug('Test /termsrequired/ after login')
        logged_in_response = self.c.get('/termsrequired/', follow=True)
        self.assertRedirects(logged_in_response, "http://testserver/terms/accept/?returnTo=/termsrequired/")

        LOGGER.debug('Test no redirect for /termsrequired/ after accept')
        accepted_response = self.c.post('/terms/accept/', {'terms': 2, 'returnTo': '/termsrequired/'}, follow=True)
        LOGGER.debug('Test response after termsrequired accept')
        LOGGER.debug(accepted_response)
        termsrequired_response = self.c.get('/termsrequired/', follow=True)
        self.assertContains(termsrequired_response, "Terms and Conditions Acceptance Required")

    def test_accept(self):
        """Validate that accepting terms works"""

        LOGGER.debug('Test user1 login for accept')
        login_response = self.c.login(username='user1', password='user1password')
        self.assertTrue(login_response)

        LOGGER.debug('Test /terms/accept/ get')
        logged_in_response = self.c.get('/terms/accept/', follow=True)
        self.assertContains(logged_in_response, "Accept")

        LOGGER.debug('Test /terms/accept/ post')
        logged_in_response = self.c.post('/terms/accept/', {'terms': 2, 'returnTo': '/secure/'}, follow=True)
        LOGGER.debug(logged_in_response)
        self.assertContains(logged_in_response, "Contributor")

        self.assertEquals(True, TermsAndConditions.agreed_to_latest(user=self.user1, slug='site-terms'))

    def test_auto_create(self):
        """Validate that a terms are auto created if none exist"""
        LOGGER.debug('Test auto create terms')

        TermsAndConditions.objects.all().delete()

        numTerms = TermsAndConditions.objects.count()
        self.assertEquals(0, numTerms)

        LOGGER.debug('Test user1 login for autocreate')
        login_response = self.c.login(username='user1', password='user1password')
        self.assertTrue(login_response)

        LOGGER.debug('Test /termsrequired/ after login with no TermsAndConditions')
        logged_in_response = self.c.get('/termsrequired/', follow=True)
        self.assertRedirects(logged_in_response, "http://testserver/terms/accept/?returnTo=/termsrequired/")

        LOGGER.debug('Test TermsAndConditions Object Was Created')
        numTerms = TermsAndConditions.objects.count()
        self.assertEquals(1, numTerms)

        terms = TermsAndConditions.objects.get()
        self.assertEquals('site-terms-1.00', str(terms))

        LOGGER.debug('Test Not Creating Non-Default TermsAndConditions')
        non_default_response = self.c.get('/terms/accept/contributor-terms/', follow=True)
        self.assertEquals(404, non_default_response.status_code)


    def test_terms_upgrade(self):
        """Validate a user is prompted to accept terms again when new version comes out"""

        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms2)

        LOGGER.debug('Test user1 login pre upgrade')
        login_response = self.c.login(username='user1', password='user1password')
        self.assertTrue(login_response)

        LOGGER.debug('Test user1 not redirected after login')
        logged_in_response = self.c.get('/secure/', follow=True)
        self.assertContains(logged_in_response, "Contributor")

        LOGGER.debug('Test upgrade terms')
        self.terms5 = TermsAndConditions.objects.create(slug="site-terms", name="Site Terms",
            text="Terms and Conditions2", version_number=2.5, date_active="2012-02-05")

        LOGGER.debug('Test user1 is redirected when changing pages')
        post_upgrade_response = self.c.get('/secure/', follow=True)
        self.assertRedirects(post_upgrade_response, "http://testserver/terms/accept/site-terms?returnTo=/secure/")

    def test_no_middleware(self):
        """Test a secure page with the middleware excepting it"""

        UserTermsAndConditions.objects.create(user=self.user1, terms=self.terms2)

        LOGGER.debug('Test user1 login no middleware')
        login_response = self.c.login(username='user1', password='user1password')
        self.assertTrue(login_response)

        LOGGER.debug('Test user1 not redirected after login')
        logged_in_response = self.c.get('/securetoo/', follow=True)
        self.assertContains(logged_in_response, "SECOND")

        LOGGER.debug("Test startswith '/admin' pages not redirecting")
        admin_response = self.c.get('/admin', follow=True)
        self.assertContains(admin_response, "administration")

    def test_terms_view(self):
        """Test Accessing the View Terms and Conditions Functions"""

        LOGGER.debug('Test /terms/')
        response1 = self.c.get('/terms/', follow=True)
        self.assertContains(response1, 'Terms and Conditions')

        LOGGER.debug('Test /terms/view/site-terms')
        response2 = self.c.get('/terms/view/site-terms', follow=True)
        self.assertContains(response2, 'Terms and Conditions')

        LOGGER.debug('Test /terms/view/site-terms/1.0')
        response2 = self.c.get('/terms/view/site-terms/1.0', follow=True)
        self.assertContains(response2, 'Terms and Conditions')


