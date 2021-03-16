
from JSON4JSON import JSON4JSON
import json
import objgraph

config = JSON4JSON()

path = "./tests/1/"

config.load(f"{path}config.json", f"{path}rules.json")
print("\n\n")
#print("variables:", config.vars)

def removeUnderscored(d, keep=[]):
	doItAgain = False
	for key in d:
		if key.startswith("_") and key not in keep:
			#reMOVE
			del d[key]
			doItAgain = True
			break
		if type(d[key]) == dict:
			removeUnderscored(d[key], keep=keep)
	if doItAgain:
		removeUnderscored(d, keep=keep)

def getObjectPath(myKey, o, level=0):
	txt = level * "-" + myKey
	for key in o:
		if key.startswith("_"):
			continue
		if type(o[key]) == dict:
			txt += "\n" + getObjectPath(key, o[key], level = level + 3)
	return txt





print(getObjectPath("root", config.data, level=0))
#print("parent", config.getParent(config.data['someObject2']['nestedObject']['anotherObject'], level = 0)['_uid'], config.data['someObject2']['nestedObject']['anotherObject']['_uid'])
removeUnderscored(config.data, keep=["_uid", "_parent", "_variables"])
objgraph.show_refs(config.data, max_depth=8)



#dumps the converted dictionary to output.json.
#this is good for getting a reference for what your config object will look like when you use advancedJSON
json.dump(config.data, open(f"{path}output.json", "w+"), indent=4)
json.dump(config.rules, open(f"{path}outputtedRules.json", "w+"), indent=4)

