from django.template.response import TemplateResponse

from huntsite.puzzles import selectors as puzzle_selectors
from huntsite.teams import models


def team_detail(request, pk: int):
    """View to display the team profile of the user."""
    team = models.User.objects.select_related("profile").get(pk=pk)
    solves = puzzle_selectors.solve_list(team)
    context = {
        "user": request.user,
        "team": team,
        "solves": solves,
        "is_self": request.user == team,
    }
    return TemplateResponse(request, "team_detail.html", context)


def team_list(request):
    """View to display a list of all teams."""
    teams = models.User.objects.select_related("profile").all()
    context = {
        "user": request.user,
        "teams": teams,
    }
    return TemplateResponse(request, "team_list.html", context)
