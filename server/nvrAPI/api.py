from calendarAPI.calendarSettings import createCalendar, deleteCalendar, configCalendar
from calendarAPI.calendar_daemon import configDaemon, updateDaemon, changedSound
from driveAPI.driveSettings import createFolder, configDrive
from driveAPI.startstop import start, stop
from threading import Thread
from multiprocessing import Process
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from .email import send_verify_email
from .models import db, Room, Source, User
import jwt

api = Blueprint('api', __name__)

threads = {}
copies = {}


building = "ФКМД"


# AUTHENTICATE
def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Ошибка доступа',
            'autheticated': False
        }
        expired_msg = {
            'message': 'Истёкшая сессия',
            'autheticated': False
        }

        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            user = User.query.filter_by(email=data['sub']['email']).first()
            if not user:
                raise RuntimeError('Пользователь не найден')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401
        except (jwt.InvalidTokenError):
            return jsonify(invalid_msg), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401

    return _verify


@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    send_verify_email(user)
    return jsonify(user.to_dict()), 201


@api.route('/verify_email/<token>', methods=['POST', 'GET'])
def verify_email(token):
    user = User.verify_email_token(token)
    if not user:
        return "", 401

    user.email_verified = True
    db.session.commit()
    return "", 201


@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.authenticate(**data)

    if not user:
        return jsonify({'message': "Неверные данные", 'authenticated': False}), 401

    if not user.access:
        return jsonify({'message': 'Ошибка доступа. Администратор ещё не открыл доступ для этого аккаунта',
                        'authenticated': False}), 401

    token = jwt.encode({
        'sub': {'email': user.email, 'role': user.role},
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=80)},
        current_app.config['SECRET_KEY'])

    return jsonify({'token': token.decode('UTF-8')})


@api.route('/users', methods=['GET'])
def getUsers():
    users = [u.to_dict() for u in User.query.all() if u.email_verified]
    return jsonify(users)


@api.route('/users/<user_id>', methods=['PUT'])
@token_required
def grantAccess(current_user, user_id):
    if current_user.role != 'admin':
        return "", 401
    user = User.query.get(user_id)
    user.access = True
    db.session.commit()
    return "", 201


@api.route('/users/roles/<user_id>', methods=['PUT'])
@token_required
def userRole(current_user, user_id):
    if current_user.role != 'admin':
        return "", 401
    user = User.query.get(user_id)
    print(request.get_json()['role'])
    user.role = request.get_json()['role']
    db.session.commit()
    return "", 201


@api.route('/users/<user_id>', methods=['DELETE'])
@token_required
def deleteUser(current_user, user_id):
    if current_user.role != 'admin':
        return "", 401
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return "", 201


# RECORD AND GOOGLE API
@api.route('/rooms', methods=['POST'])
@token_required
def createRoom(current_user):
    if current_user.role != 'admin':
        return "", 401
    post_data = request.get_json()
    room = Room(name=post_data['name'])
    room.drive = createFolder(
        building,
        post_data.get('name')
    )
    room.calendar = createCalendar(
        building,
        post_data.get('name')
    )
    room.sources = []
    db.session.add(room)
    db.session.commit()
    configCalendar(room.to_dict())
    configDrive(room.to_dict())
    configDaemon(room.to_dict())
    return jsonify(room.to_dict())


@api.route('/rooms/', methods=['GET'])
def getRooms():
    rooms = Room.query.all()
    for room in rooms:
        try:
            room.timestamp = copies[room.id][0]
            room.free = copies[room.id][1]
        except:
            pass
    return jsonify([r.to_dict() for r in rooms])


@api.route('/rooms/<room_id>', methods=['DELETE'])
@token_required
def deleteRoom(current_user, room_id):
    if current_user.role != 'admin':
        return "", 401
    room = Room.query.get(room_id)
    deleteCalendar(room.calendar)
    db.session.delete(room)
    db.session.commit()
    return "", 201


@api.route("/rooms/<room_id>", methods=['PUT'])
@token_required
def editRoom(current_user, room_id):
    if current_user.role != 'admin':
        return "", 401
    post_data = request.get_json()
    room = Room.query.get(room_id)
    updateDaemon(room.to_dict())
    room.sources = []
    for s in post_data['sources']:
        if s.get('id'):
            source = Source.query.get(s['id'])
        else:
            source = Source()
        room.sources.append(source)
        source.room_id = s['room_id']
        source.ip = s['ip']
        source.name = s['name']
        source.sound = s['sound'] if s['sound'] != False else None
        source.tracking = s['tracking']
        source.mainCam = s['mainCam']
    db.session.commit()
    return ""


@api.route('/startRec', methods=['POST'])
@token_required
def startRec(current_user):
    post_data = request.get_json()
    id = post_data['id']
    room = Room.query.get(id)
    copies[id] = [0, False]

    if room.free == True:
        threads[id] = Thread(
            target=startTimer, args=(id,), daemon=True)
        threads[id].start()

        Thread(target=start,
               args=(id, room.name, room.chosenSound,
                     [s.to_dict() for s in room.sources])
               ).start()

    room.free = False
    db.session.commit()

    return ""


def startTimer(id):
    while copies[id][1] == False:
        copies[id][0] += 1
        time.sleep(1)


@api.route('/stopRec', methods=["POST"])
@token_required
def stopRec(current_user):
    post_data = request.get_json()
    id = post_data['id']

    room = Room.query.get(id)
    copies[id] = [0, True]

    if room.free == False:
        Thread(target=stop, args=(id,)).start()

    room.free = True
    room.timestamp = 0
    db.session.commit()

    return ""


@api.route('/sound', methods=['POST'])
@token_required
def soundChange(current_user):
    post_data = request.get_json()
    id = post_data['id']
    soundType = post_data['sound']

    room = Room.query.get(id)
    room.chosenSound = soundType
    changedSound(room.to_dict())
    db.session.commit()

    return ""
