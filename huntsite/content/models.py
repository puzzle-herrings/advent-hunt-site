from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
import markdown


class AboutEntry(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    order_by = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "About Entries"

    def __str__(self):
        return self.title

    def render_content(self):
        return markdown.markdown(self.content)


class StoryEntry(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    order_by = models.IntegerField(default=0)
    puzzle = models.OneToOneField("puzzles.Puzzle", on_delete=models.CASCADE)
    is_final = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Story Entries"

    def __str__(self):
        return self.title

    def clean(self):
        if self.is_final and self.puzzle is None:
            raise ValidationError("Final story entries must be associated with a puzzle.")

    def render_content(self):
        return markdown.markdown(self.content)


class AttributionsEntry(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    order_by = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Attributions Entries"

    def __str__(self):
        return self.title

    def render_content(self):
        return markdown.markdown(self.content)


class UpdateEntry(models.Model):
    content = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Update Entries"

    def __str__(self):
        return self.content[:64] + "..."

    def render_content(self):
        return markdown.markdown(self.content)
