from django.shortcuts import render

def debug(request):
    left = request.GET.get("left", None)
    right = request.GET.get("right", None)

    return render(request, "debug.html", {"left": left, "right": right, "this_user": request.user.username})

def index(request):
    return render(request, "index.html", { "this_user": request.user.username })

def rules(request):
    return render(request, "rules.html", { "this_user": request.user.username })