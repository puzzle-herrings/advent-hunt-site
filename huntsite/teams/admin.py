from django.contrib import admin

from huntsite.admin import UneditableAsReadOnlyAdminMixin
import huntsite.teams.models as models


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


class TeamProfileAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("user", "team_name")
    list_select_related = ("user",)
    search_fields = ("user", "user__team_name")

    @admin.display(description="Team Name")
    def team_name(self, obj):
        return obj.user.team_name


# Register your models here.
admin.site.register(models.User, UserAdmin)
admin.site.register(models.TeamProfile, TeamProfileAdmin)
