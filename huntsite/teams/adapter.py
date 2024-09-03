from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        if getattr(settings, "ACCOUNT_DISABLE_REGISTRATION", False):
            return False
        return super().is_open_for_signup(request)

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.team_name = form.cleaned_data.get("team_name", "").strip()
        user.full_clean()
        if commit:
            user.save()
