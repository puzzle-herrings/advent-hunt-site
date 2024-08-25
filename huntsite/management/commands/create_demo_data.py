import random

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.utils import timezone
from environs import Env
from loguru import logger
from tqdm import tqdm, trange

from huntsite.content import factories as content_factories
from huntsite.puzzles import factories as puzzle_factories
from huntsite.puzzles import services as puzzle_services
from huntsite.teams import factories as team_factories

env = Env()
env.read_env()

ANY_PROGRESS_PROP = 0.8
PUZZLE_STARTED_PROP = 0.4
PUZZLE_SOLVED_PROP = 0.75
INCORRECTED_GUESS_MAX = 10


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        # Arguments
        # Options
        parser.add_argument(
            "--day-offset",
            action="store",
            dest="day_offset",
            default=10,
            help=(
                "How many days to offset the start of the hunt relative to now. 0 offset means"
                "puzzle day 1 is released now."
            ),
        )
        parser.add_argument(
            "--num-users",
            action="store",
            dest="num_users",
            default=50,
            help=("Number of regular users to create."),
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            # Puzzles
            logger.info("Creating puzzles...")
            puzzles = []
            for i in trange(25):
                puzzles.append(
                    puzzle_factories.PuzzleFactory(
                        available_at=(
                            timezone.now() - timezone.timedelta(days=1 + options["day_offset"] - i)
                        ),
                        calendar_entry__day=i,
                    )
                )

            # Puzzle zero has some keep going answers
            puzzles[0].keep_going_answers = [
                puzzle_factories.answer_text_factory() for _ in range(7)
            ]
            puzzles[0].full_clean()
            puzzles[0].save()

            # Puzzle zero has some errata
            for i in range(3):
                puzzle_factories.ErratumFactory(
                    puzzle=puzzles[0],
                    published_at=timezone.now() + timezone.timedelta(seconds=i * 10),
                )

            # Puzzles for days 7, 14, and 23 are metas. Puzzle 24 is the final.
            for day, icon in [(7, "🤶"), (14, "🦌"), (23, "🧸")]:
                puzzle_factories.MetapuzzleInfoFactory(puzzle=puzzles[day], icon=icon)
            puzzle_factories.MetapuzzleInfoFactory(puzzle=puzzles[24], icon="🎅", is_final=True)

            # Test users
            logger.info("Creating test users...")
            testers = []
            for i in trange(10):
                testers.append(
                    team_factories.UserFactory(
                        username=f"tester{i}", password="hohohomerrychristmas!", is_tester=True
                    )
                )

            # Teams
            logger.info("Creating regular users...")
            users = []
            for i in trange(options["num_users"]):
                users.append(
                    team_factories.UserFactory(
                        username=f"user{i}", password="hohohomerrychristmas!"
                    )
                )

            # Make guesses
            logger.info("Creating guesses...")
            for user in tqdm(users):
                if random.random() > ANY_PROGRESS_PROP:
                    # This user has no progress, skip
                    continue
                for puzzle in puzzles:
                    if puzzle.available_at > timezone.now():
                        # Puzzle is not yet available
                        continue
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

            # Make content
            logger.info("Creating about page content...")
            for about_entry_title in tqdm(
                [
                    "What is a puzzle hunt?",
                    "What is the format for this hunt?",
                    "How difficult is this hunt?",
                    "Who made this hunt?",
                ]
            ):
                content_factories.AboutEntryFactory(title=about_entry_title)

            logger.info("Creating story content...")
            for calendar_day, story_entry_title, is_final in tqdm(
                [
                    (7, "After helping Mrs. Claus...", False),
                    (14, "After helping Rudolph...", False),
                    (23, "After cleaning up the Toy Factory...", False),
                    (24, "You've found Santa!", True),
                ]
            ):
                related_puzzle = puzzles[calendar_day]
                content_factories.StoryEntryFactory(
                    title=story_entry_title, puzzle=related_puzzle, is_final=is_final
                )

        logger.success("create_demo_data complete.")
