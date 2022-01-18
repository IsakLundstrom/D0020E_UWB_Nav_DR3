import paho.mqtt.client as mqtt #import the client1
import time
import json
import datetime
import re
############

AVREAGETIME = 5
ALERTHEIGT = 0.5

class PositionHandler:
    def __init__(self, spotD3, spotUser):
        self.spotD3 = spotD3
        self.spotUser = spotUser

        self.zCords = {}
        self.zAvg = 0

        broker_address = "130.240.74.55"
        client = mqtt.Client("P1") 
        client.on_message=self.on_message
        client.connect(broker_address)
        client.loop_start()
        client.subscribe("ltu-system/#")
        time.sleep(120) # wait
        client.loop_stop()

    def movingAverage(self, currentTime, newZ):
        print(len(self.zCords))
        for x in list(self.zCords): # Remove old z cords
            delta = currentTime - x
            if(delta.seconds > AVREAGETIME):
                newsum = self.zAvg*len(self.zCords) - self.zCords[x]
                print(newsum)
                del self.zCords[x]
                self.zAvg = newsum/len(self.zCords) # Bug division by zero!!!!
            else:
                break

        # Update new avrage
        newsum = self.zAvg*len(self.zCords) + newZ
        
        print(newsum)
        self.zCords.update({currentTime: newZ})
        self.zAvg = newsum/len(self.zCords)
        print(len(self.zCords))
        print('')

    def isASpot(self, jsonMessage):
        return self.spotD3 in jsonMessage or self.spotUser in jsonMessage
    

    def on_message(self, client, userdata, message):
        # print(str(message.payload.decode("utf-8"))) # Prints all Widefind mqtt data
        mqttMsgString = message.payload.decode()
        mqttMsgJson = json.loads(mqttMsgString)
        # print(mqttMsgJson)
        #self.data_queue.put(mqttMsgJson)
        jsonMessage = json.dumps(mqttMsgJson)
        if self.isASpot(jsonMessage):
            # print(str(message.payload.decode("utf-8")))
            cordinates = self.getCordinates(jsonMessage)
            # print(cordinates)
            currentTime = self.getTime(jsonMessage)
            zCord = cordinates[2]
            self.movingAverage(currentTime, zCord)
            if(self.checkZHeight(zCord)):
                self.alert()
            # print(currentTime)

        
        # print("message topic=",message.topic)
        # print("message qos=",message.qos)
        # print("message retain flag=",message.retain)
    ########################################

    def checkZHeight(self, zCord):
        return(self.zAvg < ALERTHEIGT and zCord < ALERTHEIGT)


    def alert(self):
        print('ALERT!')


    # Returns cordinates of Widefind mqtt data
    def getCordinates(self, jsonData):
        testParse = json.loads(jsonData)
        messageData = testParse['message']
        # print(messageData)
        splitMessageData = messageData.split(",")
        x = (float(splitMessageData[2])/1000)
        y = (float(splitMessageData[3])/1000)
        z = (float(splitMessageData[4])/1000)
        return [x, y, z]

    def getTime(self, jsonData):
        testParse = json.loads(jsonData)
        timeData = testParse['time']
        splitTimeData = re.split('-|T|:', timeData)
        currentTime = datetime.datetime(int(splitTimeData[0]), int(splitTimeData[1]), int(splitTimeData[2]), int(splitTimeData[3]), int(splitTimeData[4]), int(splitTimeData[5][:2]), int(splitTimeData[5][4:10])) # Bug i sista split FIXA!!!
        return currentTime


if __name__ == '__main__':
    p = PositionHandler('DA7A27076AF8BBD2', 'vet-inte')


