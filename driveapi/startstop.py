import datetime
import subprocess
import os
import signal
import psutil
import time

from driveapi.driveSettings import upload

"""
    P505: 11 12 13 14
    P500: 21 22 23 24 25 26
    S401: 31 32 33 34
"""
rooms = {"1": "P505", "2": "P500", "3": "S401"}
processes = {}
records = {}


def start(roomIndex, soundType):
    processes[roomIndex] = []
    today = datetime.date.today()
    currTime = datetime.datetime.now().time()
    formattedTime = str(currTime.hour) + ':' + str(currTime.minute)
    records[roomIndex] = "{0}-{1}-{2}-{3}-{4}-{5}".format(
        today.year, today.month, today.day, formattedTime,rooms[roomIndex], "HSE")
    if soundType == "enc":
        enc = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                               roomIndex + "1/main -y -c:a copy -vn -f mp4 ../vids/sound-source-"
                               + records[roomIndex] + ".mp3", shell=True, preexec_fn=os.setsid)
        processes[roomIndex].append(enc)
    else:
        # cams *2 throw 401: unauthorized error in S401 and P500
        cam = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                               roomIndex + "2 -y -c:a copy -vn -f mp4 ../vids/sound-source-"
                               + records[roomIndex] + ".mp3", shell=True, preexec_fn=os.setsid)
        processes[roomIndex].append(cam)

    proc = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                               roomIndex + "1/main -y -c copy -f mp4 ../vids/1-" +
                            records[roomIndex] + ".mp4", shell=True, preexec_fn=os.setsid)
    processes[roomIndex].append(proc)
    for i in range(2, 7):
        process = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                                   roomIndex + str(i) + " -y -c:v copy -an -f mp4 ../vids/"
                                   + str(i) + "-" + records[roomIndex] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[roomIndex].append(process)


def kill(process):
    os.kill(os.getpgid(process.pid), signal.SIGTERM)
    while True:
        if int(process.pid) not in psutil.pids():
            return


def stop(roomIndex):
    for process in processes[roomIndex]:
        kill(process)
    for i in range(1, 7):
        add_sound(str(i) + "-" + records[roomIndex], records[roomIndex])
    # for i in range(1, 7):
    #     try:
    #         upload('../vids/result-' + str(i) + "-" + records[roomIndex] + ".mp4", roomIndex)
    #     except Exception:
    #         pass



def add_sound(video_cam_num, audio_cam_num):
    proc = subprocess.Popen(
            "ffmpeg -i ../vids/sound-source-" + audio_cam_num + ".mp3 "
            + "-i ../vids/" + video_cam_num + ".mp4" + " -shortest ../vids/result-" + video_cam_num + ".mp4"
            , shell=True, preexec_fn=os.setsid)
