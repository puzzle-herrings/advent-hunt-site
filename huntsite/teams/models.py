from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    team_name = models.CharField(
        max_length=255,
        unique=True,
        blank=False,
        help_text="How the team will be publicly displayed.",
    )
    is_tester = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["team_name"]

    def save(self, *args, **kwargs):
        if self.is_staff:
            self.is_tester = True
        super().save(*args, **kwargs)


class TeamProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="profile"
    )
    members = models.CharField(max_length=255, blank=True, help_text="List of team members.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=User)
def create_team_profile(sender, instance, created, **kwargs):
    if created:
        TeamProfile.objects.create(user=instance)
