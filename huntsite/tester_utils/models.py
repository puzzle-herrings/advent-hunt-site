from django.core.exceptions import ValidationError
from django.db import models


class TimeTravel(models.Model):
    user = models.OneToOneField("teams.User", on_delete=models.CASCADE, related_name="time_travel")
    time_traveling_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.is_active:
            if not self.user.is_tester:
                raise ValidationError("Only testers can time travel.")
