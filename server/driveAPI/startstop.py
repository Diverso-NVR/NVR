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
    # try:
    #     req = {
    #         'command': 'start',
    #         'ip': rooms[id]['tracking'][0],
    #         'port': '80'
    #     }
    #     response = requests.post(tracking_url, json=req)
    # except:
    #     pass

    config(id, name, sources)

    processes[id] = []
    today = datetime.date.today()
    curr_time = datetime.datetime.now().time()

    hour = "0" + str(curr_time.hour) if curr_time.hour < 10 else str(curr_time.hour)
    minute = "0" + str(curr_time.minute) if curr_time.minute < 10 else str(curr_time.minute)
    records[id] = "{}-{}-{}_{}:{}_{}_".format(
        today.year, today.month, today.day, hour, minute, rooms[id]["name"])

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
    # with lock:
    #     try:
    #         req = {
    #             'command': 'stop',
    #             'ip': rooms[id]['tracking'][0],
    #             'port': '80'
    #         }
    #         response = requests.post(tracking_url, json=req)
    #     except:
    #         pass

    kill_records(id)

    # t = Thread(target=merge, args=(id), daemon=True)
    # t.start()

    requests.post(url, json=jsonify(
        screen_num=records[id] + rooms[id]['sound']['enc'][0].split('/')[0].split('.')[-1],
        video_cam_num=records[id] + rooms[id]['mainCam'].split('/')[0].split('.')[-1],
        record_num=records[id],
        room_name=rooms[id]['name']
    ))

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


def merge(id: int) -> None:
    merge_video(records[id]
                + rooms[id]['sound']['enc'][0].split('/')[0].split('.')[-1],
                records[id] +
                rooms[id]['mainCam'].split(
                    '/')[0].split('.')[-1],
                records[id])

    res = ""
    if os.path.exists(home + "/vids/sound_" + records[id] + ".aac"):
        add_sound(records[id] +
                  "merged_2", records[id])
    else:
        res = "vid_"

    try:
        upload(home + "/vids/" + res + records[id] + "merged_2.mp4",
               rooms[id]["name"])
    except Exception:
        pass


def merge_video(screen_num: str, video_cam_num: str, record_num: str) -> None:
    lock_merge.acquire()

    mid1 = subprocess.Popen(
        ["ffmpeg", "-i", home + "/vids/vid_" + screen_num + ".mp4", "-s", "hd720",
         home + "/vids/" + record_num + "mid_1_1.mp4"], shell=False)
    os.system("renice -n 20 %s" % (mid1.pid,))
    mid1.wait()

    mid2 = subprocess.Popen(
        ["ffmpeg", "-i", home + "/vids/vid_" + video_cam_num + ".mp4", "-s", "hd720",
         home + "/vids/" + record_num + "mid_1_3.mp4"], shell=False)
    os.system("renice -n 20 %s" % (mid2.pid,))
    mid2.wait()

    crop1 = subprocess.Popen(
        ["ffmpeg", "-i", home + "/vids/" + record_num + "mid_1_3.mp4", "-filter:v", "crop=640:720:40:0",
         home + "/vids/" + record_num + "cropped_1.mp4"], shell=False)
    os.system("renice -n 20 %s" % (crop1.pid,))
    crop1.wait()

    second = subprocess.Popen(
        ["ffmpeg", "-i", home + "/vids/" + record_num + "cropped_1.mp4", "-i", home + "/vids/" +
         record_num + "mid_1_1.mp4", "-filter_complex", "hstack=inputs=2", home + "/vids/vid_" +
         record_num + "merged_2.mp4"], shell=False)
    os.system("renice -n 20 %s" % (second.pid,))
    second.wait()

    lock_merge.release()
