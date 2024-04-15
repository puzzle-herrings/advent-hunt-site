from django.conf import settings
from django.db import models

class Team(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    team_name = models.CharField(max_length=255, unique=True)

    created_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.team_name
