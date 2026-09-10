"""Forms for the termsandconditions app."""

from django import forms

from .models import TermsAndConditions


class UserTermsAndConditionsForm(forms.Form):
    """Carries the terms being accepted and where to send the user afterwards."""

    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())
    terms = forms.ModelMultipleChoiceField(
        queryset=TermsAndConditions.objects.all(),
        widget=forms.MultipleHiddenInput,
    )


class EmailTermsForm(forms.Form):
    """Collects the address to email a copy of the terms to."""

    email_subject = forms.CharField(widget=forms.HiddenInput())
    email_address = forms.EmailField()
    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())
    terms = forms.ModelChoiceField(
        queryset=TermsAndConditions.objects.all(), widget=forms.HiddenInput()
    )
