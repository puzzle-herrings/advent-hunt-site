from django.conf import settings
import django.contrib.auth
from django.contrib.auth import get_user, logout
import django.contrib.auth.context_processors
from django.contrib.auth.context_processors import auth
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AnonymousUser as DefaultAnonymousUser
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
    """Custom Manager for the User model that only returns active nonprivileged users."""

    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .filter(is_active=True)
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


class AnonymousUser(DefaultAnonymousUser):
    """Custom AnonymousUser with additional fields from our custom User model."""

    team_name = "AnonymousUser"
    is_tester = False
    is_finished = False


def get_user_patched(request):
    """Patch the get_user function to return our custom AnonymousUser."""
    user = get_user(request)
    if isinstance(user, DefaultAnonymousUser):
        return AnonymousUser()
    return user


django.contrib.auth.get_user = get_user_patched


def logout_patched(request):
    """Patch the logout function to return our custom AnonymousUser."""
    logout(request)
    if isinstance(request.user, DefaultAnonymousUser):
        request.user = AnonymousUser()


django.contrib.auth.logout = logout_patched


def auth_patched(request):
    """Patch the auth context processor to return our custom AnonymousUser."""
    context = auth(request)
    if isinstance(context["user"], DefaultAnonymousUser):
        context["user"] = AnonymousUser()
        context["perms"].user = context["user"]
    return context


django.contrib.auth.context_processors.auth = auth_patched


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
