from django.db import transaction
from loguru import logger

from huntsite.puzzles.models import Finish, Guess, GuessEvaluation, Puzzle, Solve
from huntsite.puzzles.utils import normalize_answer

ALREADY_SUBMITTED = object()
"""Sentinel object to indicate that a guess has already been submitted."""


@transaction.atomic
def guess_submit(puzzle: Puzzle, user, guess_text: str) -> GuessEvaluation:
    """Function to handle the submission of a guess to a puzzle."""
    logger.trace(
        "Team '{user.team_name}' submitted guess for puzzle {puzzle}: {guess}",
        user=user,
        puzzle=puzzle,
        guess=guess_text,
    )
    guess_text_normalized = normalize_answer(guess_text)

    # Check if guess already exists
    if Guess.objects.filter(
        user=user, puzzle=puzzle, text_normalized=guess_text_normalized
    ).exists():
        logger.trace("Guess was 'already_submitted'.")
        return ALREADY_SUBMITTED

    if guess_text_normalized == puzzle.answer_normalized:
        evaluation = GuessEvaluation.CORRECT
    elif guess_text_normalized in puzzle.keep_going_answers_normalized:
        evaluation = GuessEvaluation.KEEP_GOING
    else:
        evaluation = GuessEvaluation.INCORRECT

    logger.trace("Guess was '{evaluation}'.", evaluation=evaluation)

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
        solve = Solve(user=user, puzzle=puzzle)
        solve.full_clean()
        solve.save()

        logger.info("Team '{user.team_name}' solved puzzle '{puzzle}'!", user=user, puzzle=puzzle)

        if hasattr(puzzle, "meta_info") and puzzle.meta_info.is_final:
            finish = Finish(user=user)
            finish.full_clean()
            finish.save()
            user.is_finished = True
            user.save()

            logger.info("Team {user.team_name} finished the hunt!", user=user)

    return evaluation
