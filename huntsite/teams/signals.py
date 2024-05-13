from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import huntsite.users.models as models


@receiver(post_save, sender=User)
def create_team_profile(sender, instance, created, **kwargs):
    if created:
        models.TeamProfile.objects.create(user=instance, name=instance.username)
