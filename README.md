# Fally - a system using Widefinds UWB positioning as falldetection to drive a Double Robotics D3 robot
In health and homecare, people with cognitive and physical disabilities usally needs extensive supervision. This is where autonomous robots are very attractive as time and the possiblity to always be present is not always possible. If a fall or similar situation should arise and no other person is present except the fallen one, this could be a critical situation. A system that could detect this and similar scenarios is what the project is trying to solve.

<img src = "https://github.com/IsakLundstrom/D0020E_UWB_Nav_DR3/blob/main/webpage/static/images/Fally-logo.png?raw=true" width="700">

The project was given to us in the course 'Project in Computer Science and Engineering, D0020E', of Luleå Univerity of Technology. The task was to navigate a Double 3 Doublerobotics telepressence robot using the UWB-system developed by WideFind.

## Description
### Our system

### Used subssytems

#### Double D3

#### Widefind
Widefind is a system which uses Ultra-wideband to send positional data. Ultra-wideband can do quick 
and wireless transfer of a lot of information over short distances.
Widefind has a hub and a positionanchor which it uses as referencepoints for its' coordinates.
The system has tags whose coordinates it tracks. In this system the user will wear a tag and the robot will have
a tag tied to it. Each tag has an id to identify it, this along with the time
are sent at the beginning of the widefind-message. The messages are written in JSON.

#### Notify.run

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
Other acknowledgements goes to Nicklas Brynolf as his project '


## Project status
