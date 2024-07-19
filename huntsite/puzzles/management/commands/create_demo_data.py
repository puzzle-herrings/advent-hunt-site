from django.core.management.base import BaseCommand
from django.db import transaction

from huntsite.puzzles.factories import PuzzleFactory


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            # Puzzles
            for i in range(24):
                PuzzleFactory(calendar_entry__day=i + 1)

        self.stdout.write(self.style.SUCCESS("create_demo_data complete."))
