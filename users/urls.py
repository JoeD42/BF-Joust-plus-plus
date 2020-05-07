from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("signup/", views.user_signup, name="signup"),
    path("login/", views.user_login, name="login"),
    path("signup/do/", views.do_signup, name="do_signup"),
    path("login/do/", views.do_login, name="do_login"),
    path("<str:username>/", views.profile , name="profile"),
    # path("<str:username>/program/", , name="program"),
]