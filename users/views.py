from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404, render
from django.db import IntegrityError

from .models import SavedProgram

def user_signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:profile", args=[request.user.username])) # if already logged in, open their user profile
    else:
        return render(request, "signup.html")

def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:profile", args=[request.user.username])) # if already logged in, open their user profile
    else:
        return render(request, "login.html")

def do_signup(request):
    try:
        new_user = User.objects.create_user(request.POST["username"], password=request.POST["password"])
        new_user.save()
        login(request, new_user)
    except KeyError:
        return render(request, "signup.html", { "error": "Uh-oh! An error occurred!" })
    except IntegrityError:
        return render(request, "signup.html", { "error": "That Username already exists!" })
    else:
        return HttpResponseRedirect(reverse("users:profile", args=[user.username]))

def do_login(request):
    try:
        user = authenticate(username=request.POST["username"], password=request.POST["password"])
        if user:
            login(request, user)
        else:
            return render(request, "login.html", { "error": "Username or password is incorrect" })
    except KeyError:
        return render(request, "login.html", { "error": "Uh-oh! An error occurred!" })
    else:
        return HttpResponseRedirect(reverse("users:profile", args=[user.username]))

def profile(request, username):
    user = get_object_or_404(User, username=username)
    shown_progs = []
    if(user == request.user):
        shown_progs = user.savedprogram_set.all()
    else:
        shown_progs = user.savedprogram_set.filter(private__eq=False)
    return render(request, "profile.html", { "profile": user, "is_current": user == request.user, "programs": shown_progs })


def program(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        pass #trying to access a program that doesn't belong to them
    else:
        to_load = request.GET.get("name", None)
        if to_load == None:
            return render(request, "program.html", { "new": True }) # create a new program
        else:
            prog = get_object_or_404(SavedProgram, name=to_load, author=user.pk)
            return render(request, "program.html", { "program": prog })