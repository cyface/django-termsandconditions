"""
    Master URL Pattern List for the application.  Most of the patterns here should be top-level
    pass-offs to sub-modules, who will have their own urls.py defining actions within.
"""

# pylint: disable=W0401, W0614, E1120

from django.conf.urls import patterns, url
from django.contrib import admin
from views import TermsView, AcceptView
from models import DEFAULT_TERMS_SLUG

admin.autodiscover()

urlpatterns = patterns('termsandconditions.views',
    # View Default Terms
    url(r'^$', TermsView.as_view(), {"slug": DEFAULT_TERMS_SLUG}, name="tc_view_page"),

    # View Specific Active Terms
    url(r'^view/(?P<slug>[a-zA-Z0-9_.-]+)/$', TermsView.as_view(), name="tc_view_specific_page"),

    # View Specific Version of Terms
    url(r'^view/(?P<slug>[a-zA-Z0-9_.-]+)/(?P<version>[0-9.]+)/$', TermsView.as_view(), name="tc_view_specific_version_page"),

    # Accept Terms
    url(r'^accept/$', AcceptView.as_view(), name="tc_accept_page"),

    # Accept Specific Terms
    url(r'^accept/(?P<slug>[a-zA-Z0-9_.-]+)$', AcceptView.as_view(), name="tc_accept_specific_page"),

    # Accept Specific Terms Version
    url(r'^accept/(?P<slug>[a-zA-Z0-9_.-]+)/(?P<version_number>\[0..9\.]+)/$', AcceptView.as_view(), name="tc_accept_specific_page"),

)