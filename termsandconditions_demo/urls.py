"""URL configuration for the termsandconditions demo project."""

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from django.urls import include, path
from django.views.decorators.cache import never_cache
from django.views.generic import RedirectView, TemplateView

from termsandconditions.decorators import terms_required

from .views import IndexView, SecureView, TermsRequiredView

urlpatterns = [
    path("", never_cache(IndexView.as_view()), name="tc_demo_home_page"),
    path(
        "secure/",
        never_cache(login_required(SecureView.as_view())),
        name="tc_demo_secure_page",
    ),
    path(
        "securetoo/",
        never_cache(login_required(SecureView.as_view(template_name="securetoo.html"))),
        name="tc_demo_secure_page_too",
    ),
    path(
        "termsrequired/",
        never_cache(terms_required(login_required(TermsRequiredView.as_view()))),
        name="tc_demo_required_page",
    ),
    path("terms/", include("termsandconditions.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="tc_demo_robots",
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(url=static("images/favicon.ico"), permanent=True),
        name="tc_demo_favicon",
    ),
]
