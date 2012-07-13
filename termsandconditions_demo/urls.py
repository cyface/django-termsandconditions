"""
    Master URL Pattern List for the application.  Most of the patterns here should be top-level
    pass-offs to sub-modules, who will have their own urls.py defining actions within.
"""

# pylint: disable=W0401, W0614, E1120

from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.conf import settings
from views import TermsRequiredView, SecureView, IndexView
from django.views.decorators.cache import never_cache
from termsandconditions.decorators import terms_required
from django.contrib.auth.decorators import login_required

admin.autodiscover()

urlpatterns = patterns('',

    # Home Page
    url(r'^$', never_cache(IndexView.as_view()), name="tc_demo_home_page"),

    # Home Page
    url(r'^anon/$', never_cache(IndexView.as_view(template_name="index_anon.html")), name="tc_demo_home_anon_page"), #used for pipeline user test

    # Secure Page
    url(r'^secure/$', never_cache((login_required(SecureView.as_view()))), name="tc_demo_secure_page"),

    # Secure Page Too
    url(r'^securetoo/$', never_cache(login_required(SecureView.as_view(template_name="securetoo.html"))), name="tc_demo_secure_page_too"),

    # Terms Required
    url(r'^termsrequired/$', never_cache(terms_required(login_required(TermsRequiredView.as_view()))), name="tc_demo_required_page"),

    # Terms and Conditions
    url(r'^terms/', include('termsandconditions.urls')),

    # Auth Urls:
    (r'^accounts/', include('django.contrib.auth.urls')),
    
    # Admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Admin Site:
    (r'^admin/', include(admin.site.urls)),

    # Robots and Favicon
    (r'^robots\.txt$', 'django.views.generic.simple.direct_to_template', {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': settings.STATIC_URL + 'images/favicon.ico'}),
)