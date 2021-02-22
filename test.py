from advancedJSON import AdvancedJSON
import json

config = AdvancedJSON()

config.load("config.json", "rules.json")
print("\n\n")
print("variables:", config.vars)

#dumps the converted dictionary to output.json.
#this is good for getting a reference for what your config object will look like when you use advancedJSON
json.dump(config.data, open("./output.json", "w+"), indent=4)