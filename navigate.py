import double
import sys

class navigate():
    def __init__(self):
        self.d3 = double.DRDoubleSDK()
#        self.y 
#        self.x
     

    def navigation(self, xCordinate, yCordinate):
        #Positivt värde på X så kör roboten framåt, från origin
        #Negativt värde på X så kör roboten bakåt, från origin
        #Positivt värde på Y så kör roboten vänster, från origin
        #Negativt värde på Y så kör roboten höger, från origin
        try:
            self.d3.sendCommand('navigate.enable')
            self.d3.sendCommand('navigate.target', {'x':float(xCordinate),'y':float(yCordinate),'angleRadians':float(3.1415),'relative':False,'dock':False,'dockId':0})    
        except KeyboardInterrupt:
            self.d3.close()
            print('cleaned up')
            sys.exit(0)



