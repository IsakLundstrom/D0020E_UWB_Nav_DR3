import paho.mqtt.client as mqtt 
import time
import json
import datetime
import re

AVERAGE_TIME_WINDOW_SIZE = 5
ALERT_HEIGT = 0.5
ALERT_WINDOW_SIZE = 5
ALERT_TIME_GAP = datetime.timedelta(minutes = 1/6)
ALERT_TIME_GAP_START = datetime.timedelta(minutes = 1/12)

class PositionHandler:
    def __init__(self, spotD3, spotUser):
        self.spotD3 = spotD3
        self.spotUser = spotUser

        self.zCords = {}
        self.zAvg = 0

        self.wasAlerted = True
        self.alertTimeCooldown = datetime.datetime.now() - ALERT_TIME_GAP + ALERT_TIME_GAP_START

        print(datetime.datetime.now())
        print(self.alertTimeCooldown)

        broker_address = "130.240.74.55"
        client = mqtt.Client() 
        client.on_message=self.on_message
        client.connect(broker_address)
        # client.loop_start()
        client.subscribe("ltu-system/#")
        time.sleep(1) # wait
        client.loop_forever()

    def movingAverage(self, currentTime, newZ):
        # Remove old z cords until the diffrence is less then AVERAGE_TIME_WINDOW_SIZE
        for x in list(self.zCords): 
            delta = currentTime - x
            if(delta.seconds > AVERAGE_TIME_WINDOW_SIZE):
                newsum = self.zAvg*len(self.zCords) - self.zCords[x]
                del self.zCords[x]
                if(len(self.zCords) == 0):
                    self.zAvg = 0
                else:
                    self.zAvg = newsum/len(self.zCords)
            else:
                break

        # Update new average with a new time and cords
        newsum = self.zAvg*len(self.zCords) + newZ
        self.zCords.update({currentTime: newZ})
        self.zAvg = newsum/len(self.zCords)
        # print('Average Z: ', self.zAvg)
        # print('')

    def isSpotUser(self, jsonMessage):
        return self.spotUser in jsonMessage
    
    def on_message(self, client, userdata, message):
        # print(str(message.payload.decode("utf-8"))) # Prints all Widefind mqtt data
        mqttMsgString = message.payload.decode()
        mqttMsgJson = json.loads(mqttMsgString)
        # print(mqttMsgJson)
        #self.data_queue.put(mqttMsgJson)
        jsonMessage = json.dumps(mqttMsgJson)
        if self.isSpotUser(jsonMessage):
            # print(str(message.payload.decode("utf-8")))
            cordinates = self.getCordinates(jsonMessage)
            # print(cordinates)
            currentTime = self.getTime(jsonMessage)
            # print(currentTime)
            zCord = cordinates[2]
            self.movingAverage(currentTime, zCord)
            # Alert if Z height is low and enough measurments and no alert cooldown
            if(self.checkZHeight(zCord) and len(self.zCords) >= ALERT_WINDOW_SIZE and self.checkAlertTimeCooldown(currentTime)):
                self.updateAlertTimeCooldown(currentTime)
                self.alert()
            # print('')

        
        # print("message topic=",message.topic)
        # print("message qos=",message.qos)
        # print("message retain flag=",message.retain)
    ########################################

    def checkAlertTimeCooldown(self, currentTime):
        # print(currentTime)
        delta = currentTime - self.alertTimeCooldown
        print('delta ', delta.seconds)
        if(delta > ALERT_TIME_GAP):
            return True
        return False

    def updateAlertTimeCooldown(self, currentTime):
        self.alertTimeCooldown = currentTime


    def checkZHeight(self, zCord):
        return(self.zAvg < ALERT_HEIGT and zCord < ALERT_HEIGT)


    def alert(self):
        print('ALERT!')

    # Returns cordinates of Widefind mqtt data
    def getCordinates(self, jsonData):
        parse = json.loads(jsonData)
        messageData = parse['message']
        # print(messageData)
        splitMessageData = messageData.split(",")
        x = (float(splitMessageData[2])/1000)
        y = (float(splitMessageData[3])/1000)
        z = (float(splitMessageData[4])/1000)
        return [x, y, z]

    # Returns time of Widefind mqtt data
    def getTime(self, jsonData):
        parse = json.loads(jsonData)
        timeData = parse['time']
        splitTimeData = re.split(r"[-T:.Z]\s*", timeData)
        currentTime = datetime.datetime(int(splitTimeData[0]), int(splitTimeData[1]), int(splitTimeData[2]), int(splitTimeData[3]), int(splitTimeData[4]), int(splitTimeData[5]), int(splitTimeData[6][:6]))
        return currentTime


if __name__ == '__main__':
    p = PositionHandler('vet-inte', 'DA7A27076AF8BBD2')


