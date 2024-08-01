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
    return {"santa_missing": timezone.now() >= settings.SANTA_MISSING_DATETIME}


def user(request):
    """Context processor to add the user to the context."""
    return {"user": request.user}
