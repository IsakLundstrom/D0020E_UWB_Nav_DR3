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

# Get constants from config file
AVERAGE_TIME_WINDOW_SIZE = int(CONFIG['constants']['AVERAGE_TIME_WINDOW_SIZE'])
ALERT_HEIGT = float(CONFIG['constants']['ALERT_HEIGT'])
ALERT_WINDOW_SIZE = int(CONFIG['constants']['ALERT_WINDOW_SIZE'])
ALERT_TIME_GAP = datetime.timedelta(minutes = float(CONFIG['constants']['ALERT_TIME_GAP']))
ALERT_TIME_GAP_START = datetime.timedelta(minutes = float(CONFIG['constants']['ALERT_TIME_GAP_START']))

class FallHandler:
    def __init__(self, fallSystemLock, globalVariables):
        self.globalVariables = globalVariables
        self.fallSystemLock = fallSystemLock
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
        print('self.alertTimeCooldown: ',self.alertTimeCooldown)

        
        # time.sleep(1) # wait

    def startSystem(self):
        self.updateConstants()
        # self.turnOnSystem()
        broker_address = CONFIG['widefind']['broker_address']
        self.client = mqtt.Client() 
        self.client.on_message=self.on_message
        # self.client.on_subscribe=self.on_subscribe
        # self.client.on_unsubscribe=self.on_unsubscribe
        self.client.connect(broker_address)
        # client.loop_start()
        self.client.subscribe(CONFIG['widefind']['subscribe_address'])
        print('System Started')
        self.client.loop_forever()

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
        # f = open('config.json')
        # CONFIG = json.load(f)
        # f.close()
        # adress = CONFIG['widefind']['subscribe_address']

        # if(not(CONFIG['system']['systemOn'])):
            # print('System wait')
            # self.fallSystemLock.acquire() 
            # self.fallSystemLock.release()
            # print('System start')
        if(not self.globalVariables.systemOn):
            try:
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S")
                self.client.disconnect()
                # self.client.unsubscribe(adress)
                print('System wait, time:', current_time)
                self.fallSystemLock.acquire()
                self.fallSystemLock.release()
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print('System start, time:', current_time)
                self.startSystem()
                # self.client.subscribe(CONFIG['widefind']['subscribe_address'])
            except():
                print("uh oh")


        if(self.globalVariables.changedSettings):
            self.updateConstants()
            print('Updated constants')

    def on_unsubscribe(self, client, userdata, mid): # Only for test
        print('UNSUB')

    def on_subscribe(self, client, userdata, mid, granted_qos):# Only for test
        print('SUB')

    def on_message(self, client, userdata, message):
        # print('on_msg UWB')
        self.checkSystem()

        mqttMsgString = message.payload.decode()
        mqttMsgJson = json.loads(mqttMsgString)
        jsonMsg = json.dumps(mqttMsgJson)
        # print(jsonMsg)
        if self.isSpotUser(jsonMsg):
            self.handleSpotUser(jsonMsg)
            
        if self.isSpotD3(jsonMsg):
            self.handleSpotD3(jsonMsg)

    def handleSpotUser(self, jsonMsg):
        cordinates = self.getCordinates(jsonMsg) # cordinates = [x, y, z]
        currentTime = self.getTime(jsonMsg) # currenTime = A datetime variable
        currentZCord = cordinates[2]
        self.updateMovingZAverage(currentTime, currentZCord)
        print('User', cordinates, '     self.zUserAverage: ', self.zUserAverage, '     self.checkZHeight(currentZCord): ', self.checkZHeight(currentZCord), '     len(self.zUser) >= ALERT_WINDOW_SIZE. ', len(self.zUser) >= ALERT_WINDOW_SIZE, '     self.isAlertTimeOffCooldown(currentTime): ', self.isAlertTimeOffCooldown(currentTime))
        # Fall decetction: Alert if Z height is low and enough #measurments and no alert cooldown
        checkIfFall = self.checkZHeight(currentZCord) and len(self.zUser) >= ALERT_WINDOW_SIZE and self.isAlertTimeOffCooldown(currentTime)
        if(checkIfFall):
            self.updateAlertTimeCooldown(currentTime)
            self.alert(cordinates[0], cordinates[1])

    def handleSpotD3(self, jsonMsg):
        cordinates = self.getCordinates(jsonMsg) # cordinates = [x, y, z]
        self.xD3 = cordinates[0]
        self.yD3 = cordinates[1]
        self.zD3 = cordinates[2]
        print('D3', cordinates)


    def isAlertTimeOffCooldown(self, currentTime):
        delta = currentTime - self.alertTimeCooldown
        # print('delta: ', delta)
        if(delta > ALERT_TIME_GAP):
            return True
        return False

    def updateAlertTimeCooldown(self, currentTime):
        self.alertTimeCooldown = currentTime

    # Average and current Z heigt is below set alert height
    def checkZHeight(self, currentZCord):
        return(self.zUserAverage < ALERT_HEIGT and currentZCord < ALERT_HEIGT)

    def alert(self, targetX, targetY):
        sendstr = "Fall detected!\nThe target is at (" + str(targetX) + ", " + str(targetY) + ")!" 
        print('ALERT! Fall!')
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

    def updateConstants(self):
        f = open('config.json')
        CONFIG = json.load(f)
        f.close()
        AVERAGE_TIME_WINDOW_SIZE = int(CONFIG['constants']['AVERAGE_TIME_WINDOW_SIZE'])
        ALERT_HEIGT = float(CONFIG['constants']['ALERT_HEIGT'])
        ALERT_WINDOW_SIZE = int(CONFIG['constants']['ALERT_WINDOW_SIZE'])
        ALERT_TIME_GAP = datetime.timedelta(minutes = float(CONFIG['constants']['ALERT_TIME_GAP']))
        ALERT_TIME_GAP_START = datetime.timedelta(minutes = float(CONFIG['constants']['ALERT_TIME_GAP_START']))

        self.globalVariables.changedSettings = False


if __name__ == '__main__':
    s = FallHandler()


