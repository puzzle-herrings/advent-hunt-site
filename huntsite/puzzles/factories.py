import random

from django.conf import settings
from django.db.models.signals import post_save
from django.utils import timezone
import factory
import factory.fuzzy
from faker import Faker

fake = Faker()

MOCK_PUZZLES = [
    f"{settings.BASE_URL}/static/mock_puzzles/{mock_file.name}"
    for mock_file in (settings.BASE_DIR / "static" / "mock_puzzles").glob("*.pdf")
]


def title_text_factory() -> str:
    nb = random.randint(2, 5)
    return " ".join(fake.word() for _ in range(nb)).title()


def answer_text_factory() -> str:
    nb = random.randint(1, 2)
    return " ".join(fake.word() for _ in range(nb)).upper()


@factory.django.mute_signals(post_save)
class PuzzleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "puzzles.Puzzle"
        skip_postgeneration_save = True

    name = factory.LazyFunction(title_text_factory)
    slug = factory.Faker("slug")
    answer = factory.LazyFunction(answer_text_factory)
    pdf_url = factory.fuzzy.FuzzyChoice(MOCK_PUZZLES)
    available_at = factory.LazyFunction(timezone.now)

    calendar_entry = factory.RelatedFactory(
        "huntsite.puzzles.factories.AdventCalendarEntryFactory",
        factory_related_name="puzzle",
    )


class MetapuzzleInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "puzzles.MetapuzzleInfo"

    puzzle = factory.SubFactory(PuzzleFactory)
    icon = factory.Faker("emoji")
    is_final = False


@factory.django.mute_signals(post_save)
class AdventCalendarEntryFactory(factory.django.DjangoModelFactory):
    puzzle = factory.SubFactory("huntsite.puzzles.factories.PuzzleFactory", calendar_entry=None)

    class Meta:
        model = "puzzles.AdventCalendarEntry"
