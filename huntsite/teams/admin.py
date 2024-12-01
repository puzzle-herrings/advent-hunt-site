from allauth.account.admin import EmailAddressAdmin as AllAuthEmailAddressAdmin
from allauth.account.models import EmailAddress
from django.contrib import admin
from django.utils.safestring import mark_safe
from django_admin_action_forms import action_with_form
from django_no_queryset_admin_actions import NoQuerySetAdminActionsMixin

from huntsite.admin import UneditableAsReadOnlyAdminMixin
from huntsite.emails import send_email
from huntsite.teams.forms import SendEmailAdminForm
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


@admin.register(models.Flair)
class FlairAdmin(admin.ModelAdmin):
    list_display = ("icon_safe", "label", "order_by")
    filter_horizontal = ("users",)

    @admin.display(description="Icon")
    @mark_safe
    def icon_safe(self, obj):
        return obj.icon


@action_with_form(SendEmailAdminForm, description="Send email to selected email addresses")
def send_email_to_selected(modeladmin, request, queryset, data):
    recipients = queryset.values_list("email", flat=True)
    send_email(subject=data["subject"], message=data["message"], recipient_list=recipients)
    modeladmin.message_user(request, f"Email sent to selected {queryset.count()} addresses.")


@action_with_form(SendEmailAdminForm, description="Send email to all email addresses")
def send_email_to_all(modeladmin, request, data):
    queryset = EmailAddress.objects.all()
    recipients = queryset.values_list("email", flat=True)
    send_email(subject=data["subject"], message=data["message"], recipient_list=recipients)
    modeladmin.message_user(request, f"Email sent to all ({queryset.count()}) addresses.")


admin.site.unregister(EmailAddress)  # Unregister allauth's default admin


@admin.register(EmailAddress)
class EmailAddressAdmin(NoQuerySetAdminActionsMixin, AllAuthEmailAddressAdmin):
    actions = [send_email_to_selected, send_email_to_all]
    no_queryset_actions = [send_email_to_all]
