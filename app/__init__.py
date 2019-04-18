from driveapi.startstop import start, stop
from flask import Flask, render_template, jsonify
from time import time
import json

app = Flask(__name__)


with open('app/data.json', 'r') as f:
    data = json.loads(f.read())
with open('app/tempData.json', 'w') as f:
    json.dump(data, f)


@app.route('/')
def load_main_page():
    return render_template('index.html')


@app.route('/status', methods=['GET'])
def status():
    with open('app/tempData.json', 'r') as f:
        data = json.loads(f.read())
    return jsonify(data)


@app.route('/cameras/<camera>/<soundType>/<building>/start', methods=['POST'])
def startRec(camera, soundType, building):
    camId = 0
    for i in data[building]:
        if i['id'] == int(camera):
            break
        camId += 1

    data[building][camId]["status"] = "busy"

    with open('app/tempData.json', 'w') as f:
        json.dump(data, f)

    start(camera, soundType, building)

    return jsonify([{'timestamp': time()}])


@app.route('/cameras/<camera>/<soundType>/<building>/stop', methods=['POST'])
def stopRec(camera, soundType, building):
    camId = 0
    for i in data[building]:
        if i['id'] == int(camera):
            break
        camId += 1

    data[building][camId]["status"] = "free"

    with open('app/tempData.json', 'w') as f:
        json.dump(data, f)

    stop(camera, building)

    return jsonify([{'timestamp': time()}])


if __name__ == '__main__':
    app.run()
