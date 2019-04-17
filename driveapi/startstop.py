import datetime
import subprocess
import time
import threading
import os
import signal
import logging


from driveapi.driveSettings import upload

"""
    192.168.11.
    P505: 11 12 13 14
    P500: 21 22 23 24 25 26
    S401: 31 32 33 34
    
    192.168.13.
    
    
    192.168.15.
    513: 56 42 43
"""

# Room 4 is a temporary solution
rooms = {"1": "P505", "2": "P500", "3": "S401", "4": "MIEM"}
roomsMIEM = {"1": "504"}
processes = {}
records = {}
t = {}
stopThread = {}


def start(data, room_index, sound_type):
    stopThread[room_index] = False
    t[room_index] = threading.Thread(
        target=startTimer, args=(data, room_index), daemon=True)
    t[room_index].start()
    processes[room_index] = []
    today = datetime.date.today()
    curr_time = datetime.datetime.now().time()
    formatted_time = str(curr_time.hour) + ':' + str(curr_time.minute)
    records[room_index] = "{0}-{1}-{2}-{3}-{4}-{5}".format(
        today.year, today.month, today.day, formatted_time, rooms[room_index], "HSE")
    if room_index in ["1", "2", "3"]:
        if sound_type == "enc":
            enc = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://192.168.11." +
                                   room_index + "1/main -y -c:a copy -vn -f mp4 ../vids/sound-source-"
                                   + records[room_index] + ".mp3", shell=True, preexec_fn=os.setsid)
            processes[room_index].append(enc)
        else:
            cam = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://admin:Supervisor@192.168.11." +
                                   room_index + "2 -y -c:a copy -vn -f mp4 ../vids/sound-source-"
                                   + records[room_index] + ".mp3", shell=True, preexec_fn=os.setsid)
            processes[room_index].append(cam)

        proc = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                                room_index + "1/main -y -c:v copy -an -f mp4 ../vids/1-" +
                                records[room_index] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[room_index].append(proc)
        procSec = subprocess.Popen("ffmpeg -i rtsp://192.168.11." +
                                room_index + "1/ext -y -c:v copy -an -f mp4 ../vids/1-secondary-" +
                                records[room_index] + ".mp4", shell=True, preexec_fn=os.setsid)
        processes[room_index].append(procSec)
        for i in range(2, 7):
            process = subprocess.Popen("ffmpeg -i rtsp://admin:Supervisor@192.168.11." +
                                       room_index + str(i) + " -y -c:v copy -an -f mp4 ../vids/"
                                       + str(i) + "-" + records[room_index] + ".mp4",
                                       shell=True, preexec_fn=os.setsid)
            processes[room_index].append(process)
    else:
        snd = subprocess.Popen("ffmpeg -rtsp_transport tcp -i rtsp://192.168.15.56/main -y -c:a copy -vn " +
                               "-f mp4 ../vids/sound-source-" + records[room_index] + ".mp3",
                               shell=True, preexec_fn=os.setsid)
        processes[room_index].append(snd)
        coderVid = subprocess.Popen("ffmpeg -i rtsp://192.168.15.56/main -y -c:v copy -an " +
                                    "-f mp4 ../vids/1-" + records[room_index] + ".mp4",
                                    shell=True, preexec_fn=os.setsid)
        processes[room_index].append(coderVid)
        for i in range(2, 4):
            camVid = subprocess.Popen("ffmpeg -i rtsp://192.168.15.4" + str(i) + " -y -c:v copy " +
                                      "-an -f mp4 ../vids/" + str(i) + "-" + records[room_index] + ".mp4",
                                      shell=True, preexec_fn=os.setsid)
            processes[room_index].append(camVid)


def stop(data, room_index):
    stopThread[room_index] = True
    for process in processes[room_index]:
        os.killpg(process.pid, signal.SIGTERM)
    if os.path.isfile("../vids/sound-source-" + records[room_index] + ".mp3"):
        for i in range(1, 7):
            add_sound(str(i) + "-" + records[room_index], records[room_index])
    else:
        for i in range(1, 7):
            try:
                os.rename("../vids/" + str(i) + "-" + records[room_index] + ".mp4", "../vids/result-" + str(i) + "-" +
                          records[room_index] + ".mp4")
            except FileNotFoundError:
                pass
    logger = logging.getLogger('uploadlogger')
    hdlr = logging.FileHandler('uploadlog.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    for i in range(1, 7):
        try:
            upload('../vids/result-' + str(i) + "-" +
                   records[room_index] + ".mp4", room_index)
            logger.info("File " + str(i) + "-" + records[room_index] + " uploaded")
        except Exception as e:
            logger.error("File " + str(i) + "-" + records[room_index] + " error: " + str(e))
    try:
        upload("../vids/1-" + records[room_index] + ".mp4", room_index)
        upload("../vids/3-" + records[room_index] + ".mp4", room_index)
        upload("../vids/sound-source-" + records[room_index] + ".mp3", room_index)
    except Exception as e:
        logger.error("Additional files upload error: " + str(e))
    data[int(room_index) - 1]['is_stopped'] = 'no'
    data[int(room_index) - 1]['timestamp'] = 0
    data[int(room_index) - 1]['is_started'] = 'no'
    data[int(room_index) - 1]['status'] = 'free'
    stopThread[room_index] = False


def add_sound(video_cam_num, audio_cam_num):
    proc = subprocess.Popen(["ffmpeg", "-i", "../vids/sound-source-" + audio_cam_num + ".mp3", "-i",
                             "../vids/" + video_cam_num + ".mp4", "-c", "copy",
                             "../vids/result-" + video_cam_num + ".mp4"], shell=False)
    proc.wait()


def startTimer(data, room_index):
    counter = 0
    while (data[int(room_index) - 1]['is_stopped'] == 'no') or (stopThread[room_index] is False):
        time.sleep(1)
        counter += 1
        data[int(room_index) - 1]['timestamp'] = counter
