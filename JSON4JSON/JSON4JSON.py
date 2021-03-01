import json, os, sys, traceback, copy
from .utils import seperate_string_number
from .DataTypes import DefaultTypes
from .VarTypes import DefaultVarTypes

class JSON4JSON:
	def __init__(self):
		self.dataTypes = {}
		self.varTypes  = {}
		self.vars      = {}
		self.data      = {} #this is the loaded and mostly filtered data

		self.objects   = {"ROOT": self.data} #this keeps track of object hierarchy
		self.uidLevel = 0 #for keeping track object hierarchy
		#globals are properties for how JSON4JSON functions. Mostly for logging and stuff.
		self.globals = {"logging": 4, "tracebackLogging": True}
		#defaults are the default properties of objects. 
		self.defaults = {
			"unit": {"time": "s", "distance": "m"},
			"autoAdd": True,
			"t": "string",
			"r" : False
		}
		DefaultTypes.LoadDefaultDatatypes(self) #user created datatypes can be added via the method in this method as well
		DefaultVarTypes.LoadDefaultVarTypes(self)
		#something like 
		#configParser = JSON4JSON()
		#configParser.add_data_type(myCustomDataType)

		
	def add_data_type(self, dataType):#renamed from addDataType
		dataTypeInstance = dataType(self)
		self.dataTypes[dataTypeInstance.name] = dataTypeInstance
	def add_var_type(self, varType):
		varTypeInstance = varType(self)
		self.varTypes[varTypeInstance.name] = varTypeInstance
	def load(self, jsonFile, ruleFile):
		data = None
		self.rules = None
		try:
			with open(jsonFile, "r") as f:
				data = json.loads(f.read())
		except:
			self.log(f"Could not read JSON file \"{jsonFile}\"", error=True)	
		with open(ruleFile, "r") as f:
			self.rules = json.loads(f.read())
		self.convertAll(data, self.rules)
	
	def convertAll(self, data, rules): #data: dictionary (right after loading json), rules: dictionary from the raw json stuff...
		#this basically wraps everything into one object and then starts recursively converting it
		self.data = self.convertSingle(data, {"t": "object", "rules": rules}, parent={"_parent": "ROOT", "_uid": "ROOT", "_defaults": self.defaults, "_variables": {}}, setUID="ROOT")
	
	def convertSingle(self, data, rule, parent=None, setUID=None):
		uid = setUID
		if uid == None:
			uid = self.getUid()
		#data is the actual data, rule is the rule OBJECT for this. first, make sure the data type matches with the rule
		expectedType = self.getProperty(rule, "t", noneFound="any")
		data = self.testVar(data, parent, rule=rule) #does this start with $? if so, it's a variable.  TODO make sure this uses the parent
		#allow comments on property values
		if type(data) == str:
			try:
				data = data.split("//")[0]
			except:
				pass
		#istype?
		if expectedType in self.dataTypes:
			isValid = self.dataTypes[expectedType].matches(data) #makes sure that this is the right data type
			if isValid:
				#wait. is this a dict? if so, we need to pass the parent dictionary's defaults and variables
				if type(data) == dict:
					data["_uid"] = uid
					data["_parent"] = parent['_uid']
					self.objects[uid] = data
					data = self.dataTypes[expectedType].convert(data, rule, parent=parent)
				elif type(data) == list:
					data = self.dataTypes[expectedType].convert(data, rule, parent=parent)
				else:
					data = self.dataTypes[expectedType].convert(data, rule)
		else:
			self.log("Warning: invallid type \"" + expectedType + "\"")
		return data
	
	#returns the parent object
	def getParent(self, data, level=1):
		uid = data['_uid']
		parent = data['_uid']
		for x in range(0, level):
			parent = self.objects[parent]["_parent"]
		return self.objects[parent]
	def getUid(self):
		self.uidLevel += 1
		return str(self.uidLevel)
	def getDefault(self, rule, objectData):
		if "d" in rule:
			return rule["d"]
		if "t" not in rule:
			rule['t'] = objectData['_defaults']['t'] #default is "string"
		return copy.deepcopy(self.dataTypes[rule['t']].default) #last resort, pretty common, just use the default value associated with this type.
	
	def testVar(self, value, parent, rule={}, root=0):#run pretty much every value through this function in case it's a ref to a variable
		if type(value) == str and value.startswith("$"):#it's a variable
			if value.startswith("$$"):#it's a user defined variable
				variable = value.split("$$")[1]
				parentLevel = 0
				for x in copy.copy(variable):
					if x == ".":
						parentLevel += 1
						variable = variable[1:]
					else:
						break
				targetParent = self.getParent(parent, level = parentLevel)
				if variable in targetParent["_variables"]:
					return targetParent["_variables"][variable]
				else:
					#ok so we couldn't find this variable. Try again, but go up one parent.
					if parent['_uid'] == "ROOT":
						root += 1
					if root < 2:
						return self.testVar(value[:2] + "." + value[2:], parent, rule=rule, root=root)
					self.log(f"Variable \"{variable}\" does not exist!", level=5)
			else:
				#ok so it's a special type of variable, possibly $prompt or $arg.
				varTypeName = value.split("$")[1].split(" ")[0]
				if varTypeName in self.varTypes:
					varType = self.varTypes[varTypeName]
					if varType == None:
						self.log(f"No such varType \"{varTypeName}\"", error=True)
					else:
						return varType.get_value(rule)
		return value
	
	def getProperty(self, dictionary, key, noneFound=None): #one line way of retrieving a value from a dictionary using a key.
		if key not in dictionary:
			return noneFound
		else:
			return dictionary[key]
	
	def merge_dicts(self, d1, d2): #puts d2 into d1. i love recursive functions. note, arrays get overwritten and deep copied, they don't merge
		for x in d2:
			if type(d2[x]) not in [dict, list]:
				d1[x] = d2[x]
			elif type(d2[x]) == dict:
				self.merge_dicts(d1[x], d2[x])
			elif type(d2[x]) == list:
				d1[x] = copy.deepcopy(d2[x])
		return True
			
	def set_value(self, dictionary, key, newValue, parent=None):#dictionary = the dict to use, key = the key of the property, newValue = the new value
		self.merge_dicts(dictionary, {key: self.testVar(newValue, parent)})
		return True
	

	def log(self, *args, **kw):
		level = kw.get('level', 0)
		error = kw.get('error', False)
		warning = kw.get('warning', False)
		if error:
			level = 5
		if warning:
			level = 4
		if self.globals['logging'] > level:
			return
		out = kw.get('file',sys.stdout)
		linesep= kw.get('end','\n')
		colsep= kw.get('sep',' ')

		tb = traceback.format_stack()
		tbtxt = "\n" + tb[len(tb)-2].split("\n")[0] + "\n"
		if self.globals['tracebackLogging'] == False:
			tbtxt = ""
		if error:
			raise Exception(colsep.join(map(str,args)))
		
		out.write(tbtxt + colsep.join(map(str,args)))
		out.write(linesep)

