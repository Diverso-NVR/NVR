import datetime
import subprocess
import psutil
import time
import signal
import os
import threading


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

network = {"ФКМД": "11", "": "13", "МИЭМ": "15"}
rooms = {"ФКМД": {"1": "P505", "2": "P500", "3": "S401"},
         "МИЭМ": {"1": "504", "4": "513"}}
processes = {"ФКМД": {}, "МИЭМ": {}}
records = {"ФКМД": {}, "МИЭМ": {}}
t = {"ФКМД": {}, "МИЭМ": {}}


def start(data, room_index, sound_type, building):
    data[building][int(room_index) - 1]['status'] = 'busy'
    t[building][room_index] = threading.Thread(
        target=startTimer, args=(data, room_index, building), daemon=True)
    t[building][room_index].start()
    processes[building][room_index] = []
    today = datetime.date.today()
    curr_time = datetime.datetime.now().time()
    formatted_time = str(curr_time.hour) + ':' + str(curr_time.minute)
    records[building][room_index] = "{0}-{1}-{2}-{3}-{4}-{5}".format(
        today.year, today.month, today.day, formatted_time, rooms[building][room_index], "HSE")
    if sound_type == "enc":
        enc = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://192.168." + network[building] + "." +
                               room_index + "1/main -y -c:a copy -vn -f mp4 ../vids/sound-source-"
                               + records[building][room_index] + ".mp3", shell=True)
        processes[building][room_index].append(enc)
    else:
        cam = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://admin:Supervisor@192.168." + network[building] + "." +
                               room_index + "2 -y -c:a copy -vn -f mp4 ../vids/sound-source-"
                               + records[building][room_index] + ".mp3", shell=True)
        processes[building][room_index].append(cam)

    proc = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://192.168." + network[building] + "." +
                            room_index + "1/main -y -c copy -f mp4 ../vids/1-" +  # -c:v copy -an
                            records[building][room_index] + ".mp4", shell=True)
    processes[building][room_index].append(proc)
    for i in range(2, 7):
        process = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://admin:Supervisor@192.168." + network[building] + "." +
                                   room_index +
                                   str(i) + " -y -c:v copy -an -f mp4 ../vids/"
                                   + str(i) + "-" + records[building][room_index] + ".mp4", shell=True)
        processes[building][room_index].append(process)


def killproc(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.terminate()
    process.terminate()


def stop(data, room_index, building):
    data[building][int(room_index) - 1]['timestamp'] = 0
    for process in processes[building][room_index]:
        killproc(process.pid)
    for i in range(1, 7):
        add_sound(str(i) + "-" + records[building]
                  [room_index], records[building][room_index])
    for i in range(1, 7):
        try:
            upload('../vids/result-' + str(i) + "-" +
                   records[building][room_index] + ".mp4", room_index)
        except Exception:
            pass
    data[building][int(room_index) - 1]['is_stopped'] = 'no'
    data[building][int(room_index) - 1]['status'] = 'free'


def add_sound(video_cam_num, audio_cam_num):
    subprocess.Popen(
        "ffmpeg -i ../vids/sound-source-" + audio_cam_num + ".mp3 "
        + "-i ../vids/" + video_cam_num + ".mp4" +
        " -shortest -c copy ../vids/result-" + video_cam_num + ".mp4",
        shell=True)


def startTimer(data, room_index, building):
    counter = 0
    while data[building][int(room_index) - 1]['is_stopped'] == 'no':
        time.sleep(1)
        counter += 1
        data[building][int(room_index) - 1]['timestamp'] = counter
