from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

from django.contrib.auth.models import User
from hill.models import HillProgram
from users.models import SavedProgram

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


def raw(request):
    on_hill = request.GET.get("hill", None)
    if not on_hill: # from SavedProgram
        prog = get_object_or_404(SavedProgram, author=get_object_or_404(User, username=request.GET.get("author", None)), name=request.GET.get("name", None))
        if prog.private and request.user != prog.author:
            return HttpResponseForbidden()
    else: # from HillProgram
        prog = get_object_or_404(HillProgram, name=on_hill)
    if request.GET.get("plaintext", None): # plaintext
        return render(request, "rawtext.html", { "program": prog.content })
    else: # not plaintext
        prog_raw = prog.content.split("\n")
        return render(request, "raw.html", { "raw": prog_raw, "max_digits": len(str(len(prog_raw))), "prog_name": prog.name, "author": prog.author, "on_hill": on_hill, "this_user": request.user.username })