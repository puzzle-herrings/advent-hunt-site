from django.contrib import admin

from huntsite.admin import UneditableAsReadOnlyAdminMixin
import huntsite.teams.models as models
from huntsite.teams.services import user_clear_password, user_deactivate


@admin.action(description="Deactivate selected users")
def deactivate_users(modeladmin, request, queryset):
    for user in queryset:
        user_deactivate(user)


@admin.action(description="Clear password for selected users")
def clear_user_passwords(modeladmin, request, queryset):
    for user in queryset:
        user_clear_password(user)


@admin.register(models.User)
class UserAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        "username",
        "email_display",
        "team_name",
        "is_tester",
        "is_staff",
        "is_active",
        "last_login",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email", "team_name")
    ordering = ("-date_joined",)
    actions = [clear_user_passwords, deactivate_users]

    @admin.display(description="Email")
    def email_display(self, obj):
        email = obj.email
        if email.endswith("@deactivated.adventhunt.com"):
            return email.replace("@deactivated.adventhunt.com", "")
        return obj.email


@admin.register(models.TeamProfile)
class TeamProfileAdmin(UneditableAsReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("user", "team_name")
    list_select_related = ("user",)
    search_fields = ("user", "user__team_name")
    ordering = ("-created_at",)

    @admin.display(description="Team Name")
    def team_name(self, obj):
        return obj.user.team_name
