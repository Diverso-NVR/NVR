import datetime
import subprocess
import os
import signal
import time

from driveapi.driveSettings import upload

def start(roomIndex):
    rooms = {"1": "P505", "2": "P500", "3": "S401"}
    global process
    today = datetime.date.today()
    global record
    record = "{0}-{1}-{2}-{3}-{4}".format(
        today.year, today.month, today.day, rooms[roomIndex], "HSE") + ".mp4"
    process = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                    roomIndex + "3 -y -c:v copy -f mp4 " + "../vids/" + record, shell=True, preexec_fn=os.setsid)
    # TODO: Add multiprocessing


def stop():
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        time.sleep(1)
        upload('../vids/' + record)
    except Exception:
        pass

# TODO: Synchronization
# def get_sound(cam_num):
#     os.system('ffmpeg -i c:/temp/record' + str(cam_num) + '.mp4 -vn c:/temp/record_sound' + str(cam_num) + '.mp3')
#
#
# def add_sound(video_cam_num, audio_cam_num):
#     os.system('ffmpeg -i c:/temp/record' + str(video_cam_num) + '.mp4 -i c:/temp/record_sound' + str(
#         audio_cam_num) + '.mp3 c:/temp/record_full' + str(video_cam_num) + '.mp4')
#