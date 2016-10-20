"""Django forms for the termsandconditions application"""

# pylint: disable=E1120,W0613

from django import forms
from termsandconditions.models import TermsAndConditions


class UserTermsAndConditionsModelForm(forms.Form):
    """Form used when accepting Terms and Conditions - returnTo is used to catch where to end up."""
    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())
    terms = forms.ModelMultipleChoiceField(
        TermsAndConditions.objects.none(),
        widget=forms.MultipleHiddenInput,
    )

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs.pop('instance')

        terms_list = None

        if 'initial' in kwargs:
            initial = kwargs.get('initial')

            if 'terms' in initial:
                terms_list = initial.get('terms')

        if terms_list is None:
            terms_list = TermsAndConditions.get_active_list(as_dict=False)

        self.terms = forms.ModelMultipleChoiceField(
            terms_list,
            widget=forms.MultipleHiddenInput)

        super(UserTermsAndConditionsModelForm, self).__init__(*args, **kwargs)


class EmailTermsForm(forms.Form):
    """Form used to collect email address to send terms and conditions to."""
    email_subject = forms.CharField(widget=forms.HiddenInput())
    email_address = forms.EmailField()
    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())
    terms = forms.ModelChoiceField(queryset=TermsAndConditions.objects.all(), widget=forms.HiddenInput())
