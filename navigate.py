import double
import sys
import math

class navigate():
    def __init__(self, yStart, xStart):
        self.d3 = double.DRDoubleSDK()
        #self.setup()
        self.yStart = yStart
        self.xStart = xStart
     
    def setup(self):
        self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('navigate.obstacleAvoidance.setLevel', { "level": 2 })
        self.d3.sendCommand('navigate.exitDock')
        #self.d3.sendCommand('base.kickstand.retract')
        #self.d3.sendCommand('navigate.target', {'x':float(-1),'y':float(0),'angleRadians':float(math.pi),'relative':True,'dock':False,'dockId':0})
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
            'DRNavigateModule.target', 'DRNavigateModule.arrive'
            ]})
            self.d3.sendCommand('navigate.target', {'x':float(xCordinate),'y':float(yCordinate),'angleRadians':float(0),'relative':False,'dock':False,'dockId':0})            
            while True:
                packet = self.d3.recv()
                if packet != None:
                    event = packet['class'] + '.' + packet['key']
                    if event == 'DRNavigateModule.target':
                        print('Navigate.target-------> ', packet['data'])
                    elif event == 'DRNavigateModule.arrive':
                        print("--------------->Jag har nått till destinationen<-----------------")
                        break
        except KeyboardInterrupt:
            self.d3.close()
            print('cleaned up')
            sys.exit(0)

    def cancelNavigation(self):
        #self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('navigate.cancelTarget')
        print("stop!!!")

    def driveHome(self):
        navigation(self.xStart, self.yStart)

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

    #arr[0] x, arr[1] y

    def calcWFtoD3(self, wfStartArr, wfDestArr):
        
        d3Arr = self.getPosition()
        
        xStart = wfStartArr[0]
        yStart = wfStartArr[1]

        xDest = wfDestArr[0]
        yDest = wfDestArr[1]

        deltaX = xDest - xStart
        deltaY = yDest - yStart
        
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

"""  def hitTest(self):
        self.d3.sendCommand('events.subscribe', { 'events': [
            'DRCamera.hitResult'
            ]})
        self.d3.sendCommand('camera.hitTest', {'hit':'true', "x": 0.5, "y": 0.5, "highlight": 'true', "passToNavigate": 'true'})
        while True:
               packet = self.d3.recv()
               if packet != None:
                   event = packet['class'] + '.' + packet['key']
                   if event == 'DRCamera.hitResult':
                       print(packet['data'])
                       print("nu händer det något")
                        
        

    while True:
                packet = self.d3.recv()
                if packet != None:
                    event = packet['class'] + '.' + packet['key']
                    if event == 'DRPose.pose':
                        print(packet['data']['base']['x'])
                        print(packet['data']['base']['y'])
                        print("--------------->Jag har nått till destinationen<-----------------")
                    elif event == 'DRNavigateModule.status': 
                        print('Navigate.Status-------> ', packet['data'])
                    elif event == 'DRNavigateModule.target':
                        print('Navigate.target-------> ', packet['data'])"""



