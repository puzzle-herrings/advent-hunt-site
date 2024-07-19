from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

import huntsite.teams.models as models


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_team_profile(sender, instance, created, **kwargs):
    if created:
        models.TeamProfile.objects.create(user=instance)
