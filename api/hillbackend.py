from hill.models import HillGame, HillProgram
from bfjpp.main import playGame, verifyProgram

import json


MAX_HILL_SLOTS = 8

def getPoints(games):
    points = 0
    for game in games:
        points += game["winner"]
    return points

def getGamePoints(left, right):
    ret = HillGame.objects.filter(left=left, right=right)
    if not ret:
        ret = HillGame.objects.get(left=right, right=left)
    else:
        ret = ret[0]
    return ret.getPoints(left)

def getNewGamePoints(games, opp): # for redoScores when the new program and it's games haven't been saved
    for game in games:
        if game.right.name == opp.name:
            return -game.points # returns the temp_game's points; if you want opp's points, negate the result
        
def redoScores(progs, temp_prog=None, temp_games=None):
    worth = {}
    num_progs = len(progs) + (1 if temp_prog is not None else 0)
    for prog in progs:
        prog.points = 0
        prog.score = 0
        for game in HillGame.objects.filter(left=prog)|HillGame.objects.filter(right=prog):
            if not (temp_prog is not None and (game.left.name == temp_prog.name or game.right.name == temp_prog.name)):
                prog.points += game.getPoints(prog)
        if temp_prog is not None:
            prog.points += -getNewGamePoints(temp_games, prog)
        
        worth[prog.name] = ((prog.points/42)+num_progs)/((num_progs-1)*2)

    
    if temp_prog is not None:
        temp_prog.points = 0
        temp_prog.score = 0
        for game in temp_games:
            temp_prog.points += game.getPoints(temp_prog)
        worth[temp_prog.name] = ((temp_prog.points/42)+num_progs)/((num_progs-1)*2)


    for prog in progs:
        for opp in progs:
            if prog.name != opp.name:
                game_points = getGamePoints(prog, opp)
                if game_points > 0:
                    prog.score += int(worth[opp.name] * game_points / 42 * 100)
        if temp_prog is not None:
            game_points = -getNewGamePoints(temp_games, prog)
            if game_points > 0:
                prog.score += int(worth[temp_prog.name] * game_points / 42 * 100)
    
    if temp_prog is not None:
        for opp in progs:
            game_points = getNewGamePoints(temp_games, opp)
            if game_points > 0:
                temp_prog.score += int(worth[opp.name] * game_points / 42 * 100)


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
        for game in result["games"]:
            del game["turns"] # we need to delete the turn history, otherwise it's memory errors up the wazoo
        games.append(HillGame(left=temp_prog, right=p, games=json.dumps(result["games"]), points=getPoints(result["games"])))

    redoScores(progs, temp_prog, games)

    for prog in progs: # getting rank; this is mostly for immediate display, as all ranks will be recalculated on finalization
        if temp_prog.score > prog.score and temp_prog.rank > prog.rank:
            temp_prog.rank = prog.rank
    if temp_prog.rank > MAX_HILL_SLOTS: # last place wouldn't update on it's own
        temp_prog.rank = len(progs) + 1

    return { "success": True, "program": temp_prog, "games": games}

def sortPrograms(prog):
    return prog.score

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

        progs[i].save(update_fields=["rank", "prev_rank", "score", "points"])

