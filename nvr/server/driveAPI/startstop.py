import datetime
import os
import signal
import subprocess
from pathlib import Path
from threading import RLock, Thread
from nvrAPI.models import nvr_db_context, Room
import requests
from driveAPI.driveSettings import upload
from calendarAPI.calendarSettings import add_attachment

TRACKING_URL = "http://217.73.60.64:5000/track"
home = str(Path.home())
MERGE_SERVER_URL = os.environ.get('MERGE_SERVER_URL')
BASE_URL = os.environ.get('BASE_URL')
lock = RLock()
rooms = {}
processes = {}
record_names = {}


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
    record_names[room_id] = f"{today.year}-{today.month}-{today.day}_{hour}:{minute}_{rooms[room_id]['name']}_"

    rooms[room_id]['sound'] = {'cam': [], 'enc': []}
    rooms[room_id]['vid'] = []
    for cam in sources:
        rooms[room_id]['vid'].append(cam['ip'])
        if cam['sound']:
            rooms[room_id
                  ]['sound'][cam['sound']].append(cam['ip'])
        if cam['main_cam']:
            rooms[room_id
                  ]['main_cam'] = cam['ip']
        if cam['tracking']:
            rooms[room_id
                  ]['tracking'] = cam['ip']


# TODO: do smth with rtsp protocols
@nvr_db_context
def start(room_id: int) -> None:

    room = Room.query.get(room_id)
    config(room.id, room.name, [source.to_dict()
                                for source in room.sources])

    try:
        requests.post(TRACKING_URL, json={'ip': rooms[room_id]['tracking'].split('@')[-1]})
    except Exception as e:
        print(e)
   

    if room.chosen_sound == "enc":
        enc = subprocess.Popen("ffmpeg -rtsp_transport http -i rtsp://" +
                               rooms[room_id]['sound']['enc'][0] +
                               " -y -c:a copy -vn -f mp4 " + home + "/vids/sound_"
                               + record_names[room_id] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[room_id].append(enc)
    else:
        camera = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://" +
                                  rooms[room_id]['sound']['cam'][0] +
                                  " -y -c:a copy -vn -f mp4 " + home + "/vids/sound_"
                                  + record_names[room_id] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[room_id].append(camera)

    for cam in rooms[room_id]['vid']:
        process = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://" +
                                   cam + " -y -c:v copy -an -f mp4 " + home + "/vids/vid_" +
                                   record_names[room_id] + cam.split('/')[0].split('.')[-1] + ".mp4", shell=True,
                                   preexec_fn=os.setsid)
        processes[room_id].append(process)


@nvr_db_context
def stop(room_id: int, calendar_id: str = None, event_id: str = None) -> None:

    kill_records(room_id)

    try:
        requests.delete(TRACKING_URL)
    except Exception as e:
        print(e)

    screen_num = record_names[room_id] + \
        rooms[room_id]['sound']['enc'][0].split('/')[0].split('.')[-1]
    cam_num = record_names[room_id] + \
        rooms[room_id]['main_cam'].split('/')[0].split('.')[-1]
    record_name = record_names[room_id]

    try:
        requests.post(MERGE_SERVER_URL,
                      json={
                          'url': BASE_URL,
                          "screen_num": screen_num,
                          "cam_num": cam_num,
                          "record_name": record_name,
                          "room_id": room_id,
                          "calendar_id": calendar_id,
                          "event_id": event_id
                      },
                      headers={'content-type': 'application/json'})
    except Exception as e:
        print(e)

    room = Room.query.get(room_id)

    Thread(target=sync_and_upload, args=(
        room_id, record_name, rooms[room_id]['vid'], room.drive.split('/')[-1])).start()


def kill_records(room_id: int) -> None:
    for process in processes[room_id]:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except OSError:
            os.system("kill %s" % (process.pid))  # sudo for server


def sync_and_upload(room_id: int, record_name: str, room_sources: list, folder_id: str) -> None:
    with lock:
        res = ""
        if os.path.exists(f'{home}/vids/sound_{record_name}.aac'):
            for cam in room_sources:
                add_sound(record_name,
                          cam.split('/')[0].split('.')[-1])
        else:
            res = "vid_"

        for cam in room_sources:
            try:
                upload(home + "/vids/" + res + record_name
                       + cam.split('/')[0].split('.')[-1] + ".mp4",
                       folder_id)
            except:
                pass


def add_sound(record_name: str, source_id: str) -> None:
    proc = subprocess.Popen(["ffmpeg", "-i", home + "/vids/sound_" + record_name + ".aac", "-i",
                             home + "/vids/vid_" + record_name + source_id +
                             ".mp4", "-y", "-shortest", "-c", "copy",
                             home + "/vids/" + record_name + source_id + ".mp4"], shell=False)
    proc.wait()


def upload_file(file_name: str, folder_id: str, calendar_id: str, event_id: str) -> None:
    try:
        file_id = upload(home + "/vids/" + file_name,
                         folder_id)
    except:
        pass

    if calendar_id:
        try:
            add_attachment(calendar_id, event_id, file_id)
        except:
            pass
