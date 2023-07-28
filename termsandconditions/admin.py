"""Django Admin Site configuration"""

from django.contrib import admin
from django.utils.translation import gettext as _
from .models import TermsAndConditions, UserTermsAndConditions


class TermsAndConditionsAdmin(admin.ModelAdmin):
    """Sets up the custom Terms and Conditions admin display"""

    list_display = (
        "slug",
        "name",
        "date_active",
        "version_number",
    )
    verbose_name = _("Terms and Conditions")


class UserTermsAndConditionsAdmin(admin.ModelAdmin):
    """Sets up the custom User Terms and Conditions admin display"""

    # fields = ('terms', 'user', 'date_accepted', 'ip_address',)
    readonly_fields = ("date_accepted",)
    list_display = (
        "terms",
        "user",
        "date_accepted",
        "ip_address",
    )
    date_hierarchy = "date_accepted"
    list_select_related = True


admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)
admin.site.register(UserTermsAndConditions, UserTermsAndConditionsAdmin)
