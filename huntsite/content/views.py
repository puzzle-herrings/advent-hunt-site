from django.http import Http404
from django.template.response import TemplateResponse
from django.views.decorators.http import require_safe

from huntsite.content import models
from huntsite.puzzles import models as puzzle_models
from huntsite.utils import HuntState, get_hunt_state, is_wrapup_available


@require_safe
def about_page(request):
    entries = models.AboutEntry.objects.all().order_by("order_by")
    context = {
        "entries": entries,
    }
    return TemplateResponse(request, "about.html", context)


@require_safe
def story_page(request):
    entries = models.StoryEntry.objects.select_related("puzzle").all().order_by("order_by")
    hunt_state = get_hunt_state(request)
    if hunt_state < HuntState.ENDED:
        # Filter to only unlocked story entries by solve
        if request.user.is_anonymous:
            solves = {}
        else:
            solves = {
                solve.puzzle: solve
                for solve in puzzle_models.Solve.objects.filter(user=request.user).select_related(
                    "puzzle"
                )
            }
        entries = [entry for entry in entries if entry.puzzle is None or entry.puzzle in solves]
    context = {
        "entries": entries,
    }
    return TemplateResponse(request, "story.html", context)


@require_safe
def victory_page(request):
    if (
        request.user.is_finished
        or request.user.is_tester
        or get_hunt_state(request) >= HuntState.ENDED
    ):
        entry = models.StoryEntry.objects.get(is_final=True)
        context = {
            "entry": entry,
        }
        return TemplateResponse(request, "victory.html", context)
    else:
        raise Http404


@require_safe
def attributions_page(request):
    entries = models.AttributionsEntry.objects.all().order_by("order_by")
    puzzles = (
        puzzle_models.Puzzle.available.with_calendar_entry()
        .with_attributions_entry()
        .all()
        .order_by("calendar_entry__day")
    )
    context = {
        "entries": entries,
        "puzzles": puzzles,
    }
    return TemplateResponse(request, "attributions.html", context)


@require_safe
def updates_page(request):
    entries = models.UpdateEntry.objects.all().order_by("-published_at")
    context = {
        "entries": entries,
    }
    return TemplateResponse(request, "updates.html", context)


@require_safe
def wrapup_page(request):
    if not request.user.is_tester and not is_wrapup_available(request):
        raise Http404

    entry = models.WrapupEntry.get_solo()
    context = {
        "entry": entry,
    }
    return TemplateResponse(request, "wrapup.html", context)
