"""Django Views for the termsandconditions module"""

# pylint: disable=E1120

from django.contrib.auth.models import User
from forms import UserTermsAndConditionsModelForm
from models import TermsAndConditions, UserTermsAndConditions, DEFAULT_TERMS_SLUG
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, CreateView
import logging

LOGGER = logging.getLogger(name='termsandconditions')

class TermsView(DetailView):
    template_name = "termsandconditions/tc_view_terms.html"
    context_object_name = 'terms'

    def get_object(self, queryset=None):
        LOGGER.debug('termsandconditions.views.TermsView.get_object')

        slug = self.kwargs.get("slug", DEFAULT_TERMS_SLUG)

        if self.kwargs.get("version"):
            terms = TermsAndConditions.objects.get(slug=slug, version_number=self.kwargs.get("version"))
        else:
            terms = TermsAndConditions.get_active(slug)
        return terms

class AcceptView(CreateView):
    """
    Terms and Conditions Acceptance view

    url: /terms/accept

    template : termsandconditions/tc_accept_terms.html
    """

    model = UserTermsAndConditions
    form_class = UserTermsAndConditionsModelForm
    template_name = "termsandconditions/tc_accept_terms.html"

    def get_initial(self):
        LOGGER.debug('termsandconditions.views.AcceptView.get_object')

        slug = self.kwargs.get("slug", DEFAULT_TERMS_SLUG)

        if self.kwargs.get("version"):
            terms = TermsAndConditions.objects.get(slug=slug, version_number=self.kwargs.get("version"))
        else:
            terms = TermsAndConditions.get_active(slug)

        returnTo = self.request.GET.get('returnTo', '/')

        return {'terms': terms, 'returnTo': returnTo}

    def form_valid(self, form):
        if self.request.user.is_authenticated():
            form.instance.user = self.request.user
        else: #Get user out of saved pipeline from django-socialauth
            if self.request.session.has_key('partial_pipeline'):
                user_pk = self.request.session['partial_pipeline']['kwargs']['user']['pk']
                form.instance.user = User.objects.get(id=user_pk)
            else:
                return HttpResponseRedirect('/')
        form.instance.ip_address = self.request.META['REMOTE_ADDR']
        self.success_url = form.cleaned_data.get('returnTo', '/') or '/'
        return super(AcceptView, self).form_valid(form)