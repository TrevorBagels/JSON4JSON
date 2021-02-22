from .basics import seperate_string_number 
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
	def convert(self, data, rule):
		value = seperate_string_number(data)
		return self.units[value[1]] * float(value[0])


class time(unit):
	def __init__(self, ajson):
		super().__init__(ajson, "time", "0s", units={"":1, "sec": 1, "secs": 1, "s": 1, "m": 60, "min": 60, "mins": 60, "h": 60*60, "d": 60*60*24, "W": 60*60*24*7, "M": 60*60*24*7*30, "Y": 60*60*24*365})

class distance(unit):
	def __init__(self, ajson):
		super().__init__(ajson, "distance", "0m", units={"":1, "me": 1, "m": 1, "km": 1000, "ft": 3.280839895, "mi": 1000 * 0.621371, "cm": .001, "in": 3.280839895/12})
