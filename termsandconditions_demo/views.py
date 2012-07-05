"""Django Views for the termsandconditions-demo module"""
from django.shortcuts import render_to_response
from django.views.decorators.cache import never_cache
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(name='termsandconditions')

@never_cache
def index(request):
    """
    Main site page page.

    url: /
    
    template : index.html
    """

    logger.debug('termsandconditions_demo.views.index')

    response_data = {}

    return render_to_response('index.html', response_data, context_instance=RequestContext(request))

@login_required
@never_cache
def secure_view(request):
    """
    Secure testing page.

    url: /secure

    template : secure.html
    """

    logger.debug('termsandconditions_demo.views.secure_view')

    response_data = {}

    return render_to_response('secure.html', response_data, context_instance=RequestContext(request))

@login_required
@never_cache
def secure_view_too(request):
    """
    Secure testing page.

    url: /securetoo

    template : securetoo.html
    """

    logger.debug('termsandconditions_demo.views.secure_view_too')

    response_data = {}

    return render_to_response('securetoo.html', response_data, context_instance=RequestContext(request))