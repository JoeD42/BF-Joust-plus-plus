from django.shortcuts import render

def debug(request):
    left = request.GET.get("left", None)
    right = request.GET.get("right", None)

    return render(request, "debug.html", {"left": left, "right": right})