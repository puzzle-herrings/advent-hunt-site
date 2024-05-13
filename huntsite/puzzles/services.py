from huntsite.puzzles.models import Guess, Puzzle, Solve


def guess_submit(puzzle: Puzzle, user, guess_text: str):
    """Function to handle the submission of a guess to a puzzle."""
    is_correct = guess_text == puzzle.answer

    guess = Guess(user=user, puzzle=puzzle, text=guess_text, is_correct=is_correct)
    guess.full_clean()
    guess.save()

    if is_correct:
        solve = Solve.objects.get_or_create(user=user, puzzle=puzzle)
        solve.full_clean()
        solve.save()
