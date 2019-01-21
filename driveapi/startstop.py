import datetime
from subprocess import Popen
import os

from driveapi.driveSettings import upload

def start(roomIndex):
    rooms = {"1": "P505", "2": "P500", "3": "S401", "4": "513MIEM"}
    global process
    today = datetime.date.today()
    global record
    record = "{0}-{1}-{2}-{3}-{4}".format(
        today.year, today.month, today.day, rooms[roomIndex], "HSE") + ".mp4"
    process = Popen("ffmpeg -i rtsp://192.168.11." +
                    roomIndex + "5 -y -c:v copy -an -f mp4 " + os.getcwd() + "\\" + record)

def stop():
    Popen.kill(process)
    upload(record)
