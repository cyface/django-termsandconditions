"""
    Master path Pattern List for the application.  Most of the patterns here should be top-level
    pass-offs to sub-modules, who will have their own paths.py defining actions within.
"""

from django.contrib import admin
from django.conf import settings
from django.urls import path, include

from .views import TermsRequiredView, SecureView, IndexView
from django.views.generic import RedirectView, TemplateView
from django.views.decorators.cache import never_cache
from termsandconditions.decorators import terms_required
from django.contrib.auth.decorators import login_required

admin.autodiscover()

urlpatterns = (
    # Home Page
    path("", never_cache(IndexView.as_view()), name="tc_demo_home_page"),
    # Home Page
    path(
        "anon/",
        never_cache(IndexView.as_view(template_name="index_anon.html")),
        name="tc_demo_home_anon_page",
    ),  # used for pipeline user test
    # Secure Page
    path(
        "secure/",
        never_cache(login_required(SecureView.as_view())),
        name="tc_demo_secure_page",
    ),
    # Secure Page Too
    path(
        "securetoo/",
        never_cache(login_required(SecureView.as_view(template_name="securetoo.html"))),
        name="tc_demo_secure_page_too",
    ),
    # Terms Required
    path(
        "termsrequired/",
        never_cache(terms_required(login_required(TermsRequiredView.as_view()))),
        name="tc_demo_required_page",
    ),
    # Terms and Conditions
    path("terms/", include("termsandconditions.urls")),
    # Auth paths:
    path("accounts/", include("django.contrib.auth.urls")),
    # Admin documentation:
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    # Admin Site:
    path("admin/", admin.site.urls),
    # Robots and Favicon
    path(
        "robots.txt",
        TemplateView.as_view(),
        {"template": "robots.txt", "mimetype": "text/plain"},
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(permanent=True),
        {"path": settings.STATIC_URL + "images/favicon.ico"},
    ),
)
