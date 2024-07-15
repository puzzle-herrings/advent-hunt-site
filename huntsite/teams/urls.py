from django.urls import path

import huntsite.teams.views as views

urlpatterns = [
    path("", views.account_manage, name="account_manage"),
]
