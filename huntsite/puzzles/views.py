import base64
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_http_methods, require_safe
from loguru import logger

from huntsite.puzzles.forms import GuessForm
from huntsite.puzzles.models import GuessEvaluation, Puzzle
import huntsite.puzzles.services as puzzle_services
from huntsite.tester_utils.session_handlers import read_time_travel_session_var
from huntsite.utils import HuntState, get_hunt_state


@require_safe
def puzzle_list(request):
    """View to display a list of all puzzles."""
    if request.user.is_tester and (time_traveling_at := read_time_travel_session_var(request)):
        # Get puzzles based on time travel
        logger.trace(
            "User {user} is viewing puzzle list while time traveling at {time_traveling_at}",
            user=request.user,
            time_traveling_at=time_traveling_at,
        )
        puzzle_manager = Puzzle.objects.filter_available_at(time_traveling_at)
    else:
        # Only get available puzzles
        logger.trace("Team '{user.team_name}' is viewing puzzle list", user=request.user)
        puzzle_manager = Puzzle.available

    puzzles = (
        puzzle_manager.with_calendar_entry()
        .with_meta_info()
        .with_solves_by_user(request.user)
        .all()
        .order_by("calendar_entry__day")
    )
    day_spine = list(range(1, 25))
    context = {
        "day_spine": day_spine,
        "puzzles_by_day": {puzzle.calendar_entry.day: puzzle for puzzle in puzzles},
    }
    return TemplateResponse(request, "puzzle_list.html", context)


GUESS_EVALUATION_MESSAGES = {
    GuessEvaluation.CORRECT: "Correct! 🎉",
    GuessEvaluation.INCORRECT: "Incorrect.",
    puzzle_services.ALREADY_SUBMITTED: "You've already submitted that guess.",
    GuessEvaluation.KEEP_GOING: "You got an intermediate phrase! Keep going for the final answer.",
}


@require_http_methods(["GET", "POST"])
def puzzle_detail(request, slug: str):
    hunt_state = get_hunt_state(request)
    if hunt_state < HuntState.ENDED:
        return puzzle_detail_serverside(request, slug=slug)
    else:
        return puzzle_detail_clientside(request, slug=slug)


@login_required
def puzzle_detail_serverside(request, slug: str):
    """View to display the content page of a single puzzle and take guesses."""
    puzzle_manager = Puzzle.objects if request.user.is_tester else Puzzle.available

    if request.method == "GET":
        queryset = (
            puzzle_manager.with_errata()
            .with_clipboard_data()
            .with_external_links()
            .with_canned_hints(
                as_of=read_time_travel_session_var(request) if request.user.is_tester else None
            )
        )
        puzzle = get_object_or_404(queryset, slug=slug)

        logger.trace(
            "Team '{user.team_name}' is viewing puzzle {puzzle}.",
            user=request.user,
            puzzle=puzzle,
        )
        context = {
            "puzzle": puzzle,
            "guesses": puzzle_services.guess_list_for_puzzle_and_user(
                puzzle=puzzle,
                user=request.user,
            ),
            "form": GuessForm(slug=slug),
        }
        return TemplateResponse(request, "puzzle_detail.html", context)

    elif request.method == "POST":
        puzzle = get_object_or_404(puzzle_manager, slug=slug)

        # Submission to answer checker
        context = {}
        form = GuessForm(request.POST, slug=slug)
        if form.is_valid():
            guess_text = form.cleaned_data["guess"]
            evaluation = puzzle_services.guess_submit(puzzle, request.user, guess_text)
            context["evaluation_message"] = GUESS_EVALUATION_MESSAGES[evaluation]
            # Check for story unlock
            if evaluation == GuessEvaluation.CORRECT and hasattr(puzzle, "storyentry"):
                story_unlock_message = mark_safe(
                    """You've unlocked a new story entry: <a href="{url}">"{title}"</a>""".format(
                        url=reverse("story"),
                        title=puzzle.storyentry.title,
                    )
                )
                context["story_unlock_message"] = story_unlock_message
                messages.add_message(
                    request,
                    level=messages.INFO,
                    message=story_unlock_message,
                    extra_tags="story-unlock",
                )
        else:
            logger.error(
                "Team '{user.team_name}' submitted invalid guess for puzzle {puzzle}: {payload}",
                user=request.user,
                puzzle=puzzle,
                payload=request.POST,
            )
            context["evaluation_message"] = "Sorry, something went wrong!"

        all_puzzle_guesses = puzzle_services.guess_list_for_puzzle_and_user(
            puzzle=puzzle,
            user=request.user,
        )
        context["guesses"] = all_puzzle_guesses
        return render(request, "partials/puzzle_guess_list.html", context)


def puzzle_detail_clientside(request, slug: str):
    puzzle_manager = Puzzle.objects

    if request.method == "GET":
        queryset = (
            puzzle_manager.with_errata()
            .with_clipboard_data()
            .with_external_links()
            .with_canned_hints(
                as_of=read_time_travel_session_var(request) if request.user.is_tester else None
            )
        )
        puzzle = get_object_or_404(queryset, slug=slug)
        # Base64-encode the answers so they're not in plaintext in the HTML source
        answer_data = {
            "answer": base64.b64encode(puzzle.answer.encode()).decode(),
            "keep_goings": [
                base64.b64encode(ans.encode()).decode() for ans in puzzle.keep_going_answers
            ],
        }
        context = {
            "puzzle": puzzle,
            "answer_data": json.dumps(answer_data),
        }
        return TemplateResponse(request, "puzzle_detail.html", context)

    elif request.method == "POST":
        raise PermissionDenied


@require_safe
def puzzle_solution(request, slug: str):
    hunt_state = get_hunt_state(request)
    if hunt_state < HuntState.ENDED:
        raise Http404

    puzzle = get_object_or_404(Puzzle, slug=slug)
    context = {
        "puzzle": puzzle,
    }
    return TemplateResponse(request, "puzzle_solution.html", context)
