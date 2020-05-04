from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("debug/", views.debug, name="debug"),
    path("test_debug", views.test_debug),
]