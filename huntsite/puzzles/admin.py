from django import forms
from django.contrib import admin

import huntsite.puzzles.models as models


class UneditableAsReadOnlyAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in obj._meta.fields if not field.editable]
        return []


class PuzzleAdminForm(forms.ModelForm):
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


class PuzzleAdmin(UneditableAsReadOnlyAdmin):
    form = PuzzleAdminForm


admin.site.register(models.Puzzle, PuzzleAdmin)
admin.site.register(models.Guess, UneditableAsReadOnlyAdmin)
admin.site.register(models.Solve, UneditableAsReadOnlyAdmin)
admin.site.register(models.AdventCalendarEntry, UneditableAsReadOnlyAdmin)
