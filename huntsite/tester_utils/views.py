import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from loguru import logger

from huntsite.puzzles.models import Guess, Solve
from huntsite.tester_utils import forms, session_handlers
from huntsite.tester_utils.models import OrganizerDashboardPermission


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


def organizer_dashboard_view(request):
    """View for hunt organizers to see solves and guesses."""
    # Check permissions
    if request.user.is_anonymous:
        raise Http404
    get_object_or_404(OrganizerDashboardPermission, user=request.user)

    recent_solves = (
        Solve.objects.select_related("user").select_related("puzzle").order_by("-created_at")[:200]
    )
    recent_guesses = (
        Guess.objects.select_related("user").select_related("puzzle").order_by("-created_at")[:200]
    )

    context = {
        "recent_solves_json": json.dumps([solve.to_dict() for solve in recent_solves]),
        "recent_guesses_json": json.dumps([guess.to_dict() for guess in recent_guesses]),
    }

    return render(request, "organizer_dashboard.html", context)
