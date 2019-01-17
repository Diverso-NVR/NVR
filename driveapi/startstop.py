# import datetime
# import json
# import subprocess
# import sys
#
# from driveapi.api import upload
#
# path = "D:\\recorder\\room.json"
# with open(path, 'r') as f:
#     data = json.loads(f.read())
#     campus = data["campus"]
#     room = data["auditorium"]
# cameraIndex = "2"


def start(roomIndex):
    # global process
    # today = datetime.date.today()
    # global record
    # record = "{0}-{1}-{2}-{3}-{4}".format(
    #     today.day, today.month, today.year, room, campus) + ".mp4"
    # process = subprocess.Popen("ffmpeg -i rtsp://192.168.11." + cameraIndex +
    #                            "5 -c copy -f mp4  D:\\recorder\\driveapi\\" + record)
    print(roomIndex)


def stop():
    # subprocess.Popen.kill(process)
    # upload(record)
    # sys.exit()
    print('stop')
