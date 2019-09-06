from threading import Thread

from merge import merge_video
from flask import Flask, request

app = Flask("NVR_VIDEO_MERGE")


@app.route('/', methods=["GET", "POST"])
def main():
    return "Merge server v1.0", 200


@app.route('/merge', methods=["POST"])
def start_merge():
    json = request.get_json(force=True)
    url = "http://172.16.87.10"
    Thread(target=merge_video,
           args=(json["screen_num"], json["video_cam_num"], json["record_num"],
                 json["room_name"], url)).start()
    return "Merge started", 200


if __name__ == '__main__':
    app.run()
