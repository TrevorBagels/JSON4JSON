from JSON4JSON.DataTypes.basics import DataType
from ..utils import seperate_string_number
import math
from ..JSON4JSON import JSON4JSON

class choice(DataType):
	def __init__(self, j4j):
		super().__init__(j4j)
		self.name = "choice"
		self.t = any

	def matches(self, data):
		#choice is either gonna be a number, a string, or uh, well yeah that's basically it. I think.
		return type(data) not in [dict, list]
	
	def convert(self, data, ruleset, parentUID="ROOT"):
		options = self.j4j.get_property(ruleset, "options",
			parentUID=parentUID,
			noneFound=self.j4j.get_parent(parentUID)['_defaults']['options'])
		if data not in options:
			self.j4j.error(f"\"{data}\" is not a valid option. It should be one of the following: {', '.join(options)}")
		else:
			return data
		

	