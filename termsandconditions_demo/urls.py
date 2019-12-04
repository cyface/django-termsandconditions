"""
    Master URL Pattern List for the application.  Most of the patterns here should be top-level
    pass-offs to sub-modules, who will have their own urls.py defining actions within.
"""

# pylint: disable=E1120

from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from .views import TermsRequiredView, SecureView, IndexView
from django.views.generic import RedirectView, TemplateView
from django.views.decorators.cache import never_cache
from termsandconditions.decorators import terms_required
from django.contrib.auth.decorators import login_required

admin.autodiscover()

urlpatterns = (
    # Home Page
    url(r"^$", never_cache(IndexView.as_view()), name="tc_demo_home_page"),
    # Home Page
    url(
        r"^anon/$",
        never_cache(IndexView.as_view(template_name="index_anon.html")),
        name="tc_demo_home_anon_page",
    ),  # used for pipeline user test
    # Secure Page
    url(
        r"^secure/$",
        never_cache((login_required(SecureView.as_view()))),
        name="tc_demo_secure_page",
    ),
    # Secure Page Too
    url(
        r"^securetoo/$",
        never_cache(login_required(SecureView.as_view(template_name="securetoo.html"))),
        name="tc_demo_secure_page_too",
    ),
    # Terms Required
    url(
        r"^termsrequired/$",
        never_cache(terms_required(login_required(TermsRequiredView.as_view()))),
        name="tc_demo_required_page",
    ),
    # Terms and Conditions
    url(r"^terms/", include("termsandconditions.urls")),
    # Auth Urls:
    url(r"^accounts/", include("django.contrib.auth.urls")),
    # Admin documentation:
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    # Admin Site:
    url(r"^admin/", admin.site.urls),
    # Robots and Favicon
    url(
        r"^robots\.txt$",
        TemplateView.as_view(),
        {"template": "robots.txt", "mimetype": "text/plain"},
    ),
    url(
        r"^favicon\.ico$",
        RedirectView.as_view(permanent=True),
        {"url": settings.STATIC_URL + "images/favicon.ico"},
    ),
)
