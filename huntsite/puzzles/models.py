from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from huntsite.puzzles.utils import clean_answer, normalize_answer


class GuessEvaluation(models.TextChoices):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    KEEP_GOING = "keep_going"


class PuzzleQuerySet(models.QuerySet):
    """Custom QuerySet for the Puzzle model with some useful methods."""

    def with_calendar_entry(self):
        return self.select_related("calendar_entry")

    def with_solves_by_user(self, user):
        return self.annotate(
            is_solved=models.Exists(Solve.objects.filter(user=user, puzzle=models.OuterRef("pk")))
        )


class AvailablePuzzleManager(models.Manager):
    """Custom Manager for the Puzzle model that only returns puzzles that are available."""

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(available_at__lte=timezone.now())


class Puzzle(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    answer = models.CharField(max_length=255)
    answer_normalized = models.CharField(max_length=255, editable=False)
    keep_going_answers = models.JSONField(null=False, blank=True, default=list)
    keep_going_answers_normalized = models.JSONField(
        null=False, blank=True, default=list, editable=False
    )

    pdf_url = models.URLField()

    available_at = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PuzzleQuerySet.as_manager()
    available = AvailablePuzzleManager.from_queryset(PuzzleQuerySet)()

    class Meta:
        default_manager_name = "objects"

    def __str__(self):
        return self.name

    def get_url(self):
        """Returns the URL for the detail page of the puzzle."""
        return reverse("puzzle_detail", kwargs={"slug": self.slug})

    def clean(self):
        self.answer = clean_answer(self.answer)
        self.keep_going_answers = [clean_answer(ans) for ans in self.keep_going_answers]

    def save(self, *args, **kwargs):
        self.answer_normalized = normalize_answer(self.answer)
        self.keep_going_answers_normalized = [
            normalize_answer(ans) for ans in self.keep_going_answers
        ]
        super().save(*args, **kwargs)


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

    def __str__(self):
        return (
            f"{self.user.team_name} - {self.puzzle.name} - {self.text} - {self.display_evaluation}"
        )


class Solve(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "puzzle")

    def __str__(self):
        return f"{self.user.team_name} - {self.puzzle.name} - {self.created_at}"


class AdventCalendarEntry(models.Model):
    puzzle = models.OneToOneField(Puzzle, on_delete=models.CASCADE, related_name="calendar_entry")
    day = models.IntegerField(default=-1)

    class Meta:
        verbose_name_plural = "Advent Calendar Entries"

    def __str__(self):
        return f"{self.day} | {self.puzzle.name}"


@receiver(post_save, sender=Puzzle)
def create_advent_calendar_entry(sender, instance, created, **kwargs):
    if created:
        calendar_entry = AdventCalendarEntry(puzzle=instance)
        calendar_entry.full_clean()
        calendar_entry.save()
