import re

class Token:
    def __init__(self, t_type, line, col, value=None, pos=-1):
        self.t_type = t_type
        self.value = value
        self.line = line
        self.col = col
        self.pos = pos

    def __str__(self):
        if type(self.value) == list:
            return f"{self.t_type}( {' '.join([str(e) for e in self.value])} )"
        elif self.value:
            return f"{self.t_type}({self.value})"
        else:
            return f"'{self.t_type}'"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, a):
        return self.t_type == a.t_type and self.value == a.value

# def findMatchingParen(cmd, i, line, col):
#     level = 1
#     while i < len(cmd):
#         if cmd[i] == "(":
#             level += 1
#         elif cmd[i] == ")":
#             level -= 1
#             if level <= 0:
#                 break
#         i += 1
#     if level > 0:
#         raise JoustSyntaxError(f"Unmatched parenthesis on line {line} @ position {col}\n\t{}")
#     return i
        

# def interior_cmd_lex(cmd, line, col):
#     cmd_re = re.compile(r"(def)|(enddef)|(call)|(for)|(endfor)|(if)|(elif)|(else)|(endif)|(block)|(endblock)|(::)|(==)|(!=)|(>=)|(<=)|[-+*/%!:?<>()|&^]")
#     id_re = re.compile(r"[a-zA-Z_]\w*")
#     num_re = re.compile(r"-?[0-9]+")
#     ret = []
#     i = 0
#     while i < len(cmd):
#         # if cmd[i] == "(":
#         #     new_i = findMatchingParen(cmd, i+1, line, col)
#         #     temp = cmd[i+1:new_i]
#         #     ret.append(Token("val", line, col, interior_cmd_lex(temp, line, col)))
#         #     line, col = inline_getpos(temp, line, col)
#         #     i = new_i + 1
#         #     continue

#         temp = num_re.match(cmd, i)
#         if temp:
#             ret.append(Token("int", line, col, value=temp.group()))
#             i=temp.end()
#             col += len(temp.group())
#             continue

#         temp = cmd_re.match(cmd, i)
#         if temp:
#             ret.append(Token(temp.group(), line, col))
#             i = temp.end()
#             col += len(temp.group())
#             continue

#         temp = id_re.match(cmd, i)
#         if temp:
#             ret.append(Token("id", line, col, value=temp.group()))
#             i = temp.end()
#             col += len(temp.group())
#             continue

#         if cmd[i] == "\n":
#             col = 0
#             line += 1

#         i += 1
#         col += 1
#     return ret

def inline_getpos(raw, line, col):
    for c in raw:
        if c == "\n":
            line += 1
            col = 1
        else:
            col += 1
    return line, col

joust_cmds = "+-<>[].,#~?=!&:|;"

def lex(raw):
    ret = []
    i = 0
    joust_pre = "(){}*%"
    interior_cmds = re.compile(r"(::)|(==)|(!=)|(>=)|(<=)|[-+*/%!:?<>()|&^]")
    keywords = re.compile(r"(def)|(enddef)|(call)|(for)|(endfor)|(if)|(elif)|(else)|(endif)|(block)|(endblock)")
    comment_re = re.compile(r"\{\*(?:(?!\*\})[\s\S])*\*\}", re.MULTILINE)
    id_re = re.compile(r"[A-Za-z_]\w*")
    num_re = re.compile(r"-?[0-9]+")
    cmd_start = re.compile(r"\{%")
    cmd_end = re.compile(r"%\}")
    line = 1
    col = 1
    state = False
    while i < len(raw):
        temp = comment_re.match(raw, i)
        if temp:
            # don't add to ret, comments are ignored
            line, col = inline_getpos(temp.group(), line, col)
            i = temp.end()
            continue

        temp = keywords.match(raw, i)
        if temp:
            ret.append(Token(temp.group(), line, col))
            col += len(temp.group())
            i = temp.end()

        temp = id_re.match(raw, i)
        if temp:
            ret.append(Token("id", line, col, value=temp.group()))
            col += len(temp.group())
            i = temp.end()
            continue

        temp = num_re.match(raw, i)
        if temp:
            ret.append(Token("int", line, col, value=temp.group()))
            col += len(temp.group())
            i = temp.end()
            continue

        elif raw[i] == "\n":
            line += 1
            col = 1
            i += 1
            continue

        if state:
            temp = cmd_end.match(raw, i)
            if temp and state == "{%":
                ret.append(Token(temp.group(), line, col))
                col += len(temp.group())
                i = temp.end()
                state = False
                continue

            temp = interior_cmds.match(raw, i)
            if temp:
                ret.append(Token(temp.group(), line, col))
                col += len(temp.group())
                i = temp.end()
                continue
        else:
            temp = cmd_start.match(raw, i)
            if temp:
                ret.append(Token(temp.group(), line, col))
                col += len(temp.group())
                i = temp.end()
                state = temp.group()
                continue


            if raw[i] in joust_cmds:
                ret.append(Token(raw[i], line, col, pos=i))
            elif raw[i] in joust_pre:
                ret.append(Token(raw[i], line, col))
        
        col += 1
        i += 1
    
    return ret


if __name__ == "__main__":
    test = ">+[](.)*90{% for tape 9 30 1 :: lock (128 - 9) -1%}((+)*256 \n(>)*tape (+.)*lock{*yo\n wassup?*} (<)*tape)*{(3)}{%endfor %}(a{ (b)}c)%d"
    for e in lex(test):
        print(e, f"\n\ton line {e.line}, column {e.col}. [@{e.pos}]")