import string

from django.utils import timezone
import pytest

from huntsite.puzzles.factories import PuzzleFactory
from huntsite.puzzles.models import AdventCalendarEntry, Puzzle
from huntsite.puzzles.services import guess_submit
from huntsite.teams.factories import UserFactory
from huntsite.teams.models import AnonymousUser

pytestmark = pytest.mark.django_db


def test_puzzle_create():
    """Creating a puzzle automatically create a advent calendar entry"""
    puzzle = Puzzle.objects.create(
        title="A New Puzzle",
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


def test_puzzle_manager_with_meta_info():
    """Custom model manager method with_calendar_entry selects related calendar_entry."""

    PuzzleFactory()

    result_without = Puzzle.objects.first()
    meta_info_field = Puzzle._meta.get_field("meta_info")
    assert not meta_info_field.is_cached(result_without)

    result_with = Puzzle.objects.with_meta_info().first()
    assert meta_info_field.is_cached(result_with)


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

    # Anonmymous user should not have any solves
    anon_user = AnonymousUser()
    result_with_anon = Puzzle.objects.with_solves_by_user(anon_user).first()
    assert hasattr(result_with_anon, "is_solved")
    assert not result_with_anon.is_solved


def test_available_puzzle_manager():
    """AvailablePuzzleManager filters out puzzles that are not available yet."""
    puzzle_avail = PuzzleFactory(available_at=timezone.now() - timezone.timedelta(days=1))
    puzzle_not_avail = PuzzleFactory(available_at=timezone.now() + timezone.timedelta(days=1))

    assert set(Puzzle.objects.all()) == {puzzle_avail, puzzle_not_avail}
    assert set(Puzzle.available.all()) == {puzzle_avail}


def test_puzzle_is_available():
    """Puzzle is_available property returns True if available_at is in the past."""
    puzzle_avail = PuzzleFactory(available_at=timezone.now() - timezone.timedelta(days=1))
    puzzle_not_avail = PuzzleFactory(available_at=timezone.now() + timezone.timedelta(days=1))

    assert puzzle_avail.is_available
    assert not puzzle_not_avail.is_available


def test_puzzle_solve_stats_and_guess_stats():
    puzzle1 = PuzzleFactory()
    puzzle2 = PuzzleFactory()
    puzzle3 = PuzzleFactory()

    users = [UserFactory() for _ in range(10)]
    admin = UserFactory(is_staff=True)
    tester = UserFactory(is_tester=True)
    inactive = UserFactory(is_active=False)

    # puzzle1 has no solves, no guesses

    # puzzle2 has 5 solves, 10 guesses
    for i in range(2):
        guess_submit(puzzle2, users[0], puzzle2.answer + string.ascii_uppercase[i])
    for i in range(3):
        guess_submit(puzzle2, users[-1], puzzle2.answer + string.ascii_uppercase[i])
    for user in users[:5]:
        guess_submit(puzzle2, user, puzzle2.answer)

    # puzzle3 has 1 solve, 8 guesses, and additional guesses from inactive/admin/tester users
    for i in range(7):
        guess_submit(puzzle3, users[i], puzzle3.answer + string.ascii_uppercase[i])
    guess_submit(puzzle3, users[-1], puzzle3.answer)
    for user in (admin, tester, inactive):
        guess_submit(puzzle3, user, puzzle3.answer + "WRONG")
        guess_submit(puzzle3, user, puzzle3.answer)

    puzzles = (
        Puzzle.objects.with_calendar_entry()
        .with_solve_stats()
        .with_guess_stats()
        .order_by("id")
        .all()
    )
    assert puzzles[0].id == puzzle1.id
    assert puzzles[0].num_solves == 0
    assert puzzles[0].num_guesses == 0
    assert puzzles[1].id == puzzle2.id
    assert puzzles[1].num_solves == 5
    assert puzzles[1].num_guesses == 10
    assert puzzles[2].id == puzzle3.id
    assert puzzles[2].num_solves == 1
    assert puzzles[2].num_guesses == 8
