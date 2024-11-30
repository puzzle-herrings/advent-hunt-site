from django.conf import settings
from django.db import models


class OrganizerDashboardPermission(models.Model):
    """A model that stores the permissions for the organizer dashboard."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organizer_dashboard_permission",
        primary_key=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Organizer Dashboard Permission"
        verbose_name_plural = "Organizer Dashboard Permissions"
