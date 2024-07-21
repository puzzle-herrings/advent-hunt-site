from django.contrib import admin

import huntsite.content.models as models


class UneditableAsReadOnlyAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in obj._meta.fields if not field.editable]
        return []


class StoryEntryAdmin(UneditableAsReadOnlyAdmin):
    list_display = ("title", "order_by", "puzzle")
    ordering = ("order_by",)


admin.site.register(models.AboutEntry, UneditableAsReadOnlyAdmin)
admin.site.register(models.StoryEntry, StoryEntryAdmin)
