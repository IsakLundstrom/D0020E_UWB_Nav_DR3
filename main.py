import threading
from webpage.server import startServer
from fallHandler import FallHandler
from sessionHandler import SessionHandler
from globalVariables import GlobalVariables
from webpage.changeConfig import ChangeConfig
import time


if __name__ == '__main__':
    globalVariables = GlobalVariables() # Here we set up objects and threads for the program
    fallSystemLock = threading.Lock()
    system = FallHandler(fallSystemLock, globalVariables)
    session = SessionHandler(globalVariables)
    serverThread = threading.Thread(target=startServer, args=(fallSystemLock, globalVariables))
    systemThread = threading.Thread(target=system.startSystem)
    sessionThread = threading.Thread(target=session.listen)
    serverThread.start()
    systemThread.start()
    sessionThread.start() # all threads start
    print(threading.active_count())
    while(1): # every ten seconds we print how many active threads we have
        time.sleep(10)
        print('Nr of threads alive:', threading.active_count())