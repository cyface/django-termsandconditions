"""View Decorators for termsandconditions module"""
from django import VERSION as DJANGO_VERSION
from future.moves.urllib.parse import urlparse, urlunparse
from functools import wraps
from django.http import HttpResponseRedirect, QueryDict
from django.utils.decorators import available_attrs
from .models import TermsAndConditions
from .middleware import ACCEPT_TERMS_PATH


def terms_required(view_func):
    """
    This decorator checks to see if the user is logged in, and if so, if they have accepted the site terms.
    """

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        """Method to wrap the view passed in"""
        # If user has not logged in, or if they have logged in and already agreed to the terms, let the view through
        if DJANGO_VERSION <= (2, 0, 0):
            user_authenticated = request.user.is_authenticated()
        else:
            user_authenticated = request.user.is_authenticated

        if not user_authenticated or not TermsAndConditions.get_active_terms_not_agreed_to(request.user):
            return view_func(request, *args, **kwargs)

        # Otherwise, redirect to terms accept
        current_path = request.path
        login_url_parts = list(urlparse(ACCEPT_TERMS_PATH))
        querystring = QueryDict(login_url_parts[4], mutable=True)
        querystring['returnTo'] = current_path
        login_url_parts[4] = querystring.urlencode(safe='/')
        return HttpResponseRedirect(urlunparse(login_url_parts))

    return _wrapped_view
