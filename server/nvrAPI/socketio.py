from flask_socketio import emit, Namespace
from threading import Thread
from flask import current_app
import requests
import time
import os

from .models import db, Room, Source, User, nvr_db_context
from calendarAPI.calendarSettings import create_calendar, delete_calendar, give_permissions
from driveAPI.startstop import start, stop
from driveAPI.driveSettings import create_folder


from .api import get_tracking_cam

CAMPUS = os.environ.get('CAMPUS')
TRACKING_URL = os.environ.get('TRACKING_URL')


class NvrNamespace(Namespace):
    def emit_error(self, err):
        emit("error", {"error": err})

    def on_sound_change(self, msg_json):
        room_id = msg_json['id']
        sound_type = msg_json['sound']

        room = Room.query.get(room_id)
        room.chosen_sound = sound_type
        db.session.commit()

        emit('sound_change', {'id': room.id,
                              'sound': sound_type}, broadcast=True)

    def on_tracking_state_change(self, msg_json):
        room_id = msg_json['id']
        new_tracking_state = msg_json['tracking_state']

        room = Room.query.get(room_id)

        tracking_cam_ip = get_tracking_cam([s.to_dict() for s in room.sources])

        if not tracking_cam_ip:
            self.emit_error(
                "Камера для трекинга не выбрана в настройках комнаты")
            return

        try:
            if new_tracking_state:
                res = requests.post(f'{TRACKING_URL}/track', json={
                    'ip': tracking_cam_ip}, timeout=3)
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

    def on_start_rec(self, msg_json):
        room_id = msg_json['id']
        room = Room.query.get(room_id)

        if not room.free:
            return

        room.free = False
        room.timestamp = int(time.time())
        db.session.commit()

        Thread(
            target=start,
            args=(current_app._get_current_object(), room_id)
        ).start()

        emit('start_rec', {'id': room.id}, broadcast=True)

    def on_stop_rec(self, msg_json):
        room_id = msg_json['id']

        calendar_id = msg_json.get('calendar_id')
        event_id = msg_json.get('event_id')

        room = Room.query.get(room_id)

        if room.free:
            return

        Thread(target=stop, args=(current_app._get_current_object(),
                                  room_id, calendar_id, event_id)).start()

        room.free = True
        room.timestamp = 0
        db.session.commit()

        emit('stop_rec', {'id': room.id}, broadcast=True)

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

        for s in room.sources:
            db.session.delete(s)

        for s in msg_json['sources']:
            source = Source(**s)
            source.room_id = room.id
            db.session.add(source)

        db.session.commit()

        emit('edit_room', {'id': room.id, 'sources': [
             s.to_dict() for s in room.sources]}, broadcast=True)

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
