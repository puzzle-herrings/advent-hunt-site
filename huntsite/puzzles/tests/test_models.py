from django.utils import timezone
import pytest

from huntsite.puzzles.factories import PuzzleFactory
from huntsite.puzzles.models import AdventCalendarEntry, Puzzle
from huntsite.puzzles.services import guess_submit
from huntsite.teams.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_puzzle_create():
    """Creating a puzzle automatically create a advent calendar entry"""
    puzzle = Puzzle.objects.create(
        name="A New Puzzle",
        slug="a-new-puzzle",
        answer="A NEW ANSWER",
    )
    assert AdventCalendarEntry.objects.get(puzzle=puzzle)


def test_puzzle_manager_with_calendar_entry():
    """Custom model manager method with_calendar_entry selects related calendar_entry."""

    PuzzleFactory()

    result_without = Puzzle.objects.first()
    calendar_entry_field = Puzzle._meta.get_field("calendar_entry")
    assert not calendar_entry_field.is_cached(result_without)

    result_with = Puzzle.objects.with_calendar_entry().first()
    assert calendar_entry_field.is_cached(result_with)


def test_puzzle_manager_with_solves_by_user():
    """Custom model manager method with_solves_by_user annotates returned queryset with
    is_solved."""
    PuzzleFactory()
    user = UserFactory()

    result_without = Puzzle.objects.first()
    assert not hasattr(result_without, "is_solved")

    result_with = Puzzle.objects.with_solves_by_user(user).first()
    assert hasattr(result_with, "is_solved")
    assert not result_with.is_solved

    guess_submit(result_with, user, result_with.answer)
    result_with_after_solve = Puzzle.objects.with_solves_by_user(user).first()
    assert hasattr(result_with_after_solve, "is_solved")
    assert result_with_after_solve.is_solved


def test_available_puzzle_manager():
    """AvailablePuzzleManager filters out puzzles that are not available yet."""
    puzzle_avail = PuzzleFactory(available_at=timezone.now() - timezone.timedelta(days=1))
    puzzle_not_avail = PuzzleFactory(available_at=timezone.now() + timezone.timedelta(days=1))

    assert set(Puzzle.objects.all()) == {puzzle_avail, puzzle_not_avail}
    assert set(Puzzle.available.all()) == {puzzle_avail}