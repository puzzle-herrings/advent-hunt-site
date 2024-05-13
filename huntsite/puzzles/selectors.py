from huntsite.puzzles.models import Puzzle


def puzzle_guess_list(puzzle: Puzzle, user):
    """Function to return all guess submissions for a puzzle by a team."""
    return puzzle.guess_set.filter(user=user).order_by("-created_at")
