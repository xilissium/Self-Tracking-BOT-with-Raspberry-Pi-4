# Self-Tracking-BOT-with-Raspberry-Pi-4
all the necessary programs to make an autonomous robot using raspberry pi 4 and mbot2 platform, for tracking people


## Requirements

- Python 3.6+
- Flask
- pyserial
- opencv-python
- numpy
- flask-cors
- yolov3-tiny package

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
to use this programe you will need to edit the BOB.py script to set your serialport, serial baudrate and camera number
after that juste launch it.
###
you need to have all files in the same path as here.
###
yourrepository/
- │
- ├── static/
- │   └── photos/
- ├── templates/
- │   └── index.html
- ├── Mbot.ino
- ├── BOB.py
- └── README.md
