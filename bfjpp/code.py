class BasicCommand:
    def __init__(self, cmd, pos):
        self.cmd = cmd
        self.pos = pos # the literal position in the raw string, raw[pos]. used for debugging during the game

    def display(self, level=0):
        return self.cmd

    def __str__(self):
        return self.cmd

    def __repr__(self):
        return f"{self.cmd} @ {self.pos}"

class BasicLoop:
    def __init__(self, repeat, code=[]):
        self.repeat = repeat
        self.code = code

    def display(self, level=0):
        return f"({' '.join([x.display(level) for x in self.code])})*{self.repeat}"

    def __str__(self):
        return self.display()


class NestedLoop:
    def __init__(self, repeat, left=[], mid=[], right=[]):
        self.repeat = repeat
        self.left_code = left
        self.mid_code = mid
        self.right_code = right

    def display(self, level=0):
        return "".join([f"( {''.join([x.display(level) for x in self.left_code])}", "{ ", "".join([x.display(level) for x in self.mid_code]), " }", f"{''.join([x.display(level) for x in self.right_code])} )%{self.repeat}"])

    def __str__(self):
        return self.display()

class BlockCode:
    def __init__(self, vars):
        self.vars = vars # dictionary
        self.code = []

    def display(self, level=0):
        return "".join(["\n", "\t"*level, f"BLOCK({' '.join([f'{name}={value}' for name, value in self.vars.items()])})", "\n", "\t" * (level+1), "".join([x.display(level+1) for x in self.code])])

    def __str__(self):
        return self.display()

class ForLoop:
    def __init__(self, name, ini, end, step, vars):
        self.name = name
        self.ini = ini
        self.end = end
        self.step = step
        self.vars = vars
        self.code = []

    def display(self, level=0):
        if len(self.vars) > 0:
            add_to = ", ".join([f'({name}={vals[0]}; {name}+={vals[1]})' for name, vals in self.vars.items()])
            add_to = f"::( {add_to} ):"
        else:
            add_to = ":"
        return "".join(["\n", "\t"*level,f"FOR({self.name}={self.ini}; {self.name}<{self.end}; {self.name}+={self.step})", add_to, "\n", "\t"*(level+1), f"{''.join([x.display(level+1) for x in self.code])}"])

    def __str__(self):
        return self.display()

class Function:
    def __init__(self, name, args, vars):
        self.name = name
        self.args = args
        self.vars = vars
        self.code = []

    def display(self, level=0):
        if len(self.vars) > 0:
            add_to = "::(" + ", ".join([f"{name}={value}" for name, value in self.vars.items()]) + ")"
        else:
            add_to = ""
        return "".join(["\n", "\t"*level, f"DEF {self.name}({''.join([x for x in self.args])})", add_to, ":\n", "\t"*(level+1), f"{''.join([x.display(level+1) for x in self.code])}"])

    def __str__(self):
        return self.display()

class IfSubBlock:
    def __init__(self, cond):
        self.cond = cond
        self.code = []

    def display(self, level=0):
        return "".join(["\t"*level, "IFSUB(", str(self.cond), "):\n", "\t"*(level+1), ''.join(x.display(level+1) for x in self.code)])

    def __str__(self):
        return self.display()

class ElseSubBlock:
    def __init__(self):
        self.code = []

    def display(self, level=0):
        return "".join(["\t"*level, "ELSE:\n", "\t"*(level+1), "".join(x.display(level+1) for x in self.code)])

    def __str__(self):
        return self.display()


class IfBlock:
    def __init__(self, blocks=[]):
        self.blocks = blocks

    def display(self, level=0):
        return "".join(["\n", "\t"*level, "IF\n", "\n".join([block.display(level+1) for block in self.blocks]), "\n"])

    def __str__(self):
        return self.display()


class CallCmd:
    def __init__(self, func, params):
        self.func = func
        self.params = params

    def display(self, level=0):
        return f"CALL {self.func}({', '.join([str(x) for x in self.params])})"

    def __str__(self):
        return self.display()

    def __repr__(self):
        return self.display()



class Value:
    def __init__(self, tree=[]):
        self.tree = tree

    def __get(self, context):
        pass

    def get(self, context): # return the actual value
        pass

    def __str__(self):
        return f"(%{' '.join([str(x) for x in self.tree])}%)"