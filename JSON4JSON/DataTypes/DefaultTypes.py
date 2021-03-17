from .basics import anyType, arrayType, string, number, boolean
from .dictType import dictType
from .units import distance, time
from .extended import choice
def LoadDefaultDatatypes(j4jObject):
	dts = [anyType, arrayType, dictType, distance, string, number, boolean, time, choice]
	for x in dts:
		j4jObject.add_data_type(x)
