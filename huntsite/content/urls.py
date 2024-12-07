from django.urls import path

import huntsite.content.views as views

urlpatterns = [
    path("about/", views.about_page, name="about"),
    path("story/", views.story_page, name="story"),
    path("story/victory/", views.victory_page, name="victory"),
    path("attributions/", views.attributions_page, name="attributions"),
    path("updates/", views.updates_page, name="updates"),
]
