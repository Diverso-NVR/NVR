import os
import uuid
from datetime import datetime, timedelta, date
from functools import wraps
from threading import Thread
from pathlib import Path

import traceback

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import jwt
import requests
from flask import Blueprint, jsonify, request, current_app, render_template
from flask_socketio import SocketIO

from apis.calendar_api import create_calendar, delete_calendar, give_permissions, create_event_, get_events
from apis.drive_api import create_folder, get_folders_by_name, upload
from apis.ruz_api import get_room_ruzid
from .email import send_verify_email, send_access_request_email, send_reset_pass_email
from .models import db, Room, Source, User, Record, nvr_db_context

api = Blueprint('api', __name__)

TRACKING_URL = os.environ.get('TRACKING_URL')
NVR_CLIENT_URL = os.environ.get('NVR_CLIENT_URL')
STREAMING_URL = os.environ.get('STREAMING_URL')
STREAMING_API_KEY = os.environ.get('STREAMING_API_KEY')
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
VIDS_PATH = str(Path.home()) + '/vids/'

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
        token = request.headers.get('Token', '')
        api_key = request.headers.get('key', '')

        invalid_msg = {
            'error': 'Ошибка доступа',
            'autheticated': False
        }
        expired_msg = {
            'error': 'Истёкшая сессия',
            'autheticated': False
        }

        if token:
            try:
                data = jwt.decode(token, current_app.config['SECRET_KEY'])
                user = User.query.filter_by(email=data['sub']['email']).first()
                if not user:
                    return jsonify({'error': "User not found"}), 404
                return f(user, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify(expired_msg), 403
            except jwt.InvalidTokenError:
                return jsonify(invalid_msg), 403
            except Exception as e:
                traceback.print_exc()
                return jsonify({'error': "Server error"}), 500
        elif api_key:
            try:
                user = User.query.filter_by(api_key=api_key).first()
                if not user:
                    return jsonify({'error': "Wrong API key"}), 400
                return f(user, *args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                return jsonify({'error': "Server error"}), 500

        return jsonify(invalid_msg), 403

    return _verify


def admin_only(f):
    @wraps(f)
    def wrapper(user, *args, **kwargs):
        if user.role in ['user', 'editor']:
            return jsonify({'error': "Access error"}), 401
        return f(user, *args, **kwargs)

    return wrapper


def admin_or_editor_only(f):
    @wraps(f)
    def wrapper(user, *args, **kwargs):
        if user.role == 'user':
            return jsonify({'error': "Access error"}), 401
        return f(user, *args, **kwargs)

    return wrapper


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
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500

    return jsonify(user.to_dict()), 202


@api.route('/verify-email/<token>', methods=['POST', 'GET'])
def verify_email(token):
    user = User.verify_token(token, 'verify_email')
    if not user:
        return render_template('msg_template.html',
                               msg={'title': 'Подтверждение почты',
                                    'text': "Время на подтверждение вышло. Зарегистрируйтесь ещё раз"},
                               url=NVR_CLIENT_URL), 404

    if user.email_verified:
        return render_template('msg_template.html',
                               msg={'title': 'Подтверждение почты',
                                    'text': "Почта уже подтверждена",
                                    },
                               url=NVR_CLIENT_URL), 409

    user.email_verified = True
    db.session.commit()

    try:
        send_access_request_email(
            [u.email for u in User.query.all() if u.role not in ['user', 'editor']], user)
    except Exception as e:
        traceback.print_exc()
        return "Server error", 500

    emit_event('new_user', {'user': user.to_dict()})

    return render_template('msg_template.html',
                           msg={'title': 'Подтверждение почты',
                                'text': "Подтверждение успешно, ожидайте одобрения администратора"},
                           url=NVR_CLIENT_URL), 202


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
        'sub': {'email': user.email, 'role': user.role},
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(weeks=12)},
        current_app.config['SECRET_KEY'])

    return jsonify({'token': token.decode('UTF-8')}), 202


@api.route('/google-login', methods=['POST'])
def glogin():
    data = request.get_json()
    token = data.get('token')
    if not token:
        return jsonify({'error': "Bad request"}), 400

    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), GOOGLE_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        email = idinfo['email']

    except ValueError:
        return jsonify({'error': "Bad token"}), 403

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        user.email_verified = True
        user.access = True

        db.session.add(user)
        db.session.commit()

    token = jwt.encode({
        'sub': {'email': user.email, 'role': user.role},
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(weeks=12)},
        current_app.config['SECRET_KEY'])

    return jsonify({'token': token.decode('UTF-8')}), 202

# RESET PASS


@api.route('/reset-pass/<email>', methods=['POST'])
def send_reset_pass(email):
    user = User.query.filter_by(email=str(email)).first()
    if not user:
        return jsonify({"error": "User doesn`t exist"}), 404

    token_expiration = 300
    try:
        send_reset_pass_email(user, token_expiration)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500

    return jsonify({"message": "Reset pass token generated"}), 200


@api.route('/reset-pass/<token>', methods=['PUT'])
@json_data_required
def reset_pass(token):
    data = request.get_json()

    new_pass = data.get('new_pass')
    if not new_pass:
        return jsonify({"error": "New password required"}), 400

    user = User.verify_token(token, 'reset_pass')
    if not user:
        return jsonify({"error": "Invalid token"}), 403

    user.update_pass(new_pass)
    db.session.commit()

    return jsonify({"message": "Password updated"}), 200


# USERS
@api.route('/users', methods=['GET'])
@auth_required
@admin_only
def get_users(current_user):
    users = [u.to_dict() for u in User.query.all() if u.email_verified]
    return jsonify(users), 200


@api.route('/users/<user_id>', methods=['PUT'])
@auth_required
@admin_only
def grant_access(current_user, user_id):
    user = User.query.get(user_id)
    user.access = True
    db.session.commit()

    Thread(target=give_permissions, args=(
        current_app._get_current_object(), user.email)).start()

    emit_event('grant_access', {'id': user.id})

    return jsonify({"message": "Access granted"}), 202


@api.route('/users/roles/<user_id>', methods=['PUT'])
@auth_required
@admin_only
def user_role(current_user, user_id):
    user = User.query.get(user_id)
    user.role = request.get_json()['role']
    db.session.commit()

    emit_event('change_role', {'id': user.id, 'role': user.role})

    return jsonify({"message": "User role changed"}), 200


@api.route('/users/<user_id>', methods=['DELETE'])
@auth_required
@admin_only
def delete_user(current_user, user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    emit_event('delete_user', {'id': user.id})

    return jsonify({"message": "User deleted"}), 200


@api.route('/api-key/<email>', methods=['GET', 'POST', 'PUT', 'DELETE'])
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

        return jsonify({'key': user.api_key}), 201

    if request.method == 'GET':
        return jsonify({"key": user.api_key}), 200

    if request.method == 'PUT':
        user.api_key = uuid.uuid4().hex
        db.session.commit()

        return jsonify({'key': user.api_key}), 202

    if request.method == 'DELETE':
        user.api_key = None
        db.session.commit()

        return jsonify({'message': "API key deleted"}), 200


# GOOGLE API
@api.route('/gcalendar-event/<room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
@json_data_required
def create_calendar_event(current_user, room_name):
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
        return jsonify({'error': f"No room found with name '{room_name}'"}), 400

    return jsonify({'message': f"Successfully created event: {event_link}"}), 201


@api.route('/gdrive-upload/<room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
def upload_video_to_drive(current_user, room_name):
    if not request.files:
        return {"error": "No file provided"}, 400

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": f"Room '{room_name}' not found"}), 400

    file = request.files['file']
    file_name = file.filename
    file.save(VIDS_PATH + file_name)

    try:
        date = file_name.split('_')[0]
        time = file_name.split('_')[1].split('.')[0]
    except:
        return {"error": "Incorrect file name"}, 400

    folder = ''

    # TODO можно наверно через mimetype в функции но мне так лень и времени нет хочу сдохнуть
    date_folders = get_folders_by_name(date)
    time_folders = get_folders_by_name(time)
    for folder_id, folder_parent_id in date_folders.items():
        if folder_parent_id == room.drive.split('/')[-1]:
            for f_id, fp_id in time_folders.items():
                if fp_id == folder_id:
                    folder = f_id
    if not folder:
        folder = room.drive.split('/')[-1]

    Thread(target=upload, args=(VIDS_PATH + file_name,
                                folder)).start()

    return jsonify({"message": "Upload to disk started"}), 200


@api.route('/gconfigure/<string:room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
def create_drive_and_calendar(current_user, room_name):
    drive = create_folder(room_name)
    calendar = create_calendar(room_name)
    return jsonify({"drive": drive, "calendar": calendar}), 201


# ROOMS
@api.route('/rooms/<room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
def create_room(current_user, room_name):
    if not room_name:
        return jsonify({"error": "Room name required"}), 400

    room = Room.query.filter_by(name=room_name).first()
    if room:
        return jsonify({"error": f"Room '{room_name}' already exist"}), 409

    room = Room(name=room_name)
    room.sources = []
    db.session.add(room)
    db.session.commit()

    emit_event('add_room', {'room': room.to_dict()})

    Thread(target=config_room, args=(
        current_app._get_current_object(), room_name)).start()

    return jsonify({'message': f"Started creating '{room_name}'"}), 204


@nvr_db_context
def config_room(room_name):
    room = Room.query.filter_by(name=room_name).first()
    room.drive = create_folder(room_name)
    room.calendar = create_calendar(room_name)
    room.ruz_id = get_room_ruzid(room_name)
    db.session.commit()


@api.route('/rooms/', methods=['GET'])
@auth_required
def get_rooms(current_user):
    return jsonify([r.to_dict() for r in Room.query.all()]), 200


@api.route('/rooms/<room_name>', methods=['GET'])
@auth_required
def get_room(current_user, room_name):
    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 400
    return jsonify(room.to_dict()), 200


@api.route('/rooms/<room_name>', methods=['DELETE'])
@auth_required
@admin_or_editor_only
def delete_room(current_user, room_name):
    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 400

    Thread(target=delete_calendar, args=(room.calendar,)).start()

    db.session.delete(room)
    db.session.commit()

    emit_event('delete_room', {'id': room.id, 'name': room.name})

    return jsonify({"message": "Room deleted"}), 200


@api.route("/rooms/<room_name>", methods=['PUT'])
@auth_required
@admin_or_editor_only
@json_data_required
def edit_room(current_user, room_name):
    post_data = request.get_json()

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given 'room_name'"}), 400
    if not post_data.get('sources'):
        return jsonify({"error": "Sources array required"}), 400

    for s in post_data['sources']:
        if s.get('id'):
            source = Source.query.get(s['id'])
            source.update(**s)
        else:
            source = Source(**s)
            source.room_id = room.id
            db.session.add(source)

    db.session.commit()

    emit_event('edit_room', {room.to_dict()})

    return jsonify({"message": "Room edited"}), 200


@api.route('/set-source/<room_name>/<source_type>/<path:ip>', methods=['POST'])
@auth_required
@admin_or_editor_only
def room_settings(current_user, room_name, source_type, ip):
    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with provided room_name"}), 400

    source_type = source_type.lower()
    if source_type not in ['main', 'screen', 'track', 'sound']:
        return jsonify({"error": f"Incorrect source type: {source_type}"}), 400

    if ip not in [s.ip for s in room.sources]:
        return jsonify({"error": f"Source with provided ip not in room`s sources list"}), 400

    if source_type == 'main':
        room.main_source = ip
    elif source_type == 'screen':
        room.screen_source = ip
    elif source_type == 'sound':
        room.sound_source = ip
    else:
        room.tracking_source = ip

    db.session.commit()

    emit_event('edit_room', {room.to_dict()})

    return jsonify({"message": "Source set"}), 200


@api.route("/sources/", methods=['GET'])
@auth_required
def get_sources(current_user):
    return jsonify([s.to_dict() for s in Source.query.all()]), 200


@api.route("/sources/<path:ip>", methods=['POST', 'GET', 'DELETE', 'PUT'])
@auth_required
@admin_or_editor_only
def manage_source(current_user, ip):
    if request.method == 'POST':
        data = request.get_json()
        room_name = data.get('room_name')
        if not room_name:
            return jsonify({"error": "room_name required"}), 400
        room = Room.query.filter_by(name=str(room_name)).first()
        if not room:
            return jsonify({"error": "No room found with provided room_name"}), 400

        data['room_id'] = room.id
        source = Source(ip=ip, **data)
        db.session.add(source)
        db.session.commit()

        emit_event('edit_room', {'id': room.id, 'sources': [
            s.to_dict() for s in room.sources]})

        return jsonify({'message': 'Added'}), 201

    for source in Source.query.all():
        if ip in source.ip:
            break
    else:
        return jsonify({'error': 'No source with provided ip found'}), 400

    room_id = source.room_id

    if request.method == 'GET':
        return jsonify(source.to_dict()), 200

    if request.method == 'DELETE':
        db.session.delete(source)
        db.session.commit()

        emit_event('edit_room', {'id': room_id, 'sources': [
            s.to_dict() for s in Room.query.get(room_id).sources]})

        return jsonify({'message': 'Deleted'}), 200

    if request.method == 'PUT':
        s = request.get_json()
        source_dict = source.to_dict()
        updated_source_dict = {**source_dict, **s}

        db.session.delete(source)

        source = Source(**updated_source_dict)
        db.session.add(source)
        db.session.commit()

        emit_event('edit_room', {'id': room_id, 'sources': [
            s.to_dict() for s in Room.query.get(room_id).sources]})

        return jsonify({'message': 'Updated'}), 200


# MERGER
@api.route('/calendar-notifications/', methods=["POST"])
def gcalendar_webhook():
    calendar_id = request.headers['X-Goog-Resource-Uri'].split('/')[6]
    calendar_id = calendar_id.replace('%40', '@')
    events = get_events(calendar_id)

    room = Room.query.filter_by(calendar=calendar_id).first()
    records = Record.query.filter(
        Record.room_name == room.name,
        Record.event_id != None).all()
    calendar_events = set(events.keys())
    db_events = {record.event_id for record in records}

    new_events = calendar_events - db_events
    deleted_events = db_events - calendar_events
    events_to_check = calendar_events & db_events

    for event_id in deleted_events:
        record = Record.query.filter_by(event_id=event_id).first()
        if record.done or record.processing:
            continue

        db.session.delete(record)

    for event_id in new_events:
        event = events[event_id]
        start_date = event['start']['dateTime'].split('T')[0]
        end_date = event['end']['dateTime'].split('T')[0]

        if start_date != end_date:
            continue

        new_record = Record()
        new_record.update_from_calendar(**event, room_name=room.name)
        db.session.add(new_record)

    for event_id in events_to_check:
        event = events[event_id]
        if date.today().isoformat() != event['updated'].split('T')[0]:
            continue

        record = Record.query.filter_by(event_id=event_id).first()
        if record.done or record.processing:
            continue

        record.update_from_calendar(**event, room_name=room.name)

    db.session.commit()
    db.session.close()

    return jsonify({"message": "Room calendar events patched"}), 200


@api.route('/montage-event/<room_name>', methods=["POST"])
@auth_required
@json_data_required
def create_montage_event(current_user, room_name):
    json = request.get_json()

    event_name = json.get("event_name")
    date = json.get("date")
    start_time = json.get("start_time")
    end_time = json.get("end_time")
    user_email = json.get("user_email", current_user.email)

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 400

    if not date:
        return jsonify({"error": "'date' required"}), 400
    if not start_time:
        return jsonify({"error": "'start_time' required"}), 400
    if not end_time:
        return jsonify({"error": "'end_time' required"}), 400

    date_time_start = datetime.strptime(
        f'{date} {start_time}', '%Y-%m-%d %H:%M')
    date_time_end = datetime.strptime(
        f'{date} {end_time}', '%Y-%m-%d %H:%M')

    start_timestamp = int(date_time_start.timestamp())
    end_timestamp = int(date_time_end.timestamp())

    if start_timestamp >= end_timestamp:
        return jsonify({"error": "Неверный промежуток времени"}), 400

    record = Record(event_name=event_name, room_name=room.name, date=date,
                    start_time=start_time, end_time=end_time, user_email=user_email)

    db.session.add(record)
    db.session.commit()
    db.session.close()

    return jsonify({'message': f"Merge event '{event_name}' added to queue"}), 201


@api.route('/tracking/<room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
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
        return jsonify({"error": "No room found with given room_name"}), 400

    if not room.tracking_source:
        return jsonify({"error": "No tracking cam selected in requested room"}), 400

    command = command.lower()
    try:
        if command == 'start':
            res = requests.post(f'{TRACKING_URL}/track', json={
                'ip': room.tracking_source}, timeout=5)
        else:
            res = requests.delete(f'{TRACKING_URL}/track')

        room.tracking_state = True if command == 'start' else False
        db.session.commit()

        emit_event('tracking_state_change', {
            'id': room.id, 'tracking_state': room.tracking_state, 'room_name': room.name})

        return jsonify(res.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/streaming-start/<room_name>', methods=['POST'])
@auth_required
@json_data_required
def streaming_start(current_user, room_name):
    data = request.get_json()

    sound_ip = data.get('sound_ip')
    camera_ip = data.get('camera_ip')
    title = data.get('title')

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": f"Room {room_name} not found"}), 404
    if room.stream_url:
        return jsonify({"error": f"Stream is already running on {room.stream_url}"}), 409

    if not sound_ip:
        return jsonify({"error": "Sound source ip not provided"}), 400
    if not camera_ip:
        return jsonify({"error": "Camera ip not provided"}), 400

    sound_source = Source.query.filter_by(ip=sound_ip).first()
    camera_source = Source.query.filter_by(ip=camera_ip).first()

    try:
        response = requests.post(f"{STREAMING_URL}/streams/{room_name}", json={
            "camera_ip": camera_source.rtsp,
            "sound_ip": sound_source.rtsp,
            'title': title
        }, headers={'X-API-KEY': STREAMING_API_KEY})
        url = response.json()['url']
        room.stream_url = url
        db.session.commit()
    except:
        return jsonify({"error": "Unable to start stream"}), 500

    return jsonify({"message": "Streaming started", 'url': url}), 200


@api.route('/streaming-stop/<room_name>', methods=['POST'])
@auth_required
@json_data_required
def streaming_stop(current_user, room_name):
    data = request.get_json()

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": f"Room {room_name} not found"}), 404
    if not room.stream_url:
        return jsonify({"error": f"Stream is not running"}), 400

    try:
        response = requests.delete(
            f'{STREAMING_URL}/streams/{room_name}',
            headers={'X-API-KEY': STREAMING_API_KEY})
    except:
        return jsonify({"error": "Unable to stop stream"}), 500
    finally:
        room.stream_url = None
        db.session.commit()

    return jsonify({"message": "Streaming stopped"}), 200


@api.route('/auto-control/<room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
@json_data_required
def auto_control(current_user, room_name):
    data = request.get_json()

    auto_control = data.get('auto_control')

    if auto_control is None:
        return jsonify({"error": "Boolean value not provided"}), 400

    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": f"Room {room_name} not found"}), 404

    room.auto_control = auto_control
    db.session.commit()

    emit_event('auto_control_change', {
        'id': room.id, 'auto_control': room.auto_control, 'room_name': room.name})

    return jsonify({"message": f"Automatic control within room {room_name} \
                    has been set to {auto_control}"}), 200


@api.route('/records/<user_email>', methods=['GET'])
@auth_required
def get_urls(current_user, user_email):
    records = Record.query.filter(
        Record.user_email == user_email).all()
    return jsonify([rec.to_dict() for rec in records]), 200