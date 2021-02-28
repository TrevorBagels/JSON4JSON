
from copy import deepcopy
import random

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
	def convert(self, data, rules, parent={}, root=False):#this ones different, since it's a dictionary, therefore it has multiple values of different types (including other dictionaries/objects)
		data['_defaults'] = {} #reserved property defaults
		data['_variables'] = {} #reserved property variables
		#set defaults to parent's defaults, then override some of them.
		data['_defaults'] = deepcopy(parent['_defaults'])
		
		oldRules = rules #rules set for the object
		rules = oldRules['rules'] #these rules are basically the properties of the object
		for key in rules:
			if key.startswith("//"): #ignore, this is a comment
				continue
			#region rule file only			
			if key.startswith("@@"): #this sets the settings of JSON4JSON
				self.ajson.set_value(self.ajson.globals, key.split("@@")[1], rules[key])
				continue
			if key[0] == "@": #this overrides default settings
				self.ajson.set_value(data['_defaults'], key.split("@")[1], rules[key])
				continue
			#endregion

			#if this property wasn't supplied, and autoAdd is enabled
			if key not in data and self.ajson.getProperty(rules[key], "autoAdd", noneFound=data["_defaults"]['autoAdd']):
				#add the property
				data[key] = self.ajson.getDefault(rules[key], data)
			
			#check if this makes a variable. if so, set the variable to the value.
			if "varSet" in rules[key]:
				self.ajson.log(f"Setting variable {rules[key]['varSet']}", level=-1)
				self.ajson.vars[rules[key]['varSet']] = data[key]
			if key in data:
				data[key] = self.ajson.convertSingle(data[key], rules[key], parent=data)
		return data