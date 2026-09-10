"""Helpers shared by the middleware, decorator and views."""

from collections.abc import Iterable
from hashlib import sha256
from typing import Any
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


def not_agreed_terms_cache_key(user_pk: Any, active_terms_ids: Iterable[int]) -> str:
    """Cache key holding the terms the user with ``user_pk`` has yet to agree to.

    Keyed on the primary key rather than the username: the username has to be
    fetched, and it may contain spaces or non-ASCII, which memcached rejects.

    The ids of the terms in force are folded in, because that is what the
    cached answer depends on.  A terms change therefore retires every user's
    entry at once, with nothing to enumerate: sweeping them one user at a time
    costs a scan of the acceptance table on every save, and still misses anyone
    who has accepted nothing and so appears in no row of it.  ``get_active_terms_ids``
    orders by slug, so the digest is stable, and an evicted id cache recomputes
    to the same value rather than to a new one.
    """
    joined_ids = ",".join(str(pk) for pk in active_terms_ids)
    digest = sha256(joined_ids.encode()).hexdigest()[:12]
    return f"tandc.not_agreed_terms_{digest}_{user_pk}"


#: Cache key holding the ids of every active terms object.
ACTIVE_TERMS_IDS_CACHE_KEY = "tandc.active_terms_ids"

#: Cache key holding the queryset of every active terms object.
ACTIVE_TERMS_LIST_CACHE_KEY = "tandc.active_terms_list"
