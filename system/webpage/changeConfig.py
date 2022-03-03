import json

class ChangeConfig:

    def changeConstant(self, configFile, parent, variable, newValue): # This function changes one value on the config file
        with open(configFile, "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()

        data[parent][variable] = float(newValue)

        with open(configFile, "w") as jsonFile:
            json.dump(data, jsonFile)
            jsonFile.close()

