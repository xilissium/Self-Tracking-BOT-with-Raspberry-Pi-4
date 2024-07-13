# Self-Tracking-BOT-with-Raspberry-Pi-4
all the necessary programs to make an autonomous robot using raspberry pi 4 and mbot2 platform, for tracking people


## Requirements
### Software
- Python 3.6+
- Flask
- pyserial
- opencv-python
- numpy
- flask-cors
- yolov3-tiny package
### Hardware
- Raspberry pi 4 (or similare board with enough compute power for video recognition)
- Mbot2 (with ultrasonic sensor and 2 motor), if you want to use an arduino you need to do the programe yourself
- Generic camera/ webcam (i use the playstation 3 eyes camera)

## Installation
clone the git in the folder of your choice, installe all the necesary librarys and uplaod the arduino (Mbot.ino) on the board and run the BOB.py
### for python libraries:
- pip install Flask pyserial opencv-python numpy flask-cors

### for the yoloV3 
- wget https://pjreddie.com/media/files/yolov3-tiny.weights
- wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg
- wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names

###
make sure to have all of the yolo file in the same folder as the python scripte
and for arduino you will need the mcore librairies

## Use
to use this programe you will need to edit the BOB.py script to set your serial port, serial baudrate and camera number
after that juste launch it.
###
you need to have all files in the same path as here.
###
- yourrepository/
- │
- ├── static/
- │   └── photos/(all arrown)
- ├── templates/
- │   └── index.html
- ├── Mbot.ino
- ├── BOB.py
- ├── yolov3-tiny
- ├── yolov3-tiny.weights
- ├── coco.names
- └── README.md
## USAGE
- After starting the Python script, open your web browser and navigate to http://0.0.0.0:5000 or use the IP address of your device followed by port 5000 (x.x.x.x:5000).
- The web interface will display the video feed from your camera.
- Use the controls on the web page to interact with the robot.
- Note: Disable person recognition system when no one is present to avoid unnecessary FPS drops.
###
take note that you can controle the bot with keyboard but its curently made for azerty key board (so z,q,s,d to controle it)
feel free to edit the code for other keyboard layout.
