"""Django forms for the termsandconditions application"""

# pylint: disable=W0613

from django import forms
from termsandconditions.models import UserTermsAndConditions

import logging

LOGGER = logging.getLogger(name='termsandconditions')

class UserTermsAndConditionsModelForm(forms.ModelForm):
    LOGGER.debug("termsandconditions.forms.UserTermsAndConditionsModelForm")

    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())

    class Meta:
        model = UserTermsAndConditions
        exclude = ('date_accepted', 'ip_address', 'user')
        widgets = {'terms': forms.HiddenInput()}