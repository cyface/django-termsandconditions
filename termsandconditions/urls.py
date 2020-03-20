"""
    Master URL Pattern List for the application.  Most of the patterns here should be top-level
    pass-offs to sub-modules, who will have their own urls.py defining actions within.
"""

# pylint: disable=W0401, W0614, E1120

from django.contrib import admin
from django.urls import path, register_converter
from django.views.decorators.cache import never_cache

from .views import TermsView, AcceptTermsView, EmailTermsView
from .models import DEFAULT_TERMS_SLUG

admin.autodiscover()


class TermsVersionConverter:
    """
    Registers Django URL path converter for Terms Version Numbers
    """
    regex = "[0-9.]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(TermsVersionConverter, 'termsversion')

urlpatterns = (
    # View Default Terms
    path("", never_cache(TermsView.as_view()), name="tc_view_page"),
    # View Specific Active Terms
    path(
        "view/<slug:slug>/",
        never_cache(TermsView.as_view()),
        name="tc_view_specific_page",
    ),
    # View Specific Version of Terms
    path(
        "view/<slug:slug>/<termsversion:version>/",
        never_cache(TermsView.as_view()),
        name="tc_view_specific_version_page",
    ),
    # Print Specific Version of Terms
    path(
        "print/<slug:slug>/<termsversion:version>/",
        never_cache(TermsView.as_view(template_name="termsandconditions/tc_print_terms.html")),
        name="tc_print_page",
    ),
    # Accept Terms
    path("accept/", AcceptTermsView.as_view(), name="tc_accept_page"),
    # Accept Specific Terms
    path(
        "accept/<slug:slug>/",
        AcceptTermsView.as_view(),
        name="tc_accept_specific_page",
    ),
    # Accept Specific Terms Version
    path(
        "accept/<slug:slug>/<termsversion:version>/",
        AcceptTermsView.as_view(),
        name="tc_accept_specific_version_page",
    ),
    # Email Terms
    path("email/", EmailTermsView.as_view(), name="tc_email_page"),
    # Email Specific Terms Version
    path(
        "email/<slug:slug>/<termsversion:version>/",
        never_cache(EmailTermsView.as_view()),
        name="tc_specific_version_page",
    ),
)
