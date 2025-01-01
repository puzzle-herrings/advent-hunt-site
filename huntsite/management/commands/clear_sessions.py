from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Force logout all users by clearing sessions"

    def handle(self, *args, **kwargs):
        # Clear database sessions
        self.stderr.write("Clearing all sessions.")
        Session.objects.all().delete()
        self.stderr.write(self.style.SUCCESS("All sessions cleared."))
        if "cached_db" in settings.SESSION_ENGINE:
            # Clear cached sessions
            self.stderr.write("Using cached_db session engine. Clearing cache.")
            cache.clear()
            self.stderr.write(self.style.SUCCESS("Cache is cleared."))
