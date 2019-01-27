from driveapi.startstop import start, stop
from flask import Flask, render_template, request, jsonify
from time import time

app = Flask(__name__)


@app.route('/')
def load_main_page():
    return render_template('index.html')


@app.route('/status', methods=['GET'])
def status():
    return jsonify([
         {'id': 1, 'building': 'FCMD', 'auditorium': 'П505', 'status': 'free', 'timestamp': 0},
         {'id': 2, 'building': 'FCMD', 'auditorium': 'П500', 'status': 'free', 'timestamp': 0},
         {'id': 3, 'building': 'FCMD', 'auditorium': 'С401', 'status': 'free', 'timestamp': 0},
         {'id': 4, 'building': 'MIEM', 'auditorium': '513', 'status': 'free', 'timestamp': 0}
    ])


@app.route('/cameras/<camera>/start', methods=['POST'])
def start(camera):
    # start(camera)
    return jsonify([{'timestamp': time()}])


@app.route('/cameras/<camera>/stop', methods=['POST'])
def stop(camera):
    # stop()
    return jsonify([{'timestamp': None}])


if __name__ == '__main__':
    app.run()
