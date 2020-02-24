import os
from threading import Thread

import requests
from flask import current_app
from flask_socketio import emit, Namespace

from calendarAPI.calendarSettings import create_calendar, delete_calendar, give_permissions
from driveAPI.driveSettings import create_folder
from .models import db, Room, Source, User, Stream, nvr_db_context

TRACKING_URL = os.environ.get('TRACKING_URL')
STREAMING_URL = os.environ.get('STREAMING_URL')


class NvrNamespace(Namespace):
    def emit_error(self, err):
        emit("error", {"error": err})

    def on_tracking_state_change(self, msg_json):
        room_id = msg_json['id']
        new_tracking_state = msg_json['tracking_state']

        room = Room.query.get(room_id)

        if not room.tracking_source:
            self.emit_error(
                "Камера для трекинга не выбрана в настройках комнаты")
            return

        try:
            if new_tracking_state:
                requests.post(f'{TRACKING_URL}/track', json={
                    'ip': room.tracking_source}, timeout=3)
            else:
                requests.delete(f'{TRACKING_URL}/track', timeout=3)
        except:
            self.emit_error("Ошибка при запуске трекинга")
            return

        room.tracking_state = new_tracking_state
        db.session.commit()

        emit('tracking_state_change', {
            'id': room.id, 'tracking_state': room.tracking_state, 'room_name': room.name},
            broadcast=True)

    def on_auto_control_change(self, msg_json):
        room_id = msg_json['id']
        auto_control_enabled = msg_json['auto_control']

        room = Room.query.get(room_id)
        room.auto_control = auto_control_enabled
        db.session.commit()

        emit('auto_control_change', {
            'id': room.id, 'auto_control': room.auto_control, 'room_name': room.name},
            broadcast=True)

    def on_delete_room(self, msg_json):
        room_id = msg_json['id']

        room = Room.query.get(room_id)

        Thread(target=delete_calendar, args=(
            room.calendar,), daemon=True).start()

        db.session.delete(room)
        db.session.commit()

        emit('delete_room', {'id': room.id, 'name': room.name}, broadcast=True)

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

    def on_delete_user(self, msg_json):
        user = User.query.get(msg_json['id'])
        db.session.delete(user)
        db.session.commit()

        emit('delete_user', {'id': user.id}, broadcast=True)

    def on_change_role(self, msg_json):
        user = User.query.get(msg_json['id'])
        user.role = msg_json['role']
        db.session.commit()

        emit('change_role', {'id': user.id, 'role': user.role}, broadcast=True)

    def on_grant_access(self, msg_json):
        user = User.query.get(msg_json['id'])
        user.access = True
        db.session.commit()

        Thread(target=give_permissions,
               args=(
                   current_app._get_current_object(), user.email),
               daemon=True).start()

        emit('grant_access', {'id': user.id}, broadcast=True)

    def on_streaming_start(self, msg_json):
        sound_ip = msg_json['soundIp']
        camera_ip = msg_json['cameraIp']
        yt_url = msg_json['ytUrl']
        room_name = msg_json['roomName']

        response = requests.post(f'{STREAMING_URL}/start', timeout=2, json={
            "image_addr": camera_ip,
            "sound_addr": sound_ip,
            "yt_addr": yt_url
        })

        if response.status_code != 200:
            self.emit_error("Ошибка при запуске трансляции")
            return

        response_json = response.json()

        stream = Stream(url=response_json['yt_addr'], pid=response_json['pid'])
        db.session.add(stream)
        db.session.commit()

        emit('streaming_start', {'name': room_name}, broadcast=True)

    def on_streaming_stop(self, msg_json):
        stream_url = msg_json['ytUrl']
        room_name = msg_json['roomName']

        stream = Stream.query.filter_by(url=stream_url).first()

        requests.post(f'{STREAMING_URL}/stop/{stream.pid}', timeout=2)

        db.session.delete(stream)
        db.session.commit()

        emit('streaming_stop', {'name': room_name}, broadcast=True)
