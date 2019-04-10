from driveapi.startstop import start, stop
from flask import Flask, render_template, jsonify
from time import time

app = Flask(__name__)


data = {"fcmd": [{'id': 1, 'building': 'ФКМД', 'auditorium': 'П505', 'status': 'free', 'timestamp': 0,
                  'source': 'https://drive.google.com/drive/folders/15Ant5hntmfl84Rrkzr9dep2nh13sbXft',
                  'is_stopped': 'no'},
                 {'id': 2, 'building': 'ФКМД', 'auditorium': 'П500', 'status': 'free', 'timestamp': 0,
                  'source': 'https://drive.google.com/drive/folders/1EbJg0IzJLP788qWVr0u_Y9SmZ8ygzKwr',
                  'is_stopped': 'no'},
                 {'id': 3, 'building': 'ФКМД', 'auditorium': 'С401', 'status': 'free', 'timestamp': 0,
                  'source': 'https://drive.google.com/drive/folders/1L4icf2QJsv7dBBDygNNXCG9dOnPwxY9r',
                  'is_stopped': 'no'}],
        "miem": [{'id': 4, 'building': 'МИЭМ', 'auditorium': '513', 'status': 'free', 'timestamp': 0,
                  'source': 'https://drive.google.com/drive/u/2/folders/1NjJIEr0bOK0MNfFKjzzYF3NRUghjIiZz',
                  'is_stopped': 'no'}]}


@app.route('/')
def load_main_page():
    return render_template('index.html')


@app.route('/status', methods=['GET'])
def status():
    return jsonify(data)


@app.route('/cameras/<camera>/<soundType>/<building>/start', methods=['POST'])
def startRec(camera, soundType, building):
    start(data, camera, soundType)
    return jsonify([{'timestamp': time()}])


@app.route('/cameras/<camera>/<soundType>/<building>/stop', methods=['POST'])
def stopRec(camera, soundType, building):
    stop(data, camera)
    return jsonify([{'timestamp': time()}])


# @app.route('/cameras/<camera>/<soundType>/is_stopped', methods=['POST'])
# def stopClicked(camera, soundType):
#     data[int(camera) - 1]['is_stopped'] = 'yes'
#     return jsonify([{'timestamp': time()}])


if __name__ == '__main__':
    app.run()
