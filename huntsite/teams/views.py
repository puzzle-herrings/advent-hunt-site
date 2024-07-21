from django.db.models import Prefetch
from django.template.response import TemplateResponse

from huntsite.puzzles import models as puzzle_models
from huntsite.puzzles import selectors as puzzle_selectors
from huntsite.teams import models


def team_detail(request, pk: int):
    """View to display the team profile of the user."""
    team = models.User.objects.select_related("profile").get(pk=pk)
    solves = puzzle_selectors.solve_list(team)
    context = {
        "team": team,
        "solves": solves,
        "is_self": request.user == team,
    }
    return TemplateResponse(request, "team_detail.html", context)


def team_list(request):
    """View to display a list of all teams."""
    teams = (
        models.User.objects.select_related("profile")
        .prefetch_related(
            Prefetch(
                "solve_set__puzzle__calendar_entry",
                queryset=puzzle_models.AdventCalendarEntry.objects.only("day"),
            )
        )
        .all()
    )
    days = list(range(25))
    solves_by_team = {
        team.id: [solve.puzzle.calendar_entry.day for solve in team.solve_set.all()]
        for team in teams
    }
    teams = sorted(
        teams,
        key=lambda team: (
            24 not in solves_by_team[team.id],  # False < True
            -len(solves_by_team[team.id]),
            team.team_name,
        ),
    )
    context = {
        "teams": teams,
        "days": days,
        "solves_by_team": solves_by_team,
    }
    return TemplateResponse(request, "team_list.html", context)
