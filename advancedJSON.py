import json, os, sys, traceback
from datatypes import DataTypes
from utils import seperate_string_number
#region utils from the internet
#can't remember where I stole this from, somewhere on stack overflow.
#endregion
class AdvancedJSON:
	def __init__(self):
		self.units = {}
		self.units["time"] = {"":1, "sec": 1, "secs": 1, "s": 1, "m": 60, "min": 60, "mins": 60, "h": 60*60, "d": 60*60*24, "W": 60*60*24*7, "M": 60*60*24*7*30, "Y": 60*60*24*365}
		self.units["distance"] = {"":1, "me": 1, "m": 1, "km": 1000, "ft": 3.280839895, "mi": 1000 * 0.621371, "cm": .001, "in": 3.280839895/12}
		self.dataTypes = {}
		self.vars = {}
		self.defaults = {
			"unit": {"time": "s", "distance": "m"},
			"autoAdd": True,
			"t": "string",
			"logging": 5,
			"tracebackLogging": True
		}
		self.data = {} #this is the loaded and mostly filtered data
		for x in DataTypes.allTypes:
			xinstance = x(self)
			self.dataTypes[xinstance.name] = xinstance
		


	def load(self, jsonFile, ruleFile):
		data = None
		rules = None
		with open(jsonFile, "r") as f:
			data = json.loads(f.read())
		with open(ruleFile, "r") as f:
			rules = json.loads(f.read())
		self.convertAll(data, rules)
	
	def convertAll(self, data, rules): #data: dictionary (right after loading json), rules: dictionary from the raw json stuff...
		#start by setting up
		#hmmm maybe we should just use the conversion from datatypes.dicttype. unify everything, yknow
		for key in rules:
			if key.startswith("//"): #ignore, this is a comment
				continue
			if key[0] == "@": #this overrides default settings
				self.set_value(self.defaults, key.split("@")[1], rules[key])
				continue
			if key not in data:
				self.log(f"Key \"{key}\" not in data file. Setting to default.", level=-2)
				data[key] = self.getDefault(rules[key])
			#check if this makes a variable. if so, set the variable to the value.
			if "varSet" in rules[key]:
				self.log(f"Setting variable {rules[key]['varSet']}", level=-1)
				self.vars[rules[key]['varSet']] = data[key]
			data[key] = self.convertSingle(data[key], rules[key])
		self.data = data
	
	def log(self, *args, **kw):
		level = kw.get('level', 0)
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
		data = self.testVar(data)
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
		self.log(rule)
		return self.dataTypes[rule['t']].default
	
	def testVar(self, value):#run pretty much every value through this function in case it's a ref to a variable
		if type(value) == str and value.startswith("$$"):#it's a variable, does it exist?
			variable = value.split("$$")[1]
			if variable in self.vars:
				return self.vars[variable]
			else:
				self.log(f"ERROR: Variable \"{variable}\" does not exist!", level=5)
		return value
	
	def getProperty(self, dictionary, key, noneFound=None): #one line way of retrieving a value from a dictionary using a key.
		if key not in dictionary:
			return noneFound
		else:
			return dictionary[key]
	#region parsing
	def parse_time(self, txt):
		txt = txt.replace(" ", "")
		value = seperate_string_number(txt)
		return float(value[0]) * self.units["seconds"][value[1]]
	def parse_measurement(self, txt): #returns meters
		txt = txt.replace(" ", "")
		value = seperate_string_number(txt)
		return float(value[0]) * self.units["meters"][value[1]]
	
	def merge_dicts(self, d1, d2): #puts d2 into d1
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

