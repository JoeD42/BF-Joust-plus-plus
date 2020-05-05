from .game import *
from .code import *
from .bfparser import JoustSyntaxError
from .program import Program
import json

# *************************
# Archive
# *************************
class Turn:
    def __init__(self, tape, l_pos, r_pos, l_code, r_code, l_cmp, r_cmp, l_frame, r_frame):
        self.tape = [n for n in tape]
        self.l_pos = l_pos
        self.r_pos = r_pos
        self.l_code = l_code
        self.r_code = r_code
        self.l_cmp = l_cmp
        self.r_cmp = r_cmp
        self.l_frame = l_frame
        self.r_frame = r_frame

    def __str__(self):
        cmps = { "?": "t!0", "=": "t=r", "!": "t!r", "&": "r!0"}
        return " ".join([
            f"@{self.l_code}",
            cmps[self.l_cmp],
            " ".join([
                f"{'X' if (i == self.l_pos and i == self.r_pos) else ('>' if i == self.l_pos else ('<' if self.r_pos == i else ' '))}{'0' if len(hex(self.tape[i])) < 4 else ''}{hex(self.tape[i])[2:]}"
                for i in range(len(self.tape))
            ]),
            "",
            cmps[self.r_cmp],
            f"@{self.r_code}",
            f"$L({self.l_frame})",
            f"$R({self.r_frame})"
        ])

    def toJSON(self):
        return {
            "tape": self.tape,
            "l_pos": self.l_pos,
            "r_pos": self.r_pos,
            "l_code": self.l_code,
            "r_code": self.r_code,
            "l_cmp": self.l_cmp,
            "r_cmp": self.r_cmp,
            "l_frame": self.l_frame,
            "r_frame": self.r_frame
        }

class Archive:
    def __init__(self, tape_len, polarity, turns, winner):
        self.tape_len = tape_len
        # self.left = left
        # self.right = right
        self.turns = turns
        self.winner = winner
        self.polarity = polarity

    # def __str__(self):
    #     return "\n".join([
    #         str(self.winner),
    #         str(self.tape_len),
    #         str(self.polarity),
    #         "\n".join([f"{('0'*(len(str(len(self.turns)))-len(str(i))))}{i}: {self.turns[i]}" for i in range(len(self.turns))])
    #     ])

    def display(self):
        counter = 0
        i = 0
        for tape in self.turns:
            print(f"{('0'*(len(str(len(self.turns)))-len(str(i))))}{i}: {tape}")
            counter += 1
            i += 1
            if counter >= 100:
                input("PAUSE")
                counter = 0
    
    def toJSON(self):
        return {
            "tape_len": self.tape_len,
            "polarity": self.polarity,
            "winner": self.winner,
            "turns": self.turns
        }

# *************************
# Game Execution
# *************************

def getCurrentFrame(call_stack):
    if call_stack[-1].substack == []:
        return call_stack[-1]
    else:
        return call_stack[-1].substack[-1]


def turnAction(cmd, position, tape, polarity, player, comparision):
    # player = true for left, false for right
    # returns position
    polarity = polarity if player else False # only left player has polarity affect them
    register = 0 if player else -1 # position of the register

    if (cmd == "+" and not polarity) or (cmd == "-" and polarity):
        tape[position] = (tape[position] + 1) % 256
    elif (cmd == "-" and not polarity) or (cmd == "+" and polarity):
        tape[position] = (tape[position] - 1) % 256
    elif (cmd == ">" and player) or (cmd == "<" and not player):
        position += 1
    elif (cmd == "<" and player) or (cmd == ">" and not player):
        position -= 1
    elif cmd == ",":
        tape[register] = tape[position]
    elif (cmd == "#" and not polarity) or (cmd == "~" and polarity):
        tape[register] = (tape[register] + 1) % 256
    elif (cmd == "~" and not polarity) or (cmd == "#" and polarity):
        tape[register] = (tape[register] - 1) % 256
    elif cmd in "?!=&":
        comparision = cmd
    # else, we reached a branch which isn't handeled in this function, or a . or ; command which does nothing anyway

    return position, comparision


def turnBranch(cmd, tape_cell, reg_cell, comparision, call_stack):
    result = False
    if comparision == "?" and tape_cell != 0:
        result = True
    elif comparision == "=" and tape_cell == reg_cell:
        result = True
    elif comparision == "!" and tape_cell != reg_cell:
        result = True
    elif comparision == "&" and reg_cell != 0:
        result = True
    
    if cmd == "[" and result == False:
        # print("branchWhileForward")
        getCurrentFrame(call_stack).branchWhileForward()
    elif cmd == "]" and result == True:
        getCurrentFrame(call_stack).branchWhileBackward()
    elif cmd == ":" and result == False:
        getCurrentFrame(call_stack).branchIf()
    elif cmd == "|": # result doesn't matter when running into an | because that means we reached the end of a :
        getCurrentFrame(call_stack).branchElse()
    # else either we don't need to jump or we didn't get a branch command



class Game:
    def __init__(self, tape_size, polarity, left, right):
        self.tape = [128 if i == 1 or i == tape_size-2 else 0 for i in range(tape_size)]
        self.tape_size = tape_size
        self.polarity = polarity # True for polarity, False for no polarity
        self.left = left # the program
        self.right = right
        self.l_stack = [CallStackFrame(left.code, [], [])] # player's call stack
        self.r_stack = [CallStackFrame(right.code, [], [])]
        self.l_pos = 1 # player's position on the tape
        self.r_pos = tape_size - 2
        self.l_cmp = "?" # comparisions which are affected by ? = ! and &
        self.r_cmp = "?"
        self.archive = []
        
    def step(self, call_stack, program):
        if call_stack == []:
            return BasicCommand(".", -1) #end of program has been reached, do nothing
        if call_stack[-1].substack == []:
            call_stack[-1].position += 1
            return call_stack[-1].nextInstruct(call_stack[-1], call_stack, program) # no substacks
        else:
            call_stack[-1].substack[-1].position += 1
            return call_stack[-1].substack[-1].nextInstruct(call_stack[-1], call_stack, program)

    def play(self):
        l_cmd = None # the command to execute
        r_cmd = None
        l_lose = False
        r_lose = False
        l_flag = False
        r_flag = False
        turn = 0

        while turn < 100000:
            turn += 1
            # print(turn)

            # get next instruction from left program
            l_cmd = self.step(self.l_stack, self.left)
            while l_cmd == None:
                l_cmd = self.step(self.l_stack, self.left)

            # get next instruction from right program
            r_cmd = self.step(self.r_stack, self.right)
            while r_cmd == None:
                r_cmd = self.step(self.r_stack, self.right)

            # execute conditional, branching instructions
            turnBranch(l_cmd.cmd, self.tape[self.l_pos], self.tape[0], self.l_cmp, self.l_stack)
            turnBranch(r_cmd.cmd, self.tape[self.r_pos], self.tape[-1], self.r_cmp, self.r_stack)

            # execute non-conditional, non-branching instructions
            self.l_pos, self.l_cmp = turnAction(l_cmd.cmd, self.l_pos, self.tape, self.polarity, True, self.l_cmp)
            self.r_pos, self.r_cmp = turnAction(r_cmd.cmd, self.r_pos, self.tape, self.polarity, False, self.r_cmp)

            # archive turn
            self.archive.append(Turn(self.tape, self.l_pos, self.r_pos, l_cmd.pos, r_cmd.pos, self.l_cmp, self.r_cmp, str(self.l_stack[-1]) if self.l_stack != [] else "", str(self.r_stack[-1]) if self.r_stack != [] else "").toJSON())

            # check win conditions
            l_lose = (self.tape[1] == 0 and l_flag == True) or self.l_pos < 0 or self.l_pos >= self.tape_size
            r_lose = (self.tape[-2] == 0 and r_flag == True) or self.r_pos < 0 or self.r_pos >= self.tape_size
            if l_lose or r_lose:
                break

            # check flag state
            l_flag = self.tape[1] == 0
            r_flag = self.tape[-2] == 0

            # print(f"{turn}: {self.archive[-1]} {l_cmd.cmd}")
            # if (turn % 100) == 0:
            #     input("PAUSE")

        # -1 for right winning, 1 for left winning, 0 for tie
        return Archive(self.tape_size, self.polarity, self.archive, (-1 if l_lose else 0) + (1 if r_lose else 0))



if __name__ == "__main__":
    raw = ""
    with open("test.txt", "r") as file:
        raw = file.read()

    try:
        p1 = Program(raw)
        p1.display()
    except JoustSyntaxError as err:
        print("P1", err)

    # print(p1.functions["chunk"])

    try:
        p2 = Program(":+|-;>(-)*6>(+)*7>-(+)*17>(-)*12>(+)*8>(-)*7>(+)*8>(+)*3>[(-)*5[+]]>>[(+)*7[-]]>>([(+)*14[-]]>)*3([(-)*14[+]]>)*3[(-)*7[+]]>>[(+)*6[-]]>>([(+)*14[-]]>)*3[(-)*14[+]]>[(+)*14[-]]>[(-)*16[+]]>[(-)*7[+]]")
    except JoustSyntaxError as err:
        print("P2", err)

    # p2 = Program("(+)*3")

    game = Game(20, False, p1, p2)
    history = game.play()
    input("PAUSE")
    # print(history)
    history.display()