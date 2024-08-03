from textwrap import dedent

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
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


_ROBOTS_TXT_DISALLOW_ALL = dedent(
    """\
    User-agent: *
    Disallow: /
    """
)


def robots_disallow_all(request):
    return HttpResponse(_ROBOTS_TXT_DISALLOW_ALL, content_type="text/plain")


def server_error(request):
    return TemplateResponse(request, "500.html", status=500)
