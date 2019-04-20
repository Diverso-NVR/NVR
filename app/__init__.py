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
    return render_template('login.html')


@app.route('/fcmd', methods=['GET', "POST"])
def load_fcmd():
    return render_template('fcmd.html')


@app.route('/miem', methods=['GET', "POST"])
def load_miem():
    return render_template('miem.html')


@app.route('/users', methods=['GET', "POST"])
def users():
    with open('app/users.json', 'r') as f:
        users = json.loads(f.read())
    return jsonify(users)


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
    data[building][camId]['timestamp'] = 0

    stop(camera, building)

    return ""


if __name__ == '__main__':
    app.run()
