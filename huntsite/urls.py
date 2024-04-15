from django.urls import path

import huntsite.views as views

urlpatterns = [
    path('', views.home_page, name='home_page'),
]
