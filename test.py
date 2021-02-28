
from JSON4JSON import JSON4JSON
import json

config = JSON4JSON()

path = "./tests/2/"

config.load(f"{path}config.json", f"{path}rules.json")
print("\n\n")
print("variables:", config.vars)

def removeUnderscored(d):
	doItAgain = False
	for key in d:
		if type(d[key]) == dict:
			removeUnderscored(d[key])
		if key.startswith("_"):
			#reMOVE
			del d[key]
			doItAgain = True
			break
	if doItAgain:
		removeUnderscored(d)

removeUnderscored(config.data)

#dumps the converted dictionary to output.json.
#this is good for getting a reference for what your config object will look like when you use advancedJSON
json.dump(config.data, open(f"{path}output.json", "w+"), indent=4)
json.dump(config.rules, open(f"{path}outputtedRules.json", "w+"), indent=4)

print(config.dataTypes['object'].default)