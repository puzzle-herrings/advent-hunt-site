from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        if getattr(settings, "ACCOUNT_DISABLE_REGISTRATION", False):
            return False
        return super().is_open_for_signup(request)
