"""Django Views for the termsandconditions module"""
from django.shortcuts import render_to_response
from django.db import IntegrityError
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from forms import TermsAndConditionsForm
from models import TermsAndConditions, UserTermsAndConditions, DEFAULT_TERMS_SLUG
from decorators import terms_required
from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView
import datetime
import logging

LOGGER = logging.getLogger(name='termsandconditions')

class ViewTerms(TemplateView):
    """
    Terms and Conditions View view

    url: /terms/, /terms/view/

    template : termsandconditions/tc_view_terms.html
    """

    LOGGER.debug('termsandconditions.views.ViewTerms')

    template_name = 'termsandconditions/tc_view_terms.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ViewTerms, self).get_context_data(**kwargs)
        try:
            slug = 'site-terms'
            form = TermsAndConditionsForm(slug=slug)
            context['form'] = form
        except TermsAndConditions.DoesNotExist:
            raise Http404

        return context

    def get_urls(self):
        from django.conf.urls import patterns, url

        urlpatterns = patterns('',
            url(r'^$', ViewTerms.as_view(), name='terms_index'),
            url(r'^view/$', ViewTerms.as_view(), name='terms_view'),
        )
        return urlpatterns

    urls = property(get_urls)


@never_cache
def accept_view(request, slug='default'):
    """
    Terms and Conditions Acceptance view

    url: /terms/accept

    template : termsandconditions/tc_accept_terms.html
    """

    LOGGER.debug('termsandconditions.views.accept_view')

    if request.method == 'POST': # If the form has been submitted...
        if request.user.is_authenticated():
            user = request.user
        else: #Get user out of saved pipeline from django-socialauth
            if request.session.has_key('partial_pipeline'):
                user_pk = request.session['partial_pipeline']['kwargs']['user']['pk']
                user = User.objects.get(id=user_pk)
            else:
                return HttpResponseRedirect('/')

        form = TermsAndConditionsForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            form.clean()
            try:
                terms = TermsAndConditions.objects.get(slug=form.cleaned_data['slug'], version_number=form.cleaned_data['version_number'])
                userTerms = UserTermsAndConditions()
                userTerms.terms = terms
                userTerms.user = user
                userTerms.date_accepted = datetime.datetime.now()
                userTerms.ip_address = request.META['REMOTE_ADDR']
                userTerms.save()
                if form.cleaned_data.has_key('returnTo'):
                    return HttpResponseRedirect(form.cleaned_data['returnTo'])
                else:
                    return HttpResponseRedirect('/')
            except IntegrityError as err:
                LOGGER.error('Integrity Error Saving Terms and Conditions: ' + str(err))
    else:
        if slug == 'default':
            slug = DEFAULT_TERMS_SLUG
        form = TermsAndConditionsForm(slug=slug) # Pass in User to Pre-Populate with Current Values
        if request.GET.has_key('returnTo'):
            form.initial['returnTo'] = request.GET['returnTo']

    response_data = {'form': form, }

    return render_to_response('termsandconditions/tc_accept_terms.html', response_data,
        context_instance=RequestContext(request))


@login_required
@terms_required
@never_cache
def terms_required_view(request):
    """
    Terms Required testing page.

    url: /terms_required

    template : termsandconditions/terms_required.html
    """

    LOGGER.debug('termsandconditions.views.terms_required_view')

    response_data = {}

    return render_to_response('termsandconditions/tc_terms_required.html', response_data, context_instance=RequestContext(request))