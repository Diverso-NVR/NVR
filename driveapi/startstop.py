import datetime
import subprocess
import signal
import os
import json
from threading import Lock, Thread


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

lock = Lock()

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
    records[building][room_index] = "{}-{}-{}_{}:{}_{}_".format(
        today.year, today.month, today.day, hour, minute, rooms[building][room_index]["auditorium"])

    if rooms[building][room_index]["auditorium"] == '406':
        if sound_type == "enc":
            enc = subprocess.Popen("ffmpeg -rtsp_transport http -i rtsp://admin:admin@172.18.185." +
                                   rooms[building][room_index]['sound']['enc'][0] +
                                   " -y -c:a copy -vn -f mp4 ../vids/sound_"
                                   + records[building][room_index] + ".aac", shell=True, preexec_fn=os.setsid)
            processes[building][room_index].append(enc)
        else:
            camera = subprocess.Popen("ffmpeg - rtsp_transport tcp - i rtsp://admin:Supervisor@172.18.185." +
                                      rooms[building][room_index]['sound']['cam'][0] +
                                      " -y -c:a copy -vn -f mp4 ../vids/sound_"
                                      + records[building][room_index] + ".aac", shell=True, preexec_fn=os.setsid)
            processes[building][room_index].append(camera)

        process = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://admin:admin@172.18.185." +
                                   rooms[building][room_index]['vid'][0] + + " -y -c:v copy -an -f mp4 ../vids/vid_" +
                                   records[building][room_index] + rooms[building][room_index]['vid'][0] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(process)
        process = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://admin:Supervisor@172.18.185." +
                                   rooms[building][room_index]['vid'][1] + " -y -c:v copy -an -f mp4 ../vids/vid_" +
                                   records[building][room_index] + rooms[building][room_index]['vid'][1] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[building][room_index].append(process)
        return

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
    with lock:
        for process in processes[building][room_index]:
            os.killpg(process.pid, signal.SIGTERM)

        res = ""
        if os.path.exists("../vids/sound_" + records[building][room_index] + ".aac"):
            for cam in rooms[building][room_index]['vid']:
                add_sound(records[building][room_index] +
                          cam.split('/')[0], records[building][room_index])
        else:
            res = "vid_"

        for cam in rooms[building][room_index]['vid']:
            try:
                upload("../vids/" + res + records[building][room_index] + cam.split('/')[0] + ".mp4",
                       rooms[building][room_index]["auditorium"])
            except Exception:
                pass

        # t = Thread(target=merge, args=(room_index, building), daemon=True)
        # t.start()


def merge(room_index, building):
    merge_video(records[building][room_index] + rooms[building][room_index]['vid'][0].split('/')[0],
                records[building][room_index] +
                rooms[building][room_index]['vid'][2].split('/')[0],
                records[building][room_index])

    res = ""
    if os.path.exists("../vids/sound_" + records[building][room_index] + ".aac"):
        for i in range(1, 4):
            add_sound(records[building][room_index] +
                      "merged_" + str(i), records[building][room_index])
    else:
        res = "vid_"

    for i in range(1, 4):
        try:
            upload("../vids/" + res + records[building][room_index] + "merged_" + str(i) + ".mp4",
                   rooms[building][room_index]["auditorium"])
        except Exception:
            pass


def add_sound(video_cam_num, audio_cam_num):
    proc = subprocess.Popen(["ffmpeg", "-i", "../vids/sound_" + audio_cam_num + ".aac", "-i",
                             "../vids/vid_" + video_cam_num + ".mp4", "-y", "-shortest", "-c", "copy",
                             "../vids/" + video_cam_num + ".mp4"], shell=False)
    proc.wait()


def merge_video(screen_num, video_cam_num, record_num):
    # Option 1
    first = subprocess.Popen(["ffmpeg", "-i", "../vids/vid_" + screen_num + ".mp4", "-i", "../vids/vid_" +
                              video_cam_num + ".mp4", "-filter_complex", "hstack=inputs=2", "../vids/vid_" +
                              record_num + "merged_1.mp4"], shell=False)
    first.wait()

    # Option 2
    subprocess.Popen(["ffmpeg", "-i", "../vids/vid_" + screen_num + ".mp4", "-s", "hd720",
                      "../vids/" + record_num + "mid_1_1.mp4"], shell=False).wait()
    subprocess.Popen(["ffmpeg", "-i", "../vids/vid_" + video_cam_num + ".mp4", "-s", "hd720",
                      "../vids/" + record_num + "mid_1_3.mp4"], shell=False).wait()
    subprocess.Popen(["ffmpeg", "-i", "../vids/" + record_num + "mid_1_3.mp4", "-filter:v", "crop=640:720:40:0",
                      "../vids/" + record_num + "cropped_1.mp4"], shell=False).wait()
    second = subprocess.Popen(["ffmpeg", "-i", "../vids/" + record_num + "mid_1_1.mp4", "-i", "../vids/" +
                               record_num + "cropped_1.mp4", "-filter_complex", "hstack=inputs=2", "../vids/vid_" +
                               record_num + "merged_2.mp4"], shell=False)
    second.wait()

    # Option 3
    subprocess.Popen(["ffmpeg", "-i", "../vids/vid_" + screen_num + ".mp4", "-s", "hd720",
                      "../vids/" + record_num + "mid_2_1.mp4"], shell=False).wait()
    subprocess.Popen(["ffmpeg", "-i", "../vids/vid_" + video_cam_num + ".mp4", "-s", "hd720",
                      "../vids/" + record_num + "mid_2_3.mp4"], shell=False).wait()
    subprocess.Popen(["ffmpeg", "-i", "../vids/" + record_num + "mid_2_3.mp4", "-filter:v", "crop=640:720",
                      "../vids/" + record_num + "cropped_2.mp4"], shell=False).wait()
    third = subprocess.Popen(["ffmpeg", "-i", "../vids/" + record_num + "mid_2_1.mp4", "-i", "../vids/" +
                              record_num + "cropped_2.mp4", "-filter_complex", "hstack=inputs=2", "../vids/vid_" +
                              record_num + "merged_3.mp4"], shell=False)
    third.wait()
