from huntsite.puzzles.models import Puzzle


def puzzle_guess_list(puzzle: Puzzle, user):
    """Function to return all guess submissions for a puzzle by a team."""
    return puzzle.guess_set.filter(user=user).order_by("-created_at")


def solve_list(user):
    """Function to return all solves by a team."""
    return user.solve_set.order_by("-created_at")
