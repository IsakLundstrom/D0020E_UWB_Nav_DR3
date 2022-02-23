# To start server fo into website folder and to start run: python3 server.py
from flask import Flask, Response, render_template, request, jsonify
import os
import json
import double
import threading
import pytz
from pytz import timezone
import datetime
from datetime import datetime, timezone
from notify_run import Notify 
from globalVariables import GlobalVariables
from webpage.changeConfig import ChangeConfig
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
    return render_template('index.html', systemOn = globalVariables.systemOn, msg = "")

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

@app.route('/fall', methods=['GET'])
def fall():
    return render_template('fall.html', msg = "")

@app.route('/info', methods=['GET'])
def info():
    return render_template('info.html')

@app.route('/drivingHome', methods=['GET'])
def drivingHome():
    return render_template('drivingHome.html')

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
        broker_address = data['widefind']['broker_address']
        spotD3 = data['widefind']['spotD3']
        spotUser = data['widefind']['spotUser']
        subscribe_address = data['widefind']['subscribe_address']
        # systemOn = int (data['system']['systemOn'])
        jsonFile.close()
#       print(data)
        
    return render_template('settings.html', data= json.dumps(data), angle = angle, avgTime = AVERAGE_TIME_WINDOW_SIZE, alertHeight = ALERT_HEIGT, alertWindow = ALERT_WINDOW_SIZE, alertTime = ALERT_TIME_GAP, alertStart = ALERT_TIME_GAP_START, broker = broker_address, spotU = spotUser, spotD = spotD3, subscribe = subscribe_address, systemOn = globalVariables.systemOn)

@app.route('/notify/<msg>', methods=['GET', 'POST'])
def notify(msg):
    print('%s' % msg)
#   Ändrade till en global notify, det är bara ta bort kommentaren om det inte funkar
#   notify = Notify()
    notify.send('%s' % msg)
    return render_template('index.html', systemOn = globalVariables.systemOn, msg = "Ditt meddelande har skickats, vårdare hör av sig snart")

@app.route('/changeSetting/<title>/<variable>/<value>', methods=['GET', 'POST'])
def changeSetting(title, variable, value):

    c = ChangeConfig()
    c.changeConstant('config.json', title, variable, value)
    
    # if(variable == 'systemOn' and value == 'False'):
    #     fallSystemLock.notify()
    
    globalVariables.changedSettings = True

    return settings()

@app.route('/sendCommandToD3/<command>', methods=['GET', 'POST'])
def sendCommandToD3(command):
    d3 = double.DRDoubleSDK()
    d3.sendCommand(command)
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
    sendMsg = 'Person meddelar att fallet var ett falskt alarm. Robot kör tillbaka.'
    notify.send(sendMsg)
    nav = navigate()
    nav.cancelNavigation()
    nav.driveHome()
    return index()

@app.route('/notifyOkWhenFall', methods=['GET', 'POST'])
def notifyOkWhenFall():
    sendMsg = 'Person meddelar att den mår bra. Anslut ändå snarast för att kolla situationen.'
    notify.send(sendMsg)
    popUpMsg = 'Vådare meddelat att du mår bra. Vådare ansluter för att kolla läget snart'
    return render_template('fall.html', msg = popUpMsg)

@app.route('/notifyNotOkWhenFall', methods=['GET', 'POST'])
def notifyNotOkWhenFall():
    sendMsg = 'Person meddelar att den INTE mår bra och behöver hjälp. Anslut omgående.'
    notify.send(sendMsg)
    popUpMsg = 'Vådare meddelat att du behöver hjälp. Vådare ansluter snarast'
    return render_template('fall.html', msg = popUpMsg)

@app.route('/time')
def time():
    def generate():
        return getTimezoneTime().strftime("%H:%M")
    return Response(generate(), mimetype='text') 

@app.route('/weekDay')
def weekDay():
    def generate():
        weekDays = {"monday":"Måndag", "tuesday":"Tisdag", "wednesday":"Onsdag", "thursday":"Torsdag", "friday":"Fredag", "saterday":"Lördag", "sunday":"Söndag"} 
        currentWeekDay = getTimezoneTime().strftime("%A").lower()
        for key in weekDays.keys():
            currentWeekDay = currentWeekDay.replace(key, weekDays[key])
        return currentWeekDay
    return Response(generate(), mimetype='text') 

@app.route('/date')
def date():
    def generate():
        months = {"01":"januari", "02":"februari", "03":"mars", "04":"april", "05":"maj", "06":"juni", "07":"juli", "08":"augusti", "09":"september", "10":"oktober", "11":"november", "12":"december"}
        currentMonth = getTimezoneTime().strftime("%m")
        for key in months.keys():
            currentMonth = currentMonth.replace(key, months[key])
        return getTimezoneTime().strftime("%d") + ' ' + currentMonth + ' ' +  getTimezoneTime().strftime("%Y")
    return Response(generate(), mimetype='text') 

def getTimezoneTime():
    utc_now = pytz.utc.localize(datetime.utcnow())
    pst_now = utc_now.astimezone(pytz.timezone("Europe/Stockholm"))
    return pst_now

def startServer(condition, g):
    global fallSystemLock 
    fallSystemLock = condition
#   global systemOn
    global globalVariables 
    globalVariables = g
    global notify
    notify = Notify()
    # globalVariables.systemOn = True

    # notify = notifier
    print('Server started')
    # app.run(debug=False)
    app.run(host='0.0.0.0', debug=False)



if __name__ == '__main__':
    startServer()