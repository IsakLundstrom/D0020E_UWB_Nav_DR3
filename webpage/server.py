# To start server fo into website folder and to start run: python3 server.py
from flask import Flask, Response, render_template, request, jsonify
import os
import json
import double
import threading
from globalVariables import GlobalVariables
from webpage.changeConfig import ChangeConfig
from datetime import datetime
from notify_run import Notify 
from navigate import navigate

# changeConfig = None
#fallSystemLock = threading.fallSystemLock()
app = Flask(__name__)


@app.route('/')
def index():
    # with open('config.json', 'r') as jsonFile:
    #     data = json.load(jsonFile)
    #     systemOn = int (data['system']['systemOn'])
    # print('Server: ',systemOn)
    return render_template('index.html', systemOn = globalVariables.systemOn)

# @app.route('/link', methods=['GET', 'POST'])
# def link():
#     changeConfig.changeAlertGap(11)
#     if request.method == 'POST':
#         print ('POST link')
#         return render_template('link.html')
#     else:
#         print("GET link")
#         return render_template('link.html')

@app.route('/help', methods=['GET', 'POST'])
def sendMsg():
    pass

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/drive', methods=['GET'])
def drive():

    # systemOn = False
    # print(systemOn)
    return render_template('drive.html')

@app.route('/settings', methods=['GET'])
def settings():    
    
    with open('config.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        angle = int (data['d3']['startingAngle'])
        AVERAGE_TIME_WINDOW_SIZE = int(data['constants']['AVERAGE_TIME_WINDOW_SIZE'])
        ALERT_HEIGT = float(data['constants']['ALERT_HEIGT'])
        ALERT_WINDOW_SIZE = int(data['constants']['ALERT_WINDOW_SIZE'])
        ALERT_TIME_GAP = float(data['constants']['ALERT_TIME_GAP'])
        ALERT_TIME_GAP_START = float(data['constants']['ALERT_TIME_GAP_START'])
        # systemOn = int (data['system']['systemOn'])
        jsonFile.close()
#       print(data)

    return render_template('settings.html', data= json.dumps(data), angle = angle, avgTime = AVERAGE_TIME_WINDOW_SIZE, alertHeight = ALERT_HEIGT, alertWindow = ALERT_WINDOW_SIZE, alertTime = ALERT_TIME_GAP, alertStart = ALERT_TIME_GAP_START, systemOn = globalVariables.systemOn)

@app.route('/notify/<msg>', methods=['GET', 'POST'])
def notify(msg):
    print('%s' % msg)
    notify = Notify()
    notify.send('%s' % msg)
    return index()

@app.route('/changeSetting/<title>/<variable>/<value>', methods=['GET', 'POST'])
def changeSetting(title, variable, value):

    c = ChangeConfig()
    c.changeConstant('config.json', title, variable, value)
    
    # if(variable == 'systemOn' and value == 'False'):
    #     fallSystemLock.notify()
    
    globalVariables.changedSettings = True

    return settings()

@app.route('/toggleSystemOnOff/', methods=['GET', 'POST'])
def toggleSystemOnOff():
#    global systemOn

    print(globalVariables.systemOn)
    if(globalVariables.systemOn):
        fallSystemLock.acquire()
        globalVariables.systemOn = False
    else:
        fallSystemLock.release()
        globalVariables.systemOn = True

    return settings()

@app.route('/falseAlarm')
def falseAlarm():
    d3 = double.DRDoubleSDK()
    d3.sendCommand('navigate.target', {'x':float(0),'y':float(0),'relative':False,'dock':False,'dockId':0})

    return index()

@app.route('/time')
def time():
    def generate():
        return datetime.now().strftime("%H:%M")
    return Response(generate(), mimetype='text') 

@app.route('/date')
def date():
    def generate():
        return datetime.now().strftime("%Y-%m-%d")
    return Response(generate(), mimetype='text') 

def startServer(condition, g):
    global fallSystemLock 
    fallSystemLock = condition
#   global systemOn
    global globalVariables 
    globalVariables = g
    # globalVariables.systemOn = True

    # notify = notifier
    print('Server started')
    # app.run(debug=False)
    app.run(host='0.0.0.0', debug=False)



if __name__ == '__main__':
    startServer()