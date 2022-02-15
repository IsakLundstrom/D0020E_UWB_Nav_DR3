import double


class SessionHandler():
    def __init__(self):
        self.d3 = double.DRDoubleSDK()
        self.d3.sendCommand('events.subscribe', { 'events': [
            'DREndpointModule.status'
            ]})
        self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('endpoint.requestModuleStatus') 
        self.link = "http://130.240.114.43:5000/"
        self.d3.sendCommand('gui.accessoryWebView.open',{ "url": self.link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })
        
        
    def listen(self):    
        while True:
            packet = self.d3.recv()
            if packet != None:
                event = packet['class'] + '.' + packet['key']
                if event == 'DREndpointModule.status':
                    if packet['data']['session'] == True:
                        break
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
                        self.d3.sendCommand('navigate.enable')
                        self.d3.sendCommand('navigate.target', {'x':float(0),'y':float(0),'relative':False,'dock':False,'dockId':0})
                        self.d3.sendCommand('gui.accessoryWebView.open',{ "url": self.link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })
                        break 
        self.listen()
    
    def cancelNavigation(self):
        self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('navigate.cancelTarget')
        print("stop!!!")