import paho.mqtt.client as mqtt 
import time
import json
import datetime
import re
import toml
from notify_run import Notify 

CONFIG = toml.load('config.toml')

# Determine constants from config file
AVERAGE_TIME_WINDOW_SIZE = int(CONFIG['constants']['AVERAGE_TIME_WINDOW_SIZE'])
ALERT_HEIGT = float(CONFIG['constants']['ALERT_HEIGT'])
ALERT_WINDOW_SIZE = int(CONFIG['constants']['ALERT_WINDOW_SIZE'])
ALERT_TIME_GAP = datetime.timedelta(minutes = float(CONFIG['constants']['ALERT_TIME_GAP']))
ALERT_TIME_GAP_START = datetime.timedelta(minutes = float(CONFIG['constants']['ALERT_TIME_GAP_START']))

class SystemHandler:
    def __init__(self):
        # Load spot ids
        self.spotD3 = CONFIG['widefind']['spotD3']
        self.spotUser = CONFIG['widefind']['spotUser']

        self.zCordinates = {} # Dictionary: key = time for gotten mqtt msg, value = Z value in mqtt msg
        self.zAverage = 0

        self.wasAlerted = True # Set to True to not alert until first cooldown
        self.alertTimeCooldown = datetime.datetime.now() - ALERT_TIME_GAP + ALERT_TIME_GAP_START # Calculates initial cooldown

        self.notify = Notify() 

        # print(datetime.datetime.now())
        # print(self.alertTimeCooldown)

        broker_address = CONFIG['widefind']['broker_address']
        client = mqtt.Client() 
        client.on_message=self.on_message
        client.connect(broker_address)
        # client.loop_start()
        client.subscribe(CONFIG['widefind']['subscribe_address'])
        # time.sleep(1) # wait
        print('System Started')
        client.loop_forever()

    def updateMovingZAverage(self, currentTime, currentZCord):
        # Remove old z cords until the difference is less then AVERAGE_TIME_WINDOW_SIZE
        for x in list(self.zCordinates): 
            delta = currentTime - x
            if(delta.seconds > AVERAGE_TIME_WINDOW_SIZE):
                newSum = self.zAverage*len(self.zCordinates) - self.zCordinates[x] # We continually recalculate the average Z value for every removed element
                del self.zCordinates[x]
                if(len(self.zCordinates) == 0): # Edge case to avoid dividing by zero
                    self.zAverage = 0
                else:
                    self.zAverage = newSum/len(self.zCordinates) # Normal execution
            else:
                break

        # Update new average with a new time and cords
        newSum = self.zAverage*len(self.zCordinates) + currentZCord
        self.zCordinates.update({currentTime: currentZCord})
        self.zAverage = newSum/len(self.zCordinates)

    def isSpotUser(self, jsonMsg):
        return self.spotUser in jsonMsg
    
    def on_message(self, client, userdata, message):
        mqttMsgString = message.payload.decode()
        mqttMsgJson = json.loads(mqttMsgString)
        jsonMsg = json.dumps(mqttMsgJson)
        if self.isSpotUser(jsonMsg):
            cordinates = self.getCordinates(jsonMsg) # cordinates = [x, y, z]
            currentTime = self.getTime(jsonMsg) # currenTime = A datetime variable
            currentZCord = cordinates[2]
            self.updateMovingZAverage(currentTime, currentZCord)
            # Alert if Z height is low and enough measurments and no alert cooldown
            if(self.checkZHeight(currentZCord) and len(self.zCordinates) >= ALERT_WINDOW_SIZE and self.isAlertTimeOffCooldown(currentTime)):
                self.updateAlertTimeCooldown(currentTime)
                self.alert()

    def isAlertTimeOffCooldown(self, currentTime):
        delta = currentTime - self.alertTimeCooldown
        if(delta > ALERT_TIME_GAP):
            return True
        return False

    def updateAlertTimeCooldown(self, currentTime):
        self.alertTimeCooldown = currentTime

    # Average and current Z heigt is below set alert height
    def checkZHeight(self, currentZCord):
        return(self.zAverage < ALERT_HEIGT and currentZCord < ALERT_HEIGT)

    def alert(self):
        print('ALERT! Fall occured!!')
        self.notify.send("F")

    # Returns cordinates of Widefind mqtt data
    def getCordinates(self, jsonMqttMsg):
        parse = json.loads(jsonMqttMsg)
        messageData = parse['message']
        splitMessageData = messageData.split(",")
        x = (float(splitMessageData[2])/1000)
        y = (float(splitMessageData[3])/1000)
        z = (float(splitMessageData[4])/1000)
        return [x, y, z]

    # Returns time of Widefind mqtt data
    def getTime(self, jsonMqttMsg):
        parse = json.loads(jsonMqttMsg)
        timeData = parse['time']
        splitTimeData = re.split(r"[-T:.Z]\s*", timeData)
        currentTime = datetime.datetime(int(splitTimeData[0]), int(splitTimeData[1]), int(splitTimeData[2]), int(splitTimeData[3]), int(splitTimeData[4]), int(splitTimeData[5]), int(splitTimeData[6][:6]))
        return currentTime


if __name__ == '__main__':
    s = SystemHandler()


