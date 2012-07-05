===========================
Django Terms and Conditions
===========================

Django Terms and Conditions gives you an out-of-the-box way to enable you to send users to a T&C acceptance page before they
can access the site if you wish.

.. contents:: Table of Contents

Features
========

This module is meant to be as quick to integrate as possible, and thus extensive customization will likely benefit from
a fork. That said, a number of options are available.

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

Add INSTALLED_APPS
------------------

Add termsandconditions to installed applications::

    INSTALLED_APPS = (
        ...
        'termsandconditions',
    )

Add urls to urls.py
--------------------

In your urls.py, you need to pull in the termsandconditions and/or termsandconditions urls::

    # Terms and Conditions
    url(r'^terms/', include('termsandconditions.urls')),

Terms and Conditions
=======================

You will need to set up a Terms and Conditions entry in the admin (or via direct DB load) for users to accept if
you want to use the T&C module.

The default Terms and Conditions entry has a slug of 'site-terms'.

If you don't create one, the first time a user is forced to accept the terms, it will create a default entry for you.

Terms and Conditions Versioning
-----------------------------------
Note that the versions and dates of T&Cs are important. You can create a new version of a T&C with a future date,
and once that date is in the past, it will force users to accept that new version of the T&Cs.

Terms and Conditions Middleware
-----------------------------------
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
--------------------------------------
You can protect only specific views with T&Cs using the @terms_required() decorator at the top of a function like this::

    from termsandconditions.decorators import terms_required

    @login_required
    @terms_required
    def terms_required_view(request):
        ...

Note that you can skip @login_required only if you are forcing auth on that view in some other way.

Requiring T&Cs for Anonymous Users is not supported.

Terms and Conditions Pipeline
-----------------------------------
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

