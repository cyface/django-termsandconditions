"""
    Master URL Pattern List for the application.  Most of the patterns here should be top-level
    pass-offs to sub-modules, who will have their own urls.py defining actions within.
"""

# pylint: disable=W0401, W0614

from django.conf.urls import *  #@UnusedWildImport
from django.contrib import admin
from views import ViewTerms

admin.autodiscover()

# Instantiate TermsView class-based-view in order to pull the urls property off of it.
terms_view = ViewTerms()

urlpatterns = patterns('termsandconditions.views',
    # View Terms
    url(r'', include(terms_view.urls), name="tc_view_page"),

    # Accept Terms
    url(r'^accept/$', 'accept_view', name="tc_accept_page"),

    # Accept Terms
    url(r'^accept/(?P<slug>[a-zA-Z0-9_.-]+)$', 'accept_view', name="tc_accept_specific_page"),

    # Terms Required
    url(r'^required/$', 'terms_required_view', name="tc_required_page"),
)


#url(r'^view/(?P<slug>[-\w]+)/$', 'terms_view', name="view_terms_page_with_slug"),
#url(r'^(?P<slug>\[-w])/(?P<version_number>\[0..9\.]+)$', 'accept_view', name="view_terms_page_with_version"),