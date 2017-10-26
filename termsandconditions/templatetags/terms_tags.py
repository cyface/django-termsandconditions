"""Django Tags"""
from django import template
from ..models import TermsAndConditions
from ..middleware import is_path_protected
from django.conf import settings
from future.moves.urllib.parse import urlparse

register = template.Library()
DEFAULT_HTTP_PATH_FIELD = 'PATH_INFO'
TERMS_HTTP_PATH_FIELD = getattr(settings, 'TERMS_HTTP_PATH_FIELD', DEFAULT_HTTP_PATH_FIELD)


@register.inclusion_tag('termsandconditions/snippets/termsandconditions.html',
                        takes_context=True)
def show_terms_if_not_agreed(context, field=TERMS_HTTP_PATH_FIELD):
    """Displays a modal on a current page if a user has not yet agreed to the
    given terms. If terms are not specified, the default slug is used.

    A small snippet is included into your template if a user
    who requested the view has not yet agreed the terms. The snippet takes
    care of displaying a respective modal.
    """
    request = context['request']
    url = urlparse(request.META[field])
    not_agreed_terms = TermsAndConditions.get_active_terms_not_agreed_to(request.user)

    if not_agreed_terms and is_path_protected(url.path):
        return {'not_agreed_terms': not_agreed_terms, 'returnTo': url.path}
    else:
        return {}
