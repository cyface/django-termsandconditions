"""Terms and Conditions Middleware"""
from .models import TermsAndConditions
from django.conf import settings
from django.db.models import Max
from django.utils import timezone
import logging
from .pipeline import redirect_to_terms_accept
import django

if django.VERSION >= (1, 10, 0):
    from django.utils.deprecation import MiddlewareMixin
else:
    MiddlewareMixin = object

LOGGER = logging.getLogger(name='termsandconditions')

ACCEPT_TERMS_PATH = getattr(settings, 'ACCEPT_TERMS_PATH', '/terms/accept/')
TERMS_EXCLUDE_URL_PREFIX_LIST = getattr(settings, 'TERMS_EXCLUDE_URL_PREFIX_LIST', {'/admin', '/terms'})
TERMS_EXCLUDE_URL_LIST = getattr(settings, 'TERMS_EXCLUDE_URL_LIST', {'/', '/termsrequired/', '/logout/', '/securetoo/'})


class TermsAndConditionsRedirectMiddleware(MiddlewareMixin):
    """
    This middleware checks to see if the user is logged in, and if so,
    if they have accepted the site terms.
    """

    def process_request(self, request):
        """Process each request to app to ensure terms have been accepted"""

        LOGGER.debug('termsandconditions.middleware')

        current_path = request.META['PATH_INFO']

        if request.user.is_authenticated() and is_path_protected(current_path):
            active_terms = (
                TermsAndConditions.objects.prefetch_related('users')
                .filter(
                    date_active__isnull=False,
                    date_active__lte=timezone.now(),
                )
                .values_list('slug')
                .annotate(Max('date_active'))
                .order_by()
            )
            user_agreed_terms = active_terms.filter(users=request.user)
            if not set(active_terms) == set(user_agreed_terms):
                pending_terms = set(active_terms) - set(user_agreed_terms)
                for each in pending_terms:
                    term = each[0]
                    return redirect_to_terms_accept(current_path, term)
        return None


def is_path_protected(path):
    """
    returns True if given path is to be protected, otherwise False

    The path is not to be protected when it appears on:
    TERMS_EXCLUDE_URL_PREFIX_LIST, TERMS_EXCLUDE_URL_LIST or as
    ACCEPT_TERMS_PATH
    """
    protected = True

    for exclude_path in TERMS_EXCLUDE_URL_PREFIX_LIST:
        if path.startswith(exclude_path):
            protected = False

    if path in TERMS_EXCLUDE_URL_LIST:
        protected = False

    if path.startswith(ACCEPT_TERMS_PATH):
        protected = False

    return protected
