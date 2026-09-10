"""Forms for the termsandconditions app."""

from django import forms

from .models import TermsAndConditions


class UserTermsAndConditionsForm(forms.Form):
    """Carries the terms being accepted and where to send the user afterwards.

    ``terms`` is validated against the terms currently in force.  That is what
    stops a user posting the id of a version whose ``date_active`` has not
    arrived yet: recording that acceptance would mean they were never asked for
    it once it went live.  A superseded version is refused for the same reason,
    since accepting one does not satisfy the gate either.
    """

    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())
    terms = forms.ModelMultipleChoiceField(
        queryset=TermsAndConditions.objects.none(),
        widget=forms.MultipleHiddenInput,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Set here rather than on the field: evaluating it at import time would
        # query the database before the app registry is ready, and which terms
        # are active changes as versions go live.
        self.fields["terms"].queryset = TermsAndConditions.get_active_terms_list()


class EmailTermsForm(forms.Form):
    """Collects the address to email a copy of the terms to.

    ``terms`` is multi-valued because ``/terms/email/`` offers to send every set
    of terms the user has outstanding, not just one.  Any version may be sent,
    active or not — ``/terms/email/<slug>/<version>/`` exists to mail a
    specific one, and sending a copy grants nothing.
    """

    email_subject = forms.CharField(widget=forms.HiddenInput())
    email_address = forms.EmailField()
    returnTo = forms.CharField(required=False, initial="/", widget=forms.HiddenInput())
    terms = forms.ModelMultipleChoiceField(
        queryset=TermsAndConditions.objects.all(),
        widget=forms.MultipleHiddenInput,
    )
