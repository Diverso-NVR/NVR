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
         {'id': 1, 'building': 'FCMD', 'auditorium': 'П505', 'status': 'free', 'timestamp': 0,
          'source': 'https://drive.google.com/drive/folders/15Ant5hntmfl84Rrkzr9dep2nh13sbXft'},
         {'id': 2, 'building': 'FCMD', 'auditorium': 'П500', 'status': 'free', 'timestamp': 0,
          'source': 'https://drive.google.com/drive/folders/1EbJg0IzJLP788qWVr0u_Y9SmZ8ygzKwr'},
         {'id': 3, 'building': 'FCMD', 'auditorium': 'С401', 'status': 'free', 'timestamp': 0,
          'source': 'https://drive.google.com/drive/folders/1L4icf2QJsv7dBBDygNNXCG9dOnPwxY9r'},
         {'id': 4, 'building': 'MIEM', 'auditorium': '513', 'status': 'free', 'timestamp': 0,
          'source': 'https://drive.google.com/drive/folders/1EkXrlRNtXp-YBF1-8SGanCvZRLThy3e_'}
    ])


@app.route('/cameras/<camera>/start', methods=['POST'])
def startRec(camera):
    start(camera)
    return jsonify([{'timestamp': time()}])


@app.route('/cameras/<camera>/stop', methods=['POST'])
def stopRec(camera):
    stop()
    return jsonify([{'timestamp': None}])


if __name__ == '__main__':
    app.run()
