from django.utils import timezone
import pytest

from huntsite.puzzles.admin import PuzzleAdminForm

pytestmark = pytest.mark.django_db


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
