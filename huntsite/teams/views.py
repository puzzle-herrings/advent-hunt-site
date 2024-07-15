from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

from huntsite.teams.forms import AccountManagementForm


@login_required
def account_manage(request):
    """View to manage the account of the user."""
    user = request.user
    context = {
        "user": user,
        "form": AccountManagementForm(instance=user),
    }
    return TemplateResponse(request, "account.html", context)
