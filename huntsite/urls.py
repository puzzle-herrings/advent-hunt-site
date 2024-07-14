import django.contrib.auth.views
from django.urls import include, path, reverse

import huntsite.views as views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("about/", views.about_page, name="about"),
    path("puzzles/", include("huntsite.puzzles.urls")),
    # path("accounts/", include("django.contrib.auth.urls")),
    # path(
    #     "accounts/logout/",
    #     django.contrib.auth.views.LogoutView.as_view(next_page="/"),
    #     name="logout",
    # ),
]
