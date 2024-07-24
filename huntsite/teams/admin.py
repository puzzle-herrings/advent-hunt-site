from django.contrib import admin

from huntsite.admin import UneditableAsReadOnlyAdminMixin
import huntsite.teams.models as models


@admin.register(models.User)
class UserAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "team_name",
        "is_staff",
        "is_active",
        "last_login",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email", "team_name")


@admin.register(models.TeamProfile)
class TeamProfileAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("user", "team_name")
    list_select_related = ("user",)
    search_fields = ("user", "user__team_name")

    @admin.display(description="Team Name")
    def team_name(self, obj):
        return obj.user.team_name
