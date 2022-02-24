import double
import sys
import math
import json
import time


class navigate():
    def __init__(self):
        self.d3 = double.DRDoubleSDK()
#       self.setup()
        # self.startAngle = startAngle    #0-3
        f = open('config.json')
        CONFIG = json.load(f)
        f.close()
        self.startAngle = CONFIG['d3']['startingAngle']   
        self.drivingHome = False
     
    def setup(self):
        self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('navigate.obstacleAvoidance.setLevel', { "level": 2 })
        self.d3.sendCommand('pose.resetOrigin')

    def navigation(self, xCordinate, yCordinate):
        #Positivt värde på X så kör roboten framåt, från origin
        #Negativt värde på X så kör roboten bakåt, från origin
        #Positivt värde på Y så kör roboten vänster, från origin
        #Negativt värde på Y så kör roboten höger, från origin
        #Widefind: 
        #Positiv x mot fönster
        #Positiv y mot rum med säng
        try:
            self.d3.sendCommand('events.subscribe', { 'events': [
            'DRNavigateModule.target', 'DRNavigateModule.arrive', 'DRNavigateModule.cancelTarget','DREndpointModule.status', 'DRDockTracker.docks'
            ]})
            self.d3.sendCommand('navigate.enable')
            self.d3.sendCommand('endpoint.requestModuleStatus') 
            self.d3.sendCommand('dockTracker.enable')
            self.d3.sendCommand('navigate.target', {'x':float(xCordinate),'y':float(yCordinate),'relative':False,'dock':False,'dockId':0})            
            
            while True:
                packet = self.d3.recv()
                if packet != None:
                    event = packet['class'] + '.' + packet['key']
                    if event == 'DRNavigateModule.target':
                        print('Navigate.target-------> ', packet['data'])
                    elif event == 'DRNavigateModule.arrive':
                        print("--------------->Jag har nått till destinationen<-----------------")
                        break
                    elif event == 'DRNavigateModule.cancelTarget':
                        print("---------------------Navigation canceled-------------------------")
                        self.drivingHome = not self.drivingHome
                        break
                    elif event == 'DRDockTracker.docks' and self.drivingHome:
                        print('DRIVING TO DOCK')
                        self.drivingHome = False
                        self.cancelNavigation()
                        print(packet['data']['docks'][0]['id'])
                        self.d3.sendCommand('navigate.target', { "x": 0, "y": 0, "relative": False, "dock": 'forward', "dockId": packet['data']['docks'][0]['id']})
                        link = "http://130.240.114.43:5000/"
                        self.d3.sendCommand('gui.accessoryWebView.open',{ "url": link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })


        except KeyboardInterrupt:
            self.d3.close()
            print('cleaned up')
            sys.exit(0)

    def cancelNavigation(self):
        self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('navigate.cancelTarget')
        print("stop!!!")

    def driveHome(self):
        self.d3.sendCommand('navigate.enable')
        self.drivingHome = True
        link = "http://130.240.114.43:5000/drivingHome"
        self.d3.sendCommand('gui.accessoryWebView.open',{ "url": link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })
        self.navigation(0, 0)
        if(self.drivingHome):
            link = "http://130.240.114.43:5000/"
            self.d3.sendCommand('gui.accessoryWebView.open',{ "url": link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })


    def driveWhenFall(self, xCordinate, yCordinate):
        self.drivingHome = False
        self.d3.sendCommand('navigate.enable')
        link = "http://130.240.114.43:5000/fall"
        self.d3.sendCommand('gui.accessoryWebView.open',{ "url": link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })
        
        while(self.checkCharge()):
            self.d3.sendCommand('navigate.target', {"action":"exitDock"})
            print("EXIT DOCK")
            time.sleep(8)

        self.navigation(xCordinate, yCordinate)
        
    def checkCharge(self):
        self.d3.sendCommand('events.subscribe', { 'events': ['DRBase.status']})
        while True:
            self.d3.sendCommand('base.requestStatus')
            data = self.d3.recv()
            if data != None:
                event = data['class'] + '.' + data['key']
                if event == 'DRBase.status':
                    print(data['data']['charging'])
                    return data['data']['charging']


    def handleSession(self):
        self.cancelNavigation()
        while True:
            packet = self.d3.recv()
            if packet != None:
                event = packet['class'] + '.' + packet['key']
                if event == 'DREndpointModule.status':
                    if packet['data']['session'] == False:
                        self.driveHome()
                        break



    def getPosition(self):
        self.d3.sendCommand('events.subscribe', { 'events': [
            'DRPose.pose'
            ]})  
        arr = []
        self.d3.sendCommand('base.travel.start')

        packet = self.d3.recv()
        if packet != None:
            event = packet['class'] + '.' + packet['key']
            if event == 'DRPose.pose':
                print("--------------->Här kommer positionen<-----------------")
                print(packet['data']['base']['x'])
                arr.append(packet['data']['base']['x'])
                print("Array 0 ", arr[0])
                print(packet['data']['base']['y'])
                arr.append(packet['data']['base']['y'])
                print("Array 1 ", arr[1])
        return arr


    def calcWFtoD3(self, wfStartArr, wfDestArr):
        
        d3Arr = self.getPosition()
        xStart = wfStartArr[0]
        yStart = wfStartArr[1]

        xDest = wfDestArr[0]
        yDest = wfDestArr[1]

        deltaX = xDest - xStart
        deltaY = yDest - yStart

        if(self.startAngle == 0):
            deltaXinD3 = deltaX
            deltaYinD3 = deltaY
        elif(self.startAngle == 1):
            deltaXinD3 = -deltaY
            deltaYinD3 = deltaX
        elif(self.startAngle == 2):
            deltaXinD3 = -deltaX
            deltaYinD3 = -deltaY
        else:
            deltaXinD3 = deltaY
            deltaYinD3 = -deltaX
        
    
        d3CurrentX = d3Arr[0]
        d3CurrentY = d3Arr[1]

        finalX = d3CurrentX + deltaXinD3
        finalY = d3CurrentY + deltaYinD3
        print("Final X", finalX)
        print("Final Y", finalY)

        array = [finalX, finalY]
        return array



