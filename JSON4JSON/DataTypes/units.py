from .basics import number, seperate_string_number
class unit:
	def __init__(self, ajson, name, default, units={}):
		self.name = name
		self.ajson = ajson
		self.default = default
		self.units = units
	#returns true/false, whether or not the data is this type
	def matches(self, data):
		if type(data) == str:
			if seperate_string_number(data)[1] in self.units:
				return True
			else:
				self.ajson.log(f"Error: {self.name} does not recognize \"{seperate_string_number(data)[1]}\" as a valid unit.", level=5)
		return False
	def convert(self, data, rule, skipRuleConversion=False, useUnit="none"):#useUnit, if not set to none, skips looking through the rule file and uses whatever it's set to as the new unit.
		unitToUse = self.ajson.defaults['unit'][self.name]
		#check if there's a rule for this, that would ovverride unitToUse
		if skipRuleConversion == False:
			if "unit" in rule:
				unitToUse = rule['unit']
		if useUnit != "none":
			unitToUse = useUnit
		
		if skipRuleConversion == False:
			alsoConvert = ["min", "max", "multiplier"] #we should also convert these values to preffered measurements
			for x in alsoConvert:
				if x in rule:
					rule[x] = self.convert(rule[x], rule, skipRuleConversion=True, useUnit=unitToUse)
		value = seperate_string_number(data) #gets the number and then the units
		valueInDefaultUnits = self.units[value[1]] * float(value[0]) #converts whatever units were used to seconds/meters

		valueInDesiredUnits = valueInDefaultUnits / self.units[unitToUse] #converts to the value we should be using
		numberValue = self.ajson.dataTypes['number'].convert(valueInDesiredUnits, rule)
		return numberValue


class time(unit):
	def __init__(self, ajson):
		super().__init__(ajson, "time", "0s", units={"ms":1/1000, "μs": 1/1000000, "us": 1/1000000, "ns": 1/(1000000000), "":1, "sec": 1, "secs": 1, "s": 1, "m": 60, "min": 60, "mins": 60, "h": 60*60, "d": 60*60*24, "W": 60*60*24*7, "M": 60*60*24*7*30, "Y": 60*60*24*365})

class distance(unit):
	def __init__(self, ajson):
		super().__init__(ajson, "distance", "0m", units={"":1, "me": 1, "m": 1, "km": 1000, "ft": 3.280839895, "mi": 1000 * 0.621371, "cm": .001, "in": 3.280839895/12})
