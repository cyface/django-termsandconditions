"""Django Admin Site configuration"""

# pylint: disable=R0904

from django.contrib import admin
from django.utils.translation import gettext as _
from .models import TermsAndConditions, UserTermsAndConditions


class TermsAndConditionsAdmin(admin.ModelAdmin):
    """Sets up the custom Terms and Conditions admin display"""
    list_display = (_('slug'), _('name'), _('date_active'), _('version_number'),)
    verbose_name = _("Terms and Conditions")


class UserTermsAndConditionsAdmin(admin.ModelAdmin):
    """Sets up the custom User Terms and Conditions admin display"""
    # fields = ('terms', 'user', 'date_accepted', 'ip_address',)
    readonly_fields = (_('date_accepted'),)
    list_display = (_('terms'), _('user'), _('date_accepted'), _('ip_address'),)
    date_hierarchy = _('date_accepted')
    list_select_related = True


admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)
admin.site.register(UserTermsAndConditions, UserTermsAndConditionsAdmin)
