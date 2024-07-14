from django.contrib import admin

import huntsite.puzzles.models as models


class UneditableAsReadOnlyAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in obj._meta.fields if not field.editable]
        return []


admin.site.register(models.Puzzle, UneditableAsReadOnlyAdmin)
admin.site.register(models.Guess, UneditableAsReadOnlyAdmin)
admin.site.register(models.Solve, UneditableAsReadOnlyAdmin)
