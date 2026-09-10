"""View decorators for the termsandconditions app."""

from collections.abc import Callable
from functools import wraps

from django.http import HttpRequest, HttpResponse

from .models import TermsAndConditions
from .utils import redirect_to_terms_accept


def terms_required(
    view_func: Callable[..., HttpResponse],
) -> Callable[..., HttpResponse]:
    """Send logged-in users to accept outstanding terms before running the view.

    Anonymous users pass straight through, so pair this with
    ``@login_required`` (or equivalent) when the view must be authenticated.
    """

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if (
            not request.user.is_authenticated
            or not TermsAndConditions.get_active_terms_not_agreed_to(request.user)
        ):
            return view_func(request, *args, **kwargs)

        # get_full_path, not path: the middleware carries the querystring
        # across too, and the user should land back on the same filtered page.
        return redirect_to_terms_accept(request.get_full_path())

    return _wrapped_view
