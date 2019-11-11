from .models import db, Room, Source, User, nvr_db_context
from .email import send_verify_email, send_access_request_email
from flask import Blueprint, jsonify, request, current_app

import time
from datetime import datetime, timedelta
from functools import wraps
from threading import Thread
import os
import uuid
import jwt
from calendarAPI.calendarSettings import create_calendar, delete_calendar, give_permissions
from driveAPI.startstop import start, stop, upload_file
from driveAPI.driveSettings import create_folder, move_file

api = Blueprint('api', __name__)

CAMPUS = os.environ.get('CAMPUS')


# AUTHENTICATE
def auth_required(f):
    """
    Verification wrapper to make sure that user is logged in
    """
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()
        api_key = request.headers.get('key', '')

        invalid_msg = {
            'message': 'Ошибка доступа',
            'autheticated': False
        }
        expired_msg = {
            'message': 'Истёкшая сессия',
            'autheticated': False
        }

        if len(auth_headers) == 2:
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
                print(e)
                return jsonify({'error': "Check logs"}), 401
        elif api_key:
            try:
                user = User.query.filter_by(api_key=api_key).first()
                if not user:
                    raise RuntimeError('Пользователь не найден')
                return f(user, *args, **kwargs)
            except Exception as e:
                print(e)
                return jsonify({'error': "Check logs"}), 401

        return jsonify(invalid_msg), 401

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
    try:
        send_verify_email(user, token_expiration)
        Thread(target=user.delete_user_after_token_expiration,
               args=(current_app._get_current_object(), token_expiration)).start()
    except Exception as e:
        print(e)

    return jsonify(user.to_dict()), 201


@api.route('/verify-email/<token>', methods=['POST', 'GET'])
def verify_email(token):
    user = User.verify_email_token(token)
    if not user:
        return "Ошибка. Время на подтверждение вышло", 401

    if user.email_verified:
        return "Почта уже подтверждена", 401

    user.email_verified = True
    db.session.commit()

    send_access_request_email(
        [u.email for u in User.query.all() if u.role != 'user'], user.email)

    return "Подтверждение успешно, ожидайте одобрения администратора", 201


@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.authenticate(**data)

    if not user:
        return jsonify({'message': "Неверные данные", 'authenticated': False}), 401

    if not user.email_verified:
        return jsonify({'message': 'Почта не подтверждена', 'authenticated': False}), 401

    if not user.access:
        return jsonify({'message': 'Администратор ещё не открыл доступ для этого аккаунта',
                        'authenticated': False}), 401

    token = jwt.encode({
        'sub': {'email': user.email, 'role': user.role, 'api_key': user.api_key},
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=80)},
        current_app.config['SECRET_KEY'])

    return jsonify({'token': token.decode('UTF-8')})


@api.route('/users', methods=['GET'])
@auth_required
def get_users(current_user):
    users = [u.to_dict() for u in User.query.all() if u.email_verified]
    return jsonify(users)


@api.route('/users/<user_id>', methods=['PUT'])
@auth_required
def grant_access(current_user, user_id):
    if current_user.role == 'user':
        return jsonify({'message': "Ошибка доступа"}), 401
    user = User.query.get(user_id)
    user.access = True
    db.session.commit()

    Thread(target=give_permissions, args=(
        current_app._get_current_object(), CAMPUS, user.email)).start()

    return "Success", 201


@api.route('/users/roles/<user_id>', methods=['PUT'])
@auth_required
def user_role(current_user, user_id):
    if current_user.role == 'user':
        return jsonify({'message': "Ошибка доступа"}), 401
    user = User.query.get(user_id)
    user.role = request.get_json()['role']
    db.session.commit()
    return "Success", 201


@api.route('/users/<user_id>', methods=['DELETE'])
@auth_required
def delete_user(current_user, user_id):
    if current_user.role == 'user':
        return jsonify({'message': "Ошибка доступа"}), 401
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return "Success", 201


@api.route('/api-key/<email>', methods=['POST', 'PUT', 'DELETE'])
@auth_required
def create_api_key(current_user, email):
    user = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        if user.api_key:
            return jsonify({'message': 'Ключ API уже существует'}), 401

        user.api_key = uuid.uuid4().hex
        db.session.commit()

        return jsonify({'api_key': user.api_key}), 200

    if request.method == 'PUT':
        user.api_key = uuid.uuid4().hex
        db.session.commit()

        return jsonify({'api_key': user.api_key}), 200

    if request.method == 'DELETE':
        user.api_key = None
        db.session.commit()

        return jsonify({'api_key': user.api_key}), 200


# GOOGLE API
@api.route('/move-file', methods=['POST'])
def move_file():
    data = request.get_json()

    file_id = data['file_id']
    room_id = data['room_id']

    room = Room.query.get(room_id)

    move_file(file_id, room.drive)
    return "Success", 201


# RECORD AND GOOGLE API
@api.route('/rooms', methods=['POST'])
@auth_required
def create_room(current_user):
    if current_user.role == 'user':
        return jsonify({'message': "Ошибка доступа"}), 401

    name = request.get_json()['name']

    Thread(target=config_room, args=(
        current_app._get_current_object(), name)).start()

    return jsonify({'name': name}), 201


@nvr_db_context
def config_room(name):
    room = Room(name=name)
    room.drive = create_folder(
        CAMPUS,
        name
    )
    room.calendar = create_calendar(
        CAMPUS,
        name
    )
    room.sources = []
    db.session.add(room)
    db.session.commit()


@api.route('/rooms/', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    return jsonify([r.to_dict() for r in rooms]), 200


@api.route('/rooms/<room_id>', methods=['DELETE'])
@auth_required
def delete_room(current_user, room_id):
    if current_user.role == 'user':
        return jsonify({'message': "Ошибка доступа"}), 401

    room = Room.query.get(room_id)

    Thread(target=delete_calendar, args=(room.calendar,)).start()

    db.session.delete(room)
    db.session.commit()

    return "Success", 201


@api.route("/rooms/<room_id>", methods=['PUT'])
@auth_required
def edit_room(current_user, room_id):
    if current_user.role == 'user':
        return jsonify({'message': "Ошибка доступа"}), 401

    post_data = request.get_json()
    room = Room.query.get(room_id)
    room.sources = []
    for s in post_data['sources']:
        if s.get('id'):
            source = Source.query.get(s['id'])
        else:
            source = Source()
        room.sources.append(source)
        source.ip = s['ip']
        source.name = s['name']
        source.sound = s.get('sound')
        source.tracking = s.get('tracking')
        source.main_cam = s.get('main_cam')
        source.room_id = room_id

    db.session.commit()
    return "Success", 200


@api.route('/start-record', methods=['POST'])
@auth_required
def start_rec(current_user):
    post_data = request.get_json()
    room_id = post_data['id']
    room = Room.query.get(room_id)

    if not room.free:
        return "Already recording", 401

    room.free = False
    db.session.commit()

    Thread(
        target=start_timer,
        args=(current_app._get_current_object(), room_id),
        daemon=True
    ).start()

    Thread(
        target=start,
        args=(current_app._get_current_object(), room_id)
    ).start()

    return "Started", 200


@nvr_db_context
def start_timer(room_id: int) -> None:
    while not Room.query.get(room_id).free:
        Room.query.get(room_id).timestamp += 1
        db.session.commit()
        time.sleep(1)


@api.route('/stop-record', methods=["POST"])
@auth_required
def stop_rec(current_user):
    post_data = request.get_json()
    room_id = post_data['id']

    calendar_id = post_data.get('calendar_id')
    event_id = post_data.get('event_id')

    room = Room.query.get(room_id)

    if room.free:
        return "Already stoped", 401

    room.processing = True
    db.session.commit()

    Thread(target=stop_record, args=(current_app._get_current_object(),
                                     room_id, calendar_id, event_id)).start()

    return 'Stopped', 200


@nvr_db_context
def stop_record(room_id, calendar_id, event_id):
    try:
        stop(current_app._get_current_object(), room_id, calendar_id, event_id)
    except Exception as e:
        pass
    finally:
        room = Room.query.get(room_id)
        room.processing = False
        room.free = True
        room.timestamp = 0
        db.session.commit()


@api.route('/sound-change', methods=['POST'])
@auth_required
def sound_change(current_user):
    post_data = request.get_json()
    room_id = post_data['id']
    sound_type = post_data['sound']

    room = Room.query.get(room_id)
    room.chosen_sound = sound_type
    db.session.commit()

    return "Sound source changed", 200


@api.route('/upload-merged', methods=["POST"])
@auth_required
def upload_merged(current_user):
    post_data = request.get_json(force=True)

    room_id = post_data["room_id"]

    room = Room.query.get(room_id)

    Thread(target=upload_file,
           args=(
               post_data["file_name"],
               room.drive.split('/')[-1],
               post_data.get('calendar_id'),
               post_data.get('event_id')
           ),
           daemon=True
           ).start()

    return "Video uploaded", 200
