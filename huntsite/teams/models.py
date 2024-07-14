from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    team_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="How the team will be publicly displayed.",
    )


class TeamProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TeamMember(models.Model):
    """A person on a team."""

    team = models.ForeignKey(TeamProfile, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
