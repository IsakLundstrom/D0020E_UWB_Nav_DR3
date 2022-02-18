import double


class SessionHandler():
    def __init__(self):
        self.isDocked = False
        self.d3 = double.DRDoubleSDK()
        self.d3.sendCommand('events.subscribe', { 'events': [
            'DREndpointModule.status', 'DRDockTracker.docks', 'DRBase.status'
            ]})
        self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('endpoint.requestModuleStatus') 
        self.d3.sendCommand('dockTracker.enable')
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
                elif event == 'DRDockTracker.docks':
                    self.isDocked = True
                    print("den laddar!")
                elif event == 'DRBase.status':
                    if packet['charging']=='True':
                        self.isDocked=True
                        print('Den laddar')
                    else:
                        self.isDocked=False
                        print('Den laddar inte')

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
                        break
        
        while True:
            packet = self.d3.recv()
            if packet != None:
                event = packet['class'] + '.' + packet['key']
                if event == 'DRBase.status':
                    if packet['charging']=='True':
                        self.isDocked=True
                        print('Den laddar')
                        self.d3.sendCommand('gui.accessoryWebView.open',{ "url": self.link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })
                    else:
                        self.isDocked = False
                        self.d3.sendCommand('navigate.enable')
                        self.d3.sendCommand('navigate.target', {'x':float(0),'y':float(0),'relative':False,'dock':False,'dockId':0})
                        self.d3.sendCommand('gui.accessoryWebView.open',{ "url": self.link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })
 
        self.listen()
    
    def cancelNavigation(self):
        self.d3.sendCommand('navigate.enable')
        self.d3.sendCommand('navigate.cancelTarget')
        print("stop!!!")