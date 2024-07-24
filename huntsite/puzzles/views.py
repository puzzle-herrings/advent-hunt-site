from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from huntsite.puzzles.forms import GuessForm
from huntsite.puzzles.models import GuessEvaluation, Puzzle
import huntsite.puzzles.selectors as puzzle_selectors
import huntsite.puzzles.services as puzzle_services


def puzzle_list(request):
    """View to display a list of all puzzles."""
    puzzle_manager = (
        Puzzle.objects
        if not request.user.is_anonymous and request.user.is_tester
        else Puzzle.available
    )
    puzzles = (
        puzzle_manager.with_calendar_entry()
        .with_solves_by_user(request.user)
        .all()
        .order_by("calendar_entry__day")
    )
    context = {
        "puzzles": puzzles,
    }
    return TemplateResponse(request, "puzzle_list.html", context)


@login_required
def puzzle_detail(request, slug: str):
    """View to display the content page of a single puzzle."""
    puzzle_manager = Puzzle.objects if request.user.is_tester else Puzzle.available
    puzzle = get_object_or_404(puzzle_manager.all(), slug=slug)
    context = {
        "puzzle": puzzle,
        "guesses": puzzle_selectors.puzzle_guess_list(puzzle, request.user),
        "form": GuessForm(),
    }
    return TemplateResponse(request, "puzzle_detail.html", context)


GUESS_EVALUATION_MESSAGES = {
    GuessEvaluation.CORRECT: "Correct! 🎉",
    GuessEvaluation.INCORRECT: "Incorrect.",
    puzzle_services.ALREADY_SUBMITTED: "You've already submitted that guess.",
    GuessEvaluation.KEEP_GOING: "Not the answer, but keep going!",
}


@login_required
@require_POST
def guess_submit(request, slug: str):
    """View to handle a guess submission to a puzzle."""
    puzzle_manager = Puzzle.objects if request.user.is_tester else Puzzle.available
    puzzle = get_object_or_404(puzzle_manager.all(), slug=slug)

    form = GuessForm(request.POST)
    if form.is_valid():
        guess_text = form.cleaned_data["guess"]
        evaluation = puzzle_services.guess_submit(puzzle, request.user, guess_text)
        all_puzzle_guesses = puzzle_selectors.puzzle_guess_list(puzzle, request.user)
        context = {
            "evaluation_message": GUESS_EVALUATION_MESSAGES[evaluation],
            "guesses": all_puzzle_guesses,
        }
        return render(request, "partials/puzzle_guess_list.html", context)
