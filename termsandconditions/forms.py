"""Django forms for the termsandconditions application"""

# pylint: disable=E1120,W0613

from django import forms
from termsandconditions.models import TermsAndConditions


class UserTermsAndConditionsModelForm(forms.Form):
    """Form used when accepting Terms and Conditions - returnTo is used to catch where to end up."""
    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())
    terms = forms.ModelMultipleChoiceField(
        TermsAndConditions.get_active_list(as_dict=False),
        widget=forms.MultipleHiddenInput,
    )

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs.pop('instance')

        if 'initial' in kwargs:
            initial = kwargs.get('initial')

            if 'terms' in initial:
                self.terms = forms.ModelMultipleChoiceField(
                    initial.get('terms'),
                    widget=forms.MultipleHiddenInput,
                )
        super(UserTermsAndConditionsModelForm, self).__init__(*args, **kwargs)


class EmailTermsForm(forms.Form):
    """Form used to collect email address to send terms and conditions to."""
    email_subject = forms.CharField(widget=forms.HiddenInput())
    email_address = forms.EmailField()
    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())
    terms = forms.ModelChoiceField(queryset=TermsAndConditions.objects.all(), widget=forms.HiddenInput())
