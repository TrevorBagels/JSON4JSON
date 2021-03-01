from ..utils import seperate_string_number
import math





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
		multiplier = float(self.ajson.getProperty(rule, "multiplier", noneFound=1))
		value *= multiplier
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
	def convert(self, data, rules, parent):
		#length
		minLength = self.ajson.getProperty(rules, "minLength", noneFound=0)
		maxLength = self.ajson.getProperty(rules, "maxLength", noneFound=math.inf)
		if len(data) < minLength:
			self.ajson.log("Array too short!", error=True)
		if len(data) > maxLength:
			data = data[:maxLength]
		
		for x,i in zip(data, range(0, len(data))):
			#convert single
			usedRule = rules['rule']
			#check if we have any custom defined rules
			if f"rule#{i}" in rules:
				usedRule = rules[f'rule#{i}']
			data[i] = self.ajson.convertSingle(x, usedRule, parent=parent)
		return data
