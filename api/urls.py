from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("debug/", views.debug, name="debug"),
    path("test_debug", views.test_debug),
    path("get/<str:username>/<str:name>/", views.getProgram, name="get"),
    path("list/<str:username>/", views.listPrograms, name="list")
]