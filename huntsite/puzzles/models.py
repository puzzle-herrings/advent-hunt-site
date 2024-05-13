from django.conf import settings
from django.db import models
from django.urls import reverse
import shortuuid


def get_puzzle_pdf_upload_path(instance, filename):
    slug = instance.slug
    uuid = shortuuid.uuid()
    return f"puzzles/{slug}-{uuid}.pdf"


class Puzzle(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    answer = models.CharField(max_length=255)

    pdf_file = models.FileField(upload_to=get_puzzle_pdf_upload_path)

    def __str__(self):
        return self.name

    def get_url(self):
        return reverse("puzzle_detail", kwargs={"slug": self.slug})


class Guess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def response(self):
        return "Correct" if self.is_correct else "Incorrect"

    def __str__(self):
        return f"{self.user.teamprofile.team_name} - {self.puzzle.name} - {self.text} - {self.response}"


class Solve(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "puzzle")

    def __str__(self):
        return f"{self.user.teamprofile.team_name} - {self.puzzle.name} - {self.solved_datetime}"
