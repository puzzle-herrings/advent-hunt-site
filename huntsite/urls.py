from django.urls import include, path

import huntsite.views as views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("", include("huntsite.content.urls")),
    path("puzzles/", include("huntsite.puzzles.urls")),
    path("teams/", include("huntsite.teams.urls")),
    path("accounts/", views.account_manage, name="account_manage"),
    path("testing/", include("huntsite.tester_utils.urls")),
    path("500/", views.server_error, name="server_error"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
