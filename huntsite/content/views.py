from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.template.response import TemplateResponse

from huntsite.content import models
from huntsite.puzzles.selectors import solve_list


# Create your views here.
def about_page(request):
    entries = models.AboutEntry.objects.all().order_by("order_by")
    context = {
        "entries": entries,
    }
    return TemplateResponse(request, "about.html", context)


def story_page(request):
    entries = models.StoryEntry.objects.all().order_by("order_by")
    if request.user.is_anonymous:
        solves = {}
    else:
        solves = {solve.puzzle: solve for solve in solve_list(request.user)}
    entries = [entry for entry in entries if entry.puzzle is None or entry.puzzle in solves]
    context = {
        "entries": entries,
    }
    return TemplateResponse(request, "story.html", context)


@login_required
def victory_page(request):
    is_finished = hasattr(request.user, "finish")
    if not is_finished or not request.user.is_tester:
        raise Http404

    entry = models.StoryEntry.objects.get(is_final=True)
    context = {
        "entry": entry,
    }
    return TemplateResponse(request, "victory.html", context)
