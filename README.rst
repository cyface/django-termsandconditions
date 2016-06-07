===========================
Django Terms and Conditions
===========================

.. image:: https://badge.fury.io/py/django-termsandconditions.svg
    :target: http://badge.fury.io/py/django-termsandconditions
    :alt: PyPi Package Version

.. image:: https://travis-ci.org/cyface/django-termsandconditions.svg?branch=master
    :target: https://travis-ci.org/cyface/django-termsandconditions
    :alt: Travis Build Status

.. image:: https://coveralls.io/repos/cyface/django-termsandconditions/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/cyface/django-termsandconditions?branch=master
    :alt: Coveralls Code Coverage

.. image:: https://scrutinizer-ci.com/g/cyface/django-termsandconditions/badges/quality-score.png?b=master
    :target: https://scrutinizer-ci.com/g/cyface/django-termsandconditions/
    :alt: Scrutinizer Code Quality

.. image:: https://readthedocs.org/projects/django-termsandconditions/badge/?version=latest
    :target: http://django-termsandconditions.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

Django Terms and Conditions gives you an configurable way to send users to a T&C acceptance page before they
can access the site if you wish.

Contributors:

- Tim White (tim@cyface.com)
- Adibo (https://github.com/adibo)

.. contents:: Table of Contents

Features
========

This module is meant to be as quick to integrate as possible, and thus extensive customization will likely benefit from a fork. That said, a number of options are available. Currently, the app allows for

- terms-and-conditions versioning (via version_number)
- multiple terms-and-conditions allowed (via slug field)
- per-user terms-and-conditions acceptance
- middleware to take care of redirecting to proper terms-and-conditions acceptance page upon the version change
- multi-language support

Installation
============

From `pypi <https://pypi.python.org>`_::

    $ pip install django-termsandconditions

or::

    $ easy_install django-termsandconditions

or clone from `github <http://github.com>`_::

    $ git clone git://github.com/cyface/django-termsandconditions.git

and add django-termsandconditions to the ``PYTHONPATH``::

    $ export PYTHONPATH=$PYTHONPATH:$(pwd)/django-termsandconditions/

or::

    $ cd django-termsandconditions
    $ sudo python setup.py install

Demo App
========
The termsandconditions_demo app is included to quickly let you see how to get a working installation going.

The demo is built as a mobile app using `jQueryMobile <http://jquerymobile.com/>`_ loaded from the jQuery CDN.

Take a look at the ``requirements.txt`` file in the ``termsandconditions_demo`` directory for a quick way to use pip to install
all the needed dependencies::

    $ pip install -r requirements.txt

The ``settings_main.py``, and ``settings_local_template.py`` files have a working configuration you can crib from.

The templates in the ``termsandconditions/templates``, and ``termsandconditions_demo/templates`` directories
give you a good idea of the kinds of things you will need to do if you want to provide a custom interface.

Configuration
=============

Configuration is minimal for termsandconditions itself, A quick guide to a basic setup
is below, take a look at the demo app for more details.

Requirements
------------

The app needs ``django>=1.8.3,<1.10``.

Add INSTALLED_APPS
------------------

Add termsandconditions to installed applications::

    INSTALLED_APPS = (
        ...
        'termsandconditions',
    )

Add urls to urls.py
-------------------

In your urls.py, you need to pull in the termsandconditions and/or termsandconditions urls::

    # Terms and Conditions
    url(r'^terms/', include('termsandconditions.urls')),

Terms and Conditions
====================

You will need to set up a Terms and Conditions entry in the admin (or via direct DB load) for users to accept if
you want to use the T&C module.

The default Terms and Conditions entry has a slug of ``'site-terms'``.

If you don't create one, the first time a user is forced to accept the terms, it will create a default entry for you.

Terms and Conditions Versioning
-------------------------------
Note that the versions and dates of T&Cs are important. You can create a new version of a T&C with a future date,
and once that date is in the past, it will force users to accept that new version of the T&Cs.

Terms and Conditions Middleware
-------------------------------
You can force protection of your whole site by using the T&C middleware. Once activated, any attempt to access an
authenticated page will first check to see if the user has accepted the active T&Cs. This can be a performance impact,
so you can also use the _TermsAndConditionsDecorator to protect specific views, or the pipeline setup to only check on
account creation.

Here is the middleware configuration::

    MIDDLEWARE_CLASSES = (
        ...
        'termsandconditions.middleware.TermsAndConditionsRedirectMiddleware',

By default, some pages are excluded from the middleware, you can configure exclusions with these settings::

    ACCEPT_TERMS_PATH = '/terms/accept/'
    TERMS_EXCLUDE_URL_PREFIX_LIST = {'/admin/',})
    TERMS_EXCLUDE_URL_LIST = {'/', '/terms/required/', '/logout/', '/securetoo/'}

TERMS_EXCLUDE_URL_PREFIX_LIST is a list of 'starts with' strings to exclude, while TERMS_EXCLUDE_URL_LIST is a list of
explicit full paths to exclude.

Terms and Conditions View Decorator
-----------------------------------
You can protect only specific views with T&Cs using the @terms_required() decorator at the top of a function like this::

    from termsandconditions.decorators import terms_required

    @login_required
    @terms_required
    def terms_required_view(request):
        ...

Note that you can skip @login_required only if you are forcing auth on that view in some other way.

Requiring T&Cs for Anonymous Users is not supported.

Terms and Conditions Template Tag
---------------------------------

To facilitate support of terms changes without a direct redirection to the ``/terms/accept`` url, a template tag is
supplied for convenience. Thus, instead of using e.g. the ``TermsAndConditionsRedirectMiddleware`` one can use the
template tag. The template tag will take care that a proper modal is shown to the user informing a user that new terms
have been set and need to be accepted. To use the template tag, do the following. In your template (for example in
base.html), include the following lines::

    {% load terms_tags %}
    .... your template here ....

    {% show_terms_if_not_agreed %}

Alternatively use::

    {% load terms_tags %}
    .... your template here ....

    {% show_terms_if_not_agreed field='HTTP_REFERER' %}

if you want other than default ``TERMS_HTTP_PATH_FIELD`` to be used (this can also be controlled via settings, see below).
This will ensure that on every page using the template (that is on each page using base.html in this case), respective
T&C css and js are loaded to take care for handling the modal.

The modal will show the basic information about the new terms as well as a link to page which enables the user to
accept these terms. Please note that a user may wish not to accept terms and close the modal. In such a case, the
modal will be shown again as soon as another view with the template including the template tag is called.
This simple mechanism allows to nag users with new T&C while still allowing them to use the service, without instant
redirections.

The following configuration setting applies for the template tag::

    TERMS_HTTP_PATH_FIELD = 'PATH_INFO'

which defaults to ``PATH_INFO``. When needed (e.g. while using a separate AJAX view to take care for the modal) this can be changed to ``HTTP_REFERER``.

Terms and Conditions Pipeline
-----------------------------
You can force T&C acceptance when a new user account is created using the django-socialauth pipeline::

    SOCIAL_AUTH_PIPELINE = (
        'social_auth.backends.pipeline.social.social_auth_user',
        'social_auth.backends.pipeline.associate.associate_by_email',
        'social_auth.backends.pipeline.user.get_username',
        'social_auth.backends.pipeline.user.create_user',
        'social_auth.backends.pipeline.social.associate_user',
        'social_auth.backends.pipeline.social.load_extra_data',
        'social_auth.backends.pipeline.misc.save_status_to_session',
        'termsandconditions.pipeline.user_accept_terms',
    )

Note that the configuration above also prevents django-socialauth from updating profile data from the social backends
once a profile is created, due to::

    'social_auth.backends.pipeline.user.update_user_details'

...not being included in the pipeline. This is wise behavior when you are letting users update their own profile details.

This pipeline configuration will send users to the '/terms/accept' page right before sending them on to whatever you
have set SOCIAL_AUTH_NEW_USER_REDIRECT_URL to.  However, it will not, without the middleware or decorators described
above, check that the user has accepted the latest T&Cs before letting them continue on to viewing the site.

You can use the various T&C methods in concert depending on your needs.

Multi-Language Support
======================
In case you are in need of your ``termsandconditions`` objects to handle multiple languages, we recommend to use
``django-modeltranslation <https://github.com/deschler/django-modeltranslation>`` (or similar) module.
In case of django-modeltranslation the setup is rather straight forward, but needs several steps. Here they are.

1. Modify your ``settings.py``
------------------------------

In your ``settings.py`` file, you need to specify the ``LANGUAGES`` and set ``MIGRATION_MODULES`` to point to a local
migration directory for the ``termsandconditions`` module (the migration due to modeltranslation will live there)::

    LANGUAGES = (
        ('en', 'English'),
        ('pl', 'Polish'),
    )

    MIGRATION_MODULES = {
        # local path for migration for the termsandconditions
        'termsandconditions': 'your_app.migrations.migrations_termsandconditions',
    }

Don't forget to create the respective directory and the ``__init__.py`` file there!
Please note that ``migrations_termsandconditions`` directory name is used to avoid confusion with the T&C app name.

2. Make initial local migration
-------------------------------

As we switch to the local migration for the ``termsandconditions`` module, we need to execute initial migration
for the module (as a starting point). Thus::

    python manage.py makemigrations termsandconditions

The relevant initial migration file should now be in ``your_app/migrations/migrations_termsandconditions`` directory.
Now, just execute the migration::

    python manage.py migrate termsandconditions

3. Add translation
------------------

To translate terms-and-conditions model to other languages (as specified in ``settings.py``), create a ``translation.py``
file in your project, with the following content::

    from modeltranslation.translator import translator, TranslationOptions
    from termsandconditions.models import TermsAndConditions

    class TermsAndConditionsTranslationOptions(TranslationOptions):
        fields = ('name', 'text', 'info')
    translator.register(TermsAndConditions, TermsAndConditionsTranslationOptions)

This assumes you want to have 3 most relevant model fields translated.
After that you just need to make migrations again (to account for new fields due to modeltranslation)::

    python manage.py makemigrations termsandconditions

That's it. Your model is now ready to cover the translations! Just as hint we suggest to also include some
data migration in order to populate newly created, translated fields (i.e. ``name_en``, ``name_pl``, etc.) with
the initial data (e.g. by copying the content of the base field, i.e. ``name``, etc.)
