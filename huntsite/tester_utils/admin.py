from django.contrib import admin

from huntsite.admin import UneditableAsReadOnlyAdminMixin
import huntsite.tester_utils.models as models


@admin.register(models.OrganizerDashboardPermission)
class OrganizerDashboardPermissionAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username",)

    autocomplete_fields = ("user",)
