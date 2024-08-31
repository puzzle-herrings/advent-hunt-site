import pytest

from huntsite.puzzles.factories import PuzzleFactory
from huntsite.puzzles.models import Guess, Solve
from huntsite.puzzles.services import (
    guess_list_for_puzzle_and_user,
    guess_submit,
    solve_list_for_user,
)
from huntsite.teams.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_guess_list_for_puzzle_and_user():
    """guess_list_for_puzzle_and_user should return all guesses for a puzzle by a team."""
    puzzle = PuzzleFactory()
    user = UserFactory()

    # No guesses should exist
    assert not Guess.objects.filter(puzzle=puzzle, user=user).exists()
    assert guess_list_for_puzzle_and_user(puzzle, user).count() == 0

    # Create some guesses
    guess_submit(puzzle, user, "GUESS ONE")
    guess_submit(puzzle, user, "GUESS TWO")
    guess_submit(puzzle, user, "GUESS THREE")
    # Irelevant guess
    guess_submit(PuzzleFactory(), user, "IRRELEVANT")

    # Check that the guesses are returned in the correct order
    guesses = guess_list_for_puzzle_and_user(puzzle, user)
    assert guesses.count() == 3
    assert [guess.text for guess in guesses] == ["GUESS THREE", "GUESS TWO", "GUESS ONE"]


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

    # Duplicated guess
    guess_submit(puzzle, user, "STILL WRONG ANSWER")
    assert Guess.objects.filter(puzzle=puzzle, user=user).count() == 2
    assert not Solve.objects.filter(puzzle=puzzle, user=user).exists()

    guess_submit(puzzle, user, "SUPER SECRET ANSWER")
    assert Guess.objects.filter(puzzle=puzzle, user=user).count() == 3
    assert Solve.objects.filter(puzzle=puzzle, user=user).exists()


def test_guess_submit_keep_going():
    """guess_submit should create a guess and not mark the puzzle as solved if correct but keep going."""
    puzzle = PuzzleFactory(
        answer="SUPER SECRET ANSWER",
        keep_going_answers=["KEEP GOING", "STAY THE COURSE"],
    )
    user = UserFactory()

    # No guesses should exist
    assert not Guess.objects.filter(puzzle=puzzle, user=user).exists()
    assert not Solve.objects.filter(puzzle=puzzle, user=user).exists()

    guess_submit(puzzle, user, "WRONG ANSWER")
    assert Guess.objects.filter(puzzle=puzzle, user=user).count() == 1
    assert not Solve.objects.filter(puzzle=puzzle, user=user).exists()

    # Keep going answer
    guess_submit(puzzle, user, "KEEP GOING")
    assert Guess.objects.filter(puzzle=puzzle, user=user).count() == 2
    assert not Solve.objects.filter(puzzle=puzzle, user=user).exists()

    # Other keep going answer
    guess_submit(puzzle, user, "STAY THE COURSE")
    assert Guess.objects.filter(puzzle=puzzle, user=user).count() == 3
    assert not Solve.objects.filter(puzzle=puzzle, user=user).exists()

    # Correct answer
    guess_submit(puzzle, user, "SUPER SECRET ANSWER")
    assert Guess.objects.filter(puzzle=puzzle, user=user).count() == 4
    assert Solve.objects.filter(puzzle=puzzle, user=user).exists()


def test_solve_list_for_user():
    solved_puzzles = [PuzzleFactory() for _ in range(3)]
    _ = [PuzzleFactory() for _ in range(3)]  # Extra unsolved puzzles

    user = UserFactory()

    # No solves should exist
    solve_list_for_user(user).count() == 0

    for puzzle in solved_puzzles:
        guess_submit(puzzle, user, puzzle.answer)
    assert solve_list_for_user(user).count() == 3
    # reverse order of solving
    assert [solve.puzzle for solve in solve_list_for_user(user)] == solved_puzzles[::-1]
