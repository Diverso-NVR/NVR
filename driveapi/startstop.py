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
        rooms[building][str(room['id'])] = {"auditorium": room['auditorium']}
        rooms[building][str(room['id'])]['sound'] = room["sound"]
        rooms[building][str(room['id'])]['vid'] = room["vid"]


def start(room_index, sound_type, building):
    processes[building][room_index] = []
    today = datetime.date.today()
    curr_time = datetime.datetime.now().time()
    records[building][room_index] = "{0}-{1}-{2}_{3}:{4}_{5}_".format(
        today.year, today.month, today.day, str(curr_time.hour), str(curr_time.minute), rooms[building][room_index]["auditorium"])

    # TODO add enc, cam vids sounds

    if rooms[building][room_index]["auditorium"] == '520':
        enc = subprocess.Popen("ffmpeg -rtsp_transport http -i rtsp://192.168.15.56/main -y -c:a copy -vn " +
                               "-f mp4 ../vids/sound_" +
                               records[building][room_index] + ".aac",
                               shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(enc)
        for cam in rooms[building][room_index]['vid']:
            process = subprocess.Popen("ffmpeg -i rtsp://192.168." + network[building] + "." + cam + " -y -c:v copy " +
                                       "-an -f mp4 ../vids/vid_" +
                                       records[building][room_index] +
                                       cam + ".mp4",
                                       shell=True, preexec_fn=os.setsid)
            processes[building][room_index].append(process)
        return

    # TODO fix ПТС
    # if rooms[building][room_index]["auditorium"] == 'ПТС':
    #     if sound_type == "enc":
    #         enc = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://192.168.15.11/main -y -c:a copy -vn -f mp4 ../vids/sound_"
    #                                + records[building][room_index] + ".aac", shell=True, preexec_fn=os.setsid)
    #         processes[building][room_index].append(enc)
    #     else:
    #         cam = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://192.168.15.52/live/av0 -y -c:a copy -vn -f mp4 ../vids/sound_"
    #                                + records[building][room_index] + ".aac", shell=True, preexec_fn=os.setsid)
    #         processes[building][room_index].append(cam)

    #     process = subprocess.Popen("ffmpeg -rtsp_transport http -i rtsp://192.168.15.45 -y -c:v copy " +
    #                                "-an -f mp4 ../vids/vid_" +
    #                                records[building][room_index] +
    #                                "1" + ".mp4",
    #                                shell=True, preexec_fn=os.setsid)
    #     processes[building][room_index].append(process)
    #     return

    if sound_type == "enc":
        enc = subprocess.Popen("ffmpeg -rtsp_transport http -i rtsp://192.168." + network[building] + "." +
                               rooms[building][room_index]['sound']['enc'][0] +
                               " -y -c:a copy -vn -f mp4 ../vids/sound_"
                               + records[building][room_index] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(enc)
    else:
        cam = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://admin:Supervisor@192.168." + network[building] + "." +
                               rooms[building][room_index]['sound']['cam'][0] +
                               " -y -c:a copy -vn -f mp4 ../vids/sound_"
                               + records[building][room_index] + ".aac", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(cam)

    for cam in rooms[building][room_index]['vid']:
        process = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://admin:Supervisor@192.168." + network[building] + "." +
                                   cam + " -y -c:v copy -an -f mp4 ../vids/vid_" +
                                   records[building][room_index] + cam + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(process)


def stop(room_index, building):
    for process in processes[building][room_index]:
        os.killpg(process.pid, signal.SIGTERM)
    for cam in rooms[building][room_index]['vid']:
        add_sound(records[building]
                  [room_index] + cam, records[building][room_index])
    for cam in rooms[building][room_index]['vid']:
        try:
            upload("../vids/" + records[building][room_index] + cam + ".mp4",
                   rooms[building][room_index]["auditorium"])
        except Exception:
            pass


def add_sound(video_cam_num, audio_cam_num):
    proc = subprocess.Popen(["ffmpeg", "-i", "../vids/sound_" + audio_cam_num + ".aac", "-i",
                             "../vids/vid_" + video_cam_num + ".mp4", "-y", "-shortest", "-c", "copy",
                             "../vids/" + video_cam_num + ".mp4"], shell=False)
    proc.wait()
