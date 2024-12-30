import enum

from django.conf import settings
from django.utils import timezone

from huntsite.tester_utils.session_handlers import read_time_travel_session_var


class HuntState(enum.IntEnum):
    # IntEnum to allow inequality comparisons
    PREHUNT = enum.auto()
    LIVE = enum.auto()
    ENDED = enum.auto()

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
