from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse, HttpResponseServerError

from rest_framework import generics, viewsets, permissions
from rest_framework.renderers import JSONRenderer

from django.contrib.auth.models import User

from users.models import SavedProgram
from hill.models import HillProgram, HillGame
from .permissions import IsAuthorOrPublicReadOnly, IsPublic
from .serializers import SavedProgramSerializer, HillProgramSerializer, HillGameSerializer

from bfjpp.main import playGame, verifyProgram
from .hillbackend import playTourney, finalizeTourney, MAX_HILL_SLOTS
import json



def debug(request):
    try:
        left = json.loads(request.body.decode("utf-8"))["left"]
        right = json.loads(request.body.decode("utf-8"))["right"]
        return JsonResponse(playGame(left, right))
    except KeyError:
        # print(request.body)
        return JsonResponse({ "error": 10, "err_msg": "Something went wrong"})
    return JsonResponse( {"error": 11, "err_msg": "Something has gone very wrong"})

def test_debug(request): # this is for testing the json
    return JsonResponse(playGame("", ":+|-;>(-)*6>(+)*7>-(+)*17>(-)*12>(+)*8>(-)*7>(+)*8>(+)*3>[(-)*5[+]]>>[(+)*7[-]]>>([(+)*14[-]]>)*3([(-)*14[+]]>)*3[(-)*7[+]]>>[(+)*6[-]]>>([(+)*14[-]]>)*3[(-)*14[+]]>[(+)*14[-]]>[(-)*16[+]]>[(-)*7[+]]"))

def verify(request):
    try:
        ret = json.loads(request.body.decode("utf-8"))["raw"]
        return JsonResponse(verifyProgram(ret))
    except KeyError:
        return JsonResponse({ "success": False, "msg": "Something went wrong"})
    return JsonResponse( {"success": False, "msg": "Something has gone very wrong"})

def getProgram(request, username, name):
    prog = get_object_or_404(SavedProgram, author=get_object_or_404(User, username=username), name=name)
    if prog.private and request.user != prog.author:
        return HttpResponseForbidden()
    return JsonResponse(SavedProgramSerializer(prog).data)

def listPrograms(request, username):
    user = get_object_or_404(User, username=username)
    progs = SavedProgram.objects.filter(author=user)
    if request.user != user: # prevent anyone aside from the author from seeing private programs
        progs = progs.exclude(private=True)
    return JsonResponse(SavedProgramSerializer(progs, many=True).data, safe=False)


def editProgram(request, pk):
    prog = get_object_or_404(SavedProgram, pk=pk)
    if request.user != prog.author:
        return HttpResponseForbidden() # can't edit programs that aren't yours
    to_edit = json.loads(request.body.decode("utf-8"))
    try:
        name_change = prog.name != to_edit["name"] # only check name uniqueness if the name is changed
        prog.name = to_edit["name"]
        if name_change and SavedProgram.objects.filter(name=prog.name, author=request.user).count() > 0: # not a unique name
            return HttpResponseBadRequest("Already exists!")
        prog.private = to_edit["private"]
        prog.content = to_edit["content"]
        prog.save()
        return HttpResponse() # good to go
    except KeyError:
        return HttpResponseBadRequest() # request didn't have all the info needed
    return HttpResponseServerError() # don't know how we would get here


def newProgram(request):
    if not request.user.is_authenticated:
        return HttpResponse("Only users can create new programs!", status=401) # user isn't logged in; can't make a new program if you aren't logged in
    to_add = json.loads(request.body.decode("utf-8"))
    try:
        name = to_add["name"]
        if SavedProgram.objects.filter(name=name, author=request.user).count() > 0: # not a unique name
            return HttpResponseBadRequest("Already exists!")
        private = to_add["private"]
        new_prog = SavedProgram(author=request.user, name=name, content=to_add.get("content", ""), private=private)
        new_prog.save()
        return HttpResponse(new_prog.pk) # good to go
    except KeyError:
        return HttpResponseBadRequest() # didn't have all needed info (program name and private status)
    return HttpResponseServerError() # don't know how we would get here


def deleteProgram(request, pk):
    prog = get_object_or_404(SavedProgram, pk=pk)
    if request.user != prog.author:
        return HttpResponseForbidden() # can't edit programs that aren't yours
    prog.delete()
    return HttpResponse(request.user.username) # return username of deleted program to help my javascript code on the frontend


class allHillPrograms(generics.ListAPIView):
    queryset = HillProgram.objects.all()
    serializer_class = HillProgramSerializer

class getHillProgram(generics.RetrieveAPIView):
    lookup_field = "name"
    queryset = HillProgram.objects.all()
    serializer_class = HillProgramSerializer

def getBreakdown(request, name):
    prog = get_object_or_404(HillProgram, name=name)
    games = HillGame.objects.filter(left=prog) | HillGame.objects.filter(right=prog)
    return JsonResponse(HillGameSerializer(games, many=True).data, safe=False)


def submitHill(request, pk):
    prog = get_object_or_404(SavedProgram, pk=pk)
    if request.user != prog.author: # can't submit a program that isn't yours!
        return HttpResponseForbidden()

    prog = HillProgram(author=prog.author, name=str(prog), content=prog.content, rank=9999, prev_rank=0, points=0, score=0)
    results = playTourney(prog)
    if not results["success"]:
        return JsonResponse(results)

    finalizeTourney(results)

    return JsonResponse({ "success": True, "message": f"{results['program'].name} is rank {results['program'].rank}, with a score of {results['program'].score}"})


def testHill(request, pk):
    prog = get_object_or_404(SavedProgram, pk=pk)
    if request.user != prog.author: # can't submit a program that isn't yours!
        return HttpResponseForbidden()

    prog = HillProgram(author=prog.author, name=str(prog), content=prog.content, rank=9999, prev_rank=0, points=0, score=0)
    results = playTourney(prog)
    if not results["success"]:
        return JsonResponse(results)

    return JsonResponse({ "success": True, "message": f"{results['program'].name} is rank {results['program'].rank}, with a score of {results['program'].score}"})