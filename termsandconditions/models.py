"""Django models for the termsandconditions app."""

import logging

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .conf import app_settings
from .utils import (
    ACTIVE_TERMS_IDS_CACHE_KEY,
    ACTIVE_TERMS_LIST_CACHE_KEY,
    active_terms_cache_key,
    not_agreed_terms_cache_key,
)

LOGGER = logging.getLogger(__name__)

#: Cached in place of an absent terms object.  ``cache.get`` cannot tell a
#: cached ``None`` from a miss, so a slug with no active version needs a
#: sentinel of its own to be cached at all.
NO_ACTIVE_TERMS = "tandc.no-active-terms"


def get_default_terms_slug() -> str:
    """Default for :attr:`TermsAndConditions.slug`.

    A callable so ``DEFAULT_TERMS_SLUG`` is read per row rather than frozen
    into the migration when this module is first imported.
    """
    return app_settings.DEFAULT_TERMS_SLUG


class UserTermsAndConditions(models.Model):
    """Records that a user accepted a particular version of some terms."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="userterms",
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    terms = models.ForeignKey(
        "TermsAndConditions",
        related_name="userterms",
        on_delete=models.CASCADE,
        verbose_name=_("terms"),
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name=_("IP Address")
    )
    date_accepted = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Date Accepted")
    )

    class Meta:
        get_latest_by = "date_accepted"
        verbose_name = _("User Terms and Conditions")
        verbose_name_plural = _("User Terms and Conditions")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "terms"],
                name="termsandconditions_unique_user_terms",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.user.get_username()}:{self.terms.slug}-{self.terms.version_number}"
        )


class TermsAndConditions(models.Model):
    """One version of one set of terms.

    For a given slug the active version is the most recent one whose
    ``date_active`` is set and is not in the future.
    """

    slug = models.SlugField(default=get_default_terms_slug)
    name = models.TextField(max_length=255, verbose_name=_("name"))
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through=UserTermsAndConditions, blank=True
    )
    version_number = models.DecimalField(
        default=1.0,
        decimal_places=2,
        max_digits=6,
        verbose_name=_("version number"),
    )
    text = models.TextField(default="", blank=True, verbose_name=_("text"))
    info = models.TextField(
        default="",
        blank=True,
        help_text=_("Provide users with some info about what's changed and why"),
        verbose_name=_("info"),
    )
    date_active = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Leave Null To Never Make Active"),
        verbose_name=_("date active"),
    )
    date_created = models.DateTimeField(blank=True, auto_now_add=True)

    class Meta:
        ordering = ["-date_active"]
        get_latest_by = "date_active"
        verbose_name = _("Terms and Conditions")
        verbose_name_plural = _("Terms and Conditions")

    def __str__(self) -> str:  # pragma: nocover
        return f"{self.slug}-{self.version_number:.2f}"

    def get_absolute_url(self) -> str:
        return reverse(
            "tc_view_specific_version_page", args=[self.slug, self.version_number]
        )

    @staticmethod
    def get_active(slug: str | None = None) -> "TermsAndConditions | None":
        """Return the active version of the terms identified by ``slug``."""
        slug = slug or app_settings.DEFAULT_TERMS_SLUG
        cache_key = active_terms_cache_key(slug)

        active_terms = cache.get(cache_key)
        if active_terms == NO_ACTIVE_TERMS:
            return None

        if active_terms is None:
            try:
                active_terms = TermsAndConditions.objects.filter(
                    date_active__isnull=False,
                    date_active__lte=timezone.now(),
                    slug=slug,
                ).latest("date_active")
            except TermsAndConditions.DoesNotExist:
                # The slug is client input on the view and accept URLs, so a
                # miss is a bad request rather than a server fault: logging it
                # at ERROR hands an anonymous visitor a way to fill the log.
                # Caching the miss keeps those requests off the database too.
                LOGGER.debug(
                    "Requested terms and conditions that do not exist: %s", slug
                )
                cache.set(cache_key, NO_ACTIVE_TERMS, app_settings.TERMS_CACHE_SECONDS)
                return None
            cache.set(cache_key, active_terms, app_settings.TERMS_CACHE_SECONDS)

        return active_terms

    @staticmethod
    def get_active_terms_ids() -> list[int]:
        """Return the id of the active version of every set of terms, by slug."""
        active_terms_ids = cache.get(ACTIVE_TERMS_IDS_CACHE_KEY)
        if active_terms_ids is None:
            # Ordering by date_active means later versions overwrite earlier
            # ones, leaving the currently active id for each slug.
            latest_id_by_slug = dict(
                TermsAndConditions.objects.filter(
                    date_active__isnull=False, date_active__lte=timezone.now()
                )
                .order_by("date_active")
                .values_list("slug", "id")
            )
            active_terms_ids = [
                latest_id_by_slug[slug] for slug in sorted(latest_id_by_slug)
            ]
            cache.set(
                ACTIVE_TERMS_IDS_CACHE_KEY,
                active_terms_ids,
                app_settings.TERMS_CACHE_SECONDS,
            )

        return active_terms_ids

    @staticmethod
    def get_active_terms_list() -> QuerySet["TermsAndConditions"]:
        """Return the active version of every set of terms."""
        active_terms_list = cache.get(ACTIVE_TERMS_LIST_CACHE_KEY)
        if active_terms_list is None:
            active_terms_list = TermsAndConditions.objects.filter(
                id__in=TermsAndConditions.get_active_terms_ids()
            ).order_by("slug")
            cache.set(
                ACTIVE_TERMS_LIST_CACHE_KEY,
                active_terms_list,
                app_settings.TERMS_CACHE_SECONDS,
            )

        return active_terms_list

    @staticmethod
    def get_active_terms_not_agreed_to(user) -> QuerySet["TermsAndConditions"] | list:
        """Return the active terms ``user`` has not accepted yet.

        Anonymous users are treated as having accepted nothing.  Users excluded
        by ``TERMS_EXCLUDE_USERS_WITH_PERM`` or ``TERMS_EXCLUDE_SUPERUSERS``
        get an empty list.
        """
        if not user.is_authenticated:
            return TermsAndConditions.get_active_terms_list()

        # has_perm() is True for any permission when is_superuser, so
        # superusers are only excluded via TERMS_EXCLUDE_SUPERUSERS below.
        exclude_perm = app_settings.TERMS_EXCLUDE_USERS_WITH_PERM
        if (
            exclude_perm is not None
            and not user.is_superuser
            and user.has_perm(exclude_perm)
        ):
            return []

        if app_settings.TERMS_EXCLUDE_SUPERUSERS and user.is_superuser:
            return []

        cache_key = not_agreed_terms_cache_key(user.pk)
        not_agreed_terms = cache.get(cache_key)
        if not_agreed_terms is None:
            not_agreed_terms = (
                TermsAndConditions.get_active_terms_list()
                .exclude(userterms__in=UserTermsAndConditions.objects.filter(user=user))
                .order_by("slug")
            )
            cache.set(cache_key, not_agreed_terms, app_settings.TERMS_CACHE_SECONDS)

        return not_agreed_terms
