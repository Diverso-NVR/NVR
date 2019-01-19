from driveAPI.startstop import start, stop
from flask import render_template, request, redirect
from flask import Flask

app = Flask(__name__)


@app.route('/')
def load_main_page():
    return render_template('index.html')


@app.route('/start_stop', methods=['POST'])
def start_stop_action():
    data = request.form['index']
    if 'start' in data:
        start(data.split()[1])
    elif 'stop' in data:
        stop()
    return redirect('/')


if __name__ == '__main__':
    app.run()
