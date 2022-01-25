import double
import sys
from navigate import navigate
d3 = double.DRDoubleSDK()
nav = navigate(0,0)

#nav.navigation(5,5)
#nav.driveHome()
d3.sendCommand('navigate.target', {'x':float(1),'y':float(1),'relative':False,'dock':False,'dockId':0})            

""" d3.sendCommand('events.subscribe', { 'events': [
            'DREndpointModule.status']})

d3.sendCommand('endpoint.requestModuleStatus')
packet = d3.recv()
print('-------> ', packet['data'])


while True:
    packet = d3.recv()
    if packet != None:
        event = packet['class'] + '.' + packet['key']
        if event == 'DREndpointModule.status':
            print('-------> ', packet['data']) """
                    



""" arr1 = nav.getPosition()
widefindStart = [0.677, -2.656]
widefindDest = [1.77, -1.94]
arr2 = nav.calcWFtoD3(arr1, widefindStart, widefindDest)

nav.navigation(arr2[0], arr2[1]) """

#nav.navigation(0,0)
#nav.cancelNavigation()