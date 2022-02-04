import threading
from webpage.server import startServer
from systemHandler import SystemHandler
from webpage.changeConfig import ChangeConfig
import time

if __name__ == '__main__':
    changeConfig = ChangeConfig()
    system = SystemHandler()
    serverThread = threading.Thread(target=startServer, args=(changeConfig, ))
    systemThread = threading.Thread(target=system.startSystem)
    serverThread.start()
    systemThread.start()
    print(threading.active_count())
    while(1):
        time.sleep(1)
        print(threading.active_count())