from .program import Program
from .bfparser import JoustSyntaxError
from .code import *

def dict2str(dictionary):
    return "".join(["(", ",".join([f"{key}:{dictionary[key]}" for key in dictionary.keys()]), ")"])

def getActualValue(value, call_stack_frame, where=-1):
    # print(f"getActualValue {value}")
    if value.tree[0] == "int":
        return int(value.tree[1])
    elif value.tree[0] == "id":
        return call_stack_frame.getVariable(value.tree[1], where)
    elif value.tree[0] == "!":
        return 0 if getActualValue(value.tree[1], call_stack_frame, where) != 0 else 1
    elif value.tree[0] == "?":
        return getActualValue(value.tree[2], call_stack_frame, where) if getActualValue(value.tree[1], call_stack_frame, where) != 0 else getActualValue(value.tree[3], call_stack_frame, where)
    elif value.tree[0] == "+":
        return getActualValue(value.tree[1], call_stack_frame, where) + getActualValue(value.tree[2], call_stack_frame, where)
    elif value.tree[0] == "-":
        return getActualValue(value.tree[1], call_stack_frame, where) - getActualValue(value.tree[2], call_stack_frame, where)
    elif value.tree[0] == "*":
        return getActualValue(value.tree[1], call_stack_frame, where) * getActualValue(value.tree[2], call_stack_frame, where)
    elif value.tree[0] == "/":
        return getActualValue(value.tree[1], call_stack_frame, where) // getActualValue(value.tree[2], call_stack_frame, where)
    elif value.tree[0] == "%":
        return getActualValue(value.tree[1], call_stack_frame, where) % getActualValue(value.tree[2], call_stack_frame, where)
    elif value.tree[0] == "==":
        return 1 if getActualValue(value.tree[1], call_stack_frame, where) == getActualValue(value.tree[2], call_stack_frame, where) else 0
    elif value.tree[0] == "!=":
        return 1 if getActualValue(value.tree[1], call_stack_frame, where) != getActualValue(value.tree[2], call_stack_frame, where) else 0
    elif value.tree[0] == ">":
        return 1 if getActualValue(value.tree[1], call_stack_frame, where) > getActualValue(value.tree[2], call_stack_frame, where) else 0
    elif value.tree[0] == "<":
        return 1 if getActualValue(value.tree[1], call_stack_frame, where) < getActualValue(value.tree[2], call_stack_frame, where) else 0
    elif value.tree[0] == ">=":
        return 1 if getActualValue(value.tree[1], call_stack_frame, where) >= getActualValue(value.tree[2], call_stack_frame, where) else 0
    elif value.tree[0] == "<=":
        return 1 if getActualValue(value.tree[1], call_stack_frame, where) <= getActualValue(value.tree[2], call_stack_frame, where) else 0
    elif value.tree[0] == "|":
        return 1 if (getActualValue(value.tree[1], call_stack_frame, where) != 0) or (getActualValue(value.tree[2], call_stack_frame, where) != 0) else 0
    elif value.tree[0] == "&":
        return 1 if (getActualValue(value.tree[1], call_stack_frame, where) != 0) and (getActualValue(value.tree[2], call_stack_frame, where) != 0) else 0
    elif value.tree[0] == "^":
        return 1 if (getActualValue(value.tree[1], call_stack_frame, where) != 0) != (getActualValue(value.tree[2], call_stack_frame, where) != 0) else 0
    else:
        return -13379432 # this shouldn't happen


class StackFrame:
    def __init__(self, block):
        self.block = block
        self.position = -1 # we always add one to position after a non bfjpp cmd, and since more often than not that just happend when creating a stackframe, position should be initialized at -1 so it will become 0
        self.vars = dict()

    def hasVariable(self, name):
        try:
            temp = self.vars[name]
            # print("hasVar True")
            return True
        except KeyError:
            return False

    def currentCode(self):
        return self.block.code

    def nextInstruct(self, context, call_stack, program): # return None if no bfjpp cmd was done (+-<>[] ect...)
        """Does not edit instruction pointer
        Context is current CallStackFrame"""
        # print(str(type(self)))
        if self.position >= len(self.currentCode()):
            if context.substack != []:
                context.substack.pop()
            else:
                call_stack.pop()
            return None

        current = self.currentCode()[self.position]

        if type(current) == BasicCommand:
            return current
        
        if type(current) == BasicLoop:
            context.substack.append(BasicLoopFrame(current, context))
        elif type(current) == NestedLoop:
            context.substack.append(NestedLoopFrame(current, context))
        elif type(current) == BlockCode:
            context.substack.append(BlockCodeFrame(current, context))
        elif type(current) == ForLoop:
            context.substack.append(ForLoopFrame(current, context))
        elif type(current) == IfBlock:
            context.substack.append(IfBlockFrame(current, context))
        elif type(current) == CallCmd:
            to_call = program.functions.get(current.func)
            if to_call:
                call_stack.append(CallStackFrame(to_call, current.params, call_stack))
                # print(call_stack[-1].vars)

        return None

    def branchWhileForward(self): # condition was false, goto matching ]
        level = 1
        length = len(self.currentCode())
        while level > 0 and self.position < (length - 1):
            self.position += 1
            if type(self.currentCode()[self.position]) == BasicCommand:
                if self.currentCode()[self.position].cmd == "[":
                    level += 1
                elif self.currentCode()[self.position].cmd == "]":
                    level -= 1
        return level

    def branchWhileBackward(self): # condition was true, goto matching [
        level = 1
        length = len(self.currentCode())
        while level > 0 and self.position > 0:
            self.position -= 1
            if type(self.currentCode()[self.position]) == BasicCommand:
                if self.currentCode()[self.position].cmd == "[":
                    level -= 1
                elif self.currentCode()[self.position].cmd == "]":
                    level += 1
        return level

    def branchIf(self): # condition was false, goto either matching | or ;
        level = 1
        length = len(self.currentCode())
        while level > 0 and self.position < (length - 1):
            self.position += 1
            if type(self.currentCode()[self.position]) == BasicCommand:
                if self.currentCode()[self.position].cmd == ":":
                    level += 1
                elif self.currentCode()[self.position].cmd == ";":
                    level -= 1
                elif self.currentCode()[self.position].cmd == "|" and level == 1:
                    level = 0
        return level

    def branchElse(self): # condition was true, found matching |, goto matching ;
        level = 1
        length = len(self.currentCode())
        while level > 0 and self.position < (length - 1):
            self.position += 1
            if type(self.currentCode()[self.position]) == BasicCommand:
                if self.currentCode()[self.position].cmd == ":":
                    level += 1
                elif self.currentCode()[self.position].cmd == ";":
                    level -= 1
        return level




class CallStackFrame(StackFrame):
    def __init__(self, function, arguments, call_stack):
        super().__init__(function)
        self.substack = []
        # get values of all arguments and variables
        if len(function.args) < len(arguments): # more arguments given than needed; ignore them
            for i in range(len(function.args)):
                self.vars[function.args[i]] = getActualValue(arguments[i], call_stack[-1])
        else:
            for i in range(len(function.args)):
                if i >= len(arguments):
                    self.vars[function.args[i]] = 0 # any arguments we don't get the value for are set to zero
                else:
                    self.vars[function.args[i]] = getActualValue(arguments[i], call_stack[-1])
        for var_id in function.vars.keys():
            self.vars[var_id] = getActualValue(function.vars[var_id], call_stack[-1])
    
    # TODO: fix (for loop isn't working)
    # I think one problem is that function is called before paramaters are assigned? YES it's cause making __init__ passes the function as the call stack
    # would getActualValue be necessary?
    def getVariable(self, name, where=-1):
        # print(f"getVar substack {len(self.substack)} where {where}")
        for i in range(-1, -len(self.substack)-1, -1): # look in substacks first, going from youngest to oldest
            # print("\tgetVar Forloop")
            if self.substack[i].hasVariable(name):
                if type(self.substack[i].vars[name]) == Value:
                    return getActualValue(self.substack[i].vars[name], self)
                return self.substack[i].vars[name]
        if self.hasVariable(name): # look in self
            if type(self.vars[name]) == Value:
                return getActualValue(self.vars[name], self)
            return self.vars[name]
        print(f"Could not find var {name}")
        print(self.vars)
        print(self.block.name)
        return 0 # if we couldn't find a variable, the default value is zero

    def __str__(self):
        return f"{self.block.name}{dict2str(self.vars)}::{':'.join([str(n) for n in self.substack])}"



class BasicLoopFrame(StackFrame):
    def __init__(self, block, context):
        super().__init__(block)
        self.loop = getActualValue(block.repeat, context)
        self.level = 0

    def nextInstruct(self, context, call_stack, program):
        # print(f"BasicLoopFrame loop={self.loop} level={self.level}")
        if self.position >= len(self.currentCode()):
            self.position = -1
            self.level += 1
            if self.level >= self.loop and not (self.loop < 0):
                context.substack.pop()
            return None

        return super().nextInstruct(context, call_stack, program)

    def __str__(self):
        return f"LOOP[{self.loop}>{self.level}]"


class NestedLoopFrame(BasicLoopFrame):
    def __init__(self, block, context):
        super().__init__(block, context)
        self.side = -1 # -1 for left, 0 for middle, 1 for right

    def __str__(self):
        return f"NEST[{self.side}|{self.loop}>{self.level}]"

    def currentCode(self):
        if self.side == -1:
            return self.block.left_code
        elif self.side == 0:
            return self.block.mid_code
        else:
            return self.block.right_code

    def nextInstruct(self, context, call_stack, program):
        if self.position >= len(self.currentCode()):
            self.level -= self.side # from 0 to len on left side, from len to 0 on right side
            self.position = -1
            if (self.side == -1 and self.level >= self.loop) and not (self.loop < 0):
                self.side = 0
            elif (self.side == 1 and self.level >= self.loop) and not (self.loop < 0):
                context.substack.pop()
            elif self.side == 0:
                self.side = 1
                self.level = self.loop

            return None
        return super().nextInstruct(context, call_stack, program)

    def branchWhileForward(self):
        if self.side != -1: # if in middle or on right, branching forward is same as default
            return super().branchWhileForward()
        level = super().branchWhileForward()
        if level > 0:
            self.side = 1 # skip the middle
            self.position = -1 # remember that we increment the position before checking anything
            level = super().branchWhileForward()
        return level

    def branchWhileBackward(self):
        if self.side != 1:
            return super().branchWhileBackward()
        level = super().branchWhileBackward()
        if level > 0:
            self.side = -1
            self.position = len(self.block.left_code) #once again, we decrement position before checking anything
            level = super().branchWhileBackward()
        return level

    def branchIf(self):
        if self.side != -1:
            return super().branchIf()
        level = super().branchIf()
        if level > 0:
            self.side = 1
            self.position = -1
            level = super().branchIf()
        return 
        
    def branchElse(self):
        if self.side != -1:
            return super().branchElse()
        level = super().branchElse()
        if level > 0:
            self.side = 1
            self.position = -1
            level = super().branchElse()
        return level


class BlockCodeFrame(StackFrame):
    def __init__(self, block, context):
        super().__init__(block)
        for var_id in block.vars.keys():
            self.vars[var_id] = getActualValue(block.vars[var_id], context, -1)

    def __str__(self):
        return f"BLK{dict2str(self.vars)}"


class ForLoopFrame(StackFrame):
    def __init__(self, block, context):
        super().__init__(block)
        self.end = getActualValue(block.end, context, -1)
        # set initial values
        self.vars[block.name] = getActualValue(block.ini, context, -1)
        for var in block.vars.keys():
            self.vars[var] = getActualValue(block.vars[var][0], context, -1)
        # set step values
        self.steps = dict()
        self.steps[block.name] = getActualValue(block.step, context, -1)
        for step in block.vars.keys():
            self.steps[step] = getActualValue(block.vars[step][1], context, -1)

    def __str__(self):
        return f"FOR[{self.end}>{self.vars[self.block.name]}]{dict2str(self.vars)}"

    def nextInstruct(self, context, call_stack, program):
        if self.position >= len(self.currentCode()):
            self.position = -1
            
            for var in self.vars.keys():
                self.vars[var] += self.steps[var]

            if self.steps[self.block.name] < 0:
                if self.vars[self.block.name] <= self.end:
                    context.substack.pop()
            else:
                if self.vars[self.block.name] >= self.end:
                    context.substack.pop()

            return None

        return super().nextInstruct(context, call_stack, program)


class IfBlockFrame(StackFrame):
    def __init__(self, block, context):
        super().__init__(block)
        which = None
        for cmp in block.blocks: # determine where to branch, if anywhere
            if type(cmp) == ElseSubBlock or getActualValue(cmp.cond, context, -2):
                which = cmp
                break
        if which == None:
            which = ElseSubBlock() # if no else block and no conditions were true, pass an empty code block to simulate nothing
        self.block = which

    def __str__(self):
        return f"IF"
