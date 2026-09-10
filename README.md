# Django Terms and Conditions

[![PyPi Package Version](https://badge.fury.io/py/django-termsandconditions.svg)](http://badge.fury.io/py/django-termsandconditions)
[![Actions Status](https://github.com/cyface/django-termsandconditions/workflows/Python%20package/badge.svg)](https://github.com/cyface/django-termsandconditions/actions)
[![codecov](https://codecov.io/gh/cyface/django-termsandconditions/branch/main/graph/badge.svg?token=RvtjZ2bngZ)](https://codecov.io/gh/cyface/django-termsandconditions)
[![docs](https://readthedocs.org/projects/django-termsandconditions/badge/)](https://django-termsandconditions.readthedocs.io/)

Django Terms and Conditions gives you a configurable way to send users to a
T&C acceptance page before they can access the site.

**Version 3.0 requires Python 3.12+ and Django 5.2+.** It removes
django-social-auth pipeline support and ships a migration — see
[CHANGELOG.md](CHANGELOG.md) before upgrading from 2.x.

Creator and maintainer: Tim White (<tim@cyface.com>)

Contributors: [Adibo](https://github.com/adibo), [Nathan Swain](https://github.com/swainn)

## Features

This module is meant to be quick to integrate, so extensive customization will
likely benefit from a fork. That said, a number of options are available:

- terms-and-conditions versioning (via `version_number`)
- multiple sets of terms-and-conditions (via the `slug` field)
- per-user acceptance, recorded with a timestamp and optionally an IP address
- middleware that redirects to the acceptance page when a version changes
- a decorator and a template tag for finer-grained control
- multi-language support

## Installation

```console
$ pip install django-termsandconditions
```

Add the app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "termsandconditions",
]
```

And include the URLs:

```python
path("terms/", include("termsandconditions.urls")),
```

Then run `python manage.py migrate` and create a `TermsAndConditions` entry in
the admin for users to accept.

## Demo app

The `termsandconditions_demo` project shows a working installation. It is plain
Django with no front-end dependencies.

```console
$ uv sync
$ uv run python manage.py migrate
$ uv run python manage.py createsuperuser
$ uv run python manage.py runserver
```

`termsandconditions_demo/settings.py` has a working configuration to crib from,
and the templates in `termsandconditions/templates/` and
`termsandconditions_demo/templates/` show what a custom interface needs.

## Terms and Conditions

### Versioning

The version and date of each T&C matter. Create a new version with a future
`date_active`, and once that date passes users will be asked to accept it.

### Default URLs

Prefixed by wherever you included the URLs (e.g. `/terms/accept/`):

| URL | Description |
| --- | --- |
| `/` | List all terms that have not been accepted |
| `/accept/` | List all unaccepted terms, with accept links |
| `/accept/<slug>/` | Accept the latest version of a specific terms |
| `/accept/<slug>/<version>/` | Accept a specific version |
| `/active/` | List all active terms |
| `/email/` | Email all unaccepted terms |
| `/email/<slug>/<version>/` | Email a specific version |
| `/view/<slug>/` | View the latest version of a specific terms |
| `/view/<slug>/<version>/` | View a specific version |
| `/print/<slug>/<version>/` | Printable view of a specific version |

Requesting a slug that does not exist renders an empty state; requesting a
*version* that does not exist returns a 404.

### Middleware

Protect the whole site with the middleware. Once active, any attempt to reach
an authenticated page first checks whether the user has accepted the active
T&Cs. That has a performance cost, so you can instead use the decorator to
protect specific views.

```python
MIDDLEWARE = [
    ...
    "termsandconditions.middleware.TermsAndConditionsRedirectMiddleware",
]
```

Some paths are excluded by default. Configure exclusions with:

```python
ACCEPT_TERMS_PATH = "/terms/accept/"
TERMS_EXCLUDE_URL_PREFIX_LIST = {"/admin", "/terms"}
TERMS_EXCLUDE_URL_LIST = {"/", "/termsrequired/", "/logout/", "/securetoo/"}
TERMS_EXCLUDE_URL_CONTAINS_LIST = set()
```

`TERMS_EXCLUDE_URL_PREFIX_LIST` is a list of "starts with" strings;
`TERMS_EXCLUDE_URL_LIST` is a list of exact paths; and
`TERMS_EXCLUDE_URL_CONTAINS_LIST` is a list of fragments — useful for i18n,
where a language code can be prepended to your URLs.

You can also exclude users holding a permission you define yourself:

```python
TERMS_EXCLUDE_USERS_WITH_PERM = "MyModel.can_skip_terms"
```

This is useful for continuous login integration tests, or to exempt specific
users. Superusers are *not* excluded by this, because Django's `has_perm()`
returns `True` for any permission check on a superuser. To exclude them:

```python
TERMS_EXCLUDE_SUPERUSERS = True
```

### View decorator

```python
from termsandconditions.decorators import terms_required

@login_required
@terms_required
def terms_required_view(request):
    ...
```

You can skip `@login_required` only if the view is authenticated some other
way. Requiring T&Cs for anonymous users is not supported.

### Template tag

Instead of redirecting, show a modal and let users keep browsing:

```django
{% load terms_tags %}
{% show_terms_if_not_agreed %}
```

The modal links to the acceptance page. A user may dismiss it, in which case it
reappears on the next page that includes the tag. This nags users about new
T&Cs without interrupting them.

Pass `field` to read the current path from a different `request.META` key —
useful when a separate AJAX view renders the modal:

```django
{% show_terms_if_not_agreed field='HTTP_REFERER' %}
```

The default comes from `TERMS_HTTP_PATH_FIELD` (`PATH_INFO`).

### Rendering terms that contain template tags

If your terms text includes template syntax (e.g. `{% url 'your-url' %}`),
render it with the `as_template` filter:

```django
{% load terms_tags %}
{% include terms.text|as_template %}
```

You will need to adapt the default templates, which use `terms` as a template
variable.

### Base template

Most templates extend `base.html`. Point `TERMS_BASE_TEMPLATE` at a different
one:

```python
TERMS_BASE_TEMPLATE = "page.html"
```

A bare minimum base template:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>[My Title]</title>
    {% block styles %}{% endblock %}
  </head>
  <body>
    <main>
      <h2>{% block title %}{% endblock %}</h2>
      {% block content %}{% endblock %}
    </main>
  </body>
</html>
```

### Rich-text editing in the admin

The terms `text` and `info` fields are plain textareas by default and rendered
with `|safe`, so they can hold HTML. To edit them as rich text, install any
editor that provides a Django form widget and point this setting at it:

```python
# pip install django-ckeditor-5
TERMS_ADMIN_TEXT_WIDGET = "django_ckeditor_5.widgets.CKEditor5Widget"
```

```python
# pip install django-tinymce
TERMS_ADMIN_TEXT_WIDGET = "tinymce.widgets.TinyMCE"
```

django-termsandconditions does not depend on either — you choose the editor and
its version. Leave the setting unset to keep Django's default textarea.

Note that this field is rendered unescaped, so only trust it to staff you would
trust with raw HTML on your site.

### Useful methods

- `TermsAndConditions.get_active_terms_list()` — every active terms, accepted or not
- `TermsAndConditions.get_active_terms_not_agreed_to(user)` — terms `user` has not accepted
- `TermsAndConditions.get_active(slug)` — the active terms for `slug`

### Caching

Terms and their acceptance are cached to keep the middleware cheap:

```python
TERMS_CACHE_SECONDS = 30
```

Seconds to cache (default 30). Set to 0 to disable caching.

### Pruning old acceptance records

```console
$ python manage.py remove_old_version_acceptance
```

Deletes acceptance records for every superseded version, keeping only the
active one for each slug.

## Settings reference

Every setting is optional and read at access time, so `override_settings` works
in tests. `termsandconditions.conf.DEFAULTS` is the canonical list.

| Setting | Default | Description |
| --- | --- | --- |
| `ACCEPT_TERMS_PATH` | `"/terms/accept/"` | Where users are sent to accept |
| `DEFAULT_TERMS_SLUG` | `"site-terms"` | Slug used when none is given |
| `TERMS_ADMIN_TEXT_WIDGET` | `None` | Dotted path to a widget for `text`/`info` in the admin |
| `TERMS_BASE_TEMPLATE` | `"base.html"` | Template the shipped templates extend |
| `TERMS_CACHE_SECONDS` | `30` | Cache lifetime; 0 disables |
| `TERMS_EXCLUDE_SUPERUSERS` | `False` | Skip the check for superusers |
| `TERMS_EXCLUDE_USERS_WITH_PERM` | `None` | Skip the check for holders of this permission |
| `TERMS_EXCLUDE_URL_CONTAINS_LIST` | `frozenset()` | Path fragments to skip |
| `TERMS_EXCLUDE_URL_LIST` | see `conf.py` | Exact paths to skip |
| `TERMS_EXCLUDE_URL_PREFIX_LIST` | `{"/admin", "/terms"}` | Path prefixes to skip |
| `TERMS_HTTP_PATH_FIELD` | `"PATH_INFO"` | `request.META` key the template tag reads |
| `TERMS_IP_HEADER_NAME` | `"REMOTE_ADDR"` | `request.META` key holding the client IP |
| `TERMS_RETURNTO_PARAM` | `"returnTo"` | Query parameter for the redirect target |
| `TERMS_STORE_IP_ADDRESS` | `True` | Record the accepting user's IP |

Behind a proxy, set `TERMS_IP_HEADER_NAME` to `"HTTP_X_FORWARDED_FOR"` (or
whichever header your proxy sets). Only the first address in the chain is
stored.

## Multi-language support

To translate the terms themselves, use
[django-modeltranslation](https://github.com/deschler/django-modeltranslation)
or similar. With django-modeltranslation the setup is:

### 1. Modify your settings

Specify `LANGUAGES` and point `MIGRATION_MODULES` at a local migration
directory for this app, where the modeltranslation migration will live:

```python
LANGUAGES = (
    ("en", "English"),
    ("pl", "Polish"),
)

MIGRATION_MODULES = {
    "termsandconditions": "your_app.migrations.migrations_termsandconditions",
}
```

Create that directory with an `__init__.py`. The name
`migrations_termsandconditions` avoids confusion with the app name.

Add `modeltranslation` to `INSTALLED_APPS`, along with the module containing
your `translation.py`.

### 2. Make the initial local migration

```console
$ python manage.py makemigrations termsandconditions
$ python manage.py migrate termsandconditions
```

### 3. Add the translation options

Create a `translation.py` in your project:

```python
from modeltranslation.translator import TranslationOptions, translator

from termsandconditions.models import TermsAndConditions


class TermsAndConditionsTranslationOptions(TranslationOptions):
    fields = ("name", "text", "info")


translator.register(TermsAndConditions, TermsAndConditionsTranslationOptions)
```

Then make and run migrations again to add the translated fields. Consider a
data migration to populate `name_en`, `name_pl` and so on from the base fields.

### 4. Exclude `/terms/` from the middleware

With internationalized URLs, add this to prevent redirect loops with
language-code-prefixed URLs (e.g. `/en/terms/`):

```python
TERMS_EXCLUDE_URL_CONTAINS_LIST = {"/terms/", "/i18n/setlang/"}
```

## Contributing

```console
$ uv sync
$ uv run ruff check .
$ uv run ruff format .
$ uv run coverage run manage.py test
```

CI runs against Python 3.12–3.14 with Django 5.2 LTS and 6.1.

## License

BSD-3-Clause. See [LICENSE.txt](LICENSE.txt).
