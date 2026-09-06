from django.urls import path

from .views import MonitorListView


urlpatterns = [
    path("monitors/", MonitorListView.as_view()),
]