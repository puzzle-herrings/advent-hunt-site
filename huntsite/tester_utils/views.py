from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from loguru import logger

from huntsite.tester_utils import forms, session_handlers


@login_required
@require_POST
def time_travel(request):
    """View to allow users to time travel."""
    if not request.user.is_tester:
        raise PermissionDenied()
    form = forms.TimeTravelForm(request.POST)
    logger.info("hello")
    if form.is_valid():
        logger.success(
            f"User {request.user} is time traveling to {form.cleaned_data['time_travel_to']}."
        )
        time_travel_to = form.cleaned_data["time_travel_to"]
        logger.info(f"Time traveling to: {time_travel_to}")
        session_handlers.write_time_travel_session_var(request, time_travel_to)
        messages.success(request, "Time travel successful.")
        response = HttpResponse("Traveling through time...")
        response["HX-Refresh"] = "true"
        return response
    else:
        return redirect("server_error")


@login_required
@require_POST
def time_travel_reset(request):
    """View to allow users to time travel."""
    if not request.user.is_tester:
        raise PermissionDenied()
    session_handlers.write_time_travel_session_var(request, None)
    messages.success(request, "Returned to the present.")
    response = HttpResponse("Traveling through time...")
    response["HX-Refresh"] = "true"
    return response
