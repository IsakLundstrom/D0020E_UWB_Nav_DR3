import double
from navigate import navigate
from globalVariables import GlobalVariables


class SessionHandler():
    def __init__(self, globals):
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
        
        
    def listen(self):    
        while True:
            packet = self.d3.recv()
            if packet != None:
                event = packet['class'] + '.' + packet['key']
                if event == 'DREndpointModule.status':
                    if packet['data']['session'] == True:
                        self.d3.sendCommand('speaker.enable')
                        self.g.doNotifyLoop = False
                        break
                # elif event == 'DRDockTracker.docks':
                #     self.isDocked = True
                #     print("den laddar!")
                #     print(packet['data'])
                # elif event == 'DRBase.status':
                #     print('DRBase.status data:')
                #     print(packet['data']['charging'])
                #     if packet['data']['charging']==True:
                #         self.isDocked=True
                #         print('Den laddar')
                #     else:
                #         self.isDocked=False
                #         print('Den laddar inte')

        self.handleSession()

    def handleSession(self):
        self.cancelNavigation()
        print("handling session from the new Thread------------------------------")
        while True:
            packet = self.d3.recv()
            if packet != None:
                event = packet['class'] + '.' + packet['key']
                if event == 'DREndpointModule.status':
                    if packet['data']['session'] == False:
                        self.d3.sendCommand('speaker.disable')
                        break
        
        self.d3.sendCommand('events.unsubscribe', { 'events': ['DREndpointModule.status']})
        self.d3.sendCommand('base.requestStatus')
        self.g.doNotifyLoop = True
        while True:
            data = self.d3.recv()
            #print(data['data'])
            if data != None:
                event = data['class'] + '.' + data['key']
                if event == 'DRBase.status':
                    if(data['data']['charging'] == False):
                        print("den laddar inte")
                        nav = navigate()
                        nav.driveHome()
                    else:
                        self.d3.sendCommand('base.kickstand.deploy')
                        self.d3.sendCommand('gui.accessoryWebView.open',{ "url": self.link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })  
                    break
                    
        self.d3.sendCommand('events.subscribe', { 'events': ['DREndpointModule.status']})
                        
        self.listen()
    
    def cancelNavigation(self):
        self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('navigate.cancelTarget')
        print("stop!!!")