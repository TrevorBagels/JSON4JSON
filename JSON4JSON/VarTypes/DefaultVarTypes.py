from .basicVarTypes import prompt, arg

def LoadDefaultVarTypes(j4jObject):
	vts = [prompt, arg]
	for x in vts:
		j4jObject.add_var_type(x)