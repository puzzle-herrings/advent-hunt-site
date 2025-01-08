from django.contrib import admin
from solo.admin import SingletonModelAdmin

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


@admin.register(models.AttributionsEntry)
class AttributionsEntryAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("title", "order_by")
    ordering = ("order_by",)


@admin.register(models.UpdateEntry)
class UpdateEntryAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("__str__", "published_at")
    ordering = ("-published_at",)


admin.site.register(models.WrapupEntry, SingletonModelAdmin)
