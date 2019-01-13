import datetime
import json
import subprocess
import sys
from tkinter import Button, Tk

from API import upload

root = Tk()
path = "D:\\recorder\\room.json"
with open(path, 'r') as f:
    data = json.loads(f.read())
    campus = data["campus"]
    room = data["auditorium"]
cameraIndex = "2"


def start():
    global process
    today = datetime.date.today()
    global record
    record = "{0}-{1}-{2}-{3}-{4}".format(
        today.day, today.month, today.year, room, campus) + ".mp4"
    process = subprocess.Popen("ffmpeg -i rtsp://192.168.11." + cameraIndex +
                               "5 -c copy -f mp4  D:\\recorder\\driveAPI\\" + record)


def stop():
    subprocess.Popen.kill(process)
    upload(record)
    sys.exit()


startButton = Button(root, text="Старт", command=start)
startButton.place(x=20, y=20)

stopButton = Button(root, text="Стоп", command=stop)
stopButton.place(x=70, y=20)

root.mainloop()
