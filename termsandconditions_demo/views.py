"""Django Views for the termsandconditions-demo module"""

from django.views.generic import TemplateView

class IndexView(TemplateView):
    """
    Main site page page.

    url: /
    """

    template_name = "index.html"


class SecureView(TemplateView):
    """
    Secure testing page.

    url: /secure & /securetoo
    """

    template_name = "secure.html"


class TermsRequiredView(TemplateView):
    """
    Terms Required testing page.

    url: /terms_required
    """

    template_name = "terms_required.html"