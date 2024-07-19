from django.urls import include, path

import huntsite.views as views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("about/", views.about_page, name="about"),
    path("puzzles/", include("huntsite.puzzles.urls")),
    path("accounts/", include("huntsite.teams.urls")),
]
