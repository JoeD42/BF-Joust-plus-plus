from django.urls import path

from . import views

app_name = "static_apps"
urlpatterns = [
    path("debug/", views.debug, name="debug"),
]