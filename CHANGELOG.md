# Changelog

## 3.0.0 (unreleased)

A major release. Social-auth pipeline support is gone, the app has been brought
up to current Django and Python practice, and a migration ships with it.

### Breaking changes

- **Removed django-social-auth pipeline support.**
  - `termsandconditions.pipeline` is deleted. `user_accept_terms` no longer
    exists; drop `termsandconditions.pipeline.user_accept_terms` from any
    `SOCIAL_AUTH_PIPELINE` setting.
  - `redirect_to_terms_accept` moved to `termsandconditions.utils`. Its `slug`
    argument now defaults to `None` rather than the string `"default"`.
  - `AcceptTermsView` no longer reads a partially-created user out of a
    `partial_pipeline` session key. Anonymous POSTs are redirected to `/`.
- **Requires Python 3.12+ and Django 5.2+.** Tested against Python 3.12, 3.13
  and 3.14 with Django 5.2 LTS and 6.1.
- **New migration `0005_modernize_constraints_and_pks`.** It replaces
  `Meta.unique_together` with a named `UniqueConstraint`, makes the terms slug
  default a callable, and widens both primary keys to `BigAutoField`. The
  primary key change rewrites the `id` column on both tables — run it in a
  maintenance window if `usertermsandconditions` is large, or subclass the
  AppConfig with `default_auto_field = "django.db.models.AutoField"` to keep
  the old width.
- **`UserTermsAndConditionsModelForm` renamed to `UserTermsAndConditionsForm`.**
  It was never a `ModelForm`. `AcceptTermsView` is now a `FormView` rather than
  a `CreateView`.
- **Settings are read at access time**, through `termsandconditions.conf.app_settings`.
  `DEFAULT_TERMS_SLUG` and the other module-level constants in `models.py`,
  `middleware.py` and `templatetags/terms_tags.py` are gone. This makes
  `override_settings` work in downstream tests. `is_path_protected` and
  `ACCEPT_TERMS_PATH` are still importable from `termsandconditions.middleware`.
- **`TermsAndConditionsRedirectMiddleware` is a plain callable middleware**, no
  longer built on `MiddlewareMixin`. No configuration change is needed.
- **Requesting an unknown terms version now returns 404** instead of raising
  `TermsAndConditions.DoesNotExist` (a 500). An unknown *slug* still renders
  the "No terms defined." page.
- **`default_app_config` removed** from `termsandconditions/__init__.py`; it
  has been a no-op since Django 3.2.
- **The demo app no longer uses jQuery Mobile.** Its templates are plain
  semantic HTML with a small local stylesheet and no CDN requests.

### Added

- `TERMS_ADMIN_TEXT_WIDGET` — dotted path to a form widget used for the terms
  `text` and `info` fields in the admin, so you can plug in a rich-text editor
  (django-ckeditor-5, django-tinymce, …) without this package depending on one.
- `termsandconditions.conf.DEFAULTS` documents every setting and its default in
  one place.
- The admin gained search, filtering, date drill-down and `list_select_related`
  on both models.
- `remove_old_version_acceptance` now reports how many records it deleted.
- Test suite grew from 31 to 81 tests and moved to a top-level `tests/` package
  (so it is no longer shipped in the wheel).

### Fixed

- **Accepting terms no longer poisons an enclosing transaction.** Each
  acceptance is written inside a savepoint, so a duplicate can no longer break
  the request under `ATOMIC_REQUESTS`.
- **A missing IP header no longer raises `TypeError`.** `TERMS_IP_HEADER_NAME`
  pointing at an absent header now stores `NULL` instead of crashing the accept
  view.
- **`TERMS_RETURNTO_PARAM` is now honoured when reading the redirect target.**
  Previously it was only used when *writing* the querystring, so setting it to
  anything other than `returnTo` silently broke the post-acceptance redirect.
- **Cache invalidation no longer issues one query per acceptance row.** Saving
  a `TermsAndConditions` used to trigger an N+1 over the whole
  `usertermsandconditions` table; it is now a single distinct query plus one
  `delete_many`.
- **Non-numeric terms ids posted to the accept view** are ignored rather than
  raising `ValueError`.
- **The demo's `robots.txt` and `favicon.ico` routes worked at all.** Both
  passed keyword arguments the views do not accept and raised on request.
- **The demo's sign-out link is a POST form**, as Django 5.0+ requires.
- The dead `if terms_list is QuerySet:` branch in the accept form is gone — it
  compared an object against a class and was never true.
- `django.db.backends.postgresql_psycopg2` (removed in Django 3.0) replaced
  with `django.db.backends.postgresql` in the demo settings.
- Package metadata declared the MIT license; the project is BSD-3-Clause.

### Tooling

- `black` dropped in favour of `ruff format`. Ruff's lint set widened to
  include isort, pyupgrade, bugbear, logging, pathlib, simplify and more.
- CI runs a separate lint job (`ruff check`, `ruff format --check`, and
  `makemigrations --check`) and tests the full Python × Django matrix with
  deprecation warnings enabled (`-Wa`).

## 2.1.1 and earlier

See the [release history on GitHub](https://github.com/cyface/django-termsandconditions/releases).
