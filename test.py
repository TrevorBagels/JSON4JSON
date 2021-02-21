from advancedJSON import AdvancedJSON
import json

config = AdvancedJSON()

config.load("config.json", "rules.json")
print(config.data)
print(config.vars)
json.dump(config.data, open("./output.json", "w+"), indent=4)