from django.template.response import TemplateResponse

from huntsite.content import models
from huntsite.puzzles.selectors import solve_list


# Create your views here.
def about_page(request):
    entries = models.AboutEntry.objects.all().order_by("order_by")
    context = {
        "user": request.user,
        "entries": entries,
    }
    return TemplateResponse(request, "about.html", context)


def story_page(request):
    entries = models.StoryEntry.objects.all().order_by("order_by")
    solves = {solve.puzzle: solve for solve in solve_list(request.user)}
    context = {
        "user": request.user,
        "solves": solves,
        "entries": entries,
    }
    return TemplateResponse(request, "story.html", context)
