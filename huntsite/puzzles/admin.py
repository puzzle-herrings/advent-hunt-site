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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.instance:
            # Hide keep_going_answers field
            self.fields["keep_going_answers"].widget = forms.HiddenInput()

            # Populate the keep_going_answers_ field with real keep_going_answers model field
            self.fields["keep_going_answers_"].initial = "\n".join(
                self.instance.keep_going_answers
            )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("keep_going_answers_").strip():
            cleaned_data["keep_going_answers"] = [
                ans.strip() for ans in cleaned_data["keep_going_answers_"].split("\n")
            ]
        else:
            cleaned_data["keep_going_answers"] = []
        return cleaned_data


@admin.register(models.Puzzle)
class PuzzleAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    form = PuzzleAdminForm
    list_display = ("name", "answer", "calendar_entry_day", "available_at")
    ordering = ("calendar_entry__day",)

    @admin.display(description="Calendar Entry Day")
    def calendar_entry_day(self, obj):
        return obj.calendar_entry.day


@admin.register(models.Guess)
class GuessAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "puzzle", "text", "evaluation", "created_at")
    list_filter = ("puzzle", "evaluation")
    search_fields = ("user__username",)
    ordering = ("-created_at",)


@admin.register(models.Solve)
class SolveAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "puzzle", "created_at")
    list_filter = ("puzzle",)
    ordering = ("-created_at",)


@admin.register(models.AdventCalendarEntry)
class AdventCalendarEntryAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("day", "puzzle")
    ordering = ("day",)
