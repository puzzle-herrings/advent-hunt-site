from django.urls import path

import huntsite.tester_utils.views as views

urlpatterns = [
    path("time_travel/", views.time_travel, name="time_travel"),
    path("time_travel_reset/", views.time_travel_reset, name="time_travel_reset"),
    path("organizer_dashboard/", views.organizer_dashboard_view, name="organizer_dashboard"),
]
