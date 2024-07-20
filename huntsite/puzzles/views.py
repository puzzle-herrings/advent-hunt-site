from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from huntsite.puzzles.forms import GuessForm
from huntsite.puzzles.models import Puzzle
import huntsite.puzzles.selectors as puzzle_selectors
import huntsite.puzzles.services as puzzle_services


def puzzle_list(request):
    """View to display a list of all puzzles."""
    puzzles = Puzzle.objects.select_related("calendar_entry").all()
    if request.user.is_authenticated:
        solves = {solve.puzzle: solve for solve in puzzle_selectors.solve_list(request.user)}
    else:
        solves = {}
    context = {
        "puzzles": puzzles,
        "solves": solves,
    }
    return TemplateResponse(request, "puzzle_list.html", context)


@login_required
def puzzle_detail(request, slug: str):
    """View to display the content page of a single puzzle."""
    puzzle = get_object_or_404(Puzzle.objects.all(), slug=slug)
    context = {
        "puzzle": puzzle,
        "guesses": puzzle_selectors.puzzle_guess_list(puzzle, request.user),
        "form": GuessForm(),
    }
    return TemplateResponse(request, "puzzle_detail.html", context)


GUESS_EVALUATION_MESSAGES = {
    puzzle_services.GuessEvaluation.CORRECT: "Correct!",
    puzzle_services.GuessEvaluation.INCORRECT: "Incorrect.",
    puzzle_services.GuessEvaluation.ALREADY_SUBMITTED: "You've already submitted that guess.",
    puzzle_services.GuessEvaluation.KEEP_GOING: "Incorrect.",
}


@login_required
@require_POST
def guess_submit(request, slug: str):
    """View to handle a guess submission to a puzzle."""
    puzzle = get_object_or_404(Puzzle.objects.all(), slug=slug)
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
