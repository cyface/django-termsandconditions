"""Django Models for TermsAndConditions App"""

# pylint: disable=W0613

from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.http import Http404
import datetime
import logging

LOGGER = logging.getLogger(name='termsandconditions')

DEFAULT_TERMS_SLUG = getattr(settings, 'DEFAULT_TERMS_SLUG', 'site-terms')

class UserTermsAndConditions(models.Model):
    """Holds mapping between TermsAndConditions and Users"""
    user = models.ForeignKey(User, related_name="userterms")
    terms = models.ForeignKey("TermsAndConditions", related_name="userterms")
    ip_address = models.IPAddressField(null=True, blank=True, verbose_name='IP Address')
    date_accepted = models.DateTimeField(auto_now_add=True, verbose_name='Date Accepted')

    class Meta:
        """Model Meta Information"""
        get_latest_by = 'date_accepted'
        verbose_name = 'User Terms and Conditions'
        verbose_name_plural = 'User Terms and Conditions'
        unique_together = ('user', 'terms',)


class TermsAndConditions(models.Model):
    """Holds Versions of TermsAndConditions
    Active one for a given slug is: date_active is not Null and is latest not in future"""
    slug = models.SlugField(default=DEFAULT_TERMS_SLUG)
    name = models.TextField(max_length=255)
    users = models.ManyToManyField(User, through=UserTermsAndConditions, blank=True, null=True, )
    version_number = models.DecimalField(default=1.0, decimal_places=2, max_digits=6)
    text = models.TextField(null=True, blank=True)
    date_active = models.DateTimeField(blank=True, null=True, help_text="Leave Null To Never Make Active")
    date_created = models.DateTimeField(blank=True, auto_now_add=True)

    class Meta:
        """Model Meta Information"""
        ordering = ['-date_active', ]
        get_latest_by = 'date_active'
        verbose_name = 'Terms and Conditions'
        verbose_name_plural = 'Terms and Conditions'

    def __unicode__(self):
        return "{0}-{1:.2f}".format(self.slug, self.version_number)

    @models.permalink
    def get_absolute_url(self):
        return ('tc_view_specific_version_page', [self.slug, self.version_number]) # pylint: disable=E1101

    @staticmethod
    def create_default_terms():
        """Create a default TermsAndConditions Object"""
        default_terms = TermsAndConditions.objects.create(
            slug=DEFAULT_TERMS_SLUG,
            name=DEFAULT_TERMS_SLUG,
            date_active=datetime.datetime.now(),
            version_number=1,
            text=DEFAULT_TERMS_SLUG + " Text. CHANGE ME.")
        return default_terms

    @staticmethod
    def get_active(slug=DEFAULT_TERMS_SLUG):
        """Finds the latest of a particular terms and conditions"""

        try:
            activeTerms = TermsAndConditions.objects.filter(
                date_active__isnull=False,
                date_active__lte=datetime.datetime.now(),
                slug=slug).latest('date_active')
        except TermsAndConditions.DoesNotExist:
            if slug == DEFAULT_TERMS_SLUG:
                activeTerms = TermsAndConditions.create_default_terms()
            else:
                raise Http404

        return activeTerms

    @staticmethod
    def get_active_list():
        """Finds the latest of all terms and conditions"""
        terms_list = {}
        try:
            all_terms_list = TermsAndConditions.objects.filter(
                date_active__isnull=False,
                date_active__lte=datetime.datetime.now())
            for term in all_terms_list:
                terms_list.update({term.slug: TermsAndConditions.get_active(slug=term.slug)})
        except TermsAndConditions.DoesNotExist:
            terms_list.update({DEFAULT_TERMS_SLUG: TermsAndConditions.create_default_terms()})

        return terms_list

    @staticmethod
    def agreed_to_latest(user, slug=DEFAULT_TERMS_SLUG):
        """Checks to see if a specified user has agreed to the latest of a particular terms and conditions"""

        try:
            UserTermsAndConditions.objects.get(user=user, terms=TermsAndConditions.get_active(slug))
            return True
        except UserTermsAndConditions.MultipleObjectsReturned:
            return True
        except UserTermsAndConditions.DoesNotExist:
            return False

    @staticmethod
    def agreed_to_terms(user, terms=None):
        """Checks to see if a specified user has agreed to a specific terms and conditions"""

        try:
            UserTermsAndConditions.objects.get(user=user, terms=terms)
            return True
        except UserTermsAndConditions.DoesNotExist:
            return False