from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from huntsite.puzzles.forms import GuessForm
from huntsite.puzzles.models import Puzzle
import huntsite.puzzles.services as puzzle_services
import huntsite.puzzles.selectors as puzzle_selectors


def puzzle_list(request):
    """View to display a list of all puzzles."""
    puzzles = Puzzle.objects.all()
    context = {
        "puzzles": puzzles,
    }
    return TemplateResponse(request, "puzzle_list.html", context)


def puzzle_detail(request, slug: str):
    """View to display the content page of a single puzzle."""
    puzzle = get_object_or_404(Puzzle.objects.all(), slug=slug)
    context = {
        "puzzle": puzzle,
        "guesses": puzzle_selectors.puzzle_guess_list(puzzle, request.user),
        "form": GuessForm(),
    }
    return TemplateResponse(request, "puzzle_detail.html", context)


@require_POST
def guess_submit(request, slug: str):
    """View to handle a guess submission to a puzzle."""
    puzzle = get_object_or_404(Puzzle.objects.all(), slug=slug)
    form = GuessForm(request.POST)
    if form.is_valid():
        guess_text = form.cleaned_data["guess"]
        puzzle_services.guess_submit(puzzle, request.user, guess_text)
        all_puzzle_guesses = puzzle_selectors.puzzle_guess_list(puzzle, request.user)
        context = {
            "guesses": all_puzzle_guesses,
        }
        return render(request, "partials/puzzle_guess_list.html", context)
