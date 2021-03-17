import json, os, sys, traceback, copy, argparse
from math import exp
import colorama

from colorama.ansi import Fore

class DBG:
	def __init__(self, devmode):
		self.colors = {"red": Fore.RED, "green": Fore.GREEN, "blue": Fore.BLUE, "yellow": Fore.YELLOW, "orange": Fore.LIGHTRED_EX, "purple": Fore.MAGENTA}
		colorama.init() #for testing
	def print(self, *args, color="green"):
		c = Fore.CYAN
		if color in self.colors: c = self.colors[color]
		print(c + "", *args)
		print(colorama.Style.RESET_ALL)


class JSON4JSON:
	def __init__(self):
		from .utils import seperate_string_number
		from .DataTypes import DefaultTypes
		from .VarTypes import DefaultVarTypes
		self.debugger = DBG(True)
		self.print = self.debugger.print

		self.init_self_variables()
		self.dataTypes = {}
		self.varTypes  = {}
		DefaultTypes.LoadDefaultDatatypes(self) #user created datatypes can be added via the method in this method as well
		DefaultVarTypes.LoadDefaultVarTypes(self)
		#something like 
		#configParser = JSON4JSON()
		#configParser.add_data_type(myCustomDataType)
	
	def init_self_variables(self):
		self.vars      = {}
		self.data      = {} #this is the loaded and mostly filtered data
		self.objects   = {"ROOT": self.data} #this keeps track of object hierarchy
		self.uidLevel = 0 #for keeping track object hierarchy
		#globals are properties for how JSON4JSON functions. Mostly for logging and stuff. Accessed via "@@property"
		self.globals = {"logging": 4, "tracebackLogging": False}
		#defaults are the default properties of objects. 
		self.defaults = {
			"unit": {"time": "s", "distance": "m"},
			"autoAdd": True,
			"t": "string",
			"r" : False,
			"options": ["yes", "no"]
		}
		self.data["_defaults"] = self.defaults
		self.data["_uid"] = "ROOT"
		self.data["_variables"] = self.vars
		self.data['_parent'] = "ROOT"

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
			self.error(f"Could not read JSON file \"{jsonFile}\"")
		with open(ruleFile, "r") as f:
			self.rules = json.loads(f.read())
		self.convert_all(data, self.rules)
	
	def convert_all(self, data, rules): #data: dictionary (right after loading json), rules: dictionary from the raw json stuff...
		#this basically wraps everything into one object and then starts recursively converting it
		self.init_self_variables()
		self.data = self.convert_single(data, {"t": "object", "rules": rules}, parentUID="ROOT", name="root", setUID="ROOT")
	
	def convert_single(self, property, ruleset, setUID=None, parentUID="ROOT", name=""):
		#property = property value (not name) (from config)
		#allow comments on property values
		if type(property) == str:
			try:
				property = property.split("//")[0]
			except:
				pass
		#Generate UID
		uid = setUID
		if uid == None:
			uid = self.generate_uid()
		
		#data = self.test_variable(data, parent, rule=rule) #does this start with $? if so, it's a variable.
		
		expectedType = self.get_property(ruleset, "t", parentUID, noneFound="any")
		if expectedType in self.dataTypes:
			property = self.test_variable(property, parentUID, ruleset)
			isValid = self.dataTypes[expectedType].matches(property) #whether or not this matches the expected datatype
			if isValid:
				#wait. is this a dict? if so, we need to pass the parent dictionary's defaults and variables
				if type(property) == dict:
					property["_uid"] = uid
					property["_parent"] = parentUID
					if uid not in self.objects:
						self.objects[uid] = property
					else:
						self.merge_dicts(self.objects, property)
					property = self.dataTypes[expectedType].convert(property, ruleset, parentUID=parentUID)
				elif type(property) == list:
					property = self.dataTypes[expectedType].convert(property, ruleset, parentUID=parentUID)
				else:
					property = self.dataTypes[expectedType].convert(property, ruleset, parentUID=parentUID)
			else:
				self.error(f"Property \"{name}\" is supposed to be {expectedType}. Got \"{type(property).__name__}\" instead.")
		else:
			raise Exception(f"Invallid DataType \"{expectedType}\"")
		return property
	
	#returns the parent object


	def get_parent(self, propertyUID, level=1):
		"""Gets the parent of an object

		Args:
			propertyUID (string, dictionary): Either the UID of the property, or the property itself.
			level (int, optional): How many levels to go up. Defaults to 1.

		Returns:
			[string]: UID of the parent. 
		"""
		"""
		Parent structure from the perspective of "ParentC"
		ROOT - level = 3 (all the way to infinity!)
		ROOT - level = 2
			ParentB - level = 1
				ParentC - level = 0
		"""
		#get the UID of the data object.
		uid = propertyUID
		if type(propertyUID) == dict: uid = propertyUID['_uid']
		
		parent = self.get_object(uid)['_uid'] #first parent at level 0 (which is itself.)
		for x in range(0, level): #iterate until we get the target parent
			parent = self.get_object(parent)["_parent"]
		
		return self.get_object(parent)
	
	def get_object(self, UID):
		"""Gets an object from a specified UID

		Args:
			UID (string): The UID of the target object.
		Raises:
			Exception - The object wasn't found
		Returns:
			[dictionary]: The object we're looking for.
		"""
		if UID not in self.objects:
			raise Exception("Object not found")
		return self.objects[UID]

	def generate_uid(self):
		"""Generates a unique identifier as a string.

		Returns:
			[string]: The newly generated UID
		"""
		self.uidLevel += 1
		return str(self.uidLevel)
	
	def get_default(self, ruleset, property):
		#enforce types
		if "t" not in ruleset:
			ruleset['t'] = self.get_property(property['_defaults'], 't', property['_parent']) #default is "string"
		#return the default if it exists
		if "d" in ruleset:
			defaults = self.get_property(ruleset, "d", property["_parent"])
			if type(defaults) == list and ruleset['t'] != "array":
				#go through the list of default choices until we find one that works/matches
				for d in defaults:
					newD = self.get_property({'a':d}, 'a', property['_uid'])
					if self.dataTypes[ruleset['t']].matches(newD):
						return newD
				return None
			else:
				return defaults
		#no default, return the default specified in the DataType.
		return copy.deepcopy(self.dataTypes[ruleset['t']].default) #last resort, pretty common, just use the default value associated with this type.
	
	def test_variable(self, property, parentUID, ruleset, root=0, checked=""):#run pretty much every value through this function in case it's a ref to a variable
		#self.print(checked.count("/")*"_"+"_", "-"*root, parentUID, property)
		checked += "/" + parentUID
		if type(property) == str and property.startswith("$"):#it's a variable
			if property.startswith("$$"):#it's a user defined variable
				parentLevel = property.count(".")
				variable = property.split("$$" + (property.count(".") * ".") )[1] #this works, don't question it.

				target_parent = self.get_parent(parentUID, level = parentLevel)
				if variable in target_parent["_variables"]:
					return target_parent["_variables"][variable]
				else:
					#ok so we couldn't find this variable. Try again, but go up one parent.
					if parentUID == "ROOT":
						root += 1
					if root < 2:
						next = target_parent['_uid']
						if next == parentUID:
							next = target_parent["_parent"]

						return self.test_variable(property, next, ruleset, root=root, checked=checked)
					self.warn(f"Variable \"{variable}\" does not exist!", checked)
			else:
				#ok so it's a special type of variable, possibly $prompt or $arg.
				varTypeName = property.split("$")[1].split(" ")[0]
				if varTypeName in self.varTypes:
					varType = self.varTypes[varTypeName]
					if varType == None:
						raise Exception(f"No such varType \"{varTypeName}\"")
					else:
						return varType.get_value(ruleset, property)
		return property
	
	def get_property(self, dictionary: dict, key: str, parentUID: str, noneFound=None):
		"""Gets a value from a dictionary with a given key. Also tests for variables.

		Args:
			dictionary (dict): The dictionary to retrieve from
			key (str): The key to use
			parentUID (str): The UID of the parent. This is used to test variables
			noneFound (any, optional): The value to return if nothing is found. Defaults to None.

		Returns:
			[any]: The property you're looking for.
		"""
		if key not in dictionary:
			return noneFound
		else:
			return self.test_variable(dictionary[key], 
			parentUID, 
			dictionary)
	
	def merge_dicts(self, d1, d2): #puts d2 into d1. i love recursive functions. note, arrays get overwritten and deep copied, they don't merge
		"""Puts D2 into D1.

		Args:
			d1 ([type]): [description]
			d2 ([type]): [description]

		Returns:
			[type]: [description]
		"""
		for x in d2:
			if type(d2[x]) not in [dict, list]:
				d1[x] = d2[x]
			elif type(d2[x]) == dict:
				self.merge_dicts(d1[x], d2[x])
			elif type(d2[x]) == list:
				d1[x] = copy.deepcopy(d2[x])
		return True
			
	def set_value(self, dictionary:dict, key:str, newValue):#dictionary = the dict to use, key = the key of the property, newValue = the new value
		"""Sets the value of a dictionary without overwriting everything if the new value is a dictionary.
		Args:
			dictionary (dict): [description]
			key (str): [description]
			newValue (any): [description]
		"""
		self.merge_dicts(dictionary, {key: newValue})
	
	def error(self, *args):
		print(colorama.Fore.RED+"", *args)
		if self.globals['tracebackLogging']:
			raise Exception(*args)
		sys.exit()
	
	def warn(self, *args, level=4):
		if self.globals['logging'] <= level:
			print(colorama.Fore.YELLOW, *args)

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

