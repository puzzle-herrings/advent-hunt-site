from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from huntsite.puzzles.models import Puzzle

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
    }
    return TemplateResponse(request, "puzzle_detail.html", context)
