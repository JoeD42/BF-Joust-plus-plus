from .bfparser import JoustSyntaxError
from .program import Program
from .gameplay import Turn, Archive, Game

def playGame(left, right): #return the results of a game between two programs
    # compile the programs
    left_prog = ""
    try:
        left_prog = Program(left)
    except JoustSyntaxError as err:
        return {
            "error": -1,
            "err_msg": err.msg
        }
    right_prog = ""
    try:
        right_prog = Program(right)
    except JoustSyntaxError as err:
        return {
            "error": 1,
            "err_msg": err.msg
        }

    #play the games
    games = []

    for i in range(12, 33):
        temp_game = Game(i, False, left_prog, right_prog)
        games.append(temp_game.play().toJSON())

    for i in range(12, 33):
        temp_game = Game(i, True, left_prog, right_prog)
        games.append(temp_game.play().toJSON())

    return {
        "error": 0,
        "games": games
    }

def playSingleGame(left, right, tape_len, polarity): # return the results of a single match between two programs
    # compile the programs
    left_prog = ""
    try:
        left_prog = Program(left)
    except JoustSyntaxError as err:
        return {
            "error": -1,
            "err_msg": err.msg
        }
    right_prog = ""
    try:
        right_prog = Program(right)
    except JoustSyntaxError as err:
        return {
            "error": 1,
            "err_msg": err.msg
        }

    #play the game
    game = Game(tape_len, polarity, left_prog, right_prog)
    game = game.play().toJSON()
    
    return {
        "error": 0,
        "game": game
    }

def verifyProgram(raw): # verify that a program has no errors
    try:
        Program(raw)
        return { "success": True }
    except JoustSyntaxError as err:
        return { "success": False, "msg": err.msg }