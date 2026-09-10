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
  `ACCEPT_TERMS_PATH` are still importable from `termsandconditions.middleware`
  — the latter through a module `__getattr__`, so it is resolved on access
  rather than frozen at import.
- **`TermsAndConditionsRedirectMiddleware` is a plain callable middleware**, no
  longer built on `MiddlewareMixin`. It declares `sync_capable` and
  `async_capable`, so an ASGI stack still runs the middleware below it natively.
  No configuration change is needed.
- **`TERMS_EXCLUDE_URL_LIST` now defaults to `{"/"}`.** It used to ship
  `{"/", "/termsrequired/", "/logout/", "/securetoo/"}` — two paths that exist
  only in this repo's demo project, and a logout URL that is not where
  `django.contrib.auth.urls` actually lands. **If you relied on that default to
  keep your logout page reachable, add your real logout path to the setting**,
  or a user with outstanding terms will not be able to sign out.
- **`EmailTermsForm.terms` is a `ModelMultipleChoiceField`.** It was a
  single-valued `ModelChoiceField` that the view fed a list, so the form could
  not validate anything a browser submitted (see *Fixed*). The emailed body
  template now iterates `terms_list` rather than rendering a single `terms`.
- **`not_agreed_terms_cache_key()` takes a user primary key and the active
  terms ids**, not a username. Cached acceptance keys from 2.x are simply
  missed and rebuilt.
- **Accepting a version that is not in force is a 404.**
  `/terms/accept/<slug>/<version>/` used to render an Accept button for any
  version named, including superseded ones and ones dated in the future.
  Viewing, printing and emailing any version are unchanged — only accepting is
  narrowed to what is currently active.
- **Requesting an unknown terms version now returns 404** instead of raising
  `TermsAndConditions.DoesNotExist` (a 500). An unknown *slug* still renders
  the "No terms defined." page.
- **`default_app_config` removed** from `termsandconditions/__init__.py`; it
  has been a no-op since Django 3.2.
- **The demo app no longer uses jQuery Mobile.** Its templates are plain
  semantic HTML with a small local stylesheet and no CDN requests.
- **The demo project enables `CsrfViewMiddleware`.** Its middleware list has
  never had it, while every template renders `{% csrf_token %}` and sign-out is
  now a POST — so the token was validated by nothing. `settings.py` is the file
  the README points readers at to crib from, so it now also lists middleware in
  the order Django documents.

### Added

- `TERMS_ADMIN_TEXT_WIDGET` — dotted path to a form widget used for the terms
  `text` and `info` fields in the admin, so you can plug in a rich-text editor
  (django-ckeditor-5, django-tinymce, …) without this package depending on one.
- `termsandconditions.conf.DEFAULTS` documents every setting and its default in
  one place.
- The admin gained search, filtering, date drill-down and `list_select_related`
  on both models.
- `remove_old_version_acceptance` now reports how many records it deleted.
- Test suite grew from 31 to 112 tests and moved to a top-level `tests/` package
  (so it is no longer shipped in the wheel). Statement and branch coverage of
  `termsandconditions/` is 100%.

### Fixed

- **A version dated in the future can no longer be accepted early.** The accept
  view recorded any `TermsAndConditions` primary key the client posted. Posting
  the id of a version whose `date_active` had not arrived created an acceptance
  row, and when that version went live the user was never shown it — the
  outstanding-terms query excluded it as already accepted, and the middleware
  never redirected. Primary keys are sequential integers, so this took no more
  than guessing one. The view now validates through
  `UserTermsAndConditionsForm`, whose `terms` field accepts only the terms
  currently in force; a superseded version is refused for the same reason.
- **The accept page no longer returns a 500 for an unknown slug.**
  `/terms/accept/<unknown-slug>/` resolved to `[None]` and the template built a
  print link from it, raising `NoReverseMatch`. It renders the "No terms
  defined." empty state, as the view page already did.
- **The email form can be submitted.** `EmailTermsView` put a list into the
  initial data of a single-valued `ModelChoiceField`, so the hidden input
  rendered a Python repr (`[<TermsAndConditions: site-terms-1.00>]`, or
  `<QuerySet [...]>` on `/terms/email/`) and every submission a browser made
  failed validation with "Invalid Email Address." No terms email could be sent
  at all. The heading and subject line were built from the same mismatch and
  showed the repr too.
- **An unknown slug no longer logs at ERROR or re-queries.** The slug is client
  input on the view and accept URLs, so a loop over made-up ones filled the log
  — and any handler behind it, `mail_admins` included — and hit the database
  every time. It logs at DEBUG, and the miss is cached for
  `TERMS_CACHE_SECONDS`.
- **A path-exclusion setting written as a string no longer disables the terms
  check.** `TERMS_EXCLUDE_URL_PREFIX_LIST = "/admin"` was iterated character by
  character; every path starts with `/`, so every request was excluded and the
  gate was off site-wide, silently. A string is now read as the one path it
  names. The same applies to `TERMS_EXCLUDE_URL_LIST` and
  `TERMS_EXCLUDE_URL_CONTAINS_LIST`.
- **`terms_required` keeps the querystring.** It redirected with `request.path`,
  so a user sent from `/report/?range=90d` landed back on `/report/` after
  accepting. It uses `request.get_full_path()`, matching the middleware.
- **The accept and email pages are `never_cache`.** Every other route in the
  URLconf already was. Both render per-user content and a CSRF token, and only
  escaped a shared cache because `SessionMiddleware` happens to set
  `Vary: Cookie` — a property of unrelated middleware, not of the view.
- **A terms change now invalidates every user's cached acceptance list.**
  The handler swept the users named in the acceptance table, which missed
  anyone who had accepted nothing — exactly the users with terms outstanding.
  Their list stood until it expired, so for up to `TERMS_CACHE_SECONDS` after a
  new version went live they were still being asked for the old one. The cache
  key now carries the ids of the terms in force, so a change retires every
  entry at once. That also drops the sweep itself: invalidation no longer scans
  the acceptance table and issues one delete per user on every terms save.
- **Invalidating the acceptance cache no longer fetches each user.** The
  `post_save`/`post_delete` handler dereferenced `instance.user` to build the
  cache key, costing one `auth_user` SELECT per row — in exactly the bulk path
  `remove_old_version_acceptance` uses. It reads `instance.user_id`, which also
  keeps usernames containing spaces or non-ASCII out of the cache key, where
  memcached rejects them.
- **The outstanding-terms lookup no longer fails open.** It caught `TypeError`
  and `UserTermsAndConditions.DoesNotExist` and returned `[]` on either, which
  reads as "this user has accepted everything" and quietly waves them past the
  gate. Neither exception was reachable — `.filter()` does not raise
  `DoesNotExist`, and a cache returning a non-queryset raises `AttributeError`,
  which was never caught. The handler is gone, so an unexpected error surfaces
  instead of silently disabling the terms check.
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
