""" Signals for Django """

# pylint: disable=C1001,E0202,W0613

import logging
from django.core.cache import cache
from django.dispatch import receiver
from .models import TermsAndConditions, UserTermsAndConditions
from django.db.models.signals import post_delete, post_save

LOGGER = logging.getLogger(name="termsandconditions")


@receiver([post_delete, post_save], sender=UserTermsAndConditions)
def user_terms_updated(sender, **kwargs):
    """Called when user terms and conditions is changed - to force cache clearing"""
    LOGGER.debug("User T&C Updated Signal Handler")
    if kwargs.get("instance").user:
        cache.delete(
            "tandc.not_agreed_terms_" + kwargs.get("instance").user.get_username()
        )


@receiver([post_delete, post_save], sender=TermsAndConditions)
def terms_updated(sender, **kwargs):
    """Called when terms and conditions is changed - to force cache clearing"""
    LOGGER.debug("T&C Updated Signal Handler")
    cache.delete("tandc.active_terms_ids")
    cache.delete("tandc.active_terms_list")
    if kwargs.get("instance").slug:
        cache.delete("tandc.active_terms_" + kwargs.get("instance").slug)
    for utandc in UserTermsAndConditions.objects.all():
        cache.delete("tandc.not_agreed_terms_" + utandc.user.get_username())
