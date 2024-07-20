import random

from django.core.management.base import BaseCommand
from django.db import transaction

from huntsite.puzzles import factories as puzzle_factories
from huntsite.puzzles import services as puzzle_services
from huntsite.teams import factories as team_factories

PUZZLE_STARTED_PROP = 0.4
PUZZLE_SOLVED_PROP = 0.75
INCORRECTED_GUESS_MAX = 10


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            # Puzzles
            puzzles = []
            for i in range(24):
                puzzles.append(puzzle_factories.PuzzleFactory(calendar_entry__day=i + 1))

            # Teams
            users = []
            for i in range(10):
                users.append(
                    team_factories.UserFactory(
                        username=f"user{i}", password="hohohomerrychristmas!"
                    )
                )

            # Make guesses
            for puzzle in puzzles:
                for user in users:
                    if random.random() < PUZZLE_STARTED_PROP:
                        # Incorrect guesses
                        for _ in range(random.randint(0, INCORRECTED_GUESS_MAX)):
                            puzzle_services.guess_submit(
                                puzzle=puzzle,
                                user=user,
                                guess_text=puzzle_factories.answer_text_factory(),
                            )
                    if random.random() < PUZZLE_SOLVED_PROP:
                        puzzle_services.guess_submit(
                            puzzle=puzzle, user=user, guess_text=puzzle.answer
                        )

        self.stdout.write(self.style.SUCCESS("create_demo_data complete."))
