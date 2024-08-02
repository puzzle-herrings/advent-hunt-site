from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from loguru import logger

from huntsite.tester_utils import forms, models


@login_required
@require_POST
def time_travel(request):
    """View to allow users to time travel."""
    if not request.user.is_tester:
        raise PermissionDenied()
    form = forms.TimeTravelForm(request.POST)
    if form.is_valid():
        time_travel_to = form.cleaned_data["time_travel_to"]
        time_travel_record, created = models.TimeTravel.objects.get_or_create(user=request.user)
        time_travel_record.time_travel_to = time_travel_to
        time_travel_record.is_active = True
        time_travel_record.save()

        messages.success(request, "Time travel successful.")
        return redirect(request.META["HTTP_REFERER"])
    else:
        logger.error(form.errors)
        form = forms.TimeTravelForm()
        context = {"time_travel_form": form}
        return TemplateResponse(request, "time_travel.html", context)
