from django.conf import settings
from django.utils import timezone


def meta(request):
    """Context processor to add the HTML metadata information from settings to the context."""
    return {
        "META_TITLE": settings.META_TITLE,
        "META_DESCRIPTION": settings.META_DESCRIPTION,
        "META_AUTHOR": settings.META_AUTHOR,
        "META_KEYWORDS": settings.META_KEYWORDS,
        "META_OG_IMAGE": settings.META_OG_IMAGE,
    }


def santa_missing(request):
    """Context processor to add the Santa missing flag to the context."""
    if request.user.is_authenticated and request.user.is_tester:
        if time_traveling_at := request.user.time_traveling_at():
            return {"santa_missing": time_traveling_at >= settings.SANTA_MISSING_DATETIME}
    return {"santa_missing": timezone.now() >= settings.SANTA_MISSING_DATETIME}


def user(request):
    """Context processor to add the user to the context."""
    return {"user": request.user}


def time_travel(request):
    if request.user.is_authenticated and request.user.is_tester:
        return {"time_traveling_at": request.user.time_traveling_at()}
    return {}
