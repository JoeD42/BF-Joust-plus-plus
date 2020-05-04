from bfjpp.lexer import Token, joust_cmds
from bfjpp.code import *

class JoustSyntaxError(BaseException):
    def __init__(self, msg):
        self.msg = msg

#TODO: keywords are parsed even when they're part of a larger word, fix

def getMatching(stream, position, stream_len):
    matching = {"(": ")", "{":"}", "{%": "%}"}
    match_stack = [stream[position].t_type]
    # ret = []
    position += 1
    while position < stream_len:
        if stream[position].t_type in matching.keys():
            match_stack.append(stream[position].t_type)
        elif stream[position].t_type == matching[match_stack[-1]]:
            match_stack.pop()
            if match_stack == []: # all matches matched; RETURN
                return position
        elif stream[position].t_type in matching.values(): # found an end match with no start
            if len(match_stack) > 1:
                raise JoustSyntaxError(f"Unexpected {stream[position].t_type} on line {stream[position].line}, column {stream[position].col}; expected {matching[match_stack[-1]]}")
            else:
                raise JoustSyntaxError(f"Unmatched {stream[position].t_type} on line {stream[position].line}, column {stream[position].col}")
        # else:
        #     ret.append(stream[position])
        position += 1
        
    # we got to the end of the stream without matching everything
    raise JoustSyntaxError(f"Unexpected EOF on line {stream[-1].line}; expected {matching[match_stack[-1]]}")


precedence = { "+": 6, "-": 6, "*": 7, "/": 7, "%": 7, "|": 1, "&": 3, "^": 2, "==": 4, "!=": 4,
">": 5, "<": 5, ">=": 5, "<=": 5 }

def calcReduce(calc_stack):
	if len(calc_stack) > 2:
		#calc_stack.append(Value([calc_stack.pop(-2), calc_stack.pop(-2), calc_stack.pop(-1)]))
		calc_stack[-2].tree.append(calc_stack.pop(-3))
		calc_stack[-2].tree.append(calc_stack.pop())
		
def trinaryParse(stream):
	stream1, stream2 = [], []
	level = 1
	stream_len = len(stream)
	position = 0
	while position < stream_len: # first stream
		if stream[position].t_type == ":":
			level -= 1
			if level == 0:
				position += 1
				break
		elif stream[position].t_type == "?":
			level += 1
		stream1.append(stream[position])
		position += 1
	
	while position < stream_len: # second stream
		stream2.append(stream[position])
		position += 1
		
	if stream1 == []:
		raise JoustSyntaxError(f"")
	if stream2 == []:
		raise JoustSyntaxError(f"")
	
	return stream1, stream2
	
	

def parseCalc(stream):
	calc_stack = []
	position = 0
	stream_len = len(stream)
	while position < stream_len:
		if stream[position].t_type == "id" or stream[position].t_type == "int":
			if calc_stack != [] and calc_stack[-1].tree[0] == "!": # deal with unary operators
				calc_stack.append(Value([stream[position].t_type, stream[position].value]))
				while calc_stack[-2].tree[0] == "!": # deal with multiple unary operators
					calc_stack[-2].tree.append(calc_stack.pop())
			elif calc_stack != [] and (calc_stack[-1].tree[0] == "int" or calc_stack[-1].tree[0] == "id" or calc_stack[-1].tree[0] == "val"): # 2 consecutive values
				raise JoustSyntaxError(f"Unexpected {stream[position].value} on line {stream[position].line}, column {stream[position].col}")
			else:
				calc_stack.append(Value([stream[position].t_type, stream[position].value]))
			position += 1
		elif stream[position].t_type == "!":
			if position > 0 and (stream[position-1].t_type == "id" or stream[position-1].t_type == "int"): # ! after a value is the same as a value after a value
				raise JoustSyntaxError(f"Unexpected ! on line {stream[position].line}, column {stream[position].col}")
			calc_stack.append(Value(["!"]))
			position += 1
		elif stream[position].t_type in precedence.keys():
			if len(calc_stack) == 0 or calc_stack[-1].tree[0] in precedence.keys():
				raise JoustSyntaxError(f"Unexpected {stream[position].t_type} on line {stream[position].line}, column {stream[position].col}")
			while len(calc_stack) > 2 and precedence[calc_stack[-2].tree[0]] <= precedence[stream[position].t_type]:
				calcReduce(calc_stack)
			calc_stack.append(Value([stream[position].t_type]))
			position += 1
		elif stream[position].t_type == "(":
			if calc_stack != [] and (calc_stack[-1].tree[0] == "int" or calc_stack[-1].tree[0] == "id" or calc_stack[-1].tree[0] == "val"): # 2 consecutive values
				raise JoustSyntaxError(f"Unexpected {stream[position].t_type} on line {stream[position].line}, column {stream[position].col}")
			new_pos = getMatching(stream, position, stream_len)
			calc_stack.append(parseCalc(stream[position+1:new_pos]))
			while len(calc_stack) > 1 and calc_stack[-2].tree[0] == "!":
				calc_stack[-2].tree.append(calc_stack.pop())
			position = new_pos + 1
		elif stream[position].t_type == "?":
			# trinary operator
			if calc_stack == []:
				raise JoustSyntaxError(f"No first argument for trinary operator '?' on line {stream[position].line}, column {stream[position].col}")
			while len(calc_stack) > 2:
				calcReduce(calc_stack)
			temp1, temp2 = trinaryParse(stream[position+1:])
			calc_stack.append(parseCalc(temp1))
			calc_stack.append(parseCalc(temp2))
			calc_stack = [Value(["?", calc_stack[-3], calc_stack[-2], calc_stack[-1]])]
			position = stream_len # break
		elif stream[position].t_type in ":)":
			raise JoustSyntaxError(f"Unmatched {stream[position].t_type} on line {stream[position].line}, column {stream[position].col}")
		else:
			raise JoustSyntaxError(f"Unexpected command {stream[position].t_type} on line {stream[position].line}, column {stream[position].col}")
		
			
	while len(calc_stack) > 2:
		calcReduce(calc_stack)
		
	if len(calc_stack) > 1:
		raise JoustSyntaxError(f"Unexpected {stream[-1].t_type} on line {stream[-1].line}, column {stream[-1].col}")
		
	return calc_stack[0]

def parseCmd(stream, cmd, line, col):
	ret = None
	if cmd == "call":
		if len(stream) > 0 and stream[0].t_type == "id":
			temp = []
			for element in stream[1:]:
				temp.append(getValue(element))
			ret = CallCmd(stream[0].value, temp)
		else:
			raise JoustSyntaxError(f"Expected id in call command instead of {stream[0].t_type if stream != [] else 'nothing'} on line {stream[0].line if stream != [] else line}, column {stream[0].col if stream != [] else col}")
	elif cmd == "block":
		vars = dict()
		last = None
		for element in stream:
			if not last: # variable name
				if element.t_type == "id":
					vars[element.value] = None
					last = element.value
				else:
					JoustSyntaxError(f"Expected id in block header instead of {element.t_type} on line {element.line}, column {element.col}")
			else: # variable value
				vars[last] = getValue(element)
				last = None # reset
		if last: # if a variable isn't given a value
			raise JoustSyntaxError(f"Expected value after id in block header on line {stream[-1].line}, column {stream[-1].col}")
		ret = BlockCode(vars)
	elif cmd == "def":
		if len(stream) > 0 and stream[0].t_type == "id":
			position = 1
			args = []
			vars = dict()
			while position < len(stream): # args first
				if stream[position].t_type == "id":
					args.append(stream[position].value)
				elif stream[position].t_type == "::":
					position += 1
					break
				else:
					raise JoustSyntaxError(f"Expected id instead of {stream[position].t_type} in def header on line {stream[position].line}, column {stream[position].col}")
				position += 1
			last = None
			for element in stream[position:]: # then vars, if any
				if not last: # variable name
					if element.t_type == "id":
						vars[element.value] = None
						last = element.value
					else:
						JoustSyntaxError(f"Expected id in block header instead of {element.t_type} on line {element.line}, column {element.col}")
				else: # variable value
					vars[last] = getValue(element)
					last = None # reset
			if last: # if a variable isn't given a value
				raise JoustSyntaxError(f"Expected value after id in block header on line {stream[-1].line}, column {stream[-1].col}")
			ret = Function(stream[0].value, args, vars)
		else:
			raise JoustSyntaxError(f"Expected function name in def header instead of {stream[0].t_type if stream != [] else 'nothing'} on line {stream[0].line if stream != [] else line}, column {stream[0].col if stream != [] else col}")
	elif cmd == "if" or cmd == "elif":
		if len(stream) > 0:
			cond = getValue(stream[0])
		else:
			raise JoustSyntaxError(f"Expected conditional in {cmd} header instead of {stream[0].t_type if stream != [] else 'nothing'} on line {stream[0].line if stream != [] else line}, column {stream[0].col if stream != [] else col}")
		ret = IfSubBlock(cond)
	elif cmd == "for":
		if len(stream) >= 4 and stream[0].t_type == "id":
			main = []
			for pos in range(1, 4):
				main.append(getValue(stream[pos]))
			vars = dict()
			if len(stream) > 4:
				if stream[4].t_type == "::":
					state = 0 # 0 name, 1 ini, 2 step
					last = None
					for element in stream[5:]:
						if state == 0 and element.t_type == "id":
							vars[element.value] = []
							last = element.value
						elif state == 1 or state == 2:
							vars[last].append(getValue(element))
						else:
							raise JoustSyntaxError(f"Expected id in for header instead of {element.t_type} on line {element.line}, column {element.col}")
						state = (state + 1) % 3
					if state != 0: # didn't get the two arguments after a variable declaration
						raise JoustSyntaxError(f"Expected value after id in block header on line {stream[-1].line}, column {stream[-1].col}")
				else:
					raise JoustSyntaxError(f"Expected :: in for header instead of {stream[4].t_type} on line {stream[4].line}, column {stream[4].col}")
			ret = ForLoop(stream[0].value, main[0], main[1], main[2], vars)
		elif len(stream) < 4:
			raise JoustSyntaxError(f"Not enough arguments in for header on line {line}, column {col}")
		else:
			raise JoustSyntaxError(f"Expected id in for header instead of {stream[0].t_type} on line {stream[0].line}, column {stream[0].column}")


	return ret
	



def interiorCmd(stream):
	stream_len = len(stream)
	ret = Token("", stream[0].line, stream[0].col, value=[])
	position = 0
	if stream[0].t_type in ["for", "endfor", "def", "enddef", "block", "endblock", "call", "if", "elif", "else", "endif"]:
		ret.t_type = stream[0].t_type
		position = 1
	else:
		ret.t_type = "val"
		ret.value = parseCalc(stream)
		return ret

	while position < stream_len:
		if stream[position].t_type == "(":
			new_pos = getMatching(stream, position, stream_len)
			ret.value.append(Token("val", stream[0], stream[0], parseCalc(stream[(position+1):new_pos])))
			position = new_pos + 1
		else:
			ret.value.append(stream[position])
			position += 1

	ret.value = parseCmd(ret.value, ret.t_type, ret.line, ret.col)
	return ret

# define all cmd blocks, and what's inside them

def firstParse(stream):
	stream_len = len(stream)
	position = 0
	ret = []
	try:
		while position < stream_len:
			if stream[position].t_type == "{%":
				new_pos = getMatching(stream, position, stream_len)
				ret.append(interiorCmd(stream[position+1:new_pos]))
				position = new_pos + 1
			else:
				ret.append(stream[position])
				position += 1
		return ret
	except JoustSyntaxError as err:
		print(err.msg)
		return []


def matchingBlock(stream, position, stream_len):
	matching = {"if": "endif", "for":"endfor", "def": "enddef", "block": "endblock", }
	match_stack = [stream[position].t_type]
	position += 1
	while position < stream_len:
		if stream[position].t_type in matching.keys():
			match_stack.append(stream[position].t_type)
		elif stream[position].t_type == matching[match_stack[-1]]:
			match_stack.pop()
			if match_stack == []: # all matches matched; RETURN
				return position
		elif stream[position].t_type in matching.values(): # found an end match with no start
			if len(match_stack) > 1:
				raise JoustSyntaxError(f"Unexpected {stream[position].t_type} on line {stream[position].line}, column {stream[position].col}; expected {matching[match_stack[-1]]}")
			else:
				raise JoustSyntaxError(f"Unmatched {stream[position].t_type} on line {stream[position].line}, column {stream[position].col}")
		position += 1
        
    # we got to the end of the stream without matching everything
	raise JoustSyntaxError(f"Unexpected EOF on line {stream[-1].line}; expected {matching[match_stack[-1]]}")



def getValue(token):
	if token.t_type == "id" or token.t_type == "int":
		return Value([token.t_type, token.value])
	elif token.t_type == "val":
		return token.value
	else:
		raise JoustSyntaxError(f"Expected value instead of {token.t_type} on line {token.line}, column {token.col}")

	
# first sub if seems to not get condition
def secondParse(stream, loop=False): # loop="{" for (a{b}c)%1 kinds of loops, "?" for if blocks, False for everything else
	position = 0
	stream_len = len(stream)
	ret = []
	final_ret = []
	if loop == "?": # make sure we get that first if subblock
		final_ret.append(stream[0].value)
		position = 1
	while position < stream_len:
		if stream[position].t_type in joust_cmds: # basic bf commands
			ret.append(BasicCommand(stream[position].t_type, stream[position].pos))
			position += 1
		elif stream[position].t_type == "(": # basic loops
			new_pos = getMatching(stream, position, stream_len)
			if (new_pos + 2) < stream_len: # make sure there's stuff afterwards
				if stream[new_pos+1].t_type == "%":
					loop_num = getValue(stream[new_pos+2])
					temp = secondParse(stream[position+1:new_pos], loop="{")
					ret.append(NestedLoop(loop_num, temp[0], temp[1], temp[2]))
				elif stream[new_pos+1].t_type == "*":
					ret.append(BasicLoop(getValue(stream[new_pos+2]), secondParse(stream[position+1:new_pos])))
				else:
					raise JoustSyntaxError(f"Expected * or % after ) but got {stream[new_pos+1].t_type if (new_pos + 1) < stream_len else 'EOF'} on line {stream[new_pos+1].line if  (new_pos + 1) < stream_len else stream[-1].line}, column {stream[new_pos+1].col if  (new_pos + 1) < stream_len else stream[-1].col}")
			else:
				raise JoustSyntaxError(f"Expected value after parenthesis on line {stream[-1].line}, column {stream[-1].col}")
			position = new_pos + 3
		elif stream[position].t_type == "call":
			ret.append(stream[position].value)
			position += 1
		elif stream[position].t_type == "def" or stream[position].t_type == "block" or stream[position].t_type == "for":
			ret.append(stream[position].value)
			new_pos = matchingBlock(stream, position, stream_len)
			ret[-1].code = secondParse(stream[position+1:new_pos])
			position = new_pos + 1
		elif stream[position].t_type == "if":
			new_pos = matchingBlock(stream, position, stream_len)
			ret.append(IfBlock(secondParse(stream[position:new_pos], loop="?")))
			position = new_pos + 1
		elif stream[position].t_type == "{" and loop == "{":
			new_pos = getMatching(stream, position, stream_len)
			final_ret.append(ret)
			final_ret.append(secondParse(stream[position+1:new_pos]))
			ret = []
			position = new_pos + 1
		elif stream[position].t_type == "elif" and loop == "?":
			if type(final_ret[-1]) == ElseSubBlock:
				raise JoustSyntaxError(f"Cannot have an elif after an else! Line {stream[position].line}, column {stream[position].col}")
			final_ret[-1].code = ret
			final_ret.append(stream[position].value)
			ret = []
			position += 1
		elif stream[position].t_type == "else" and loop == "?":
			if type(final_ret[-1]) == ElseSubBlock:
				raise JoustSyntaxError(f"Cannot have two elses in an if block! Line {stream[position].line}, column {stream[position].col}")
			final_ret[-1].code = ret
			final_ret.append(ElseSubBlock())
			ret = []
			position += 1
		else:
			raise JoustSyntaxError(f"Unexpected {stream[position].t_type} on line {stream[position].line}, column {stream[position].col}")
	
	if loop == "{":
		final_ret.append(ret)
		ret = final_ret
	elif loop == "?":
		final_ret[-1].code = ret
		ret = final_ret
	
	return ret

if __name__ == "__main__":
	from lexer import lex
	# test = """>+[](.)*90{% for tape 9 30 1 :: lock (128 - 9) -1%}((+)*256 \n(>)*tape (+.)*lock{*yo\n wassup?*} (<)*tape)*{%3%}{%endfor %}(+{(-)*1}[])%1"""
	test = None
	with open("test.txt", "r") as file:
		test = file.read()
	try:
		for i in secondParse(firstParse(lex(test))):
			print(i)
		# for i in firstParse(lex(test)):
		# 	print(i)
	except JoustSyntaxError as err:
		print(err.msg)