from driveapi.startstop import start, stop
from flask import Flask, render_template, jsonify
import time
import threading
import json

app = Flask(__name__)


with open('app/data.json', 'r') as f:
    data = json.loads(f.read())

threads = {}
for building in data:
    threads[building] = {}


@app.route('/')
def load_main_page():
    return render_template('index.html')


@app.route('/status', methods=['GET'])
def status():
    return jsonify(data)


@app.route('/cameras/<camera>/<soundType>/<building>/start', methods=['POST'])
def startRec(camera, soundType, building):
    camId = 0
    for i in data[building]:
        if i['id'] == int(camera):
            break
        camId += 1

    data[building][camId]["status"] = "busy"

    threads[building][camera] = threading.Thread(
        target=startTimer, args=(building, camId), daemon=True)
    threads[building][camera].start()

    start(camera, soundType, building)

    return ""


def startTimer(building, camId):
    while data[building][camId]['status'] == 'busy':
        data[building][camId]['timestamp'] += 1
        time.sleep(1)


@app.route('/cameras/<camera>/<building>/stop', methods=['POST'])
def stopRec(camera, building):
    camId = 0
    for i in data[building]:
        if i['id'] == int(camera):
            break
        camId += 1

    data[building][camId]["status"] = "free"

    stop(camera, building)

    return ""


if __name__ == '__main__':
    app.run()
