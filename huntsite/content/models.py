import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
import markdown
from solo.models import SingletonModel


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


def _wrapup_entry_available_at_default():
    return timezone.now() + timezone.timedelta(days=30)


class WrapupEntry(SingletonModel):
    content = models.TextField()
    available_at = models.DateTimeField(default=_wrapup_entry_available_at_default)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Wrapup Entry"

    def is_available_at(self, dt: datetime.datetime):
        return self.available_at <= dt

    def render_content(self):
        return markdown.markdown(self.content)
