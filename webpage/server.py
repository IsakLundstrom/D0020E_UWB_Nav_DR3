# To start server fo into website folder and to start run: python3 server.py
from flask import Flask, Response, render_template, request
import os
from webpage.changeConfig import ChangeConfig
from datetime import datetime
from notify_run import Notify 
from navigate import navigate

changeConfig = None
app = Flask(__name__)

@app.route('/')
def index():
    # os.system('python3 test.py')
    return render_template('index.html')

@app.route('/link', methods=['GET', 'POST'])
def link():
    changeConfig.changeAlertGap(11)
    if request.method == 'POST':
        print ('POST link')
        return render_template('link.html')
    else:
        print("GET link")
        return render_template('link.html')

@app.route('/help', methods=['GET', 'POST'])
def sendMsg():
    pass

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/drive', methods=['GET'])
def drive():
    return render_template('drive.html')

@app.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html')


@app.route('/notify/<msg>', methods=['GET', 'POST'])
def notify(msg):
    print('%s' % msg)
    notify = Notify()
    notify.send('%s' % msg)
    return render_template('index.html')

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

def startServer(changeConfig):
    changeConfig = changeConfig
    # notify = notifier
    print('Server started')
    # app.run(debug=False)
    app.run(host='0.0.0.0', debug=False)



if __name__ == '__main__':
    startServer()