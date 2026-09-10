"""Template tags for the termsandconditions app."""

from urllib.parse import urlparse

from django import template

from ..conf import app_settings
from ..middleware import is_path_protected
from ..models import TermsAndConditions

register = template.Library()


@register.inclusion_tag(
    "termsandconditions/snippets/termsandconditions.html", takes_context=True
)
def show_terms_if_not_agreed(context, field: str | None = None) -> dict:
    """Render a modal when the current user has terms left to accept.

    Unlike the middleware this does not redirect, so users can keep browsing
    and accept later.  ``field`` names the ``request.META`` key holding the
    current path; it defaults to ``TERMS_HTTP_PATH_FIELD``.
    """
    request = context["request"]
    url = urlparse(request.META[field or app_settings.TERMS_HTTP_PATH_FIELD])
    not_agreed_terms = TermsAndConditions.get_active_terms_not_agreed_to(request.user)

    if not_agreed_terms and is_path_protected(url.path):
        return {"not_agreed_terms": not_agreed_terms, "returnTo": url.path}

    return {"not_agreed_terms": False}


@register.filter
def as_template(obj) -> template.Template:
    """Turn a string into a Template so its tags are rendered.

    Useful when a terms ``text`` field contains template syntax, for example
    ``<a href="{% url 'my-url' %}">My url</a>``::

        {% include terms.text|as_template %}
    """
    return template.Template(obj)
