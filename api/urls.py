from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("debug/", views.debug, name="debug"),
    path("test_debug", views.test_debug),
    path("get/<str:username>/<str:name>/", views.getProgram, name="get"),
    path("list/<str:username>/", views.listPrograms, name="list"),
    path("edit/<int:pk>/", views.editProgram, name="edit"),
    path("new/", views.newProgram, name="new"),
    path("delete/<int:pk>/", views.deleteProgram, name="delete"),
    path("verify/", views.verify, name="verify"),

    path("hill/", views.allHillPrograms.as_view(), name="hill_all"),
    path("hill/<str:name>/", views.getHillProgram.as_view(), name="hill"),
    path("submit/<int:pk>/", views.submitHill, name="submit"),
    path("test/<int:pk>/", views.testHill, name="test"),
    path("breakdown/<str:name>/", views.getBreakdown, name="breakdown")
]