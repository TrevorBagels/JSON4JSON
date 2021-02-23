class prompt:
	def __init__(self, j4j):
		self.j4j = j4j
		self.name = "prompt" #this makes it so that the type is used when $prompt is found
	#returns true/false, whether or not the data is this type
	#rule = the rule for this specific property. this includes the variable
	#rulename = the key of the rule that this property is found in. only place possible as of now would be under the default option.
	def get_value(self, rule, rulename='d'): 
		#get the prompt text
		pText = rule[rulename].split("$prompt ")[1]
		return input(pText)

class arg:
	def __init__(self, j4j):
		self.j4j = j4j
		self.name = "arg" #this makes it so that the type is used when $prompt is found
	#returns true/false, whether or not the data is this type
	def get_value(self, data, rule): #strings have no rules YET (todo: add min/max length)
		return str(data)