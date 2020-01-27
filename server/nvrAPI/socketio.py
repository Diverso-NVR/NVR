from flask_socketio import emit, Namespace
from threading import Thread
from flask import current_app
import requests
import time
import os

from .models import db, Room, Source, User, Stream, nvr_db_context
from calendarAPI.calendarSettings import create_calendar, delete_calendar, give_permissions
from driveAPI.driveSettings import create_folder


CAMPUS = os.environ.get('CAMPUS')
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
                res = requests.post(f'{TRACKING_URL}/track', json={
                    'ip': room.tracking_source}, timeout=3)
            else:
                res = requests.delete(f'{TRACKING_URL}/track', timeout=3)
        except:
            self.emit_error("Ошибка при запуске трекинга")
            return

        room.tracking_state = new_tracking_state
        db.session.commit()

        emit('tracking_state_change', {
             'id': room.id, 'tracking_state': room.tracking_state, 'room_name': room.name},
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
        name = msg_json['name']

        room = Room.query.filter_by(name=name).first()
        if room:
            self.emit_error(f"Комната {name} уже существует")
            return

        room = Room(name=name)
        room.drive = create_folder(f'{CAMPUS}-{name}')
        room.sources = []
        db.session.add(room)
        db.session.commit()

        Thread(target=NvrNamespace.make_calendar, args=(
            current_app._get_current_object(), name), daemon=True).start()

        emit('add_room', {'room': room.to_dict()},
             broadcast=True)

    @staticmethod
    @nvr_db_context
    def make_calendar(name):
        room = Room.query.filter_by(name=name).first()
        room.calendar = create_calendar(CAMPUS, name)
        db.session.commit()

    def on_edit_room(self, msg_json):
        room_id = msg_json['id']
        room = Room.query.get(room_id)

        room.main_source = msg_json['main_source']
        room.screen_source = msg_json['screen_source']
        room.tracking_source = msg_json['tracking_source']
        room.sound_source = msg_json['sound_source']

        for s in room.sources:
            db.session.delete(s)

        for s in msg_json['sources']:
            source = Source(**s)
            source.room_id = room.id
            db.session.add(source)

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

        stream = Stream(
            url=response_json['yt_addr'], pid=response_json['pid'])
        db.session.add(stream)
        db.session.commit()

        emit('streaming_start', {'name': room_name}, broadcast=True)

    def on_streaming_stop(self, msg_json):
        try:
            stream_url = msg_json['ytUrl']
            room_name = msg_json['roomName']

            stream = Stream.query.filter_by(url=stream_url).first()

            requests.post(f'{STREAMING_URL}/stop/{stream.pid}', timeout=2)

            db.session.delete(stream)
            db.session.commit()

            emit('streaming_stop', {'name': room_name}, broadcast=True)
        except Exception as e:
            print(e)
