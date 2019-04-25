import datetime
import subprocess
import signal
import os
import json
from threading import Thread


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
        rooms[building][str(room['id'])] = room['auditorium']


def start(room_index, sound_type, building):
    processes[building][room_index] = []
    today = datetime.date.today()
    curr_time = datetime.datetime.now().time()
    formatted_time = str(curr_time.hour) + ':' + str(curr_time.minute)
    records[building][room_index] = "{0}-{1}-{2}-{3}-{4}-{5}".format(
        today.year, today.month, today.day, formatted_time, rooms[building][room_index], "HSE")

    if rooms[building][room_index] == '513':
        enc = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://192.168.15.56/main -y -c:a copy -vn " +
                               "-f mp4 ../vids/sound-source-" +
                               records[building][room_index] + ".mp3",
                               shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(enc)
        for i in range(2, 4):
            process = subprocess.Popen("ffmpeg -i rtsp://192.168.15.4" + str(i) + " -y -c:v copy " +
                                       "-an -f mp4 ../vids/" +
                                       str(i) + "-" +
                                       records[building][room_index] + ".mp4",
                                       shell=True, preexec_fn=os.setsid)
            processes[building][room_index].append(process)
        return

    if sound_type == "enc":
        enc = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://192.168." + network[building] + "." +
                               room_index + "1/main -y -c:a copy -vn -f mp4 ../vids/sound-source-"
                               + records[building][room_index] + ".mp3", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(enc)
    else:
        cam = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://admin:Supervisor@192.168." + network[building] + "." +
                               room_index + "2 -y -c:a copy -vn -f mp4 ../vids/sound-source-"
                               + records[building][room_index] + ".mp3", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(cam)

    proc = subprocess.Popen("ffmpeg -i rtsp://192.168." + network[building] + "." +
                            room_index + "1/main -y -c:v copy -an -f mp4 ../vids/1-" +
                            records[building][room_index] + ".mp4", shell=True, preexec_fn=os.setsid)
    processes[building][room_index].append(proc)
    for i in range(2, 7):
        process = subprocess.Popen("ffmpeg -i rtsp://admin:Supervisor@192.168." + network[building] + "." +
                                   room_index +
                                   str(i) + " -y -c:v copy -an -f mp4 ../vids/"
                                   + str(i) + "-" + records[building][room_index] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(process)


def stop(room_index, building):
    for process in processes[building][room_index]:
        os.killpg(process.pid, signal.SIGTERM)
    for i in range(1, 7):
        add_sound(str(i) + "-" + records[building]
                  [room_index], records[building][room_index])
    for i in range(1, 7):
        try:
            upload('../vids/result-' + str(i) + "-" + records[building][room_index] + ".mp4",
                   rooms[building][room_index])
        except Exception:
            pass


def add_sound(video_cam_num, audio_cam_num):
    proc = subprocess.Popen(["ffmpeg", "-i", "../vids/sound-source-" + audio_cam_num + ".mp3", "-i",
                             "../vids/" + video_cam_num + ".mp4", "-shortest", "-c", "copy",
                             "../vids/result-" + video_cam_num + ".mp4"], shell=False)
    proc.wait()
