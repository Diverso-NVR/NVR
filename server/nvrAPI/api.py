from flask import Blueprint, jsonify, request, current_app
from flask_socketio import SocketIO
from datetime import datetime, timedelta
from functools import wraps
from threading import Thread
import os
import uuid
import jwt
import requests
import time

from .models import db, Room, Source, User, nvr_db_context
from .email import send_verify_email, send_access_request_email
from calendarAPI.calendarSettings import create_calendar, delete_calendar, give_permissions, create_event_
from driveAPI.startstop import start, stop, upload_file
from driveAPI.driveSettings import create_folder, move_file

api = Blueprint('api', __name__)

CAMPUS = os.environ.get('CAMPUS')
TRACKING_URL = os.environ.get('TRACKING_URL')
NVR_CLIENT_URL = os.environ.get('NVR_CLIENT_URL')

socketio = SocketIO(message_queue='redis://',
                    cors_allowed_origins=NVR_CLIENT_URL)


def emit_event(event, data):
    socketio.emit(event,
                  data,
                  broadcast=True,
                  namespace='/websocket')


# DECORATORS
def auth_required(f):
    """
    Verification wrapper to make sure that user is logged in
    """
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()
        api_key = request.headers.get('key', '')

        invalid_msg = {
            'error': 'Ошибка доступа',
            'autheticated': False
        }
        expired_msg = {
            'error': 'Истёкшая сессия',
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
                return jsonify({'error': str(e)}), 400
        elif api_key:
            try:
                user = User.query.filter_by(api_key=api_key).first()
                if not user:
                    raise RuntimeError('Неверный ключ API')
                return f(user, *args, **kwargs)
            except Exception as e:
                print(e)
                return jsonify({'error': str(e)}), 500

        return jsonify(invalid_msg), 401

    return _verify


def json_data_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        post_data = request.get_json()
        if not post_data:
            return jsonify({"error": "json data required"}), 400
        return f(*args, **kwargs)
    return wrapper

# AUTHENTICATE
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(**data)

    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify({"error": 'Пользователь с данной почтой существует'}), 409

    token_expiration = 600

    try:
        send_verify_email(user, token_expiration)
        Thread(target=user.delete_user_after_token_expiration,
               args=(current_app._get_current_object(), token_expiration)).start()
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

    return jsonify(user.to_dict()), 202


@api.route('/verify-email/<token>', methods=['POST', 'GET'])
def verify_email(token):
    user = User.verify_email_token(token)
    if not user:
        return "Время на подтверждение вышло. Зарегистрируйтесь ещё раз", 404

    if user.email_verified:
        return "Почта уже подтверждена", 200

    user.email_verified = True
    db.session.commit()

    try:
        send_access_request_email(
            [u.email for u in User.query.all() if u.role != 'user'], user.email)
    except Exception as e:
        return str(e), 500

    return "Подтверждение успешно, ожидайте одобрения администратора", 202


@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.authenticate(**data)

    if not user:
        return jsonify({'error': "Неверные данные", 'authenticated': False}), 401

    if not user.email_verified:
        return jsonify({'error': 'Почта не подтверждена', 'authenticated': False}), 401

    if not user.access:
        return jsonify({'error': 'Администратор ещё не открыл доступ для этого аккаунта',
                        'authenticated': False}), 401

    token = jwt.encode({
        'sub': {'email': user.email, 'role': user.role, 'api_key': user.api_key},
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=80)},
        current_app.config['SECRET_KEY'])

    return jsonify({'token': token.decode('UTF-8')}), 202


@api.route('/users', methods=['GET'])
@auth_required
def get_users(current_user):
    users = [u.to_dict() for u in User.query.all() if u.email_verified]
    return jsonify(users), 200


@api.route('/users/<user_id>', methods=['PUT'])
@auth_required
def grant_access(current_user, user_id):
    if current_user.role == 'user':
        return jsonify({'error': "Access error"}), 401

    user = User.query.get(user_id)
    user.access = True
    db.session.commit()

    Thread(target=give_permissions, args=(
        current_app._get_current_object(), user.email)).start()

    emit_event('grant_access', {'id': user.id})

    return jsonify({"message": "Access granted"}), 202


@api.route('/users/roles/<user_id>', methods=['PUT'])
@auth_required
def user_role(current_user, user_id):
    if current_user.role == 'user':
        return jsonify({'error': "Access error"}), 401

    user = User.query.get(user_id)
    user.role = request.get_json()['role']
    db.session.commit()

    emit_event('change_role', {'id': user.id, 'role': user.role})

    return jsonify({"message": "User role changed"}), 200


@api.route('/users/<user_id>', methods=['DELETE'])
@auth_required
def delete_user(current_user, user_id):
    if current_user.role == 'user':
        return jsonify({'error': "Access error"}), 401

    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    emit_event('delete_user', {'id': user.id})

    return jsonify({"message": "User deleted"}), 200


@api.route('/api-key/<email>', methods=['POST', 'PUT', 'DELETE'])
@auth_required
def manage_api_key(current_user, email):
    user = User.query.filter_by(email=email).first()
    if current_user.role == 'user' or email != current_user.email:
        return jsonify({'error': "Access error"}), 401

    if request.method == 'POST':
        if user.api_key:
            return jsonify({'error': 'Ключ API уже существует'}), 409

        user.api_key = uuid.uuid4().hex
        db.session.commit()

        return jsonify({'api_key': user.api_key}), 201

    if request.method == 'PUT':
        user.api_key = uuid.uuid4().hex
        db.session.commit()

        return jsonify({'api_key': user.api_key}), 202

    if request.method == 'DELETE':
        user.api_key = None
        db.session.commit()

        return jsonify({'api_key': user.api_key}), 202


# GOOGLE API
@api.route('/create-event/<room_name>', methods=['POST'])
@auth_required
@json_data_required
def create_event(current_user, room_name):
    data = request.get_json()

    start_time = data.get('start_time')

    if not start_time:
        return jsonify({"error": "Start time required"}), 400

    end_time = data.get('end_time')
    summary = data.get('summary', '')

    try:
        event_link = create_event_(
            current_app._get_current_object(), room_name=str(room_name),
            start_time=start_time, end_time=end_time, summary=summary)
    except ValueError:
        return jsonify({'error': 'Format error: date format should be YYYY-MM-DDTHH:mm'}), 400
    except NameError:
        return jsonify({'error': f"No room found with name '{room_name}'"}), 404

    return jsonify({'message': f"Successfully created event: {event_link}"}), 201

# ROOMS
@api.route('/rooms/<room_name>', methods=['POST'])
@auth_required
def create_room(current_user, room_name):
    if current_user.role == 'user':
        return jsonify({'error': "Access error"}), 401

    if not room_name:
        return jsonify({"error": "Room name required"}), 400

    room = Room.query.filter_by(name=room_name).first()
    if room:
        return jsonify({"error": f"Room '{room_name}' already exist"}), 409

    room = Room(name=room_name)
    db.session.add(room)
    db.session.commit()

    Thread(target=config_room, args=(
        current_app._get_current_object(), room_name)).start()

    return jsonify({'message': f"Started creating '{room_name}'"}), 201


@nvr_db_context
def config_room(name):
    room = Room.query.filter_by(name=name).first()
    room.drive = create_folder(f'{CAMPUS}-{name}')
    room.calendar = create_calendar(CAMPUS, name)
    room.sources = []
    db.session.commit()

    emit_event('add_room', {'room': room.to_dict()})


@api.route('/rooms/', methods=['GET'])
@auth_required
def get_rooms(current_user):
    return jsonify([r.to_dict() for r in Room.query.all()]), 200


@api.route('/rooms/<room_name>', methods=['GET'])
@auth_required
def get_room(current_user, room_name):
    return jsonify({"room": Room.query.filter_by(name=str(room_name)).first().to_dict()}), 200


@api.route('/rooms/<room_name>', methods=['DELETE'])
@auth_required
def delete_room(current_user, room_name):
    if current_user.role == 'user':
        return jsonify({'error': "Access error"}), 401

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 404

    Thread(target=delete_calendar, args=(room.calendar,)).start()

    db.session.delete(room)
    db.session.commit()

    emit_event('delete_room', {'id': room.id, 'name': room.name})

    return jsonify({"message": "Room deleted"}), 200


@api.route("/rooms/<room_name>", methods=['PUT'])
@auth_required
@json_data_required
def edit_room(current_user, room_name):
    if current_user.role == 'user':
        return jsonify({'error': "Access error"}), 401

    post_data = request.get_json()

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 404
    if not post_data.get('sources'):
        return jsonify({"error": "Sources required"}), 400

    for s in post_data['sources']:
        if s.get('id'):
            source = Source.query.get(s['id'])
        else:
            source = Source()
            room.sources.append(source)
        source.ip = s.get('ip', "0.0.0.0")
        source.name = s.get('name', 'камера')
        source.sound = s.get('sound', 'enc')
        source.tracking = s.get('tracking', False)
        source.main_cam = s.get('main_cam', False)
        source.room_id = room.id

    db.session.commit()

    emit_event('edit_room', {'id': room.id, 'sources': [
        s.to_dict() for s in room.sources]})

    return jsonify({"message": "Room edited"}), 200


@api.route('/start-record/<room_name>', methods=['POST'])
@auth_required
def start_rec(current_user, room_name):
    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 404

    if not room.free:
        return jsonify({"message": "Already recording"}), 409

    room.free = False
    room.timestamp = int(time.time())
    db.session.commit()

    Thread(
        target=start,
        args=(current_app._get_current_object(), room.id)
    ).start()

    emit_event('start_rec', {'id': room.id})

    return jsonify({"message": f"Record started in '{room.name}'"}), 200


@api.route('/stop-record/<room_name>', methods=["POST"])
@auth_required
def stop_rec(current_user, room_name):
    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 404

    post_data = request.get_json()

    if post_data:
        calendar_id = post_data.get('calendar_id')
        event_id = post_data.get('event_id')
    else:
        calendar_id, event_id = None, None

    if room.free:
        return jsonify({"message": "Already stopped"}), 409

    Thread(target=stop,
           args=(current_app._get_current_object(),
                 room.id, calendar_id, event_id)).start()

    room = Room.query.get(room.id)
    room.free = True
    room.timestamp = 0
    db.session.commit()

    emit_event('stop_rec', {'id': room.id})

    return jsonify({"message": f"Record stopped in '{room.name}'"}), 200


@api.route('/sound-change/<room_name>', methods=['POST'])
@auth_required
@json_data_required
def sound_change(current_user, room_name):
    post_data = request.get_json()
    sound_type = post_data.get('sound')

    if not sound_type:
        return jsonify({"error": "Sound type required"}), 400

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 404

    room.chosen_sound = sound_type
    db.session.commit()

    emit_event('sound_change', {'id': room.id,
                                'sound': sound_type})

    return jsonify({"message": "Sound source changed"}), 200


@api.route('/tracking/<room_name>', methods=['POST'])
@auth_required
@json_data_required
def tracking_manage(current_user, room_name):
    post_data = request.get_json()

    command = post_data.get('command')

    if not command:
        return jsonify({"error": "Command required"}), 400
    if command not in ['start', 'stop', 'status']:
        return jsonify({'error': "Incorrect command"}), 400

    if command == 'status':
        res = requests.get(f'{TRACKING_URL}/status', timeout=5)
        return jsonify(res.json()), 200

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 404

    tracking_cam_ip = get_tracking_cam(
        [s.to_dict() for s in room.sources])

    if not tracking_cam_ip:
        return jsonify({"error": "No tracking cam selected in requested room"}), 405

    command = command.lower()

    try:
        if command == 'start':
            res = requests.post(f'{TRACKING_URL}/track', json={
                                'ip': tracking_cam_ip}, timeout=5)
        else:
            res = requests.delete(f'{TRACKING_URL}/track')

        room.tracking_state = True if command == 'start' else False
        db.session.commit()

        emit_event('tracking_state_change', {
            'id': room.id, 'tracking_state': room.tracking_state, 'room_name': room.name})

        return jsonify(res.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 417


def get_tracking_cam(sources):
    for source in sources:
        if source['tracking']:
            return source['ip'].split('@')[-1]


@api.route('/upload-merged', methods=["POST"])
@auth_required
@json_data_required
def upload_merged(current_user):
    post_data = request.get_json(force=True)

    room_id = post_data.get("room_id")
    if not room_id:
        return jsonify({"error": "Room id required"}), 400

    room = Room.query.get(room_id)

    Thread(target=upload_file,
           args=(
               post_data["file_name"],
               post_data["folder_id"],
               post_data.get('calendar_id'),
               post_data.get('event_id')
           ),
           daemon=True
           ).start()

    return jsonify({"message": "Video uploading"}), 200
