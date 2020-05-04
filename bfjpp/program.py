from bfjpp.bfparser import firstParse, secondParse, JoustSyntaxError
from bfjpp.lexer import lex
from bfjpp.code import *

def getFuncs(stream, all_funcs):
    ret = []
    for code in stream:
        if type(code) == Function:
            code.code = getFuncs(code.code, all_funcs)
            all_funcs[code.name] = code
        elif type(code) in (BasicLoop, BlockCode, ForLoop):
            code.code = getFuncs(code.code, all_funcs)
            ret.append(code)
        elif type(code) == IfBlock:
            for subblock in code.blocks:
                subblock.code = getFuncs(subblock.code, all_funcs)
            ret.append(code)
        elif type(code) == NestedLoop:
            code.left_code = getFuncs(code.left_code, all_funcs)
            code.mid_code = getFuncs(code.mid_code, all_funcs)
            code.right_code = getFuncs(code.right_code, all_funcs)
            ret.append(code)
        else:
            ret.append(code)
    return ret



def validateNested(nest):
    ret = []
    vstack = []
    for code in nest.left_code:
        if type(code) in (Function, BasicLoop, BlockCode, ForLoop):
            ret.extend(validateBrackets(code.code))
        elif type(code) == IfBlock:
            for blocks in code.blocks:
                ret.extend(validateBrackets(blocks.code))
        elif type(code) == NestedLoop:
            ret.extend(validateNested(code))
        elif type(code) == BasicCommand:
            if code.cmd == "[" or code == ":":
                vstack.append(code)
            elif code.cmd == "]":
                if vstack != [] and vstack[-1].cmd == "[":
                    vstack.pop()
                else:
                    ret.append(code)
            elif code.cmd == ";":
                if vstack != [] and vstack[-1].cmd == ":":
                    vstack.pop()
                else:
                    ret.append(code)
            elif code.cmd == "|":
                if not (vstack != [] and vstack[-1].cmd == ":"):
                    ret.append(code)

    ret.extend(validateBrackets(nest.mid_code))
    
    for code in nest.right_code:
        if type(code) in (Function, BasicLoop, BlockCode, ForLoop):
            ret.extend(validateBrackets(code.code))
        elif type(code) == IfBlock:
            for blocks in code.blocks:
                ret.extend(validateBrackets(blocks.code))
        elif type(code) == NestedLoop:
            ret.extend(validateNested(code))
        elif type(code) == BasicCommand:
            if code.cmd == "[" or code.cmd == ":":
                vstack.append(code)
            elif code.cmd == "]":
                if vstack != [] and vstack[-1].cmd == "[":
                    vstack.pop()
                else:
                    ret.append(code)
            elif code.cmd == ";":
                if vstack != [] and vstack[-1].cmd == ":":
                    vstack.pop()
                else:
                    ret.append(code)
            elif code.cmd == "|":
                if not (vstack != [] and vstack[-1].cmd == ":"):
                    ret.append(code)

    for unmatched in vstack:
        ret.append(unmatched)

    return ret


def validateBrackets(stream):
    ret = []
    vstack = []
    for code in stream:
        if type(code) in (Function, BasicLoop, BlockCode, ForLoop):
            ret.extend(validateBrackets(code.code))
        elif type(code) == IfBlock:
            for blocks in code.blocks:
                ret.extend(validateBrackets(blocks.code))
        elif type(code) == NestedLoop:
            ret.extend(validateNested(code))
        elif type(code) == BasicCommand:
            if code.cmd == "[" or code.cmd == ":":
                vstack.append(code)
            elif code.cmd == "]":
                if vstack != [] and vstack[-1].cmd == "[":
                    vstack.pop()
                else:
                    ret.append(code)
            elif code.cmd == ";":
                if vstack != [] and vstack[-1].cmd == ":":
                    vstack.pop()
                else:
                    ret.append(code)
            elif code.cmd == "|":
                if not (vstack != [] and vstack[-1].cmd == ":"):
                    ret.append(code)
    

    for unmatched in vstack:
        ret.append(unmatched)

    return ret





class Program:
    def __init__(self, raw):
        self.raw = raw
        self.functions = dict()
        self.code =secondParse(firstParse(lex(raw))) # parse the code
        unmatched = validateBrackets(self.code) # ensure all [, ], :, |, and ; are matched
        if unmatched != []:
            raise JoustSyntaxError("\n".join([f"Unmatched {x.cmd} @ {x.pos}" for x in unmatched]))
        self.code = getFuncs(self.code, self.functions) # remove functions from the code and move them to the dictionary
        temp = Function("$main", [], dict())
        temp.code = self.code
        self.code = temp

    def display(self):
        for func in self.functions.values():
            print(func, end="\n\n")
        print(self.code)


def ensurePosition(raw, stream): # this is a debug function to ensure the compiled code matches the raw text exactly
    for n in stream:
        if(type(n) == BasicCommand):
            if n.cmd != raw[n.pos]:
                print(f"Mismatch! CODE:({n.__repr__()}) RAW:({raw[n.pos]} @ {n.pos})")
        elif type(n) in (Function, BasicLoop, BlockCode, ForLoop):
            ensurePosition(raw, n.code)
        elif type(n) == IfBlock:
            for blocks in n.blocks:
                ensurePosition(raw, blocks.code)
        elif type(n) == NestedLoop:
            ensurePosition(raw, n.left_code)
            ensurePosition(raw, n.mid_code)
            ensurePosition(raw, n.right_code)
        



if __name__ == "__main__":
    raw = None
    with open("test.txt") as file:
        raw = file.read()

    try:
        test = Program(raw)

        ensurePosition(test.raw, test.code.code)
        for func in test.functions.values():
            ensurePosition(test.raw, func.code)
        print("ensurePosition complete.")

        print(test.functions)
        print(test.code)
        for value in test.functions.values():
            print(value, end="\n\n")

    except JoustSyntaxError as err:
        print(err)
    