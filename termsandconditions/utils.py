"""Helpers shared by the middleware, decorator and views."""

from urllib.parse import urlparse, urlunparse

from django.http import HttpResponseRedirect, QueryDict

from .conf import app_settings


def redirect_to_terms_accept(
    current_path: str = "/", slug: str | None = None
) -> HttpResponseRedirect:
    """Redirect to the terms acceptance page, remembering where to return to.

    ``slug`` narrows the redirect to one set of terms; omit it to send the user
    to the page listing everything they still have to accept.
    """
    redirect_url_parts = list(urlparse(app_settings.ACCEPT_TERMS_PATH))
    if slug:
        redirect_url_parts[2] += f"{slug}/"
    querystring = QueryDict(redirect_url_parts[4], mutable=True)
    querystring[app_settings.TERMS_RETURNTO_PARAM] = current_path
    redirect_url_parts[4] = querystring.urlencode(safe="/")
    return HttpResponseRedirect(urlunparse(redirect_url_parts))


def active_terms_cache_key(slug: str) -> str:
    """Cache key holding the active terms for ``slug``."""
    return f"tandc.active_terms_{slug}"


def not_agreed_terms_cache_key(username: str) -> str:
    """Cache key holding the terms ``username`` has yet to agree to."""
    return f"tandc.not_agreed_terms_{username}"


#: Cache key holding the ids of every active terms object.
ACTIVE_TERMS_IDS_CACHE_KEY = "tandc.active_terms_ids"

#: Cache key holding the queryset of every active terms object.
ACTIVE_TERMS_LIST_CACHE_KEY = "tandc.active_terms_list"
