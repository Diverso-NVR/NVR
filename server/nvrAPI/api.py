from .models import db, Room, Source, User
from .email import send_verify_email
from flask import Blueprint, jsonify, request, current_app
from driveAPI.startstop import start, stop, upload_file
from driveAPI.driveSettings import create_folder, config_drive, move_file
import time
from datetime import datetime, timedelta
from functools import wraps
from threading import Thread

import jwt
from calendarAPI.calendarSettings import create_calendar, delete_calendar, config_calendar
from calendarAPI.calendar_daemon import config_daemon, update_daemon, changed_sound

api = Blueprint('api', __name__)

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
        return jsonify({"message": 'Пользователь с данной почтой существует'}), 400

    token_expiration = 600
    send_verify_email(user, token_expiration)
    Thread(target=user.delete_user_after_token_expiration,
           args=(current_app._get_current_object(), token_expiration)).start()

    return jsonify(user.to_dict()), 201


@api.route('/verify_email/<token>', methods=['POST', 'GET'])
def verify_email(token):
    user = User.verify_email_token(token)
    if not user:
        return "Время на подтверждение вышло", 401

    user.email_verified = True
    db.session.commit()
    return "Подтверждение успешно", 201


@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.authenticate(**data)

    if not user:
        return jsonify({'message': "Неверные данные", 'authenticated': False}), 401

    if not user.email_verified:
        return jsonify({'message': 'Почта не подтверждена', 'authenticated': False}), 401

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
@token_required
def get_users(current_user):
    users = [u.to_dict() for u in User.query.all() if u.email_verified]
    return jsonify(users)


@api.route('/users/<user_id>', methods=['PUT'])
@token_required
def grant_access(current_user, user_id):
    if current_user.role != 'admin':
        return jsonify({'message': "Ошибка доступа"}), 401
    user = User.query.get(user_id)
    user.access = True
    db.session.commit()
    return "", 201


@api.route('/users/roles/<user_id>', methods=['PUT'])
@token_required
def user_role(current_user, user_id):
    if current_user.role != 'admin':
        return jsonify({'message': "Ошибка доступа"}), 401
    user = User.query.get(user_id)
    user.role = request.get_json()['role']
    db.session.commit()
    return "", 201


@api.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    if current_user.role != 'admin':
        return jsonify({'message': "Ошибка доступа"}), 401
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return "", 201


# GOOGLE API
@api.route('/move-file', methods=['POST'])
def move_file():
    data = request.get_json()

    file_id = data['file_id']
    room_name = data['room_name']

    move_file(file_id, room_name)
    return "Success", 201


# RECORD AND GOOGLE API
@api.route('/rooms', methods=['POST'])
@token_required
def create_room(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': "Ошибка доступа"}), 401
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
    return jsonify([r.to_dict() for r in rooms]), 200


@api.route('/rooms/<room_id>', methods=['DELETE'])
@token_required
def delete_room(current_user, room_id):
    if current_user.role != 'admin':
        return jsonify({'message': "Ошибка доступа"}), 401
    room = Room.query.get(room_id)
    delete_calendar(room.calendar)
    db.session.delete(room)
    db.session.commit()
    return "", 201


@api.route("/rooms/<room_id>", methods=['PUT'])
@token_required
def edit_room(current_user, room_id):
    if current_user.role != 'admin':
        return jsonify({'message': "Ошибка доступа"}), 401
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
        source.room_id = room_id
        source.ip = s['ip']
        source.name = s['name']
        source.sound = s['sound'] if s['sound'] != False else None
        source.tracking = s['tracking']
        source.main_cam = s['main_cam']
    db.session.commit()
    return "", 200


@api.route('/startRec', methods=['POST'])
@token_required
def start_rec(current_user):
    post_data = request.get_json()
    id = post_data['id']
    room = Room.query.get(id)

    if not room.free:
        return "Already recording", 401

    room.free = False
    db.session.commit()

    Thread(target=start_timer, args=(
        current_app._get_current_object(), id), daemon=True).start()

    Thread(target=start,
           args=(id,
                 room.name,
                 room.chosen_sound,
                 [s.to_dict() for s in room.sources])
           ).start()

    return "Started", 200


def start_timer(app, id):
    with app.app_context():
        while not Room.query.get(id).free:
            Room.query.get(id).timestamp += 1
            db.session.commit()
            time.sleep(1)


@api.route('/stopRec', methods=["POST"])
@token_required
def stop_rec(current_user):
    post_data = request.get_json()
    id = post_data['id']

    room = Room.query.get(id)

    if room.free:
        return "Already stoped", 401

    room.processing = True
    db.session.commit()

    stop(id)

    room.processing = False
    room.free = True
    room.timestamp = 0
    db.session.commit()

    return "Stoped", 200


@api.route('/sound', methods=['POST'])
@token_required
def sound_change(current_user):
    post_data = request.get_json()
    id = post_data['id']
    sound_type = post_data['sound']

    room = Room.query.get(id)
    room.chosen_sound = sound_type
    changed_sound(room.to_dict())
    db.session.commit()

    return "Sound source changed", 200


@api.route('/upload_merged', methods=["POST"])
def upload_merged():
    post_data = request.get_json(force=True)

    Thread(target=upload_file,
           args=(
               post_data["file_name"],
               post_data["room_name"],
               post_data.get('calendar_id'),
               post_data.get('event_id')
           ),
           daemon=True
           ).start()

    return "Video uploaded", 200
