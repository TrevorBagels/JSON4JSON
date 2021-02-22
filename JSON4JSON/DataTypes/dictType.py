
class dictType:
	def __init__(self, ajson):
		self.name = "object"
		self.ajson = ajson
		self.default = {}
	#returns true/false, whether or not the data is this type
	def matches(self, data):
		if type(data) == dict:
			return True
		return False
	def convert(self, data, rules):#this ones different, since it's a dictionary, therefore it has multiple values of different types (including other dictionaries/objects)
		oldRules = rules
		rules = oldRules['rules']
		for key in rules:
			if key.startswith("//"): #ignore, this is a comment
				continue
			if key[0] == "@": #this overrides default settings
				self.ajson.set_value(self.ajson.defaults, key.split("@")[1], rules[key])
				continue
			if key not in data and self.ajson.getProperty(rules[key], "autoAdd", noneFound=self.ajson.defaults['autoAdd']):
				self.ajson.log(f"Key \"{key}\" not in data file. Setting to default.", level=-2)
				data[key] = self.ajson.getDefault(rules[key])
			#check if this makes a variable. if so, set the variable to the value.
			if "varSet" in rules[key]:
				self.ajson.log(f"Setting variable {rules[key]['varSet']}", level=-1)
				self.ajson.vars[rules[key]['varSet']] = data[key]
			if key in data:
				data[key] = self.ajson.convertSingle(data[key], rules[key])
		return data