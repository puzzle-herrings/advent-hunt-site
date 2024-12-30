from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from huntsite.utils import HuntState, get_hunt_state


def canonical(request):
    """Add canonical URL for the current page. Used to populate rel="canonical" meta tag."""
    site = get_current_site(request)
    return {"CANONICAL_URL": f"https://{site.domain}{request.path}"}


def meta(request):
    """Context processor to add the HTML metadata information from settings to the context."""
    return {
        "META_TITLE": settings.META_TITLE,
        "META_DESCRIPTION": settings.META_DESCRIPTION,
        "META_AUTHOR": settings.META_AUTHOR,
        "META_KEYWORDS": settings.META_KEYWORDS,
        "META_OG_IMAGE": settings.META_OG_IMAGE,
        "META_OG_IMAGE_PREHUNT": settings.META_OG_IMAGE_PREHUNT,
    }


def hunt_state(request):
    """Context processor to set the hunt state."""
    return {
        "HuntState": HuntState,
        "hunt_state": get_hunt_state(request),
    }


def announcement_message(request):
    """Context processor to add the announcement message to the context."""
    return {"ANNOUNCEMENT_MESSAGE": settings.ANNOUNCEMENT_MESSAGE}


def discord_server_link(request):
    """Context processor to add the discord server link to the context."""
    return {"DISCORD_SERVER_LINK": settings.DISCORD_SERVER_LINK}
