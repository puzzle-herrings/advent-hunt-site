from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

from huntsite.teams.forms import AccountManagementForm


def home_page(request):
    return TemplateResponse(request, "home.html", {})


@login_required
def account_manage(request):
    """View to manage the account of the user."""
    user = request.user
    context = {
        "form": AccountManagementForm(instance=user),
    }
    return TemplateResponse(request, "account.html", context)


def robots_txt(request):
    context = {
        "robots_disallow_all": False,
    }
    return TemplateResponse(request, "robots.txt", context, content_type="text/plain")


def server_error(request):
    return TemplateResponse(request, "500.html", status=500)
