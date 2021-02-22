from utils import seperate_string_number
import math

class DataTypes:
	class string:
		def __init__(self, ajson):
			self.ajson = ajson
			self.name = "string"
			self.default = ""
		#returns true/false, whether or not the data is this type
		def matches(self, data):
			if type(data) == str:
				return True
			return False
		def convert(self, data, rule): #strings have no rules YET (todo: add min/max length)
			return str(data)
	class number:
		def __init__(self, ajson):
			self.name = "number"
			self.ajson = ajson
			self.default = 0
		#returns true/false, whether or not the data is this type
		def matches(self, data):
			newData = data
			try:
				newData = float(data)
			except:
				return False
			return type(newData) == float or type(newData) == int
		def convert(self, data, rule):
			value = float(data)
			minval = self.ajson.getProperty(rule, "min", noneFound=-math.inf)
			maxval = self.ajson.getProperty(rule, "max", noneFound=math.inf)
			isInt = self.ajson.getProperty(rule, "int", noneFound=False)
			if isInt:
				value = int(value)
			return min(max(value, minval), maxval)
	class anyType:
		def __init__(self, ajson):
			self.name = "any"
			self.ajson = ajson
			self.default = None
		#returns true/false, whether or not the data is this type
		def matches(self, data):
			return True
		def convert(self, data, rule):
			return data
	class boolean:
		def __init__(self, ajson):
			self.name = "bool"
			self.ajson = ajson
			self.default = False
		#returns true/false, whether or not the data is this type
		def matches(self, data):
			return type(data) == bool
		def convert(self, data, rule):
			return data == True
	class time:
		def __init__(self, ajson):
			self.name = "time"
			self.ajson = ajson
			self.default = "0s"
		#returns true/false, whether or not the data is this type
		def matches(self, data):
			if type(data) == str:
				if seperate_string_number(data)[1] in self.ajson.units[self.name]:
					return True
			return False
		def convert(self, data, rule):
			value = seperate_string_number(data)
			return self.ajson.units[self.name][value[1]] * float(value[0])
	class distance:
		def __init__(self, ajson):
			self.name = "distance"
			self.ajson = ajson
			self.default = "0m"
		#returns true/false, whether or not the data is this type
		def matches(self, data):
			if type(data) == str:
				if seperate_string_number(data)[1] in self.ajson.units[self.name]:
					return True
			return False
		def convert(self, data, rule):
			value = seperate_string_number(data)
			return self.ajson.units[self.name][value[1]] * float(value[0])
	class arrayType:
		def __init__(self, ajson):
			self.name = "array"
			self.ajson = ajson
			self.default = []
		#returns true/false, whether or not the data is this type
		def matches(self, data):
			if type(data) == list:
				return True
			return False
		def convert(self, data, rules):#this ones different, since it's a dictionary, therefore it has multiple values of different types (including other dictionaries/objects)
			for x,i in zip(data, range(0, len(data))):
				#convert single
				data[i] = self.ajson.convertSingle(x, rules['rule'])
			return data
	
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
				if key not in data:
					self.ajson.log(f"Key \"{key}\" not in data file. Setting to default.", level=-2)
					data[key] = self.ajson.getDefault(rules[key])
				#check if this makes a variable. if so, set the variable to the value.
				if "varSet" in rules[key]:
					self.ajson.log(f"Setting variable {rules[key]['varSet']}", level=-1)
					self.ajson.vars[rules[key]['varSet']] = data[key]
				data[key] = self.ajson.convertSingle(data[key], rules[key])
			
			return data
		
	allTypes = [anyType, string, number, boolean, time, dictType, distance, arrayType]
