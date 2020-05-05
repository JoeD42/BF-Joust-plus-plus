from django.http import JsonResponse

from bfjpp.main import playGame
import json



def debug(request):
    try:
        left = json.loads(request.body.decode("utf-8"))["left"]
        right = json.loads(request.body.decode("utf-8"))["right"]
        return JsonResponse(playGame(left, right))
    except KeyError:
        print(request.body)
        return JsonResponse({ "error": 10, "err_msg": "Something went wrong"})
    return JsonResponse( {"error": 11, "err_msg": "Something has gone very wrong"})

def test_debug(request):
    return JsonResponse(playGame("", ":+|-;>(-)*6>(+)*7>-(+)*17>(-)*12>(+)*8>(-)*7>(+)*8>(+)*3>[(-)*5[+]]>>[(+)*7[-]]>>([(+)*14[-]]>)*3([(-)*14[+]]>)*3[(-)*7[+]]>>[(+)*6[-]]>>([(+)*14[-]]>)*3[(-)*14[+]]>[(+)*14[-]]>[(-)*16[+]]>[(-)*7[+]]"))