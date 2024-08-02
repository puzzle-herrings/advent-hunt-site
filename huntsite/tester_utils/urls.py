from django.urls import path

import huntsite.tester_utils.views as views

urlpatterns = [
    path("time_travel/", views.time_travel, name="time_travel"),
]
