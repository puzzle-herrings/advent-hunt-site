from django.contrib import admin

from huntsite.admin import UneditableAsReadOnlyAdminMixin
import huntsite.content.models as models


@admin.register(models.AboutEntry)
class AboutEntryAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("title", "order_by")
    ordering = ("order_by",)


@admin.register(models.StoryEntry)
class StoryEntryAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("title", "order_by", "puzzle")
    ordering = ("order_by",)
