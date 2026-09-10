"""Cache invalidation for terms and their acceptance."""

import logging

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
    # user_id, not instance.user: dereferencing the FK would fetch the row, and
    # this fires once per record when acceptances are pruned in bulk.
    cache.delete(
        not_agreed_terms_cache_key(
            instance.user_id, TermsAndConditions.get_active_terms_ids()
        )
    )


@receiver([post_delete, post_save], sender=TermsAndConditions)
def terms_updated(sender, instance, **kwargs) -> None:
    """Drop every cached view of the terms.

    Per-user acceptance lists need no sweep of their own: their keys carry the
    ids of the terms in force, so clearing those here retires all of them at
    once, including for users who have accepted nothing and therefore appear
    in no acceptance row.
    """
    LOGGER.debug("T&C updated signal handler")
    cache.delete_many([ACTIVE_TERMS_IDS_CACHE_KEY, ACTIVE_TERMS_LIST_CACHE_KEY])
    cache.delete(active_terms_cache_key(instance.slug))
