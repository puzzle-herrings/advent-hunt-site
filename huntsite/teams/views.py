from typing import NamedTuple

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


class LeaderboardEntry(NamedTuple):
    team: models.User
    solves: list[int]
    rank: int


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
    metas_by_day = {
        meta_info.puzzle.calendar_entry.day: meta_info
        for meta_info in puzzle_models.MetapuzzleInfo.objects.select_related(
            "puzzle__calendar_entry"
        ).all()
    }

    def _rank_key(team):
        return (
            24 not in solves_by_team[team.id],  # False < True
            -len(tuple(day for day in solves_by_team[team.id] if day in metas_by_day)),
            -len(solves_by_team[team.id]),
        )

    def _rank_data(teams):
        ranks_map = {}
        rank = 0
        step_size = 1
        rank_keys_by_team = {team.id: _rank_key(team) for team in teams}
        for key in sorted(rank_keys_by_team.values()):
            if key in ranks_map:
                step_size += 1
            else:
                ranks_map[key] = rank + step_size
                rank += step_size
                # Reset step size
                step_size = 1
        return {team.id: ranks_map[rank_keys_by_team[team.id]] for team in teams}

    ranks = _rank_data(teams)

    leaderboard_data = sorted(
        (
            LeaderboardEntry(
                team=team,
                solves=solves_by_team[team.id],
                rank=ranks[team.id],
            )
            for team in teams
        ),
        key=lambda entry: (
            entry.rank,
            entry.team.team_name,
        ),
    )

    context = {
        "leaderboard_data": leaderboard_data,
        "days": days,
        "metas_by_day": metas_by_day,
    }
    return TemplateResponse(request, "team_list.html", context)
