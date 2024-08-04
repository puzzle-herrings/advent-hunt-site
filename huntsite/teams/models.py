from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DefaultUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserQuerySet(models.QuerySet):
    """Custom QuerySet for the Puzzle model with some useful methods."""

    def with_profile(self):
        return self.select_related("profile")


class UserManager(DefaultUserManager.from_queryset(UserQuerySet)):
    pass


class NonprivilegedUserManager(models.Manager):
    """Custom Manager for the Puzzle model that only returns puzzles that are available."""

    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .filter(is_tester=False)
            .filter(is_staff=False)
            .filter(is_superuser=False)
        )


class User(AbstractUser):
    team_name = models.CharField(
        max_length=127,
        unique=True,
        blank=False,
        help_text="How the team will be publicly displayed.",
    )
    is_tester = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False, editable=False)

    REQUIRED_FIELDS = ["team_name"]

    objects = UserManager()
    nonprivileged = NonprivilegedUserManager.from_queryset(UserQuerySet)()

    def save(self, *args, **kwargs):
        if self.is_staff:
            self.is_tester = True
        super().save(*args, **kwargs)


class TeamProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="profile"
    )
    members = models.CharField(
        max_length=255,
        blank=True,
        help_text="Who is on your team? Will be publicly shown on your team profile.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=User)
def create_team_profile(sender, instance, created, **kwargs):
    if created:
        TeamProfile.objects.create(user=instance)
