"""Settings for the termsandconditions app, with their defaults.

Every setting is read from ``django.conf.settings`` at *access* time rather
than at import time.  That keeps ``override_settings`` working in downstream
test suites and means a project may define these after the app is imported.
"""

from typing import Any

from django.conf import settings

#: Every setting this app understands, mapped to the value used when a project
#: does not define it.  This dict doubles as the canonical list of settings.
DEFAULTS: dict[str, Any] = {
    # Dotted path to a form widget for the terms `text` and `info` fields in
    # the admin, e.g. "django_ckeditor_5.widgets.CKEditor5Widget". None leaves
    # Django's default Textarea in place.
    "TERMS_ADMIN_TEXT_WIDGET": None,
    # Where users are sent to accept outstanding terms.
    "ACCEPT_TERMS_PATH": "/terms/accept/",
    # Slug used when a view or helper is not given an explicit one.
    "DEFAULT_TERMS_SLUG": "site-terms",
    # Template the shipped templates extend.
    "TERMS_BASE_TEMPLATE": "base.html",
    # Seconds to cache active terms and per-user acceptance. 0 disables caching.
    "TERMS_CACHE_SECONDS": 30,
    # Skip the check for superusers.
    "TERMS_EXCLUDE_SUPERUSERS": False,
    # Skip the check for users holding this permission (superusers excepted).
    "TERMS_EXCLUDE_USERS_WITH_PERM": None,
    # Paths the middleware leaves alone.  Only the prefixes this app owns are
    # excluded by default; which of a project's own URLs need to stay reachable
    # is a project decision, and the wrong guess here would gate a path the
    # user needs (their logout view, say) behind terms they cannot leave.
    "TERMS_EXCLUDE_URL_CONTAINS_LIST": frozenset(),
    "TERMS_EXCLUDE_URL_LIST": frozenset({"/"}),
    "TERMS_EXCLUDE_URL_PREFIX_LIST": frozenset({"/admin", "/terms"}),
    # ``request.META`` key the template tag reads the current path from.
    "TERMS_HTTP_PATH_FIELD": "PATH_INFO",
    # ``request.META`` key holding the client IP. Behind a proxy this is
    # usually "HTTP_X_FORWARDED_FOR".
    "TERMS_IP_HEADER_NAME": "REMOTE_ADDR",
    # Query parameter carrying the post-acceptance redirect target.
    "TERMS_RETURNTO_PARAM": "returnTo",
    # Record the accepting user's IP address alongside the acceptance.
    "TERMS_STORE_IP_ADDRESS": True,
}

#: Settings holding a collection of paths.  Writing one as a bare string is an
#: easy mistake — ``"/admin"`` rather than ``{"/admin"}`` — and iterating a
#: string yields single characters.  Every path starts with "/", so the
#: middleware would match every request and switch the terms gate off site
#: wide.  A string is read as the single path it names instead.
PATH_COLLECTION_SETTINGS = frozenset(
    {
        "TERMS_EXCLUDE_URL_CONTAINS_LIST",
        "TERMS_EXCLUDE_URL_LIST",
        "TERMS_EXCLUDE_URL_PREFIX_LIST",
    }
)


class AppSettings:
    """Attribute access over ``DEFAULTS``, deferring to ``django.conf.settings``."""

    def __getattr__(self, name: str) -> Any:
        try:
            default = DEFAULTS[name]
        except KeyError:
            raise AttributeError(
                f"{name!r} is not a django-termsandconditions setting"
            ) from None

        value = getattr(settings, name, default)
        if name in PATH_COLLECTION_SETTINGS and isinstance(value, str):
            return frozenset({value})
        return value

    def __dir__(self) -> list[str]:
        return sorted(DEFAULTS)


app_settings = AppSettings()
