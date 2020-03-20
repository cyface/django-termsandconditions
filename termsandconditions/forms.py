"""Django forms for the termsandconditions application"""

# pylint: disable=E1120,W0613

from django import forms
from django.db.models import QuerySet

from termsandconditions.models import TermsAndConditions


class UserTermsAndConditionsModelForm(forms.Form):
    """Form used when accepting Terms and Conditions - returnTo is used to catch where to end up."""

    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())
    terms = forms.ModelMultipleChoiceField(
        TermsAndConditions.objects.none(), widget=forms.MultipleHiddenInput,
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance", None)

        terms_list = kwargs.get("initial", {}).get("terms", None)

        if terms_list is None:  # pragma: nocover
            terms_list = TermsAndConditions.get_active_terms_list()

        if terms_list is QuerySet:
            self.terms = forms.ModelMultipleChoiceField(
                terms_list, widget=forms.MultipleHiddenInput
            )
        else:
            self.terms = terms_list

        super().__init__(*args, **kwargs)


class EmailTermsForm(forms.Form):
    """Form used to collect email address to send terms and conditions to."""

    email_subject = forms.CharField(widget=forms.HiddenInput())
    email_address = forms.EmailField()
    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())
    terms = forms.ModelChoiceField(
        queryset=TermsAndConditions.objects.all(), widget=forms.HiddenInput()
    )
