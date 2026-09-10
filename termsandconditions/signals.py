"""Cache invalidation for terms and their acceptance."""

import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import TermsAndConditions, UserTermsAndConditions
from .utils import (
    ACTIVE_TERMS_IDS_CACHE_KEY,
    ACTIVE_TERMS_LIST_CACHE_KEY,
    active_terms_cache_key,
    not_agreed_terms_cache_key,
)

LOGGER = logging.getLogger(__name__)


@receiver([post_delete, post_save], sender=UserTermsAndConditions)
def user_terms_updated(sender, instance, **kwargs) -> None:
    """Drop the acceptance cache for the user whose record changed."""
    LOGGER.debug("User T&C updated signal handler")
    if instance.user:
        cache.delete(not_agreed_terms_cache_key(instance.user.get_username()))


@receiver([post_delete, post_save], sender=TermsAndConditions)
def terms_updated(sender, instance, **kwargs) -> None:
    """Drop every cached view of the terms, plus per-user acceptance."""
    LOGGER.debug("T&C updated signal handler")
    cache.delete_many([ACTIVE_TERMS_IDS_CACHE_KEY, ACTIVE_TERMS_LIST_CACHE_KEY])
    if instance.slug:
        cache.delete(active_terms_cache_key(instance.slug))

    # New or changed terms can invalidate anyone's acceptance, so clear the
    # cache for every user who has ever accepted something.
    username_field = get_user_model().USERNAME_FIELD
    usernames = (
        UserTermsAndConditions.objects.values_list(f"user__{username_field}", flat=True)
        .order_by()
        .distinct()
    )
    cache.delete_many([not_agreed_terms_cache_key(name) for name in usernames])
