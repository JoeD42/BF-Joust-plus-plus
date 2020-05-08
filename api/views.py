from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

from rest_framework import generics, viewsets, permissions
from rest_framework.renderers import JSONRenderer

from django.contrib.auth.models import User

from users.models import SavedProgram
from .permissions import IsAuthorOrPublicReadOnly, IsPublic
from .serializers import SavedProgramSerializer

from bfjpp.main import playGame, verifyProgram
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
    prog = get_object_or_404(SavedProgram, author=username, name=name)
    if prog.private and request.user != prog.author:
        return HttpResponseForbidden()
    return JsonResponse(JSONRenderer().render(SavedProgramSerializer(prog).data))

def listPrograms(request, username):
    user = get_object_or_404(User, username=username)
    progs = SavedProgram.objects.filter(author=user)
    if request.user != user: # prevent anyone aside from the author from seeing private programs
        progs.filter(private=False)
    # return list
    