import enum

from django.apps import apps
from django.conf import settings
from django.utils import timezone

from huntsite.tester_utils.session_handlers import read_time_travel_session_var


class HuntState(enum.IntEnum):
    # IntEnum to allow inequality comparisons
    PREHUNT = enum.auto()
    LIVE = enum.auto()
    ENDED = enum.auto()

    @property
    def do_not_call_in_templates(self):
        """Turn off calling in templates, otherwise value access doesn't work properly.
        https://stackoverflow.com/questions/35953132/how-to-access-enum-types-in-django-templates
        """
        return True

    def __str__(self):
        return self.name.lower()


def get_hunt_state(request):
    """Determine curent hunt state."""
    # Determine current time
    if (
        request.user.is_authenticated
        and request.user.is_tester
        and (time_traveling_at := read_time_travel_session_var(request))
    ):
        now = time_traveling_at
    else:
        now = timezone.now()

    if now >= settings.HUNT_IS_ENDED_DATETIME:
        return HuntState.ENDED
    elif now >= settings.HUNT_IS_LIVE_DATETIME:
        return HuntState.LIVE
    else:
        return HuntState.PREHUNT


def is_wrapup_available(request):
    """Determine if wrapup is available."""
    if (
        request.user.is_authenticated
        and request.user.is_tester
        and (time_traveling_at := read_time_travel_session_var(request))
    ):
        now = time_traveling_at
    else:
        now = timezone.now()
    wrapup_entry = apps.get_model("content", "WrapupEntry").get_solo()
    return wrapup_entry.is_available_at(now)
