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
    # Paths the middleware leaves alone.
    "TERMS_EXCLUDE_URL_CONTAINS_LIST": frozenset(),
    "TERMS_EXCLUDE_URL_LIST": frozenset(
        {"/", "/termsrequired/", "/logout/", "/securetoo/"}
    ),
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


class AppSettings:
    """Attribute access over ``DEFAULTS``, deferring to ``django.conf.settings``."""

    def __getattr__(self, name: str) -> Any:
        try:
            default = DEFAULTS[name]
        except KeyError:
            raise AttributeError(
                f"{name!r} is not a django-termsandconditions setting"
            ) from None
        return getattr(settings, name, default)

    def __dir__(self) -> list[str]:
        return sorted(DEFAULTS)


app_settings = AppSettings()
