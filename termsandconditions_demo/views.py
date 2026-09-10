"""Views for the termsandconditions demo project."""

from django.views.generic import TemplateView


class IndexView(TemplateView):
    """Landing page. url: /"""

    template_name = "index.html"


class SecureView(TemplateView):
    """Login-required page. url: /secure/ and /securetoo/"""

    template_name = "secure.html"


class TermsRequiredView(TemplateView):
    """Page gated by the terms_required decorator. url: /termsrequired/"""

    template_name = "terms_required.html"
