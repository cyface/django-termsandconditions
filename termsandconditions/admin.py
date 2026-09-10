"""Admin registrations for the termsandconditions app."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string

from .conf import app_settings
from .models import TermsAndConditions, UserTermsAndConditions

#: Fields a rich-text widget is worth swapping in for.
RICH_TEXT_FIELDS = ("text", "info")


@admin.register(TermsAndConditions)
class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "version_number", "date_active")
    list_filter = ("slug",)
    search_fields = ("slug", "name", "text", "info")
    ordering = ("slug", "-date_active")
    date_hierarchy = "date_active"
    readonly_fields = ("date_created",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Swap in the configured rich-text widget, if a project set one.

        Set ``TERMS_ADMIN_TEXT_WIDGET`` to the dotted path of a widget class
        (from django-ckeditor-5, django-tinymce, or anything else) to edit the
        terms as rich text.  Left unset, Django's Textarea is used.
        """
        widget_path = app_settings.TERMS_ADMIN_TEXT_WIDGET
        if widget_path and db_field.name in RICH_TEXT_FIELDS:
            kwargs.setdefault("widget", import_string(widget_path))
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(UserTermsAndConditions)
class UserTermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ("terms", "user", "date_accepted", "ip_address")
    list_filter = ("terms__slug",)
    list_select_related = ("user", "terms")
    date_hierarchy = "date_accepted"
    readonly_fields = ("date_accepted",)
    autocomplete_fields = ("terms",)

    def get_search_fields(self, request) -> tuple[str, ...]:
        # Resolved at request time because AUTH_USER_MODEL is swappable and
        # need not have a `username` field.
        return (
            f"user__{get_user_model().USERNAME_FIELD}",
            "terms__slug",
            "terms__name",
        )
