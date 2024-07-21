from django.urls import path

import huntsite.content.views as views

urlpatterns = [
    path("about/", views.about_page, name="about"),
    path("story/", views.story_page, name="story"),
]
