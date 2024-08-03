from huntsite.tester_utils.forms import TimeTravelForm
from huntsite.tester_utils.session_handlers import read_time_travel_session_var


def time_travel(request):
    if request.user.is_authenticated and request.user.is_tester:
        time_traveling_at = read_time_travel_session_var(request)
        form = TimeTravelForm({"time_travel_to": time_traveling_at})
        return {
            "time_traveling_at": time_traveling_at,
            "time_travel_form": form,
        }
    return {}
