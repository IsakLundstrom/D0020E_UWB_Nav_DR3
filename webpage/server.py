# To start server fo into website folder and to start run: python3 server.py
from flask import Flask, render_template, request
import os
from webpage.changeConfig import ChangeConfig


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

def startServer(changeConfig):
    changeConfig = changeConfig
    print('Server started')
    app.run(host='0.0.0.0', debug=False)


if __name__ == '__main__':
    startServer()