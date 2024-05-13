from django.conf import settings
import factory
from fpdf import FPDF

from django.core.files import File


def create_pdf_file():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=64)
    pdf.cell(text="Hello", new_x="CENTER", align="C")
    pdf.output("tuto1.pdf")


class PuzzleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "puzzles.Puzzle"

    name = factory.Faker("sentence", nb_words=4)
    slug = factory.Faker("slug")
    answer = factory.Faker("word")

    @factory.lazy_attribute
    def pdf_file(self):
        actual_filepath = str(
            settings.BASE_DIR / "puzzles" / "tests" / "assets" / "test_puzzle.pdf"
        )
        return File(open(actual_filepath, "rb"))


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
