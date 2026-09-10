"""Views for the termsandconditions app."""

import logging
from collections.abc import Sequence
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.generic import DetailView, FormView

from .conf import app_settings
from .forms import EmailTermsForm, UserTermsAndConditionsForm
from .models import TermsAndConditions, UserTermsAndConditions

LOGGER = logging.getLogger(__name__)


class GetTermsViewMixin:
    """Resolves which terms a request is about, and where to return afterwards."""

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["terms_base_template"] = app_settings.TERMS_BASE_TEMPLATE
        return context

    def get_terms(self, kwargs: dict) -> Sequence["TermsAndConditions | None"]:
        """Pick the terms named by the URL, falling back to the user's outstanding ones."""
        slug = kwargs.get("slug")
        version = kwargs.get("version")

        if slug and version:
            try:
                return [
                    TermsAndConditions.objects.filter(
                        slug=slug, version_number=version
                    ).latest("date_active")
                ]
            except TermsAndConditions.DoesNotExist:
                raise Http404(
                    f"No terms with slug {slug!r} at version {version!r}."
                ) from None

        if slug:
            return [TermsAndConditions.get_active(slug)]

        return TermsAndConditions.get_active_terms_not_agreed_to(self.request.user)

    def get_return_to(self, from_dict) -> str:
        """Read the redirect target out of ``from_dict``, rejecting off-site URLs.

        The configured ``TERMS_RETURNTO_PARAM`` wins, but the form field is
        always named ``returnTo``, so that name is honoured as a fallback.
        """
        return_to = from_dict.get(app_settings.TERMS_RETURNTO_PARAM) or from_dict.get(
            "returnTo", "/"
        )

        if url_has_allowed_host_and_scheme(return_to, settings.ALLOWED_HOSTS):
            return iri_to_uri(return_to)

        LOGGER.debug("Unsafe URL found: %s", return_to)
        return "/"


class AcceptTermsView(GetTermsViewMixin, FormView):
    """Show outstanding terms and record the user's acceptance.

    url: /terms/accept/
    """

    form_class = UserTermsAndConditionsForm
    template_name = "termsandconditions/tc_accept_terms.html"

    def get_initial(self) -> dict:
        return {
            "terms": self.get_terms(self.kwargs),
            "returnTo": self.get_return_to(self.request.GET),
        }

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # get_terms yields [None] for a slug with no active version. There is
        # nothing to accept in that case, so the template shows the empty state
        # and suppresses the form rather than rendering a print link with no
        # slug or version to build the URL from.
        context["terms_to_accept"] = [
            terms for terms in context["form"].initial["terms"] if terms
        ]
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return_url = self.get_return_to(request.POST)

        if not request.user.is_authenticated:
            return HttpResponseRedirect("/")

        form = self.get_form()
        if not form.is_valid():
            # The field accepts only the terms currently in force, so this is
            # a posted id that is missing, malformed, superseded, or dated in
            # the future. None of those should be recorded as an acceptance.
            LOGGER.debug("Terms not accepted: %s", form.errors.as_json())
            return HttpResponseRedirect(return_url)

        ip_address = self.get_ip_address(request)

        for terms in form.cleaned_data["terms"]:
            try:
                # Saved one at a time so the cache-clearing signals fire, and
                # inside a savepoint so a duplicate does not poison an
                # enclosing transaction (ATOMIC_REQUESTS, say).
                with transaction.atomic():
                    UserTermsAndConditions.objects.create(
                        user=request.user, terms=terms, ip_address=ip_address
                    )
            except IntegrityError:
                # Already accepted, possibly concurrently. Nothing to record.
                LOGGER.debug("Terms %s already accepted by this user", terms.pk)

        return HttpResponseRedirect(return_url)

    @staticmethod
    def get_ip_address(request: HttpRequest) -> str | None:
        """The client IP to store, or None when disabled or unavailable."""
        if not app_settings.TERMS_STORE_IP_ADDRESS:
            return None

        ip_address = request.META.get(app_settings.TERMS_IP_HEADER_NAME)
        if not ip_address:
            return None

        # Proxy headers such as X-Forwarded-For hold a chain; the client is first.
        return ip_address.split(",")[0].strip()


class EmailTermsView(GetTermsViewMixin, FormView):
    """Email a copy of the terms.

    url: /terms/email/
    """

    template_name = "termsandconditions/tc_email_terms_form.html"
    form_class = EmailTermsForm

    def get_initial(self) -> dict:
        # A slug with no active version yields [None]; drop it so the form
        # renders no hidden input rather than one with an empty value.
        return {
            "terms": [terms for terms in self.get_terms(self.kwargs) if terms],
            "returnTo": self.get_return_to(self.request.GET),
        }

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # One label for however many sets of terms the URL resolved to, used
        # for both the heading and the default subject line.
        context["terms_names"] = ", ".join(
            terms.name for terms in context["form"].initial["terms"]
        )
        return context

    def form_valid(self, form: EmailTermsForm) -> HttpResponse:
        template = get_template("termsandconditions/tc_email_terms.html")
        template_rendered = template.render({"terms_list": form.cleaned_data["terms"]})

        LOGGER.debug("Email terms body: %s", template_rendered)

        try:
            send_mail(
                form.cleaned_data.get("email_subject", _("Terms")),
                template_rendered,
                settings.DEFAULT_FROM_EMAIL,
                [form.cleaned_data.get("email_address")],
                fail_silently=False,
            )
            messages.add_message(
                self.request, messages.INFO, _("Terms and Conditions Sent.")
            )
        except SMTPException:  # pragma: no cover
            messages.add_message(
                self.request,
                messages.ERROR,
                _("An Error Occurred Sending Your Message."),
            )

        self.success_url = self.get_return_to(form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form: EmailTermsForm) -> HttpResponse:
        LOGGER.debug("Invalid email form submitted")
        messages.add_message(self.request, messages.ERROR, _("Invalid Email Address."))
        return super().form_invalid(form)


class TermsView(GetTermsViewMixin, DetailView):
    """Show the terms the current user still has to accept.

    url: /terms/
    """

    template_name = "termsandconditions/tc_view_terms.html"
    context_object_name = "terms_list"

    def get_object(self, queryset=None):
        return self.get_terms(self.kwargs)


class TermsActiveView(TermsView):
    """Show every currently active set of terms.

    url: /terms/active/
    """

    def get_object(self, queryset=None):
        return TermsAndConditions.get_active_terms_list()
