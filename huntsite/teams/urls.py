from django.urls import include, path

import huntsite.teams.views as views

urlpatterns = [
    path("accounts/", views.account_manage, name="account_manage"),
    path("accounts/username/", views.account_username_update, name="account_username"),
    path("accounts/", include("allauth.urls")),
    path("teams/", views.team_list, name="team_list"),
    path("teams/<int:pk>/", views.team_detail, name="team_detail"),
]
