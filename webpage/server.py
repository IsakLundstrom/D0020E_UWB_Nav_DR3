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
def index(): # Loads the main menu
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
def contact(): # Loads the contact screen
    return render_template('contact.html')

@app.route('/fall', methods=['GET'])
def fall(): # Loads the fall screen
    return render_template('fall.html', msg = "")

@app.route('/info', methods=['GET'])
def info(): # Loads the info screen
    return render_template('info.html')

@app.route('/drivingHome', methods=['GET'])
def drivingHome(): # Loads the drive-home-screen
    return render_template('drivingHome.html')

@app.route('/settings', methods=['GET'])
def settings():    # Loads all settings and then uses them for the settings menu
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
        d3name = data['user']['D3Name']
        username = data['user']['Name']
        useraddress = data['user']['Address']
        jsonFile.close()
        
    return render_template('settings.html', data= json.dumps(data), d3name = d3name, username = username, useraddress = useraddress, angle = angle, avgTime = AVERAGE_TIME_WINDOW_SIZE, alertHeight = ALERT_HEIGT, alertWindow = ALERT_WINDOW_SIZE, alertTime = ALERT_TIME_GAP, alertStart = ALERT_TIME_GAP_START, broker = broker_address, spotUser = spotUser, spotD3 = spotD3, subscribe = subscribe_address, systemOn = globalVariables.systemOn)

@app.route('/keyBoardInput', methods=['GET'])
def keyBoardInput(): # Loads the screen that uses the keyboard
    with open('config.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        broker_address = data['widefind']['broker_address']
        spotD3 = data['widefind']['spotD3']
        spotUser = data['widefind']['spotUser']
        subscribe_address = data['widefind']['subscribe_address']
        d3name = data['user']['D3Name']
        username = data['user']['Name']
        useraddress = data['user']['Address']
        jsonFile.close()
    return render_template('keyBoardInput.html', data= json.dumps(data), d3name = d3name, username = username, useraddress = useraddress, broker = broker_address, spotUser = spotUser, spotD3 = spotD3, subscribe = subscribe_address)

@app.route('/notify/<msg>', methods=['GET', 'POST'])
def notify(msg): # Sends a message from the robot, then returns to the main menu
    with open('config.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        username = data['user']['Name']
        address = data['user']['Address']
        d3name = data['user']['D3Name']
    sendMsg = 'MSG: ' + username + ', ' + address + ', ' + msg + '. Robot: ' + d3name
    # print(sendMsg)
#   Ändrade till en global notify, det är bara ta bort kommentaren om det inte funkar
#   notify = Notify()
    notify.send(sendMsg)
    return render_template('index.html', systemOn = globalVariables.systemOn, msg = "Ditt meddelande har skickats, vårdare hör av sig snart")

@app.route('/changeSetting/<title>/<variable>/<value>', methods=['GET', 'POST'])
def changeSetting(title, variable, value): # Changes a chosen setting

    c = ChangeConfig()
    c.changeConstant('config.json', title, variable, value)
    
    globalVariables.changedSettings = True

    return settings()

@app.route('/changeUserInfo', methods=['GET', 'POST'])
def changeUserInfo(): # Updates user info based on what the user typed
    form_data = request.form
    print(form_data["username"])
    with open("config.json", "r") as jsonFile:
        data = json.load(jsonFile)
        jsonFile.close()

    data["user"]["Name"] = form_data["username"]
    data["user"]["Address"] = form_data["address"]
    data["user"]["D3Name"] = form_data["d3name"]
    
    with open("config.json", "w") as jsonFile:
        json.dump(data, jsonFile)
        jsonFile.close()
    
    globalVariables.changedSettings = True
    return goFromkeyBoardPage()

@app.route('/changeWidefindInfo', methods=['GET', 'POST'])
def changeWidefindInfo(): # Changes widefind info based on what the user has typed
    form_data = request.form
    with open("config.json", "r") as jsonFile:
        data = json.load(jsonFile)
        jsonFile.close()

    data["widefind"]["broker_address"] = form_data["broker"]
    data["widefind"]["spotD3"] = form_data["spotD3"]
    data["widefind"]["spotUser"] = form_data["spotUser"]
    data["widefind"]["subscribe_address"] = form_data["subscribe"]
    
    with open("config.json", "w") as jsonFile:
        json.dump(data, jsonFile)
        jsonFile.close()
    # if(variable == 'systemOn' and value == 'False'):
    #     fallSystemLock.notify()
    
    globalVariables.changedSettings = True
    return goFromkeyBoardPage()

@app.route('/sendCommandToD3/<command>', methods=['GET', 'POST'])
def sendCommandToD3(command): # Sends a chosen command to the robot then returns to the settings screen
    d3 = double.DRDoubleSDK()
    d3.sendCommand(command)
    return settings()

@app.route('/toggleSystemOnOff/', methods=['GET', 'POST'])
def toggleSystemOnOff(): # When a user presses the button the system is turned on or off
    print(globalVariables.systemOn)

    if(globalVariables.systemOn):
        fallSystemLock.acquire()
        globalVariables.systemOn = False
    else:
        fallSystemLock.release()
        globalVariables.systemOn = True

    return settings()
    
@app.route('/gotokeyBoardPage', methods=['GET', 'POST'])
def gotokeyBoardPage(): # Opens the keyboard input page with keyboard enabled
    d3 = double.DRDoubleSDK()
    link = "http://130.240.114.43:5000/keyBoardInput"
    d3.sendCommand('gui.accessoryWebView.open',{ "url": link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": True, "hidden": False })
    return keyBoardInput()

@app.route('/goFromkeyBoardPage', methods=['GET', 'POST'])
def goFromkeyBoardPage(): # Disables the keyboard and returns to settings
    d3 = double.DRDoubleSDK()
    link = "http://130.240.114.43:5000/settings"
    d3.sendCommand('gui.accessoryWebView.open',{ "url": link, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })
    return settings()

@app.route('/falseAlarm')
def falseAlarm(): # If a fall was a (fall)se alarm we notify and then drive home
    globalVariables.doNotifyLoop = False
    with open('config.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        username = data['user']['Name']
        address = data['user']['Address']
        d3name = data['user']['D3Name']
    sendMsg = 'FALSKT ALARM: ' + username + ', ' + address + ', meddelar att fallet var ett falsk alarm. D3Robot: ' + d3name
    notify.send(sendMsg)
    nav = navigate()
    nav.cancelNavigation()
    if(not nav.checkCharge()): # if the robot isn't already charging we drive home
        nav.driveHome()
    return index()

@app.route('/notifyOkWhenFall', methods=['GET', 'POST'])
def notifyOkWhenFall(): # If a user is okay after having fallen we notify and the robot stays put
    with open('config.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        username = data['user']['Name']
        address = data['user']['Address']
        d3name = data['user']['D3Name']
    sendMsg = 'MÅR BRA: ' + username + ', '+ address + ', meddelar att den mår bra. Anslut snarast för att kolla situationen. D3Robot: ' + d3name 
    notify.send(sendMsg)
    popUpMsg = 'Vådare meddelad att du mår bra. Vådare ansluter för att kolla läget snart'
    return render_template('fall.html', msg = popUpMsg)

@app.route('/notifyNotOkWhenFall', methods=['GET', 'POST'])
def notifyNotOkWhenFall(): # Is a user is not okay after having fallen we notify and the robot stays put
    with open('config.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        username = data['user']['Name']
        address = data['user']['Address']
        d3name = data['user']['D3Name']
    sendMsg = 'HJÄLP: ' + username + ', '+ address + ', meddelar att den INTE mår bra och behöver hjälp. Anslut omgående. D3Robot: ' + d3name
    notify.send(sendMsg)
    popUpMsg = 'Vådare meddelad att du behöver hjälp. Vådare ansluter snarast'
    return render_template('fall.html', msg = popUpMsg)

@app.route('/time')
def time(): # This function is used for the clock in the main menu
    def generate():
        return getTimezoneTime().strftime("%H:%M")
    return Response(generate(), mimetype='text') 

@app.route('/weekDay')
def weekDay(): # Is used for the clock in the main menu, displays the weekday
    def generate():
        weekDays = {"monday":"Måndag", "tuesday":"Tisdag", "wednesday":"Onsdag", "thursday":"Torsdag", "friday":"Fredag", "saterday":"Lördag", "sunday":"Söndag"} 
        currentWeekDay = getTimezoneTime().strftime("%A").lower()
        for key in weekDays.keys():
            currentWeekDay = currentWeekDay.replace(key, weekDays[key])
        return currentWeekDay
    return Response(generate(), mimetype='text') 

@app.route('/date')
def date(): # Displays the current date
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

def startServer(condition, g): # This starts the server, g and condition are our global variables and our mutex
    global fallSystemLock 
    fallSystemLock = condition
    global globalVariables 
    globalVariables = g
    global notify
    notify = Notify() # We set up our variables which the server will use
    print('Server started')
    app.run(host='0.0.0.0', debug=False)



if __name__ == '__main__':
    startServer()