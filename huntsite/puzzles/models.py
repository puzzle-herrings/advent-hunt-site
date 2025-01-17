import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Subquery, Value
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
import markdown

from huntsite.puzzles.utils import clean_answer, normalize_answer


class PuzzleQuerySet(models.QuerySet):
    """Custom QuerySet for the Puzzle model with some useful methods."""

    def with_calendar_entry(self):
        return self.select_related("calendar_entry")

    def with_meta_info(self):
        return self.select_related("meta_info")

    def with_canned_hints(self, as_of: datetime.datetime | None = None):
        as_of = as_of or timezone.now()
        return self.prefetch_related(
            models.Prefetch(
                "canned_hints",
                queryset=CannedHint.objects.filter(
                    puzzle__canned_hints_available_at__lte=as_of
                ).order_by("order_by"),
            )
        )

    def with_clipboard_data(self):
        return self.select_related("clipboard_data")

    def with_external_links(self):
        return self.prefetch_related(
            models.Prefetch("external_links", queryset=ExternalLink.objects.order_by("order_by"))
        )

    def with_errata(self):
        return self.prefetch_related(
            models.Prefetch("errata", queryset=Erratum.objects.order_by("-published_at"))
        )

    def with_solves_by_user(self, user):
        if user.is_anonymous:
            return self.annotate(is_solved=models.Value(False, output_field=models.BooleanField()))
        return self.annotate(
            is_solved=models.Exists(Solve.objects.filter(user=user, puzzle=models.OuterRef("pk")))
        )

    def with_attributions_entry(self):
        return self.select_related("attributions_entry")

    def filter_available_at(self, dt: datetime.datetime):
        return self.filter(available_at__lte=dt)

    def with_solve_stats(self):
        solves_count = (
            Solve.objects.filter(puzzle=models.OuterRef("pk"))
            .filter(
                user__is_active=True,
                user__is_staff=False,
                user__is_tester=False,
            )
            .values("puzzle")
            .annotate(c=Count("*"))
            .values("c")
        )
        return self.annotate(num_solves=Coalesce(Subquery(solves_count), Value(0)))

    def with_guess_stats(
        self,
        annotate_name="num_guesses",
        filter_evaluations: list["GuessEvaluation"] | None = None,
    ):
        guesses = Guess.objects.filter(puzzle=models.OuterRef("pk")).filter(
            user__is_active=True,
            user__is_staff=False,
            user__is_tester=False,
        )
        if filter_evaluations is not None:
            guesses = guesses.filter(evaluation__in=filter_evaluations)
        guesses_count = guesses.values("puzzle").annotate(c=Count("*")).values("c")
        annotation = {annotate_name: Coalesce(Subquery(guesses_count), Value(0))}
        return self.annotate(**annotation)


class AvailablePuzzleManager(models.Manager):
    """Custom Manager for the Puzzle model that only returns puzzles that are available."""

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter_available_at(timezone.now())


class Puzzle(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    answer = models.CharField(max_length=255)
    answer_normalized = models.CharField(max_length=255, editable=False)
    keep_going_answers = models.JSONField(null=False, blank=True, default=list)
    keep_going_answers_normalized = models.JSONField(
        null=False, blank=True, default=list, editable=False
    )

    pdf_url = models.URLField()
    solution_pdf_url = models.URLField(blank=True)

    available_at = models.DateTimeField(default=timezone.now)

    canned_hints_available_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PuzzleQuerySet.as_manager()
    available = AvailablePuzzleManager.from_queryset(PuzzleQuerySet)()

    class Meta:
        default_manager_name = "objects"

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.available_at <= timezone.now()

    @property
    def is_hints_available(self):
        return self.canned_hints_available_at and self.canned_hints_available_at <= timezone.now()

    def get_absolute_url(self):
        """Returns the URL for the detail page of the puzzle."""
        return reverse("puzzle_detail", kwargs={"slug": self.slug})

    def get_solution_absolute_url(self):
        """Returns the URL for the detail page of the puzzle."""
        return reverse("puzzle_solution", kwargs={"slug": self.slug})

    def clean(self):
        self.answer = clean_answer(self.answer)
        self.keep_going_answers = [clean_answer(ans) for ans in self.keep_going_answers]

    def save(self, *args, **kwargs):
        self.answer_normalized = normalize_answer(self.answer)
        self.keep_going_answers_normalized = [
            normalize_answer(ans) for ans in self.keep_going_answers
        ]
        super().save(*args, **kwargs)


class MetapuzzleInfo(models.Model):
    puzzle = models.OneToOneField(Puzzle, on_delete=models.CASCADE, related_name="meta_info")
    icon = models.CharField(max_length=255, blank=False)
    is_final = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Metapuzzle Info"

    def clean(self):
        if self.is_final:
            if MetapuzzleInfo.objects.filter(is_final=True).exclude(pk=self.pk).exists():
                raise ValidationError("There can only be one final metapuzzle.")


class CannedHint(models.Model):
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, related_name="canned_hints")
    keywords = models.CharField(max_length=255, blank=False)
    text = models.TextField()
    order_by = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def render_keywords(self):
        return markdown.markdown(self.keywords).removeprefix("<p>").removesuffix("</p>")

    def render_text(self):
        return markdown.markdown(self.text).removeprefix("<p>").removesuffix("</p>")


class ClipboardData(models.Model):
    """Model for clipboard data related to a puzzle that users can copy when viewing a puzzle
    detail page."""

    puzzle = models.OneToOneField(
        Puzzle, on_delete=models.CASCADE, related_name="clipboard_data", primary_key=True
    )
    text = models.TextField()

    class Meta:
        verbose_name_plural = "Clipboard Data"


class ExternalLink(models.Model):
    """Model for external links related to a puzzle that will be displayed on the puzzle detail
    page."""

    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, related_name="external_links")
    html = models.CharField(
        default='<i class="bi bi-box-arrow-up-right"></i>',
        max_length=255,
        help_text="HTML displayed for the link (child of <a> tag).",
    )
    description = models.CharField(max_length=255)
    url = models.URLField()
    order_by = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "External Links"

    def __str__(self):
        return f"{self.puzzle.title} - {self.description}"


class Erratum(models.Model):
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, related_name="errata")
    text = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Errata"

    def __str__(self):
        return f"{self.puzzle.title} - {self.created_at}"


class PuzzleAttributionsEntry(models.Model):
    puzzle = models.OneToOneField(
        Puzzle, on_delete=models.CASCADE, related_name="attributions_entry", primary_key=True
    )
    content = models.TextField()

    class Meta:
        verbose_name_plural = "Puzzle Attributions"

    def render(self):
        return markdown.markdown(self.content)


class GuessEvaluation(models.TextChoices):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    KEEP_GOING = "keep_going"


class Guess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, editable=False)
    text = models.CharField(max_length=255, editable=False)
    text_normalized = models.CharField(max_length=255, editable=False)
    evaluation = models.CharField(max_length=255, choices=GuessEvaluation, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Guesses"

    @property
    def display_evaluation(self):
        match self.evaluation:
            case GuessEvaluation.CORRECT:
                return "Correct"
            case GuessEvaluation.INCORRECT:
                return "Incorrect"
            case GuessEvaluation.KEEP_GOING:
                return "Keep going!"

    def clean(self):
        self.text = clean_answer(self.text)

    def to_dict(self):
        """Returns a dictionary representation of the Guess object that can be serialized as
        JSON."""
        return {
            "team": self.user.team_name,
            "puzzle": self.puzzle.title,
            "text": self.text,
            "evaluation": self.display_evaluation,
            "timestamp": self.created_at.isoformat(),
        }

    def __str__(self):
        return " - ".join(
            [
                self.user.team_name,
                self.puzzle.title,
                self.text,
                self.display_evaluation,
            ]
        )


class Solve(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "puzzle")

    def to_dict(self):
        """Returns a dictionary representation of the Solve object that can be serialized as
        JSON."""
        return {
            "team": self.user.team_name,
            "puzzle": self.puzzle.title,
            "timestamp": self.created_at.isoformat(),
        }

    def __str__(self):
        return f"{self.user.team_name} - {self.puzzle.title} - {self.created_at}"


class Finish(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Finishes"

    def __str__(self):
        return f"{self.user.team_name} - {self.created_at}"


class AdventCalendarEntry(models.Model):
    puzzle = models.OneToOneField(
        Puzzle, on_delete=models.CASCADE, primary_key=True, related_name="calendar_entry"
    )
    day = models.IntegerField(default=-1)

    class Meta:
        verbose_name_plural = "Advent Calendar Entries"

    def __str__(self):
        return f"{self.day} | {self.puzzle.title}"


@receiver(post_save, sender=Puzzle)
def create_advent_calendar_entry(sender, instance, created, **kwargs):
    if created:
        calendar_entry = AdventCalendarEntry(puzzle=instance)
        calendar_entry.full_clean()
        calendar_entry.save()
