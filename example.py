import double
import sys

d3 = double.DRDoubleSDK()

try:
    d3.sendCommand('events.subscribe', { 'events': [
        'DRBase.status',
        'DRCamera.enable'
    ]})
    d3.sendCommand('screensaver.nudge');
    d3.sendCommand('camera.enable', { 'template': 'screen' });
    d3.sendCommand('base.requestStatus');
    d3.sendCommand('navigate.enable')
    d3.sendCommand('navigate.target', {'x':float(0.5),'y':float(0.5),'angleRadians':float(0),'relative':True,'dock':False,'dockId':0})
    # d3.sendCommand('navigate.target', {'x':float(-0.5),'y':float(-0.5),'angleRadians':float(6.28),'relative':True,'dock':False,'dockId':0})
    while True:
        packet = d3.recv()
        if packet != None:
            event = packet['class'] + '.' + packet['key']
            if event == 'DRBase.status':
                print(packet['data'])
            elif event == 'DRCamera.enable':
                print('camera enabled')

except KeyboardInterrupt:
    d3.sendCommand('camera.disable');
    d3.sendCommand('screensaver.nudge');
    d3.close()
    print('cleaned up')
    sys.exit(0)