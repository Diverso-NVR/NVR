import datetime
import subprocess
import os
import time
import multiprocessing
import signal

from driveapi.driveSettings import upload

def start(roomIndex):
    rooms = {"1": "P505", "2": "P500", "3": "S401", "4": "513MIEM"}
    global process
    today = datetime.date.today()
    global record
    record = "{0}-{1}-{2}-{3}-{4}".format(
        today.year, today.month, today.day, rooms[roomIndex], "HSE") + ".mp4"
    process = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                    roomIndex + "3 -y -c:v copy -f mp4 " + os.getcwd() + "/" + record, shell=True, preexec_fn=os.setsid)


# def start(roomIndex):
#     global proc
#     proc = multiprocessing.Process(target=startProcess, args=(roomIndex,))
#     proc.start()


def stop():
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    upload(record)
