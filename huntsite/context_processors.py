from django.conf import settings
from django.utils import timezone

from huntsite.tester_utils.session_handlers import read_time_travel_session_var


def meta(request):
    """Context processor to add the HTML metadata information from settings to the context."""
    return {
        "META_TITLE": settings.META_TITLE,
        "META_DESCRIPTION": settings.META_DESCRIPTION,
        "META_AUTHOR": settings.META_AUTHOR,
        "META_KEYWORDS": settings.META_KEYWORDS,
        "META_OG_IMAGE": settings.META_OG_IMAGE,
    }


def robots(request):
    """Context processor for robots settings."""
    return {"robots_disallow_all": False}


def santa_missing(request):
    """Context processor to add the Santa missing flag to the context."""
    if (
        request.user.is_authenticated
        and request.user.is_tester
        and (time_traveling_at := read_time_travel_session_var(request))
    ):
        now = time_traveling_at
    else:
        now = timezone.now()

    if now < settings.HUNT_IS_LIVE_DATETIME:
        return {"santa_missing": False}

    if request.user.is_authenticated and request.user.is_finished:
        return {"santa_missing": False}

    return {"santa_missing": True}


def user(request):
    """Context processor to add the user to the context."""
    return {"user": request.user}
