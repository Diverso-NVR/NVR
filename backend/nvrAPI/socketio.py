import logging
import os
from functools import wraps
from threading import Thread

import requests
from flask import current_app, render_template
from flask_socketio import emit, Namespace

from apis.calendar_api import create_calendar, delete_calendar, give_permissions
from apis.drive_api import create_folder
from .email import send_email
from .models import db, Room, Source, User, nvr_db_context

TRACKING_URL = os.environ.get('TRACKING_URL')
STREAMING_URL = os.environ.get('STREAMING_URL')
STREAMING_API_KEY = os.environ.get('STREAMING_API_KEY')
NVR_CLIENT_URL = os.environ.get('NVR_CLIENT_URL')


def log_info(f):
    @wraps(f)
    def wrapper(*args):
        logging.getLogger('flask.app').info(
            f"Emitted function {f.__name__} with args: {args}")

        return f(*args)

    return wrapper


class NvrNamespace(Namespace):

    @log_info
    def emit_error(self, err):
        emit("error", {"error": err})

    @log_info
    def on_tracking_state_change(self, msg_json):
        room_id = msg_json['id']
        new_tracking_state = msg_json['tracking_state']

        room = Room.query.get(room_id)

        if not room.tracking_source:
            emit('tracking_switch_error', {
                "id": room.id,
                'tracking_state': room.tracking_state,
                "error": "Камера для трекинга не выбрана в настройках комнаты"})
            return

        try:
            if new_tracking_state:
                requests.post(f'{TRACKING_URL}/track', json={
                    'ip': room.tracking_source}, timeout=3)
            else:
                requests.delete(f'{TRACKING_URL}/track', timeout=3)
        except:
            emit('tracking_switch_error', {
                "id": room.id,
                'tracking_state': room.tracking_state,
                "error": "Ошибка при запуске трекинга"})
            return

        room.tracking_state = new_tracking_state
        db.session.commit()

        emit('tracking_state_change', {
            'id': room.id, 'tracking_state': room.tracking_state, 'room_name': room.name},
            broadcast=True)

    @log_info
    def on_auto_control_change(self, msg_json):
        room_id = msg_json['id']
        auto_control_enabled = msg_json['auto_control']

        room = Room.query.get(room_id)
        room.auto_control = auto_control_enabled
        db.session.commit()

        emit('auto_control_change', {
            'id': room.id, 'auto_control': room.auto_control, 'room_name': room.name},
            broadcast=True)

    @log_info
    def on_delete_room(self, msg_json):
        room_id = msg_json['id']

        room = Room.query.get(room_id)

        Thread(target=delete_calendar, args=(
            room.calendar,), daemon=True).start()

        db.session.delete(room)
        db.session.commit()

        emit('delete_room', {'id': room.id, 'name': room.name}, broadcast=True)

    @log_info
    def on_add_room(self, msg_json):
        room_name = msg_json['name']

        room = Room.query.filter_by(name=room_name).first()
        if room:
            self.emit_error(f"Комната {room_name} уже существует")
            return

        room = Room(name=room_name)
        room.drive = create_folder(room_name)
        room.sources = []
        db.session.add(room)
        db.session.commit()

        Thread(target=NvrNamespace.make_calendar, args=(
            current_app._get_current_object(), room_name), daemon=True).start()

        emit('add_room', {'room': room.to_dict()},
             broadcast=True)

    @staticmethod
    @nvr_db_context
    def make_calendar(room_name):
        room = Room.query.filter_by(name=room_name).first()
        room.calendar = create_calendar(room_name)
        db.session.commit()

    @log_info
    def on_edit_room(self, msg_json):
        room_id = msg_json['id']
        room = Room.query.get(room_id)

        room.main_source = msg_json['main_source']
        room.screen_source = msg_json['screen_source']
        room.tracking_source = msg_json['tracking_source']
        room.sound_source = msg_json['sound_source']

        for s in msg_json['sources']:
            source = Source.query.get(s['id'])
            source.update(**s)

        db.session.commit()

        emit('edit_room', {room.to_dict()}, broadcast=True)

    @log_info
    def on_delete_user(self, msg_json):
        user = User.query.get(msg_json['id'])
        emit('delete_user', {'id': user.id}, broadcast=True)

        if user.access == False:
            send_email('[NVR] Отказано в доступе',
                       sender=current_app.config['ADMINS'][0],
                       recipients=[user.email],
                       html_body=render_template('email/access_deny.html',
                                                 user=user))
        db.session.delete(user)
        db.session.commit()

    @log_info
    def on_change_role(self, msg_json):
        user = User.query.get(msg_json['id'])
        user.role = msg_json['role']
        db.session.commit()

        emit('change_role', {'id': user.id, 'role': user.role}, broadcast=True)

    @log_info
    def on_grant_access(self, msg_json):
        user = User.query.get(msg_json['id'])
        user.access = True
        db.session.commit()

        emit('grant_access', {'id': user.id}, broadcast=True)

        send_email('[NVR] Доступ открыт',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[user.email],
                   html_body=render_template('email/access_approve.html',
                                             user=user, url=NVR_CLIENT_URL))

        Thread(target=give_permissions,
               args=(
                   current_app._get_current_object(), user.email),
               daemon=True).start()

    @log_info
    def on_streaming_start(self, msg_json):
        sound_ip = msg_json['soundIp']
        camera_ip = msg_json['cameraIp']
        room_name = msg_json['roomName']
        title = msg_json['title']

        room = Room.query.filter_by(name=str(room_name)).first()
        sound_source = Source.query.filter_by(ip=sound_ip).first()
        camera_source = Source.query.filter_by(ip=camera_ip).first()

        try:
            response = requests.post(f"{STREAMING_URL}/streams/{room_name}", json={
                "camera_ip": camera_source.rtsp,
                "sound_ip": sound_source.rtsp,
                'title': title
            }, headers={'X-API-KEY': STREAMING_API_KEY})
            room.stream_url = response.json()['url']
            db.session.commit()
        except:
            self.emit_error(f"Ошибка при запуске стрима")
            return

        emit('streaming_start', {
            'name': room_name, 'stream_url': room.stream_url}, broadcast=True)

    @log_info
    def on_streaming_stop(self, msg_json):
        room_name = msg_json['roomName']

        room = Room.query.filter_by(name=str(room_name)).first()

        try:
            response = requests.delete(
                f'{STREAMING_URL}/streams/{room_name}',
                headers={'X-API-KEY': STREAMING_API_KEY})
        except:
            pass
        finally:
            room.stream_url = None
            db.session.commit()
            emit('streaming_stop', {'name': room_name,
                                    'stream_url': None}, broadcast=True)
