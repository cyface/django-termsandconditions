"""Django Views for the termsandconditions module"""

# pylint: disable=E1120,R0901,R0904
from django import VERSION as DJANGO_VERSION
from django.contrib.auth.models import User
from django.db import IntegrityError

from .forms import UserTermsAndConditionsModelForm, EmailTermsForm
from .models import TermsAndConditions, UserTermsAndConditions
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, CreateView, FormView
from django.template.loader import get_template
from django.core.mail import send_mail
import logging
from smtplib import SMTPException

LOGGER = logging.getLogger(name='termsandconditions')
DEFAULT_TERMS_BASE_TEMPLATE = 'base.html'


class GetTermsViewMixin(object):
    """Checks URL parameters for slug and/or version to pull the right TermsAndConditions object"""

    def get_terms(self, kwargs):
        """Checks URL parameters for slug and/or version to pull the right TermsAndConditions object"""

        slug = kwargs.get("slug")
        version = kwargs.get("version")

        if slug and version:
            terms = [TermsAndConditions.objects.filter(slug=slug, version_number=version).latest('date_active')]
        elif slug:
            terms = [TermsAndConditions.get_active(slug)]
        else:
            # Return a list of not agreed to terms for the current user for the list view
            terms = TermsAndConditions.get_active_terms_not_agreed_to(self.request.user)
        return terms


class TermsView(DetailView, GetTermsViewMixin):
    """
    View Terms and Conditions View

    url: /terms/view
    """
    template_name = "termsandconditions/tc_view_terms.html"
    context_object_name = 'terms_list'

    def get_context_data(self, **kwargs):
        """Pass additional context data"""
        context = super(TermsView, self).get_context_data(**kwargs)
        context['terms_base_template'] = getattr(settings, 'TERMS_BASE_TEMPLATE', DEFAULT_TERMS_BASE_TEMPLATE)
        return context

    def get_object(self, queryset=None):
        """Override of DetailView method, queries for which T&C to return"""
        LOGGER.debug('termsandconditions.views.TermsView.get_object')
        return self.get_terms(self.kwargs)


class AcceptTermsView(CreateView, GetTermsViewMixin):
    """
    Terms and Conditions Acceptance view

    url: /terms/accept
    """

    model = UserTermsAndConditions
    form_class = UserTermsAndConditionsModelForm
    template_name = "termsandconditions/tc_accept_terms.html"

    def get_context_data(self, **kwargs):
        """Pass additional context data"""
        context = super(AcceptTermsView, self).get_context_data(**kwargs)
        context['terms_base_template'] = getattr(settings, 'TERMS_BASE_TEMPLATE', DEFAULT_TERMS_BASE_TEMPLATE)
        return context

    def get_initial(self):
        """Override of CreateView method, queries for which T&C to accept and catches returnTo from URL"""
        LOGGER.debug('termsandconditions.views.AcceptTermsView.get_initial')

        terms = self.get_terms(self.kwargs)
        return_to = self.request.GET.get('returnTo', '/')

        return {'terms': terms, 'returnTo': return_to}

    def post(self, request, *args, **kwargs):
        """
        Handles POST request.
        """
        return_url = request.POST.get('returnTo', '/')
        terms_ids = request.POST.getlist('terms')

        if not terms_ids:  # pragma: nocover
            return HttpResponseRedirect(return_url)

        if DJANGO_VERSION <= (2, 0, 0):
            user_authenticated = request.user.is_authenticated()
        else:
            user_authenticated = request.user.is_authenticated

        if user_authenticated:
            user = request.user
        else:
            # Get user out of saved pipeline from django-socialauth
            if 'partial_pipeline' in request.session:
                user_pk = request.session['partial_pipeline']['kwargs']['user']['pk']
                user = User.objects.get(id=user_pk)
            else:
                return HttpResponseRedirect('/')

        store_ip_address = getattr(settings, 'TERMS_STORE_IP_ADDRESS', True)
        if store_ip_address:
            ip_address = request.META['REMOTE_ADDR']
        else:
            ip_address = ""

        for terms_id in terms_ids:
            try:
                new_user_terms = UserTermsAndConditions(
                    user=user,
                    terms=TermsAndConditions.objects.get(pk=int(terms_id)),
                    ip_address=ip_address
                )
                new_user_terms.save()
            except IntegrityError:  # pragma: nocover
                pass

        return HttpResponseRedirect(return_url)


class EmailTermsView(FormView, GetTermsViewMixin):
    """
    Email Terms and Conditions View

    url: /terms/email
    """
    template_name = "termsandconditions/tc_email_terms_form.html"

    form_class = EmailTermsForm

    def get_context_data(self, **kwargs):
        """Pass additional context data"""
        context = super(EmailTermsView, self).get_context_data(**kwargs)
        context['terms_base_template'] = getattr(settings, 'TERMS_BASE_TEMPLATE', DEFAULT_TERMS_BASE_TEMPLATE)
        return context

    def get_initial(self):
        """Override of CreateView method, queries for which T&C send, catches returnTo from URL"""
        LOGGER.debug('termsandconditions.views.EmailTermsView.get_initial')

        terms = self.get_terms(self.kwargs)

        return_to = self.request.GET.get('returnTo', '/')

        return {'terms': terms, 'returnTo': return_to}

    def form_valid(self, form):
        """Override of CreateView method, sends the email."""
        LOGGER.debug('termsandconditions.views.EmailTermsView.form_valid')

        template = get_template("termsandconditions/tc_email_terms.html")
        template_rendered = template.render({"terms": form.cleaned_data.get('terms')})

        LOGGER.debug("Email Terms Body:")
        LOGGER.debug(template_rendered)

        try:
            send_mail(form.cleaned_data.get('email_subject', _('Terms')),
                      template_rendered,
                      settings.DEFAULT_FROM_EMAIL,
                      [form.cleaned_data.get('email_address')],
                      fail_silently=False)
            messages.add_message(self.request, messages.INFO, _("Terms and Conditions Sent."))
        except SMTPException:  # pragma: no cover
            messages.add_message(self.request, messages.ERROR, _("An Error Occurred Sending Your Message."))

        self.success_url = form.cleaned_data.get('returnTo', '/') or '/'

        return super(EmailTermsView, self).form_valid(form)

    def form_invalid(self, form):
        """Override of CreateView method, logs invalid email form submissions."""
        LOGGER.debug("Invalid Email Form Submitted")
        messages.add_message(self.request, messages.ERROR, _("Invalid Email Address."))
        return super(EmailTermsView, self).form_invalid(form)
