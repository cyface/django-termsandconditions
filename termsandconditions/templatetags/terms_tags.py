from django import template
from ..models import TermsAndConditions, DEFAULT_TERMS_SLUG
from ..middleware import is_path_protected
from urlparse import urlparse

register = template.Library()


@register.inclusion_tag('termsandconditions/snippets/termsandconditions.html',
                        takes_context=True)
def show_terms_if_not_agreed(context, slug=DEFAULT_TERMS_SLUG):
    """Displays a modal on a current page if a user has not yet agreed to the
    given terms. If terms are not specified, the default slug is used.

    How it works? A small snippet is included into your template if a user
    who requested the view has not yet agreed the terms. The snippet takes
    care of displaying a respective modal.
    """
    request = context['request']
    terms = TermsAndConditions.get_active(slug)
    agreed = TermsAndConditions.agreed_to_terms(request.user, terms)

    # stop here, if terms has been agreed
    if agreed:
        return {}

    # handle excluded url's
    url = urlparse(request.META['HTTP_REFERER'])
    protected = is_path_protected(url.path)

    if not agreed and terms and protected:
        return {'terms': terms}

    return {}
