from textwrap import dedent

from django.http import HttpResponse
from django.template.response import TemplateResponse


def home_page(request):
    return TemplateResponse(request, "home.html", {})


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
