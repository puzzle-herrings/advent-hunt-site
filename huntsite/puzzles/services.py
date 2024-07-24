from django.db import transaction

from huntsite.puzzles.models import Guess, GuessEvaluation, Puzzle, Solve
from huntsite.puzzles.utils import normalize_answer

ALREADY_SUBMITTED = object()
"""Sentinel object to indicate that a guess has already been submitted."""


@transaction.atomic
def guess_submit(puzzle: Puzzle, user, guess_text: str) -> GuessEvaluation:
    """Function to handle the submission of a guess to a puzzle."""
    guess_text_normalized = normalize_answer(guess_text)

    # Check if guess already exists
    if Guess.objects.filter(
        user=user, puzzle=puzzle, text_normalized=guess_text_normalized
    ).exists():
        return ALREADY_SUBMITTED

    if guess_text_normalized == puzzle.answer_normalized:
        evaluation = GuessEvaluation.CORRECT
    elif guess_text_normalized in puzzle.keep_going_answers_normalized:
        evaluation = GuessEvaluation.KEEP_GOING
    else:
        evaluation = GuessEvaluation.INCORRECT

    guess = Guess(
        user=user,
        puzzle=puzzle,
        text=guess_text,
        text_normalized=guess_text_normalized,
        evaluation=evaluation,
    )
    guess.full_clean()
    guess.save()

    if evaluation == GuessEvaluation.CORRECT:
        solve, created = Solve.objects.get_or_create(user=user, puzzle=puzzle)
        if created:
            solve.full_clean()
            solve.save()

    return evaluation
