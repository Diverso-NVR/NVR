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


@app.route('/requestsFcmd', methods=['GET', "POST"])
def load_reqFcmd():
    return render_template('requestsFcmd.html')


@app.route('/miem', methods=['GET', "POST"])
def load_miem():
    return render_template('miem.html')


@app.route('/requestsMiem', methods=['GET', "POST"])
def load_reqMiem():
    return render_template('requestsMiem.html')


@app.route('/users', methods=['GET', "POST"])
def users():
    with open('app/users.json', 'r') as f:
        users = json.loads(f.read())
    return jsonify(users)


@app.route('/reqUsers', methods=['GET', "POST"])
def reqUsers():
    with open('app/newUsers.json', 'r') as f:
        users = json.loads(f.read())
    return jsonify(users)


@app.route('/signup', methods=["GET"])
def signup():
    return render_template('signup.html')


@app.route('/newuser/<login>/<password>/<building>/<permissions>', methods=["GET", "POST"])
def newUser(login, password, building, permissions):
    new_user = {
        'login': login,
        'password': password,
        'building': building,
        'permissions': permissions
    }
    with open('app/newUsers.json', 'r') as f:
        users = json.loads(f.read())
    users['users'].append(new_user)
    with open('app/newUsers.json', 'w') as f:
        json.dump(users, f)
    return ""


@app.route('/addUser/<mail>', methods=["POST"])
def addUser(mail):
    with open('app/newUsers.json', 'r') as f:
        newUsers = json.loads(f.read())
    with open('app/users.json', 'r') as f:
        users = json.loads(f.read())
    for user in newUsers['users']:
        if user['login'] == mail:
            users['users'].append(user)
            newUsers['users'].remove(user)
    with open('app/newUsers.json', 'w') as f:
        json.dump(newUsers, f)
    with open('app/users.json', 'w') as f:
        json.dump(users, f)
    return ""


@app.route('/deleteUser/<mail>', methods=["POST"])
def deleteUser(mail):
    with open('app/newUsers.json', 'r') as f:
        users = json.loads(f.read())
    for user in users['users']:
        if user['login'] == mail:
            users['users'].remove(user)
    with open('app/newUsers.json', 'w') as f:
        json.dump(users, f)
    return ""


@app.route('/status', methods=['GET'])
def status():
    return jsonify(data)


@app.route('/cameras/<camera>/<building>/<soundType>/soundCheck', methods=['POST'])
def soundCheck(camera, building, soundType):
    camId = 0
    for i in data[building]:
        if i['id'] == int(camera):
            break
        camId += 1

    data[building][camId]["soundType"] = soundType

    return ""


@app.route('/cameras/<camera>/<building>/start', methods=['POST'])
def startRec(camera, building):
    camId = 0
    for i in data[building]:
        if i['id'] == int(camera):
            break
        camId += 1

    data[building][camId]["status"] = "busy"

    threads[building][camera] = threading.Thread(
        target=startTimer, args=(building, camId), daemon=True)
    threads[building][camera].start()

    start(camera, data[building][camId]["soundType"], building)

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
