from datetime import datetime

TIME_TRAVEL_SESSION_VAR = "time_traveling_at"


def read_time_travel_session_var(request):
    time_traveling_at = request.session.get(TIME_TRAVEL_SESSION_VAR)
    if time_traveling_at:
        return datetime.fromisoformat(time_traveling_at)
    return None


def write_time_travel_session_var(request, time_travel_to: datetime):
    if time_travel_to is None:
        if TIME_TRAVEL_SESSION_VAR in request.session:
            request.session.pop(TIME_TRAVEL_SESSION_VAR)
    else:
        request.session[TIME_TRAVEL_SESSION_VAR] = time_travel_to.isoformat()
