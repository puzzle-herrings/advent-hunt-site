from django.urls import path

import huntsite.teams.views as views

urlpatterns = [
    path("", views.team_list, name="team_list"),
    path("<int:pk>/", views.team_detail, name="team_detail"),
]
