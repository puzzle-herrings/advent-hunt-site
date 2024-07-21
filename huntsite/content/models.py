from django.db import models
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
    puzzle = models.OneToOneField(
        "puzzles.Puzzle", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    _PARAGRAPH_ATTRIBUTE_LIST = "{: .card_text }"

    class Meta:
        verbose_name_plural = "Story Entries"

    def __str__(self):
        return self.title

    def render_content(self):
        paragraphs = self.content.split("\n\n")
        content = "\n\n".join(para + f"\n{self._PARAGRAPH_ATTRIBUTE_LIST}" for para in paragraphs)
        return markdown.markdown(content, extensions=["attr_list"])
