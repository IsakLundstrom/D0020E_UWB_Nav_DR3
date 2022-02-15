import double
import sys
import paho.mqtt.client as mqtt 
import time
import json
import datetime
import re
import toml
import threading
from notify_run import Notify 
from navigate import navigate
from webpage.changeConfig import ChangeConfig

#CONFIG = toml.load('config.toml')
f = open('config.json')
CONFIG = json.load(f)
f.close()

# Determine constants from config file
AVERAGE_TIME_WINDOW_SIZE = int(CONFIG['constants']['AVERAGE_TIME_WINDOW_SIZE'])
ALERT_HEIGT = float(CONFIG['constants']['ALERT_HEIGT'])
ALERT_WINDOW_SIZE = int(CONFIG['constants']['ALERT_WINDOW_SIZE'])
ALERT_TIME_GAP = datetime.timedelta(minutes = float(CONFIG['constants']['ALERT_TIME_GAP']))
ALERT_TIME_GAP_START = datetime.timedelta(minutes = float(CONFIG['constants']['ALERT_TIME_GAP_START']))

class SystemHandler:
    def __init__(self, condition):
        self.condition = condition
        updateConstants()
        # Load spot ids
        self.spotD3 = CONFIG['widefind']['spotD3']
        self.spotUser = CONFIG['widefind']['spotUser']

        self.zUser = {} # Dictionary: key = time for gotten mqtt msg, value = Z value in mqtt msg
        self.zUserAverage = 0
        self.xD3 = None
        self.yD3 = None
        self.zD3 = None

    #   self.wasAlerted = True # Set to True to not alert until first cooldown
        self.alertTimeCooldown = datetime.datetime.now() - ALERT_TIME_GAP + ALERT_TIME_GAP_START # Calculates initial cooldown

        self.notify = Notify() 

        # print(datetime.datetime.now())
        # print(self.alertTimeCooldown)

        
        # time.sleep(1) # wait

    def startSystem(self):
        self.turnOnSystem()
        broker_address = CONFIG['widefind']['broker_address']
        self.client = mqtt.Client() 
        self.client.on_message=self.on_message
        self.client.connect(broker_address)
        # client.loop_start()
        self.client.subscribe(CONFIG['widefind']['subscribe_address'])
        print('System Started')
        self.client.loop_forever()

    def turnOnSystem(self): 
        c = ChangeConfig()
        c.changeConstant('config.json', 'system', 'systemOn', True)

    def updateMovingZAverage(self, currentTime, currentZCord):
        # Remove old z cords until the difference is less then AVERAGE_TIME_WINDOW_SIZE
        for x in list(self.zUser): 
            delta = currentTime - x
            if(delta.seconds > AVERAGE_TIME_WINDOW_SIZE):
                newSum = self.zUserAverage*len(self.zUser) - self.zUser[x] # We continually recalculate the average Z value for every removed element
                del self.zUser[x]
                if(len(self.zUser) == 0): # Edge case to avoid dividing by zero
                    self.zUserAverage = 0
                else:
                    self.zUserAverage = newSum/len(self.zUser) # Normal execution
            else:
                break

        # Update new average with a new time and cords
        newSum = self.zUserAverage*len(self.zUser) + currentZCord
        self.zUser.update({currentTime: currentZCord})
        self.zUserAverage = newSum/len(self.zUser)

    def isSpotUser(self, jsonMsg):
        return self.spotUser in jsonMsg

    def isSpotD3(self, jsonMsg):
        return self.spotD3 in jsonMsg

    def checkSystem(self):
        f = open('config.json')
        CONFIG = json.load(f)
        f.close()

        if(not(CONFIG['system']['systemOn'])):
            print('System wait')
            self.condition.acquire() 
            self.condition.release()
            print('System start')
            # try:
            #     self.client.unsubscribe(CONFIG['widefind']['subscribe_address'])
            #     print('System wait')
            #     self.condition.acquire() 
            #     self.condition.release()
            #     print('System start')
            #     self.client.subscribe(CONFIG['widefind']['subscribe_address'])
            # except():
            #     print("uh oh")


        if(CONFIG['system']['changedSettings'] == False):
            updateConstants()
            print('Updated constants')

    
    def on_message(self, client, userdata, message):
        # print('on_msg UWB')
        self.checkSystem()

        mqttMsgString = message.payload.decode()
        mqttMsgJson = json.loads(mqttMsgString)
        jsonMsg = json.dumps(mqttMsgJson)
        # print(jsonMsg)
        if self.isSpotUser(jsonMsg):
            cordinates = self.getCordinates(jsonMsg) # cordinates = [x, y, z]
            print('User', cordinates)
            currentTime = self.getTime(jsonMsg) # currenTime = A datetime variable
            currentZCord = cordinates[2]
            self.updateMovingZAverage(currentTime, currentZCord)
            # Alert if Z height is low and enough #measurments and no alert cooldown
            if(self.checkZHeight(currentZCord) and len(self.zUser) >= ALERT_WINDOW_SIZE and self.isAlertTimeOffCooldown(currentTime)):
                self.updateAlertTimeCooldown(currentTime)
                self.alert(cordinates[0], cordinates[1])
        if self.isSpotD3(jsonMsg):
            cordinates = self.getCordinates(jsonMsg) # cordinates = [x, y, z]
            self.xD3 = cordinates[0]
            self.yD3 = cordinates[1]
            self.zD3 = cordinates[2]
            print('D3', cordinates)

    def isAlertTimeOffCooldown(self, currentTime):
        delta = currentTime - self.alertTimeCooldown
        if(delta > ALERT_TIME_GAP):
            return True
        return False

    def updateAlertTimeCooldown(self, currentTime):
        self.alertTimeCooldown = currentTime

    # Average and current Z heigt is below set alert height
    def checkZHeight(self, currentZCord):
        return(self.zUserAverage < ALERT_HEIGT and currentZCord < ALERT_HEIGT)

    def alert(self, targetX, targetY):
        print('ALERT! Fall!')
        sendstr = "Fall detected!\nThe target is at (" + str(targetX) + ", " + str(targetY) + ")!"
        print(sendstr)
        self.notify.send(sendstr)
        if(self.xD3 != None and self.yD3 != None):
            print('Started drive')
            nav = navigate()
            
            widefindStart = [self.xD3, self.yD3]
            widefindDest = [targetX, targetY]
            print(widefindStart, ' --> ', widefindDest)
            d3Dest = nav.calcWFtoD3(widefindStart, widefindDest)

            nav.driveWhenFall(d3Dest[0], d3Dest[1])


    # Returns cordinates of Widefind mqtt data
    def getCordinates(self, jsonMqttMsg):
        parse = json.loads(jsonMqttMsg)
        # print(parse)
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

def updateConstants():
    f = open('config.json')
    CONFIG = json.load(f)
    f.close()
    AVERAGE_TIME_WINDOW_SIZE = int(CONFIG['constants']['AVERAGE_TIME_WINDOW_SIZE'])
    ALERT_HEIGT = float(CONFIG['constants']['ALERT_HEIGT'])
    ALERT_WINDOW_SIZE = int(CONFIG['constants']['ALERT_WINDOW_SIZE'])
    ALERT_TIME_GAP = datetime.timedelta(minutes = float(CONFIG['constants']['ALERT_TIME_GAP']))
    ALERT_TIME_GAP_START = datetime.timedelta(minutes = float(CONFIG['constants']['ALERT_TIME_GAP_START']))

    
    c = ChangeConfig()
    c.changeConstant('config.json', 'system', 'changedSettings', True)


if __name__ == '__main__':
    s = SystemHandler()


