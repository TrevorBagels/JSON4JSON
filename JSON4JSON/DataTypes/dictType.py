from copy import deepcopy, copy

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
	def convert(self, data, rules, parent={}):#this ones different, since it's a dictionary, therefore it has multiple values of different types (including other dictionaries/objects)
		data['_defaults'] = {} #reserved property defaults
		data['_variables'] = {} #reserved property variables
		#set defaults to parent's defaults, then override some of them. 
		data['_defaults'] = deepcopy(parent['_defaults'])
		#data["_variables"] = deepcopy(parent["_variables"]) We could do this, or we could make it so that if a variable isn't found, check the next parent up.
		oldRules = rules #rules set for the object
		rules = oldRules['rules'] #these rules are basically the properties of the object
		for property in rules:
			if property.startswith("//"): #ignore, this is a comment
				continue
			#region rule file only	
			if property.startswith("@@"): #this sets the settings of JSON4JSON
				self.ajson.set_value(self.ajson.globals, property.split("@@")[1], rules[property])
				continue
			if property[0] == "@": #this overrides default settings
				#get the parent that this refers to. as in, are there any periods after @?
				targetParent = data
				targetRule = property.split("@")[1]
				if property[1] == ".":
					targetParent = self.ajson.getParent(data, level=property.count("."))
					targetRule = property.split("@" + (property.count(".") * ".") )[1]
				self.ajson.set_value(targetParent['_defaults'], targetRule, rules[property], parent=data)
				continue
			#endregion
			if property not in data:
				if self.ajson.getProperty(rules[property], "r", noneFound=data["_defaults"]['r']): #required property. not found. throw an error.
					self.ajson.log(f"Property with key \"{property}\" was not found in the config file. ", error=True)
			#if this property wasn't supplied, and autoAdd is enabled
			if property not in data and self.ajson.getProperty(rules[property], "autoAdd", noneFound=data["_defaults"]['autoAdd']):
				#add the property
				data[property] = self.ajson.getDefault(rules[property], data)
			#check if this makes a variable. if so, set the variable to the value.
			if "varSet" in rules[property]:
				self.ajson.log(f"Setting variable {rules[property]['varSet']}", level=-1)
				varToSet = rules[property]['varSet']
				targetParentLevel = 0
				for x in copy(varToSet):
					if x == ".":
						targetParentLevel += 1
						varToSet = varToSet[1:]
					else:
						break
				targetObject = self.ajson.getParent(data, level=targetParentLevel)
				targetObject['_variables'][varToSet] = data[property]
			if property in data:
				data[property] = self.ajson.convertSingle(data[property], rules[property], parent=data)
		return data