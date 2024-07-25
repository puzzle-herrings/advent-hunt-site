import pytest

from huntsite.puzzles.factories import PuzzleFactory
from huntsite.puzzles.models import Guess, Solve
from huntsite.puzzles.services import guess_submit
from huntsite.teams.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_guess_submit():
    """guess_submit should create a guess and mark the puzzle as solved if correct."""
    puzzle = PuzzleFactory(answer="SUPER SECRET ANSWER")
    user = UserFactory()

    # No guesses should exist
    assert not Guess.objects.filter(puzzle=puzzle, user=user).exists()
    assert not Solve.objects.filter(puzzle=puzzle, user=user).exists()

    guess_submit(puzzle, user, "WRONG ANSWER")
    assert Guess.objects.filter(puzzle=puzzle, user=user).count() == 1
    assert not Solve.objects.filter(puzzle=puzzle, user=user).exists()

    guess_submit(puzzle, user, "STILL WRONG ANSWER")
    assert Guess.objects.filter(puzzle=puzzle, user=user).count() == 2
    assert not Solve.objects.filter(puzzle=puzzle, user=user).exists()

    guess_submit(puzzle, user, "SUPER SECRET ANSWER")
    assert Guess.objects.filter(puzzle=puzzle, user=user).count() == 3
    assert Solve.objects.filter(puzzle=puzzle, user=user).exists()
