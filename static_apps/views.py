from django.shortcuts import render

def debug(request):
    left = request.GET.get("left", None)
    right = request.GET.get("right", None)
    tleft = request.GET.get("tleft", None)
    tright = request.GET.get("tright", None)

    return render(request, "debug.html", {"left": left, "right": right, "tleft": tleft, "tright": tright, "this_user": request.user.username})

def index(request):
    return render(request, "index.html", { "this_user": request.user.username })

def rules(request):
    return render(request, "rules.html", { "this_user": request.user.username })

def scores(request):
    return render(request, "score.html", { "this_user": request.user.username })

def breakdown(request):
    specific = request.GET.get("prog", None)
    return render(request, "breakdown.html", { "start_prog": specific, "this_user": request.user.username })