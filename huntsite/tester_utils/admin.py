from django.contrib import admin

from huntsite.admin import UneditableAsReadOnlyAdminMixin
import huntsite.tester_utils.models as models


@admin.register(models.TimeTravel)
class TimeTravelAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("user", "team_name")
    list_select_related = ("user",)
    search_fields = ("user", "user__team_name")
    ordering = ("-created_at",)

    @admin.display(description="Team Name")
    def team_name(self, obj):
        return obj.user.team_name
