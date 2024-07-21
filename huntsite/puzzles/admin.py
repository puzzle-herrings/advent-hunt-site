from django import forms
from django.contrib import admin

from huntsite.admin import UneditableAsReadOnlyAdminMixin
import huntsite.puzzles.models as models


class PuzzleAdminForm(UneditableAsReadOnlyAdminMixin, forms.ModelForm):
    # Custom field to replace the JSON entry for keep_going_answers_
    # New-line delimited text area for easier editing
    keep_going_answers_ = forms.CharField(
        widget=forms.Textarea(attrs={"rows": "3"}),
        required=False,
        help_text="One answer per line.",
    )

    class Meta:
        model = models.Puzzle
        fields = "__all__"
        exclude = ("keep_going_answers",)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.instance:
            # Populate the keep_going_answers_ field with real keep_going_answers model field
            self.fields["keep_going_answers_"].initial = "\n".join(
                self.instance.keep_going_answers
            )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("keep_going_answers_"):
            cleaned_data["keep_going_answers"] = list(
                cleaned_data.get("keep_going_answers_").split("\n")
            )

        return cleaned_data


class PuzzleAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    form = PuzzleAdminForm
    list_display = ("name", "answer")
    ordering = ("calendar_entry__day",)


class GuessAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "puzzle", "text", "evaluation", "created_at")
    list_filter = ("puzzle", "evaluation")
    search_fields = ("user__username",)


class SolveAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "puzzle", "created_at")
    list_filter = ("puzzle",)


class AdventCalendarEntryAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("day", "puzzle")


admin.site.register(models.Puzzle, PuzzleAdmin)
admin.site.register(models.Guess, GuessAdmin)
admin.site.register(models.Solve, SolveAdmin)
admin.site.register(models.AdventCalendarEntry, AdventCalendarEntryAdmin)
