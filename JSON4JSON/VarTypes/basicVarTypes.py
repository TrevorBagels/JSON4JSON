import argparse, shlex, sys
class prompt:
	def __init__(self, j4j):
		self.j4j = j4j
		self.name = "prompt" #this makes it so that the type is used when $prompt is found
	#returns true/false, whether or not the data is this type
	#rule = the rule for this specific property. this includes the variable
	#rulename = the key of the rule that this var is found in. only place possible as of now would be under the default option.
	def get_value(self, rule, value=''):
		#get the prompt text
		pText = value.split("$prompt ")[1]
		return input(pText)

class arg:
	def __init__(self, j4j):
		self.j4j = j4j
		self.name = "arg" #this makes it so that the type is used when $arg is found
	#returns true/false, whether or not the data is this type
	def get_value(self, rule, value=''): #strings have no rules YET (todo: add min/max length)
		name = value.split("$arg ")[1]
		value = None
		for x, i in zip(sys.argv, range(len(sys.argv))):
			if x == name:
				value = sys.argv[i+1]
				break
		return value