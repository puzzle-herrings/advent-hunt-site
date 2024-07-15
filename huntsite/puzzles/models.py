from django.conf import settings
from django.db import models
from django.urls import reverse

from huntsite.puzzles.utils import clean_answer, normalize_answer


class Puzzle(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    answer = models.CharField(max_length=255)
    answer_normalized = models.CharField(max_length=255, editable=False)

    pdf_url = models.URLField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_url(self):
        """Returns the URL for the detail page of the puzzle."""
        return reverse("puzzle_detail", kwargs={"slug": self.slug})

    def clean(self):
        self.answer = clean_answer(self.answer)

    def save(self, *args, **kwargs):
        self.answer_normalized = normalize_answer(self.answer)
        super().save(*args, **kwargs)


class Guess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    text_normalized = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def evaluation(self):
        return "Correct" if self.is_correct else "Incorrect"

    def clean(self):
        self.text = clean_answer(self.text)

    def __str__(self):
        return f"{self.user.team_name} - {self.puzzle.name} - {self.text} - {self.evaluation}"


class Solve(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "puzzle")

    def __str__(self):
        return f"{self.user.teamprofile.team_name} - {self.puzzle.name} - {self.solved_datetime}"
