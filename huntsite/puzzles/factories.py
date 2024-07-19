from django.conf import settings
from django.db.models.signals import post_save
import factory
import factory.fuzzy
from faker import Faker

fake = Faker()

MOCK_PUZZLES = [
    f"{settings.BASE_URL}/static/mock_puzzles/{mock_file.name}"
    for mock_file in (settings.BASE_DIR / "static" / "mock_puzzles").glob("*.pdf")
]


@factory.django.mute_signals(post_save)
class PuzzleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "puzzles.Puzzle"

    name = factory.lazy_attribute(lambda _: " ".join(fake.words(nb=3)).title())
    slug = factory.Faker("slug")
    answer = factory.lazy_attribute(lambda _: " ".join(fake.words(nb=2)).title())
    pdf_url = factory.fuzzy.FuzzyChoice(MOCK_PUZZLES)

    calendar_entry = factory.RelatedFactory(
        "huntsite.puzzles.factories.AdventCalendarEntryFactory",
        factory_related_name="puzzle",
    )


class GuessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "puzzles.Guess"

    user = factory.SubFactory("users.factories.UserFactory")
    puzzle = factory.SubFactory(PuzzleFactory)
    text = factory.Faker("word")
    is_correct = factory.Faker("boolean")


class CorrectGuessFactory(GuessFactory):
    is_correct = True

    @factory.post_generation
    def text(self, create, extracted, **kwargs):
        self.text = self.puzzle.answer


class IncorrectGuessFactory(GuessFactory):
    is_correct = False

    @factory.post_generation
    def text(self, create, extracted, **kwargs):
        word = factory.Faker("word")
        while word == self.puzzle.answer:
            word = factory.Faker("word")
        self.text = word


@factory.django.mute_signals(post_save)
class AdventCalendarEntryFactory(factory.django.DjangoModelFactory):
    puzzle = factory.SubFactory(
        "huntsite.puzzles.factories.PuzzleFactory", calendar_entry=None
    )

    class Meta:
        model = "puzzles.AdventCalendarEntry"
