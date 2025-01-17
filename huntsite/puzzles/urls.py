from django.urls import path

import huntsite.puzzles.views as views

urlpatterns = [
    path("", views.puzzle_list, name="puzzle_list"),
    path("<str:slug>/", views.puzzle_detail, name="puzzle_detail"),
    path("<str:slug>/solution/", views.puzzle_solution, name="puzzle_solution"),
]
