from driveapi.startstop import start, stop
from flask import Flask, render_template, jsonify
from time import time
import json

app = Flask(__name__)


with open("app/data.json", "r") as f:
    data = json.loads(f.read())


@app.route('/')
def load_main_page():
    return render_template('index.html')


@app.route('/status', methods=['GET'])
def status():
    return jsonify(data)


@app.route('/cameras/<camera>/<soundType>/<building>/start', methods=['POST'])
def startRec(camera, soundType, building):
    start(data, camera, soundType, building)
    return jsonify([{'timestamp': time()}])


@app.route('/cameras/<camera>/<soundType>/<building>/stop', methods=['POST'])
def stopRec(camera, soundType, building):
    stop(data, camera, building)
    return jsonify([{'timestamp': time()}])


@app.route('/cameras/<camera>/<soundType>/<building>/is_stopped', methods=['POST'])
def stopClicked(camera, soundType, building):
    data[building][int(camera) - 1]['is_stopped'] = 'yes'
    return jsonify([{'timestamp': time()}])


if __name__ == '__main__':
    app.run()
