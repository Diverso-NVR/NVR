import datetime
import os
import signal
import subprocess
from pathlib import Path
from threading import RLock, Lock

import requests
from driveAPI.driveSettings import upload
from flask import jsonify

tracking_url = '172.18.198.31:5000/tracking'
home = str(Path.home())
lock = RLock()
lock_merge = Lock()
rooms = {}
processes = {}
records = {}


def config(id: int, name: str, sources: list) -> None:
    rooms[id] = {
        "name": name}

    processes[id] = []

    today = datetime.date.today()
    curr_time = datetime.datetime.now().time()

    hour = "0" + \
        str(curr_time.hour) if curr_time.hour < 10 else str(curr_time.hour)
    minute = "0" + \
        str(curr_time.minute) if curr_time.minute < 10 else str(curr_time.minute)
    records[id] = f"{today.year}-{today.month}-{today.day}_{hour}:{minute}_{rooms[id]['name']}_"

    rooms[id]['sound'] = {'cam': [], 'enc': []}
    rooms[id]['vid'] = []
    for cam in sources:
        rooms[id]['vid'].append(cam['ip'])
        if cam['sound']:
            rooms[id
                  ]['sound'][cam['sound']].append(cam['ip'])
        if cam['mainCam']:
            rooms[id
                  ]['mainCam'] = cam['ip']
        if cam['tracking']:
            rooms[id
                  ]['tracking'] = cam['ip']


# TODO do smth with rtsp protocols'
def start(id: int, name: str, sound_type: str, sources: list) -> None:

    config(id, name, sources)

    if sound_type == "enc":
        enc = subprocess.Popen("ffmpeg -rtsp_transport http -i rtsp://" +
                               rooms[id]['sound']['enc'][0] +
                               " -y -c:a copy -vn -f mp4 " + home + "/vids/sound_"
                               + records[id] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[id].append(enc)
    else:
        camera = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://" +
                                  rooms[id]['sound']['cam'][0] +
                                  " -y -c:a copy -vn -f mp4 " + home + "/vids/sound_"
                                  + records[id] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[id].append(camera)

    for cam in rooms[id]['vid']:
        process = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://" +
                                   cam + " -y -c:v copy -an -f mp4 " + home + "/vids/vid_" +
                                   records[id] + cam.split('/')[0].split('.')[-1] + ".mp4", shell=True,
                                   preexec_fn=os.setsid)
        processes[id].append(process)


def kill_records(id):
    for process in processes[id]:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except OSError:
            os.system("sudo kill %s" % (process.pid))  # sudo for server


def stop(id: int, url: str, calendarId: str = None, eventId: str = None) -> None:

    kill_records(id)

    requests.post(url, json={
        "screen_num": records[id] +
        rooms[id]['sound']['enc'][0].split('/')[0].split('.')[-1],
        "video_cam_num": records[id] +
        rooms[id]['mainCam'].split('/')[0].split('.')[-1],
        "record_num": records[id],
        "room_name": rooms[id]['name']
    })

    with lock:
        res = ""
        if os.path.exists(home + "/vids/sound_" + records[id] + ".aac"):
            for cam in rooms[id]['vid']:
                add_sound(records[id] +
                          cam.split('/')[0].split('.')[-1], records[id])
        else:
            res = "vid_"

        files = []
        for cam in rooms[id]['vid']:
            try:
                print(home + "/vids/" + res + records[id]
                      + cam.split('/')[0].split('.')[-1] + ".mp4", 'upload started')
                fileId = upload(home + "/vids/" + res + records[id]
                                + cam.split('/')[0].split('.')[-1] + ".mp4",
                                rooms[id]["name"])
                print(home + "/vids/" + res + records[id]
                      + cam.split('/')[0].split('.')[-1] + ".mp4", 'upload ended')
                files.append(fileId)
            except Exception as e:
                print(e)

        # TODO fix [SSL: WRONG_VERSION_NUMBER]
        # if calendarId:
        #    for fileId in files:
        #        try:
        #            add_attachment(calendarId, eventId, fileId)
        #        except Exception as e:
        #            print(e)


def add_sound(video_cam_num: str, audio_cam_num: str) -> None:
    proc = subprocess.Popen(["ffmpeg", "-i", home + "/vids/sound_" + audio_cam_num + ".aac", "-i",
                             home + "/vids/vid_" + video_cam_num +
                             ".mp4", "-y", "-shortest", "-c", "copy",
                             home + "/vids/" + video_cam_num + ".mp4"], shell=False)
    proc.wait()
