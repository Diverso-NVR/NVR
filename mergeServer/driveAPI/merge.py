import os
import subprocess
from pathlib import Path
from threading import Lock

from driveAPI.driveSettings import upload

lock = Lock()
home = str(Path.home())


def merge_video(screen_num: str, video_cam_num: str, record_num: str, room_name: str) -> None:
    lock.acquire()

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

    res = ""
    if os.path.exists(home + "/vids/sound_" + record_num + ".aac"):
        add_sound(record_num +
                  "merged_2", record_num)
    else:
        res = "vid_"

    try:
        upload(home + "/vids/" + res + record_num + "merged_2.mp4",
               room_name)
    except Exception:
        pass

    lock.release()


def add_sound(video_cam_num: str, audio_cam_num: str) -> None:
    proc = subprocess.Popen(["ffmpeg", "-i", home + "/vids/sound_" + audio_cam_num + ".aac", "-i",
                             home + "/vids/vid_" + video_cam_num +
                             ".mp4", "-y", "-shortest", "-c", "copy",
                             home + "/vids/" + video_cam_num + ".mp4"], shell=False)
    proc.wait()