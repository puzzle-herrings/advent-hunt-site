from django.contrib import admin

from huntsite.admin import UneditableAsReadOnlyAdminMixin
import huntsite.content.models as models


class AboutEntryAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("title", "order_by")
    ordering = ("order_by",)


class StoryEntryAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("title", "order_by", "puzzle")
    ordering = ("order_by",)


admin.site.register(models.AboutEntry, AboutEntryAdmin)
admin.site.register(models.StoryEntry, StoryEntryAdmin)
