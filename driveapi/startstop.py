import datetime
import subprocess
import signal
import os
import json
from threading import Thread, RLock
import requests

from driveapi.driveSettings import upload

with open("app/data.json", 'r') as f:
    data = json.loads(f.read())

tracking_url = '172.18.198.31:5000/tracking'
lock = RLock()

rooms = {}
processes = {}
records = {}
for building in data:
    rooms[building] = {}
    processes[building] = {}
    records[building] = {}
    for room in data[building]:
        rooms[building][str(room['id'])] = {"auditorium": room['auditorium']}
        rooms[building][str(room['id'])]['sound'] = room["sound"]
        rooms[building][str(room['id'])]['vid'] = room["vid"]
        rooms[building][str(room['id'])]['mainCam'] = room["mainCam"]
        rooms[building][str(room['id'])]['tracking'] = room["tracking"]


# TODO do smth with rtsp protocols'
def start(room_index, sound_type, building):
    # try:
    #     req = {
    #         'command': 'start',
    #         'ip': rooms[building][room_index]['tracking'][0],
    #         'port': '80'
    #     }
    #     response = requests.post(tracking_url, json=req)
    # except Exception:
    #     pass

    processes[building][room_index] = []
    today = datetime.date.today()
    curr_time = datetime.datetime.now().time()

    hour = "0" + \
        str(curr_time.hour) if curr_time.hour < 10 else str(curr_time.hour)
    minute = "0" + \
        str(curr_time.minute) if curr_time.minute < 10 else str(curr_time.minute)
    records[building][room_index] = "{}-{}-{}_{}:{}_{}_".format(
        today.year, today.month, today.day, hour, minute, rooms[building][room_index]["auditorium"])

    # if rooms[building][room_index]['auditorium'] == 'Техношоу-пресс-комната':
    #     proc = subprocess.Popen(
    #         "ffmpeg -rtsp_transport tcp -i rtsp://172.18.200.50/live/av0 -y -c copy ../vids/" +
    #         records[building][room_index] + ".mp4",
    #         shell=True, preexec_fn=os.setsid)

    if sound_type == "enc":
        enc = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://" +
                               rooms[building][room_index]['sound']['enc'][0] +
                               " -y -c:a copy -vn -f mp4 ../vids/sound_"
                               + records[building][room_index] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(enc)
    else:
        camera = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://" +
                                  rooms[building][room_index]['sound']['cam'][0] +
                                  " -y -c:a copy -vn -f mp4 ../vids/sound_"
                                  + records[building][room_index] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(camera)

    for cam in rooms[building][room_index]['vid']:
        process = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://" +
                                   cam + " -y -c:v copy -an -f mp4 ../vids/vid_" +
                                   records[building][room_index] + cam.split('/')[0].split('.')[-1] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(process)


def stop(room_index, building):
    # with lock:
    #     try:
    #         req = {
    #             'command': 'stop',
    #             'ip': rooms[building][room_index]['tracking'][0],
    #             'port': '80'
    #         }
    #         response = requests.post(tracking_url, json=req)
    #     except Exception:
    #         pass

    for process in processes[building][room_index]:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except OSError:
            os.system("sudo kill %s" % (process.pid))

    # t = Thread(target=merge, args=(room_index, building), daemon=True)
    # t.start()

    res = ""
    if os.path.exists("../vids/sound_" + records[building][room_index] + ".aac"):
        for cam in rooms[building][room_index]['vid']:
            add_sound(records[building][room_index] +
                      cam.split('/')[0].split('.')[-1], records[building][room_index])
    else:
        res = "vid_"

    for cam in rooms[building][room_index]['vid']:
        try:
            upload("../vids/" + res + records[building][room_index]
                   + cam.split('/')[0].split('.')[-1] + ".mp4",
                   rooms[building][room_index]["auditorium"])
        except Exception:
            pass


def add_sound(video_cam_num, audio_cam_num):
    proc = subprocess.Popen(["ffmpeg", "-i", "../vids/sound_" + audio_cam_num + ".aac", "-i",
                             "../vids/vid_" + video_cam_num + ".mp4", "-y", "-shortest", "-c", "copy",
                             "../vids/" + video_cam_num + ".mp4"], shell=False)
    proc.wait()


def merge(room_index, building):
    merge_video(records[building][room_index]
                + rooms[building][room_index]['sound']['enc'][0].split('/')[0].split('.')[-1],
                records[building][room_index] +
                rooms[building][room_index]['mainCam'].split(
                    '/')[0].split('.')[-1],
                records[building][room_index])

    res = ""
    if os.path.exists("../vids/sound_" + records[building][room_index] + ".aac"):
        add_sound(records[building][room_index] +
                  "merged_2", records[building][room_index])
    else:
        res = "vid_"

    try:
        upload("../vids/" + res + records[building][room_index] + "merged_2.mp4",
               rooms[building][room_index]["auditorium"])
    except Exception:
        pass


def merge_video(screen_num, video_cam_num, record_num):
    # Option 1
    # first = subprocess.Popen(["ffmpeg", "-i", "../vids/vid_" + video_cam_num + ".mp4", "-i", "../vids/vid_" +
    #                           screen_num + ".mp4", "-filter_complex", "hstack=inputs=2", "../vids/vid_" +
    #                           record_num + "merged_1.mp4"], shell=False)
    # os.system("renice -n 20 %s" % (first.pid, ))
    # first.wait()

    # Option 2
    mid1 = subprocess.Popen(["ffmpeg", "-i", "../vids/vid_" + screen_num + ".mp4", "-s", "hd720",
                             "../vids/" + record_num + "mid_1_1.mp4"], shell=False)
    os.system("renice -n 20 %s" % (mid1.pid, ))
    mid1.wait()
    mid2 = subprocess.Popen(["ffmpeg", "-i", "../vids/vid_" + video_cam_num + ".mp4", "-s", "hd720",
                             "../vids/" + record_num + "mid_1_3.mp4"], shell=False)
    os.system("renice -n 20 %s" % (mid2.pid, ))
    mid2.wait()
    crop1 = subprocess.Popen(["ffmpeg", "-i", "../vids/" + record_num + "mid_1_3.mp4", "-filter:v", "crop=640:720:40:0",
                              "../vids/" + record_num + "cropped_1.mp4"], shell=False)
    os.system("renice -n 20 %s" % (crop1.pid, ))
    crop1.wait()
    second = subprocess.Popen(["ffmpeg", "-i", "../vids/" + record_num + "cropped_1.mp4", "-i", "../vids/" +
                               record_num + "mid_1_1.mp4", "-filter_complex", "hstack=inputs=2", "../vids/vid_" +
                               record_num + "merged_2.mp4"], shell=False)
    os.system("renice -n 20 %s" % (second.pid, ))
    second.wait()

    # Option 3
    # mid3 = subprocess.Popen(["ffmpeg", "-i", "../vids/vid_" + screen_num + ".mp4", "-s", "hd720",
    #                          "../vids/" + record_num + "mid_2_1.mp4"], shell=False)
    # os.system("renice -n 20 %s" % (mid3.pid, ))
    # mid3.wait()
    # mid4 = subprocess.Popen(["ffmpeg", "-i", "../vids/vid_" + video_cam_num + ".mp4", "-s", "hd720",
    #                          "../vids/" + record_num + "mid_2_3.mp4"], shell=False)
    # os.system("renice -n 20 %s" % (mid4.pid, ))
    # mid4.wait()
    # crop2 = subprocess.Popen(["ffmpeg", "-i", "../vids/" + record_num + "mid_2_3.mp4", "-filter:v", "crop=640:720",
    #                           "../vids/" + record_num + "cropped_2.mp4"], shell=False)
    # os.system("renice -n 20 %s" % (crop2.pid, ))
    # crop2.wait()
    # third = subprocess.Popen(["ffmpeg", "-i", "../vids/" + record_num + "cropped_2.mp4", "-i", "../vids/" +
    #                           record_num + "mid_2_1.mp4", "-filter_complex", "hstack=inputs=2", "../vids/vid_" +
    #                           record_num + "merged_3.mp4"], shell=False)
    # os.system("renice -n 20 %s" % (third.pid, ))
    # third.wait()
