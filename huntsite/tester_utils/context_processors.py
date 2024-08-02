from huntsite.tester_utils.forms import TimeTravelForm


def time_travel(request):
    if request.user.is_authenticated and request.user.is_tester:
        return {
            "time_traveling_at": request.user.time_traveling_at(),
            "time_travel_form": TimeTravelForm(),
        }
    return {}
