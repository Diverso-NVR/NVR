import datetime
import subprocess
import os
import signal
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


def start(room_index, sound):
    processes[room_index] = []
    today = datetime.date.today()
    records[room_index] = "{0}-{1}-{2}-{3}-{4}".format(
        today.year, today.month, today.day, rooms[room_index], "HSE")
    if sound == "enc":
        enc = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                               room_index + "1/main -y -c copy -f mp4 ~/vids/snd-"
                               + records[room_index] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[room_index].append(enc)
    else:
        # cams *2 throw 401: unauthorized error in S401 and P500
        cam = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                               room_index + "2 -y -c:v copy -f mp4 .~/vids/snd-"
                               + records[room_index] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[room_index].append(cam)

    for i in range(3, 7):
        process = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                                   room_index + str(i) + " -y -c:v copy -f mp4 ~/vids/"
                                   + str(i) + "-" + records[room_index] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[room_index].append(process)


def stop(roomIndex):
    try:
        for process in processes[roomIndex]:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        get_sound(records[roomIndex])
        for i in range(3, 7):
            add_sound(str(i) + "-" + records[roomIndex], records[roomIndex])
        for i in range(3, 7):
            upload('../../vids/result-' + str(i) + "-" + records[roomIndex] + ".mp4")
    except Exception:
        pass


def get_sound(record):
    os.system("ffmpeg -y -i ~/vids/snd-" + record + ".mp4" + " -vn ~/vids/sound" + record + ".mp3")


def add_sound(video_cam_num, audio_cam_num):
    os.system(
        "ffmpeg -y -i ../../vids/" + video_cam_num + ".mp4" + " -i ../../vids/sound" + audio_cam_num
        + ".mp3 " + "../../vids/result-" + video_cam_num + ".mp4")
