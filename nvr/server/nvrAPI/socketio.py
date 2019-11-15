from flask_socketio import emit, Namespace
from .models import db, Room, Source, User, nvr_db_context
from threading import Thread
from flask import current_app

from calendarAPI.calendarSettings import create_calendar, delete_calendar, give_permissions
from driveAPI.startstop import start, stop
from driveAPI.driveSettings import create_folder
import time
import os

CAMPUS = os.environ.get('CAMPUS')


class NvrNamespace(Namespace):
    def on_sound_change(self, msg_json):
        room_id = msg_json['id']
        sound_type = msg_json['sound']

        room = Room.query.get(room_id)
        room.chosen_sound = sound_type
        db.session.commit()

        emit('sound_change', {'id': room.id,
                              'sound': sound_type}, broadcast=True)

    def on_start_rec(self, msg_json):
        room_id = msg_json['id']
        room = Room.query.get(room_id)

        if not room.free:
            return "Already recording", 401

        room.free = False
        db.session.commit()

        Thread(
            target=NvrNamespace.start_timer,
            args=(current_app._get_current_object(), room_id),
            daemon=True
        ).start()

        Thread(
            target=start,
            args=(current_app._get_current_object(), room_id)
        ).start()

        emit('start_rec', {'id': room.id}, broadcast=True)

    @staticmethod
    @nvr_db_context
    def start_timer(room_id: int) -> None:
        while not Room.query.get(room_id).free:
            Room.query.get(room_id).timestamp += 1
            db.session.commit()
            time.sleep(1)

    def on_stop_rec(self, msg_json):
        room_id = msg_json['id']

        calendar_id = msg_json.get('calendar_id')
        event_id = msg_json.get('event_id')

        room = Room.query.get(room_id)

        if room.free:
            return "Already stoped", 401

        Thread(target=NvrNamespace.stop_record, args=(current_app._get_current_object(),
                                                      room_id, calendar_id, event_id)).start()

        emit('stop_rec', {'id': room.id}, broadcast=True)

    @staticmethod
    @nvr_db_context
    def stop_record(room_id, calendar_id, event_id):
        try:
            stop(current_app._get_current_object(),
                 room_id, calendar_id, event_id)
        except Exception as e:
            pass
        finally:
            room = Room.query.get(room_id)
            room.free = True
            room.timestamp = 0
            db.session.commit()

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

        room = Room(name=name)
        room.drive = create_folder(
            CAMPUS,
            name
        )
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
        room = Room(name=name)
        room.calendar = create_calendar(
            CAMPUS,
            name
        )
        db.session.commit()

    def on_edit_room(self, msg_json):
        room_id = msg_json['id']
        room = Room.query.get(room_id)
        room.sources = []
        for s in msg_json['sources']:
            if s.get('id'):
                source = Source.query.get(s['id'])
            else:
                source = Source()
            room.sources.append(source)
            source.ip = s.get('ip', "0.0.0.0")
            source.name = s.get('name', 'камера')
            source.sound = s.get('sound', None)
            source.tracking = s.get('tracking', False)
            source.main_cam = s.get('main_cam', False)
            source.room_id = room_id

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
                   current_app._get_current_object(), CAMPUS, user.email),
               daemon=True).start()

        emit('grant_access', {'id': user.id}, broadcast=True)
