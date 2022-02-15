import threading
from webpage.server import startServer
from systemHandler import SystemHandler
from sessionHandler import SessionHandler
from webpage.changeConfig import ChangeConfig
import time


if __name__ == '__main__':
    condition = threading.RLock(blocking = True)
    system = SystemHandler(condition)
    session = SessionHandler()
    serverThread = threading.Thread(target=startServer, args=(condition,))
    systemThread = threading.Thread(target=system.startSystem)
    sessionThread = threading.Thread(target=session.listen)
    serverThread.start()
    systemThread.start()
    sessionThread.start()
    print(threading.active_count())
    while(1):
        time.sleep(5)
        print(threading.active_count())