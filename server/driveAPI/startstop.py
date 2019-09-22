import datetime
import os
import signal
import subprocess
from pathlib import Path
from threading import RLock

import requests
from driveAPI.driveSettings import upload
from calendarAPI.calendarSettings import add_attachment

tracking_url = 'http://172.18.198.31:5000/tracking'
home = str(Path.home())
merge_url = os.environ.get('MERGE_SERVER_URL')
lock = RLock()
rooms = {}
processes = {}
records = {}


def config(room_id: int, name: str, sources: list) -> None:
    rooms[room_id] = {
        "name": name}

    processes[room_id] = []

    today = datetime.date.today()
    curr_time = datetime.datetime.now().time()

    hour = "0" + \
        str(curr_time.hour) if curr_time.hour < 10 else str(curr_time.hour)
    minute = "0" + \
        str(curr_time.minute) if curr_time.minute < 10 else str(curr_time.minute)
    records[room_id] = f"{today.year}-{today.month}-{today.day}_{hour}:{minute}_{rooms[room_id]['name']}_"

    rooms[room_id]['sound'] = {'cam': [], 'enc': []}
    rooms[room_id]['vid'] = []
    for cam in sources:
        rooms[room_id]['vid'].append(cam['ip'])
        if cam['sound']:
            rooms[room_id
                  ]['sound'][cam['sound']].append(cam['ip'])
        if cam['mainCam']:
            rooms[room_id
                  ]['mainCam'] = cam['ip']
        if cam['tracking']:
            rooms[room_id
                  ]['tracking'] = cam['ip']


# TODO do smth with rtsp protocols'
def start(room_id: int, name: str, sound_type: str, sources: list) -> None:

    config(room_id, name, sources)

    if sound_type == "enc":
        enc = subprocess.Popen("ffmpeg -rtsp_transport http -i rtsp://" +
                               rooms[room_id]['sound']['enc'][0] +
                               " -y -c:a copy -vn -f mp4 " + home + "/vids/sound_"
                               + records[room_id] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[room_id].append(enc)
    else:
        camera = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://" +
                                  rooms[room_id]['sound']['cam'][0] +
                                  " -y -c:a copy -vn -f mp4 " + home + "/vids/sound_"
                                  + records[room_id] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[room_id].append(camera)

    for cam in rooms[room_id]['vid']:
        process = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://" +
                                   cam + " -y -c:v copy -an -f mp4 " + home + "/vids/vid_" +
                                   records[room_id] + cam.split('/')[0].split('.')[-1] + ".mp4", shell=True,
                                   preexec_fn=os.setsid)
        processes[room_id].append(process)


def kill_records(room_id):
    for process in processes[room_id]:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except OSError:
            os.system("sudo kill %s" % (process.pid))  # sudo for server


def stop(room_id: int, calendar_id: str = None, event_id: str = None) -> None:

    kill_records(room_id)

    # requests.post(merge_url,
    #               json={
    #                   "screen_num": records[room_id] +
    #                   rooms[room_id]['sound']['enc'][0].split(
    #                       '/')[0].split('.')[-1],
    #                   "video_cam_num": records[room_id] +
    #                   rooms[room_id]['mainCam'].split('/')[0].split('.')[-1],
    #                   "record_num": records[room_id],
    #                   "room_name": rooms[room_id]['name'],
    #                   "calendar_id": calendar_id,
    #                   "event_id": event_id
    #               },
    #               headers={'content-type': 'application/json'})

    with lock:
        res = ""
        if os.path.exists(f'{home}/vids/sound_{records[room_id]}.aac'):
            for cam in rooms[room_id]['vid']:
                add_sound(records[room_id] +
                          cam.split('/')[0].split('.')[-1], records[room_id])
        else:
            res = "vid_"

        for cam in rooms[room_id]['vid']:
            try:
                upload(home + "/vids/" + res + records[room_id]
                       + cam.split('/')[0].split('.')[-1] + ".mp4",
                       rooms[room_id]["name"])
            except Exception as e:
                print(e)


def add_sound(video_cam_num: str, audio_cam_num: str) -> None:
    proc = subprocess.Popen(["ffmpeg", "-i", home + "/vids/sound_" + audio_cam_num + ".aac", "-i",
                             home + "/vids/vid_" + video_cam_num +
                             ".mp4", "-y", "-shortest", "-c", "copy",
                             home + "/vids/" + video_cam_num + ".mp4"], shell=False)
    proc.wait()


def upload_file(file_name: str, room_name: str, calendar_id: str, event_id: str):
    try:
        file_id = upload(home + "/vids/" + file_name,
                         room_name)
    except Exception as e:
        print(e)

    if calendar_id:
        try:
            add_attachment(calendar_id, event_id, file_id)
        except Exception as e:
            print(e)
