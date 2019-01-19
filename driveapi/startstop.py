import datetime
import subprocess
import os

from driveAPI.api import upload


def start(roomIndex):
    rooms = {"4": "513MIEM", "1": "P500", "3": "P500", "2": "S401"}
    global process
    today = datetime.date.today()
    global record
    record = "{0}-{1}-{2}-{3}-{4}".format(
        today.year, today.month, today.day, rooms[roomIndex], "HSE") + ".mp4"
    process = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                               roomIndex + "3 -c:v copy -an -f mp4 " + os.getcwd() + "\\" + record)


def stop():
    subprocess.Popen.kill(process)
    upload(record)
