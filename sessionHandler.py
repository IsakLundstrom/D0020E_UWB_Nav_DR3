import double
from navigate import navigate
from globalVariables import GlobalVariables


class SessionHandler():
    def __init__(self, globals): # Initierar sessionshanteraren
        self.g = globals
        self.isDocked = False
        self.d3 = double.DRDoubleSDK()
        self.d3.sendCommand('events.subscribe', { 'events': [
            'DREndpointModule.status', 'DRBase.status'
            ]})
        self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('endpoint.requestModuleStatus') 
        self.d3.sendCommand('dockTracker.enable')
        self.d3.sendCommand('screensaver.prevent')
        self.link = "http://130.240.114.43:5000/"
        self.d3.sendCommand('gui.accessoryWebView.open',{ "url": self.link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })
        
        
    def listen(self): # This function busy-waits until someone connects to the robot   
        while True:
            packet = self.d3.recv()
            if packet != None:
                event = packet['class'] + '.' + packet['key']
                if event == 'DREndpointModule.status':
                    if packet['data']['session'] == True:
                        self.d3.sendCommand('speaker.enable') # When someone connects we turn on speakers and handle the connection
                        self.g.doNotifyLoop = False
                        break
        self.handleSession()

    def handleSession(self):
        self.cancelNavigation() # We stop driving the robot so th euser can take over
        print("handling session from the new Thread------------------------------")
        while True:
            packet = self.d3.recv()
            if packet != None:
                event = packet['class'] + '.' + packet['key']
                if event == 'DREndpointModule.status':
                    if packet['data']['session'] == False: # When the connection is broken we turn off speakers
                        self.d3.sendCommand('speaker.disable')
                        break
        
        self.d3.sendCommand('events.unsubscribe', { 'events': ['DREndpointModule.status']})
        self.d3.sendCommand('base.requestStatus')
        self.g.doNotifyLoop = True
        while True: # This loop will wait until the robot sends its' status
            data = self.d3.recv()
            if data != None:
                event = data['class'] + '.' + data['key']
                if event == 'DRBase.status': # When we recieve the status we check if it's charging or not
                    if(data['data']['charging'] == False): # if it's not  charging we drive home
                        print("den laddar inte")
                        nav = navigate()
                        nav.driveHome()
                    else: # else we just go back to the main menu
                        self.d3.sendCommand('base.kickstand.deploy')
                        self.d3.sendCommand('gui.accessoryWebView.open',{ "url": self.link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })  
                    break
                    
        self.d3.sendCommand('events.subscribe', { 'events': ['DREndpointModule.status']})
                        
        self.listen() # Then we listen for a new connection again
    
    def cancelNavigation(self): # This function just cancels the navigation to a target
        self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('navigate.cancelTarget')
        print("stop!!!")