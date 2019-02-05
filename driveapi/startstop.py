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

def start(roomIndex):
    rooms = {"1": "P505", "2": "P500", "3": "S401"}
    global processes
    processes = []
    today = datetime.date.today()
    global record
    record = "{0}-{1}-{2}-{3}-{4}".format(
        today.year, today.month, today.day, rooms[roomIndex], "HSE") + ".mp4"
    enc = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                    roomIndex + "1/main -y -c copy -f mp4 ~/vids/enc"
                    + record, shell=True, preexec_fn=os.setsid)
    processes.append(enc)

    # # cams *2 throw 401: unauthorized error in S401 and P500
    # cam = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
    #                        roomIndex + "2 -y -c:v copy -f mp4 .~/vids/cam"
    #                        + record, shell=True, preexec_fn=os.setsid)
    # processes.append(cam)

    for i in range(3, 7):
        process = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                    roomIndex + str(i) + " -y -c:v copy -f mp4 ~/vids/"
                    + str(i) + "-" + record, shell=True, preexec_fn=os.setsid)
        processes.append(process)
    # TODO: Add multiprocessing


def stop():
    try:
        for process in processes:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        time.sleep(1)
        get_sound(record)
        # for i in range(3, 7):
        #     add_sound("../../vids/" + str(i) + "-" + record, record)
        # upload('../../vids/' + record)
    except Exception:
        pass


def get_sound(record):
    os.system("ffmpeg -y -i ~/vids/enc" + record + " -vn ~/vids/sound" + record + ".mp3")


def add_sound(video_cam_num, audio_cam_num):
    os.system("ffmpeg -y -i " + video_cam_num + " -i ~/vids/sound" + audio_cam_num + ".mp3 " + video_cam_num)
