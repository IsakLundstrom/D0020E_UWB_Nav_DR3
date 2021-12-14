import paho.mqtt.client as mqtt #import the client1
import time
import json
############
def on_message(client, userdata, message):
    
    # print(str(message.payload.decode("utf-8")))


    mqttMsgString = message.payload.decode()
    mqttMsgJson = json.loads(mqttMsgString)
    # print(mqttMsgJson)
    #self.data_queue.put(mqttMsgJson)
    jsonMessage = json.dumps(mqttMsgJson)
    if "REPORT" in jsonMessage:
        cordinate = parsCordinates(jsonMessage)
        # print('hej')
        # print(cordinate[0], " ", cordinate[1], " ", cordinate[2])

    
    # print("message topic=",message.topic)
    # print("message qos=",message.qos)
    # print("message retain flag=",message.retain)
########################################


def parsCordinates(jsonData):
    testParse = json.loads(jsonData)
    cords = testParse['message']
    print(cords)
    count = 0
    for n in cords:
        if n == ',':
            count = 1 + count
    split_string = cords.split(",", count)
    xInMeter = (float(split_string[2])/1000)
    yInMeter = (float(split_string[3])/1000)
    zInMeter = (float(split_string[4])/1000)
    print('x cord: ', xInMeter)
    print('y cord: ', yInMeter)
    print('z cord: ', zInMeter)


broker_address="130.240.74.55"
#broker_address="iot.eclipse.org"
# print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
# print("connecting to broker")
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop
# print("Subscribing to topic","#")
client.subscribe("ltu-system/#")
# print("Publishing message to topic","house/bulbs/bulb1")
# client.publish("house/bulbs/bulb1","OFF")
time.sleep(120) # wait
client.loop_stop() #stop the loop






