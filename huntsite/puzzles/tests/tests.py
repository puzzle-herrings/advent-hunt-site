from django.utils import timezone
import pytest

from huntsite.puzzles.admin import PuzzleAdminForm
from huntsite.puzzles.factories import PuzzleFactory
from huntsite.puzzles.models import AdventCalendarEntry, Puzzle
from huntsite.puzzles.services import guess_submit
from huntsite.teams.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def puzzle():
    return PuzzleFactory()


@pytest.fixture()
def user():
    return UserFactory()


def test_puzzle_create(puzzle):
    """Creating a puzzle automatically create a advent calendar entry"""
    puzzle = Puzzle.objects.create(
        name="A New Puzzle",
        slug="a-new-puzzle",
        answer="A NEW ANSWER",
    )
    assert AdventCalendarEntry.objects.get(puzzle=puzzle)


def test_puzzle_manager_with_calendar_entry(puzzle):
    """Custom model manager method with_calendar_entry selects related calendar_entry."""

    calendar_entry_field = Puzzle._meta.get_field("calendar_entry")

    result_without = Puzzle.objects.first()
    assert not calendar_entry_field.is_cached(result_without)

    result_with = Puzzle.objects.with_calendar_entry().first()
    assert calendar_entry_field.is_cached(result_with)


def test_puzzle_manager_with_solves_by_user(puzzle, user):
    """Custom model manager method with_solves_by_user annotates returned queryset with
    is_solved."""

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


def test_puzzle_admin_form():
    """PuzzleAdminForm should handle keep_going_answers_ field correctly."""

    # keep_going_answers_ should be split and saved as keep_going_answers
    form = PuzzleAdminForm(
        data={
            "name": "A New Puzzle",
            "slug": "a-new-puzzle",
            "answer": "A NEW ANSWER",
            "pdf_url": "https://example.com/example.pdf",
            "available_at": timezone.now(),
            "keep_going_answers_": "A NEW ANSWER\nANOTHER ANSWER",
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["keep_going_answers"] == ["A NEW ANSWER", "ANOTHER ANSWER"]
    puzzle = form.save()
    assert puzzle.keep_going_answers == ["A NEW ANSWER", "ANOTHER ANSWER"]

    # Initial value populates from existing value of keep_going_answers
    form2 = PuzzleAdminForm(instance=puzzle)
    assert form2["keep_going_answers_"].initial == "A NEW ANSWER\nANOTHER ANSWER"

    # Setting keep_going_answers_ to empty string should clear keep_going_answers
    form3 = PuzzleAdminForm({}, instance=puzzle)
    form3.data = (
        form3.data
        | {field.name: form3[field.name].initial for field in form}
        | {"keep_going_answers_": ""}
    )
    assert form3.is_valid(), form3.errors
    assert form3.cleaned_data["keep_going_answers"] == []
    puzzle = form3.save()
    assert puzzle.keep_going_answers == []


def test_puzzle_detail_view(puzzle, client):
    pass
