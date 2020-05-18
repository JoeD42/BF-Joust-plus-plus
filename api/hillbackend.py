from hill.models import HillGame, HillProgram
from bfjpp.main import playGame, verifyProgram


MAX_HILL_SLOTS = 32

def getPoints(games):
    points = 0
    for game in games:
        points += game["winner"]
    return points

def playTourney(temp_prog):
    verify = verifyProgram(temp_prog.content) # make sure the program is valid
    if not verify["success"]:
        return {"success": False, "err_msg": verify["err_msg"]}

    progs = HillProgram.objects.all()
    if progs.filter(name=temp_prog.name).count() > 0: # update programs instead of duplicating them
        temp_prog.prev_rank = progs.get(name=temp_prog.name).rank # previous rank
        progs = progs.exclude(name=temp_prog.name) # exclude old program
    elif progs.count() >= MAX_HILL_SLOTS: # do not include last place program if hill is full
        progs = progs.exclude(rank=MAX_HILL_SLOTS)
    
    progs = list(progs)
    games = []

    for p in progs:
        result = playGame(temp_prog.content, p.content)
        if result["error"] != 0:
            return {"success": False, "err_msg": result["err_msg"]}
        games.append(HillGame(left=temp_prog, right=p, games=result["games"], points=getPoints(result["games"])))

    for game in games:
        temp_prog.points += game.getPoints(temp_prog)

    # temporary solution for score algorithm, will insert proper one later
    temp_prog.score = temp_prog.points

    for prog in progs: # getting rank; this is mostly for immediate display, as all ranks will be recalculated on finalization
        if temp_prog.score > prog.score and temp_prog.rank > prog.rank:
            temp_prog.rank = prog.rank
    if temp_prog.rank > MAX_HILL_SLOTS: # last place wouldn't update on it's own
        temp_prog.rank = len(progs) + 1

    return { "success": True, "program": temp_prog, "games": games}

def sortPrograms(prog):
    return prog.score

def redoScores(progs):
    for prog in progs:
        prog.points = 0
        prog.score = 0
        for game in HillGame.objects.filter(left=prog)|HillGame.objects.filter(right=prog):
            prog.points += game.getPoints(prog)
        
        prog.score = prog.points # replace with algorithm later
        

        prog.save(update_fields=["score", "points"])


def finalizeTourney(play_results):
    # add (and remove) programs to hill
    progs = HillProgram.objects.all()
    if progs.filter(name=play_results["program"].name).count() > 0: # update programs instead of duplicating them
        progs.get(name=play_results["program"].name).delete()
    elif progs.count() >= MAX_HILL_SLOTS: # do not include last place program if hill is full
        progs.get(rank=MAX_HILL_SLOTS).delete()
    play_results["program"].save()

    # add games to hill and update scores
    for game in play_results["games"]:
        game.save()

    # rerank hill programs and save updates
    progs = list(HillProgram.objects.all())
    redoScores(progs)
    progs.sort(reverse=True, key=sortPrograms)
    for i in range(len(progs)):
        if progs[i].name != play_results["program"].name: # don't include prev_rank of added program; either we did it already or it's new and doesn't have a prev rank
            progs[i].prev_rank = progs[i].rank
        progs[i].rank = i + 1 # update rank

        progs[i].save(update_fields=["rank", "prev_rank"])

