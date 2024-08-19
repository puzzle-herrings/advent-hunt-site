from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone

from huntsite.tester_utils.session_handlers import read_time_travel_session_var


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
    }


def hunt_is_live(request):
    """Context processor to add the Santa missing flag to the context."""
    if request.user.is_tester and (time_traveling_at := read_time_travel_session_var(request)):
        now = time_traveling_at
    else:
        now = timezone.now()
    return {"hunt_is_live": now >= settings.HUNT_IS_LIVE_DATETIME}
