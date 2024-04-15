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

class AnswerSubmission(models.Model):
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    submitted_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team.team_name} - {self.puzzle.name} - {self.submission}"

class Solve(models.Model):
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    solved_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.team_name} - {self.puzzle.name} - {self.solved_datetime}"
