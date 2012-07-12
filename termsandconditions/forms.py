"""Django forms for the termsandconditions application"""

# pylint: disable=W0613

from django import forms
from termsandconditions.models import UserTermsAndConditions

class UserTermsAndConditionsModelForm(forms.ModelForm):
    """Form used when accepting Terms and Conditions - returnTo is used to catch where to end up."""

    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())

    class Meta:
        """Configuration for this Modelform"""
        model = UserTermsAndConditions
        exclude = ('date_accepted', 'ip_address', 'user')
        widgets = {'terms': forms.HiddenInput()}