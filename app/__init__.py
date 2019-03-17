from driveapi.startstop import start, stop
from flask import Flask, render_template, jsonify
from time import time

app = Flask(__name__)


@app.route('/')
def load_main_page():
    return render_template('index.html')


@app.route('/status', methods=['GET'])
def status():
    return jsonify([
         {'id': 1, 'building': 'FCMD', 'auditorium': 'П505', 'status': 'free', 'timestamp': 0,
          'source': 'https://drive.google.com/drive/folders/15Ant5hntmfl84Rrkzr9dep2nh13sbXft'},
         {'id': 2, 'building': 'FCMD', 'auditorium': 'П500', 'status': 'free', 'timestamp': 0,
          'source': 'https://drive.google.com/drive/folders/1EbJg0IzJLP788qWVr0u_Y9SmZ8ygzKwr'},
         {'id': 3, 'building': 'FCMD', 'auditorium': 'С401', 'status': 'free', 'timestamp': 0,
          'source': 'https://drive.google.com/drive/folders/1L4icf2QJsv7dBBDygNNXCG9dOnPwxY9r'}
    ])


@app.route('/cameras/<camera>/<soundType>/start', methods=['POST'])
def startRec(camera, soundType):
    start(camera, soundType)
    return jsonify([{'timestamp': time()}])


@app.route('/cameras/<camera>/<soundType>/stop', methods=['POST'])
def stopRec(camera, soundType):
    stop(camera)
    return jsonify([{'timestamp': time()}])


if __name__ == '__main__':
    app.run()
