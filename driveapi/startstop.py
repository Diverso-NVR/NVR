import datetime
import subprocess
import signal
import os
import json


from driveapi.driveSettings import upload

"""
    192.168.11.
    P505: 11 12 13 14
    P500: 21 22 23 24 25 26
    S401: 31 32 33 34

    192.168.13.


    192.168.15.
    Для тестов 42 43 56-кодер
    45 47  51 52 53 54 55 84-кодер 206
"""

with open("app/data.json", 'r') as f:
    data = json.loads(f.read())

network = {"ФКМД": "11", "ФКН": "13", "МИЭМ": "15"}
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


# TODO do smth with rtsp protocols'
def start(room_index, sound_type, building):
    processes[building][room_index] = []
    today = datetime.date.today()
    curr_time = datetime.datetime.now().time()
    hour = "0" + \
        str(curr_time.hour) if curr_time.hour < 10 else str(curr_time.hour)
    minute = "0" + \
        str(curr_time.minute) if curr_time.minute < 10 else str(curr_time.minute)
    records[building][room_index] = "{0}-{1}-{2}_{3}:{4}_{5}_".format(
        today.year, today.month, today.day, hour, minute, rooms[building][room_index]["auditorium"])

    if sound_type == "enc":
        enc = subprocess.Popen("ffmpeg -rtsp_transport http -i rtsp://192.168." + network[building] + "." +
                               rooms[building][room_index]['sound']['enc'][0] +
                               " -y -c:a copy -vn -f mp4 ../vids/sound_"
                               + records[building][room_index] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(enc)
    else:
        camera = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://admin:Supervisor@192.168." + network[building] + "." +
                                  rooms[building][room_index]['sound']['cam'][0] +
                                  " -y -c:a copy -vn -f mp4 ../vids/sound_"
                                  + records[building][room_index] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(camera)

    for cam in rooms[building][room_index]['vid']:
        process = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://admin:Supervisor@192.168." + network[building] + "." +
                                   cam + " -y -c:v copy -an -f mp4 ../vids/vid_" +
                                   records[building][room_index] + cam.split('/')[0] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(process)


def stop(room_index, building):
    for process in processes[building][room_index]:
        os.killpg(process.pid, signal.SIGTERM)
    for cam in rooms[building][room_index]['vid']:
        add_sound(records[building]
                  [room_index] + cam.split('/')[0], records[building][room_index])
    res = ""
    if not os.path.exists("../vids/sound_" + records[building][room_index]):
        res = "vid_"
    for cam in rooms[building][room_index]['vid']:
        try:
            upload("../vids/" + res + records[building][room_index] + cam.split('/')[0] + ".mp4",
                   rooms[building][room_index]["auditorium"])
        except Exception:
            pass


def add_sound(video_cam_num, audio_cam_num):
    proc = subprocess.Popen(["ffmpeg", "-i", "../vids/sound_" + audio_cam_num + ".aac", "-i",
                             "../vids/vid_" + video_cam_num + ".mp4", "-y", "-shortest", "-c", "copy",
                             "../vids/" + video_cam_num + ".mp4"], shell=False)
    proc.wait()
