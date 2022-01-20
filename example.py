import double
import sys
from navigate import navigate
d3 = double.DRDoubleSDK()
nav = navigate(0,0.5)


nav.navigation(0, 0.5)
#nav.cancelNavigation()
""" try:
    d3.sendCommand('events.subscribe', { 'events': [
        'DRNavigateModule.targetState',
        'DRNavigateModule.newTarget'
    ]})  
    d3.sendCommand('screensaver.nudge')
    d3.sendCommand('camera.enable', { 'template': 'screen' })
    d3.sendCommand('base.requestStatus')
    d3.sendCommand('navigate.enable')
    d3.sendCommand('dockTracker.enable')
    d3.sendCommand('navigate.target', {'x':float(0.5),'y':float(0),'angleRadians':float(0),'relative':True,'dock':False,'dockId':0})
    # d3.sendCommand('navigate.target', {'x':float(-0.5),'y':float(-0.5),'angleRadians':float(6.28),'relative':True,'dock':False,'dockId':0})
    while True:
        packet = d3.recv()
        if packet != None:
            event = packet['class'] + '.' + packet['key']
            if event == 'DRNavigateModule.targetState':
                print(packet['data'])
            elif event == 'DRNavigateModule.newTarget':
                print(packet['data'])
                print('HejHejHej')

except KeyboardInterrupt:
    d3.sendCommand('camera.disable')
    d3.sendCommand('screensaver.nudge')
    d3.close()
    print('cleaned up')
    sys.exit(0)  """