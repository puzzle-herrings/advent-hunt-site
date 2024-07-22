import pytest

from huntsite.puzzles.models import AdventCalendarEntry, Puzzle

pytestmark = pytest.mark.django_db


@pytest.fixture
def puzzle():
    return Puzzle.objects.create(
        name="Test Puzzle",
        slug="test-puzzle",
        answer="TEST ANSWER",
    )


def test_puzzle_create(puzzle):
    """Create a puzzle and automatically create a advent calendar entry"""
    puzzle = Puzzle.objects.create(
        name="A New Puzzle",
        slug="a-new-puzzle",
        answer="A NEW ANSWER",
    )

    assert AdventCalendarEntry.objects.get(puzzle=puzzle)


def test_puzzle_detail_view(puzzle, client):
    pass
