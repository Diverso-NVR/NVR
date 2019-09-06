import time
from datetime import datetime, timedelta
from functools import wraps
from threading import Thread
from pathlib import Path

import jwt
from calendarAPI.calendarSettings import create_calendar, delete_calendar, config_calendar
from calendarAPI.calendar_daemon import config_daemon, update_daemon, changed_sound
from driveAPI.driveSettings import create_folder, config_drive, upload
from driveAPI.startstop import start, stop
from flask import Blueprint, jsonify, request, current_app

from .email import send_verify_email
from .models import db, Room, Source, User

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
    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify('Пользователь с данной почтой существует'), 400
    send_verify_email(user)
    return jsonify(user.to_dict()), 201


@api.route('/verify_email/<token>', methods=['POST', 'GET'])
def verify_email(token):
    user = User.verify_email_token(token)
    if not user:
        return "Ошибка", 401

    user.email_verified = True
    db.session.commit()
    return "Подтверждение успешно", 201


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
def get_users():
    users = [u.to_dict() for u in User.query.all() if u.email_verified]
    return jsonify(users)


@api.route('/users/<user_id>', methods=['PUT'])
@token_required
def grant_access(current_user, user_id):
    if current_user.role != 'admin':
        return "", 401
    user = User.query.get(user_id)
    user.access = True
    db.session.commit()
    return "", 201


@api.route('/users/roles/<user_id>', methods=['PUT'])
@token_required
def user_role(current_user, user_id):
    if current_user.role != 'admin':
        return "", 401
    user = User.query.get(user_id)
    print(request.get_json()['role'])
    user.role = request.get_json()['role']
    db.session.commit()
    return "", 201


@api.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    if current_user.role != 'admin':
        return "", 401
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return "", 201


# RECORD AND GOOGLE API
@api.route('/rooms', methods=['POST'])
@token_required
def create_room(current_user):
    if current_user.role != 'admin':
        return "", 401
    post_data = request.get_json()
    room = Room(name=post_data['name'])
    room.drive = create_folder(
        building,
        post_data.get('name')
    )
    room.calendar = create_calendar(
        building,
        post_data.get('name')
    )
    room.sources = []
    db.session.add(room)
    db.session.commit()
    config_calendar(room.to_dict())
    config_drive(room.to_dict())
    config_daemon(room.to_dict())

    return jsonify(room.to_dict()), 201


@api.route('/rooms/', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    for room in rooms:
        try:
            room.timestamp = copies[room.id][0]
            room.free = copies[room.id][1]
        except:
            pass
    return jsonify([r.to_dict() for r in rooms]), 200


@api.route('/rooms/<room_id>', methods=['DELETE'])
@token_required
def delete_room(current_user, room_id):
    if current_user.role != 'admin':
        return "", 401
    room = Room.query.get(room_id)
    delete_calendar(room.calendar)
    db.session.delete(room)
    db.session.commit()
    return "", 201


@api.route("/rooms/<room_id>", methods=['PUT'])
@token_required
def edit_room(current_user, room_id):
    if current_user.role != 'admin':
        return "", 401
    post_data = request.get_json()
    room = Room.query.get(room_id)
    update_daemon(room.to_dict())
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
    return "", 200


@api.route('/startRec', methods=['POST'])
@token_required
def start_rec(current_user):
    post_data = request.get_json()
    id = post_data['id']
    room = Room.query.get(id)
    copies[id] = [0, False]

    if room.free == True:
        threads[id] = Thread(
            target=start_timer, args=(id,), daemon=True)
        threads[id].start()

        Thread(target=start,
               args=(id, room.name, room.chosenSound,
                     [s.to_dict() for s in room.sources])
               ).start()

    room.free = False
    db.session.commit()

    return "", 200


def start_timer(id):
    while not copies[id][1]:
        copies[id][0] += 1
        time.sleep(1)


@api.route('/stopRec', methods=["POST"])
@token_required
def stop_rec(current_user):
    post_data = request.get_json()
    id = post_data['id']

    room = Room.query.get(id)
    copies[id] = [0, True]

    if room.free == False:
        Thread(target=stop, args=(id,)).start()

    room.free = True
    room.timestamp = 0
    db.session.commit()

    return "", 200


@api.route('/sound', methods=['POST'])
@token_required
def sound_change(current_user):
    post_data = request.get_json()
    id = post_data['id']
    soundType = post_data['sound']

    room = Room.query.get(id)
    room.chosenSound = soundType
    changed_sound(room.to_dict())
    db.session.commit()

    return "", 200


@api.route('/upload_merged', methods=["POST"])
def upload_merged():
    post_data = request.get_json()

    try:
        upload(str(Path.home()) + "/vids/" + post_data["file_name"],
               post_data["room_name"])
    except Exception:
        pass

    return "", 200
