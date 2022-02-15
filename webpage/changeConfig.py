import json

class ChangeConfig:

    def changeConstant(self, configFile, parent, variable, newValue):
        with open(configFile, "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()

        data[parent][variable] = float(newValue)

        with open(configFile, "w") as jsonFile:
            json.dump(data, jsonFile)
            jsonFile.close()

    # def changeAlertGap(self, newGap):
    #     self.changeConstant('../config.json', 'constants', 'ALERT_TIME_GAP', newGap)

    # def changeAlertGapTo15s(self, newGap):
    #     self.changeAlertGap(15)

    # def changeAlertGapTo30s(self, newGap):
    #     self.changeAlertGap(30)

    # def changeHeight(self, newGap):
    #     self.changeConstant('../config.json', 'constants', 'ALERT_TIME_GAP', 15)
        
