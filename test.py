from advancedJSON import AdvancedJSON
import json

config = AdvancedJSON()

config.load("config.json", "rules.json")
print("\n\n")
print("variables:", config.vars)
json.dump(config.data, open("./output.json", "w+"), indent=4)