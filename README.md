# Fally - a system using Widefinds UWB positioning as falldetection to drive a Double Robotics D3 robot
In health and homecare, people with cognitive and physical disabilities usally needs extensive supervision. This is where autonomous robots are very attractive as time and the possiblity to always be present is not always possible. If a fall or similar situation should arise and no other person is present except the fallen one, this could be a critical situation. A system that could detect this and similar scenarios is what the project is trying to solve.

<img src = "https://github.com/IsakLundstrom/D0020E_UWB_Nav_DR3/blob/main/webpage/static/images/Fally-logo.png?raw=true" width="700">

The project was given to us in the course 'Project in Computer Science and Engineering, D0020E', of Luleå Univerity of Technology. The task was to navigate a Double 3 Doublerobotics telepressence robot using the UWB-system developed by WideFind.

## Description
### Our system
The system is run by 3 threads, one for the server, one for falldetection and one for handling incoming calls to the robot. The server handles the GUI and communication between the GUI and the rest of the system. Falldetection is done with the Widefind tags and when a fall is detected it will start start navigation of the robot and a new thread for the notification process, sending repeated notifications in a time interval. To handle incoming calls a thread is always listening for incoming calls, when a fall is detected the thread will wait for the call to end and drive the robot back to the charging dock.

Description of a fall scenario.

1. Fallhandler detects a fall, start notify thread, navigation, and display the fall screen.
2. D3 robot navigates to target, wait for incoming call.
3. Carer connect to robot.
4. Session handler detects a call and turn on the speakers.
5. Carer leaves call.
6. Session handler detects that call has ended, drive robot back to charging dock and display.
drive home screen.
7. Session handler detects that robot is charging, deploy kickstand and display homescreen.

Note that the server does not change the displayed screen is this scenario. This is because  the server only handles the interaction between user and the GUI. If the fall in this scenario was false, the user would after point 2) click on the false alarm option and the server would drive the robot back to dock after that point 7) would be done. 

### Used subsytems

#### Double D3
The communication with the D3 robot is done through the double robotics [API](https://github.com/doublerobotics/d3-sdk/blob/master/docs/API.md).

Our system does not handle the navigation of the robot but instead calculating the coordinates for the destination, then the robot can navigate to the target on its own.

Telepresence communication is handled by the provided website from Double Robotics (länk?) 
, from there the robot can be controlled by the connected user. 

All code is currently hosted on the D3 robot itself but can be hosted on an external Linux machine. To read more about the robot visit [Double 3 Developer SDK](https://github.com/doublerobotics/d3-sdk).
#### Widefind
Widefind is a system which uses Ultra-wideband to send positional data. Ultra-wideband can do quick 
and wireless transfer of a lot of information over short distances.
Widefind has a hub and a positionanchor which it uses as referencepoints for its' coordinates.
The system has tags whose coordinates it tracks. In this system the user will wear a tag and the robot will have
a tag tied to it. Each tag has an id to identify it, this along with the time
are sent at the beginning of the widefind-message. The messages are written in JSON.

#### Notify.run
Notify.run is a package in python which lets you send notifications to your phone or desktop. 
To use it a user has to create a channel and subscribe to it with their devices. Each channel has its 
own HTTPS endpoint so if you POST a message to that endpoint all devices that are subscribed will get that messaged relayed to them.
In this project, notify.run is used to alert homecare personnel that the user has fallen and needs help.

#### GUI - Python Flask server

## Run and Installation
Fally runs on the D3 robot itself, but the system should work on any Linux machine (though this is not tested as of writing this). We used a SSH connection to reach the D3 robot from our computers and ran the system from there. 

To install and run the system: 
1. Fork the project and clone it down on the robot. 
2. Install the below noted libraries.
3. Run `python3 main.py` and the system should be active.

Fally was run on `Python 3.6.9`, and should work on later versions. The system uses `Flask`, `phao-mqtt`, `pytz` and to install these use `pip install`.

## Authors and acknowledgment
The project was created and worked on by Oskar Dahlbeck, Pehr Häggqvist, Isak Lundström and Hjalmar Olofsson Utsi. 
Our supervisor Kåre Synnes gave us the task and helped us with insights on meetings on a weekly basis.
Other acknowledgements goes to Nicklas Brynolf as his project 'name och länk' help us alot when starting this project and to the Doublerobotics support team as tey replied quickly about our questions on the Double D3s API.


## Project status
As for now the project is in a 
