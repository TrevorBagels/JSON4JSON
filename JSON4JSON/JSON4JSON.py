import json, os, sys, traceback
from .utils import seperate_string_number
from .DataTypes import DefaultTypes
from .VarTypes import DefaultVarTypes
class JSON4JSON:
	def __init__(self):
		self.dataTypes = {}
		self.varTypes  = {}
		self.vars      = {}
		self.data      = {} #this is the loaded and mostly filtered data
		self.defaults = {
			"unit": {"time": "s", "distance": "m"},
			"autoAdd": True,
			"t": "string",
			"logging": 4, #logs warnings (4) and errors (5). everything EQUAL TO OR GREATER THAN the logging level is what gets logged.
			"tracebackLogging": True
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
		rules = None
		try:
			with open(jsonFile, "r") as f:
				data = json.loads(f.read())
		except:
			self.log(f"Could not read JSON file {jsonFile}", error=True)
				
		with open(ruleFile, "r") as f:
			rules = json.loads(f.read())
		self.convertAll(data, rules)
	


	def convertAll(self, data, rules): #data: dictionary (right after loading json), rules: dictionary from the raw json stuff...
		#start by setting up
		#hmmm maybe we should just use the conversion from datatypes.dicttype. unify everything, yknow
		#yes
		self.data = self.convertSingle(data, {"t": "object", "rules": rules})
	def log(self, *args, **kw):
		level = kw.get('level', 0)
		error = kw.get('error', False)
		warning = kw.get('warning', False)
		if error:
			level = 5
		if warning:
			level = 4
		
		if self.defaults['logging'] > level:
			return
		
		out = kw.get('file',sys.stdout)
		linesep= kw.get('end','\n')
		colsep= kw.get('sep',' ')

		tb = traceback.format_stack()
		tbtxt = "\n" + tb[len(tb)-2].split("\n")[0] + "\n"
		if self.defaults['tracebackLogging'] == False:
			tbtxt = ""
		
		out.write(tbtxt + colsep.join(map(str,args)))
		out.write(linesep)
	
	def convertSingle(self, data, rule):
		#data is the actual data, rule is the rule OBJECT for this. first, make sure the data type matches with the rule
		expectedType = self.getProperty(rule, "t", noneFound="any")
		data = self.testVar(data, rule=rule) #does this start with $? if so, it's a variable. 
		#allow comments on property values
		if type(data) == str:
			try:
				data = data.split("//")[0]
			except:
				pass
		#istype?
		if expectedType in self.dataTypes:
			isValid = self.dataTypes[expectedType].matches(data)
			if isValid:
				data = self.dataTypes[expectedType].convert(data, rule)
		else:
			self.log("Warning: invallid type \"" + expectedType + "\"")

		return data
	
	def getDefault(self, rule):
		if "d" in rule:
			return rule["d"]
		if "t" not in rule:
			rule['t'] = self.defaults['t'] #default is "string"
		return self.dataTypes[rule['t']].default
	
	def testVar(self, value, rule={}):#run pretty much every value through this function in case it's a ref to a variable
		if type(value) == str and value.startswith("$"):#it's a variable
			if value.startswith("$$"):#it's a user defined variable
				variable = value.split("$$")[1]
				if variable in self.vars:
					return self.vars[variable]
				else:
					self.log(f"ERROR: Variable \"{variable}\" does not exist!", level=5)
			else:
				#ok so it's a special type of variable, possibly $prompt or $arg.
				varTypeName = value.split("$")[1].split(" ")[0]
				if varTypeName in self.varTypes:
					varType = self.varTypes[varTypeName]
					if varType == None:
						self.log(f"No var type known as \"{varTypeName}\"", error=True)
					else:
						return varType.get_value(rule)
		return value
	
	def getProperty(self, dictionary, key, noneFound=None): #one line way of retrieving a value from a dictionary using a key.
		if key not in dictionary:
			return noneFound
		else:
			return dictionary[key]
	
	#region parsing
	'''
	def parse_time(self, txt):#im gonna get rid of this because nothing uses it
		txt = txt.replace(" ", "")
		value = seperate_string_number(txt)
		return float(value[0]) * self.units["seconds"][value[1]]
	def parse_measurement(self, txt): #returns meters
		txt = txt.replace(" ", "")
		value = seperate_string_number(txt)
		return float(value[0]) * self.units["meters"][value[1]]
	'''
	def merge_dicts(self, d1, d2): #puts d2 into d1. i love recursive functions.
		for x in d2:
			if type(d2[x]) != dict:
				d1[x] = d2[x]
			else:
				self.merge_dicts(d1[x], d2[x])
		return True
			
	def set_value(self, dictionary, key, newValue):#dictionary = the dict to use, key = the key of the property, newValue = the new value
		self.merge_dicts(dictionary, {key: self.testVar(newValue)})
		return True
	#endregion

