from enum import Enum

from huntsite.puzzles.models import Guess, Puzzle, Solve
from huntsite.puzzles.utils import normalize_answer


class GuessEvaluation(Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    ALREADY_SUBMITTED = "already_submitted"


def guess_submit(puzzle: Puzzle, user, guess_text: str) -> GuessEvaluation:
    """Function to handle the submission of a guess to a puzzle."""
    guess_text_normalized = normalize_answer(guess_text)

    # Check if guess already exists
    if Guess.objects.filter(
        user=user, puzzle=puzzle, text_normalized=guess_text_normalized
    ).exists():
        return GuessEvaluation.ALREADY_SUBMITTED

    is_correct = guess_text_normalized == puzzle.answer_normalized

    guess = Guess(
        user=user,
        puzzle=puzzle,
        text=guess_text,
        text_normalized=guess_text_normalized,
        is_correct=is_correct,
    )
    guess.full_clean()
    guess.save()

    if is_correct:
        solve, created = Solve.objects.get_or_create(user=user, puzzle=puzzle)
        if created:
            solve.full_clean()
            solve.save()

    return GuessEvaluation.CORRECT if is_correct else GuessEvaluation.INCORRECT
