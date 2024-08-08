from textwrap import dedent

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_safe


@require_safe
def home_page(request):
    return TemplateResponse(request, "home.html", {})


_ROBOTS_TXT_DISALLOW_ALL = dedent(
    """\
    User-agent: *
    Disallow: /
    """
)


@require_safe
def health(request):
    return HttpResponse()


@require_safe
def robots_disallow_all(request):
    return HttpResponse(_ROBOTS_TXT_DISALLOW_ALL, content_type="text/plain")


@require_safe
def server_error(request):
    """If a redirect to a 500 server error is necessary."""
    return TemplateResponse(request, "500.html", status=500)


@staff_member_required
def trigger_server_error(request):
    """Throw a server error for testing purposes."""
    raise RuntimeError(f"Intentional server error by {request.user.username}")
