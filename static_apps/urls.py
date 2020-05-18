from django.urls import path

from . import views

app_name = "static_apps"
urlpatterns = [
    path("", views.index, name="index"),
    path("debug/", views.debug, name="debug"),
    path("rules/", views.rules, name="rules"),
    path("scores/", views.scores, name="scores"),
]