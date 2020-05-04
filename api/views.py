from django.http import HttpResponse

from bfjpp.main import playGame
import json



def debug(request):
    try:
        left = json.loads(request.body.decode("utf-8"))["left"]
        right = json.loads(request.body.decode("utf-8"))["right"]
        return HttpResponse(playGame(left, right))
    except KeyError:
        print(request.body)
        return HttpResponse("Something went wrong")
    return HttpResponse("Something has gone very wrong")

def test_debug(request):
    return HttpResponse(playGame("", ":+|-;>(-)*6>(+)*7>-(+)*17>(-)*12>(+)*8>(-)*7>(+)*8>(+)*3>[(-)*5[+]]>>[(+)*7[-]]>>([(+)*14[-]]>)*3([(-)*14[+]]>)*3[(-)*7[+]]>>[(+)*6[-]]>>([(+)*14[-]]>)*3[(-)*14[+]]>[(+)*14[-]]>[(-)*16[+]]>[(-)*7[+]]"))