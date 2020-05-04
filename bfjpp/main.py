from bfjpp.bfparser import JoustSyntaxError
from bfjpp.program import Program
from bfjpp.gameplay import Turn, Archive, Game

import json

def playGame(left, right):
    # compile the programs
    left_prog = ""
    try:
        left_prog = Program(left)
    except JoustSyntaxError as err:
        return json.dumps({
            "error": -1,
            "err_msg": err.msg
        })
    right_prog = ""
    try:
        right_prog = Program(right)
    except JoustSyntaxError as err:
        return json.dumps({
            "error": 1,
            "err_msg": err.msg
        })

    #play the games
    games = []

    for i in range(12, 33):
        temp_game = Game(i, False, left_prog, right_prog)
        games.append(temp_game.play().toJSON())
        # print(json.dumps(games[-1]["turns"][0]))
        # input("")

    for i in range(12, 33):
        temp_game = Game(i, True, left_prog, right_prog)
        games.append(temp_game.play().toJSON())

    return json.dumps({
        "error": 0,
        "games": games
    }) # fix

# raw = "(.)*-1"
# # with open(r"test.txt", "r") as file:
# #     raw = file.read()

# print(playGame(raw, ":+|-;>(-)*6>(+)*7>-(+)*17>(-)*12>(+)*8>(-)*7>(+)*8>(+)*3>[(-)*5[+]]>>[(+)*7[-]]>>([(+)*14[-]]>)*3([(-)*14[+]]>)*3[(-)*7[+]]>>[(+)*6[-]]>>([(+)*14[-]]>)*3[(-)*14[+]]>[(+)*14[-]]>[(-)*16[+]]>[(-)*7[+]]"))