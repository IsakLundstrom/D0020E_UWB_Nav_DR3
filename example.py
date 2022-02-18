import double
import sys
from navigate import navigate
# from tkinter import *
# from tkinter import ttk
d3 = double.DRDoubleSDK()
# nav = navigate(0,0)
link3 = "http://130.240.114.43:5000/"
#öppna porten i den map index.html finns med: python3 -m http.server 8000 
#nav.navigation(5,5)

# d3.sendCommand('gui.enable', { "standbyUrl": link2, "debug": True })
# d3.sendCommand('gui.accessoryWebView.open',{ "url": link3, "trusted": True, "transparent": False, "backgroundColor": "#FFF", "keyboard": False, "hidden": False })
d3.sendCommand('gui.accessoryWebView.close')
# nav.driveHome()
# # d3.sendCommand('navigate.target', {'x':float(1),'y':float(1),'relative':False,'dock':False,'dockId':0})            


# root = Tk()
# frm = ttk.Frame(root, padding=10)
# frm.grid()
# ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
# root.mainloop()

""" from tkinter import *
from tkinter import ttk
import sys
import os

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')


#create main window
master = Tk()
master.title("tester")
master.geometry("300x100")


#make a label for the window
label1 = Label(master, text='Hellooooo')
# Lay out label
label1.pack()

# Run forever!
master.mainloop() """