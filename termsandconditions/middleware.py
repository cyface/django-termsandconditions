"""Middleware that funnels users to the terms acceptance page."""

import logging
from collections.abc import Callable
from typing import Any

from django.http import HttpRequest, HttpResponse

from asgiref.sync import iscoroutinefunction, markcoroutinefunction, sync_to_async

from .conf import app_settings
from .models import TermsAndConditions
from .utils import redirect_to_terms_accept

LOGGER = logging.getLogger(__name__)


class TermsAndConditionsRedirectMiddleware:
    """Redirect authenticated users who have terms left to accept."""

    sync_capable = True
    async_capable = True

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    def __call__(self, request: HttpRequest):
        if iscoroutinefunction(self):
            return self.__acall__(request)
        return self.process_request(request) or self.get_response(request)

    async def __acall__(self, request: HttpRequest) -> HttpResponse:
        """Async path, so an ASGI stack is not forced back onto the thread pool.

        ``process_request`` resolves ``request.user`` and queries the database,
        so it runs in a thread — but only it does.  Declaring the middleware
        async-capable keeps everything below it in ``MIDDLEWARE`` running
        natively.
        """
        response = await sync_to_async(self.process_request)(request)
        return response or await self.get_response(request)

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        """Send the user to accept the first outstanding terms, if any."""
        current_path = request.path_info

        if not (request.user.is_authenticated and is_path_protected(current_path)):
            return None

        outstanding = TermsAndConditions.get_active_terms_not_agreed_to(request.user)
        if not outstanding:
            return None

        # Carry the querystring across so the user lands back where they were.
        query_string = request.META.get("QUERY_STRING", "")
        if query_string:
            current_path += f"?{query_string}"

        return redirect_to_terms_accept(current_path, outstanding[0].slug)


def is_path_protected(path: str) -> bool:
    """Return whether ``path`` should be gated behind terms acceptance.

    A path is left alone when it is listed in
    ``TERMS_EXCLUDE_URL_PREFIX_LIST``, ``TERMS_EXCLUDE_URL_LIST`` or
    ``TERMS_EXCLUDE_URL_CONTAINS_LIST``, or when it is the acceptance page
    itself.
    """
    if path.startswith(tuple(app_settings.TERMS_EXCLUDE_URL_PREFIX_LIST)):
        return False

    if any(
        fragment in path for fragment in app_settings.TERMS_EXCLUDE_URL_CONTAINS_LIST
    ):
        return False

    if path in app_settings.TERMS_EXCLUDE_URL_LIST:
        return False

    return not path.startswith(app_settings.ACCEPT_TERMS_PATH)


def __getattr__(name: str) -> Any:
    """Keep ``ACCEPT_TERMS_PATH`` importable from this module.

    It was a module-level constant here before 3.0 and downstream code imported
    it from this location.  Resolving it through ``app_settings`` on access
    keeps that import working without freezing the setting at import time.
    """
    if name == "ACCEPT_TERMS_PATH":
        return app_settings.ACCEPT_TERMS_PATH
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
