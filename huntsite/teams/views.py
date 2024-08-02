from collections import defaultdict
from typing import NamedTuple

from django.template.response import TemplateResponse

from huntsite.puzzles import models as puzzle_models
from huntsite.teams import models


def team_detail(request, pk: int):
    """View to display the team profile of the user."""
    team = models.User.objects.select_related("profile").get(pk=pk)
    solves = puzzle_models.Solve.objects.filter(user=team).select_related("puzzle")
    context = {
        "team": team,
        "solves": solves,
        "is_self": request.user == team,
    }
    return TemplateResponse(request, "team_detail.html", context)


class LeaderboardEntry(NamedTuple):
    team: models.User
    solved_days: list[int]
    rank: int


def team_list(request):
    """View to display a list of all teams."""

    teams = models.User.nonprivileged.select_related("profile").all()
    solves = puzzle_models.Solve.objects.exclude(user__is_tester=True)
    puzzles = puzzle_models.Puzzle.objects.with_calendar_entry().all()
    meta_infos = puzzle_models.MetapuzzleInfo.objects.order_by("-is_final").all()
    metapuzzle_ids = {meta_info.puzzle_id for meta_info in meta_infos}

    solves_by_team = defaultdict(list)
    meta_solves_by_team = defaultdict(list)
    for solve in solves:
        solves_by_team[solve.user_id].append(solve.puzzle_id)
        if solve.puzzle_id in metapuzzle_ids:
            meta_solves_by_team[solve.user_id].append(solve.puzzle_id)

    try:
        final_puzzle_id = next(
            meta_info.puzzle_id for meta_info in meta_infos if meta_info.is_final
        )
    except StopIteration:
        final_puzzle_id = None

    def _rank_key(team):
        return (
            # Finished hunt
            final_puzzle_id not in solves_by_team[team.id],  # False < True
            # Meta solves
            -len(meta_solves_by_team[team.id]),
            # All solves
            -len(solves_by_team[team.id]),
        )

    def _rank_data(teams):
        ranks_map = {}
        rank = 0
        step_size = 1
        rank_keys_by_team = {team.id: _rank_key(team) for team in teams}
        for key in sorted(rank_keys_by_team.values()):
            if key in ranks_map:
                # Is tie, increment step size
                step_size += 1
            else:
                # Next rank
                ranks_map[key] = rank + step_size
                rank += step_size
                # Reset step size
                step_size = 1
        return {team.id: ranks_map[rank_keys_by_team[team.id]] for team in teams}

    ranks = _rank_data(teams)

    puzzle_id_to_day = {puzzle.id: puzzle.calendar_entry.day for puzzle in puzzles}

    leaderboard_data = sorted(
        (
            LeaderboardEntry(
                team=team,
                solved_days=[puzzle_id_to_day[p_id] for p_id in solves_by_team[team.id]],
                rank=ranks[team.id],
            )
            for team in teams
        ),
        key=lambda entry: (
            entry.rank,
            entry.team.team_name,
        ),
    )

    day_spine = list(range(25))
    metas_by_day = {puzzle_id_to_day[meta_info.puzzle_id]: meta_info for meta_info in meta_infos}

    context = {
        "leaderboard_data": leaderboard_data,
        "day_spine": day_spine,
        "metas_by_day": metas_by_day,
    }
    return TemplateResponse(request, "team_list.html", context)
