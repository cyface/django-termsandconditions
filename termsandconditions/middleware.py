import urlparse
from django.http import HttpResponseRedirect, QueryDict
from models import TermsAndConditions
from django.conf import settings
from pipeline import redirect_to_terms_accept

ACCEPT_TERMS_PATH = getattr(settings, 'ACCEPT_TERMS_PATH', '/terms/accept/')
TERMS_EXCLUDE_URL_PREFIX_LIST = getattr(settings, 'TERMS_EXCLUDE_URL_PREFIX_LIST', {'/admin/', })
TERMS_EXCLUDE_URL_LIST = getattr(settings, 'TERMS_EXCLUDE_URL_LIST', {'/', '/terms/required/', '/socialprofile/logout/', '/securetoo/'})
MULTIPLE_ACTIVE_TERMS = getattr(settings, 'MULTIPLE_ACTIVE_TERMS', False)

class TermsAndConditionsRedirectMiddleware:
    """
    This middleware checks to see if the user is logged in, and if so, if they have accepted the site terms.
    """

    def process_request(self, request):
        current_path = request.META['PATH_INFO']
        protected_path = True

        for exclude_path in TERMS_EXCLUDE_URL_PREFIX_LIST:
            if current_path.startswith(exclude_path):
                protected_path = False

        if current_path in TERMS_EXCLUDE_URL_LIST:
            protected_path = False

        if current_path.startswith(ACCEPT_TERMS_PATH):
            protected_path = False

        if request.user.is_authenticated() and protected_path:
            if MULTIPLE_ACTIVE_TERMS:
                for term in TermsAndConditions.get_active_list():
                    if not TermsAndConditions.agreed_to_latest(request.user, term):
                        return redirect_to_terms_accept(current_path, term)
            else:
                if not TermsAndConditions.agreed_to_latest(request.user):
                    return redirect_to_terms_accept(current_path)