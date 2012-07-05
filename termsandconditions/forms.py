"""Django forms for the termsandconditions application"""
from django import forms
from termsandconditions.models import TermsAndConditions

import logging

logger = logging.getLogger(name='termsandconditions')

class TermsAndConditionsForm(forms.Form):
    """Master form for displaying and accepting Terms and Conditions"""
    text = forms.CharField(widget=forms.Textarea(attrs={'readonly': 'readonly', 'class': 'terms-text'}), required=False)
    slug = forms.SlugField(widget=forms.HiddenInput)
    version_number = forms.DecimalField(widget=forms.HiddenInput)
    returnTo = forms.CharField(widget=forms.HiddenInput, required=False) #URI to Return to After Accept

    def __init__(self, data=None, slug='default', initial=None, *args, **kwargs):
        """Lets you pass in a user= to bind this form from"""
        if initial is None:
            terms = TermsAndConditions.get_active(slug)
            text = terms.text
            slug = terms.slug
            version_number = terms.version_number

            initial = dict(text=text, slug=slug, version_number=version_number)

        super(TermsAndConditionsForm, self).__init__(data=data, initial=initial)
