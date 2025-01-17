from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path

from huntsite.sitemaps import StaticViewSitemap
import huntsite.views as views

sitemaps = {
    "static": StaticViewSitemap,
}


urlpatterns = [
    path("", views.home_page, name="home"),
    path("", include("huntsite.content.urls")),
    path("", include("huntsite.teams.urls")),
    path("puzzles/", include("huntsite.puzzles.urls")),
    path("testing/", include("huntsite.tester_utils.urls")),
    path("health/", views.health, name="health"),
    path("500/", views.server_error, name="server_error"),
    (
        path("robots.txt", views.robots_disallow_all, name="robots_disallow_all")
        if settings.ROBOTS_DISALLOW_ALL
        else re_path(r"^robots\.txt", include("robots.urls"))
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("trigger-server-error/", views.trigger_server_error, name="trigger_server_error"),
]
