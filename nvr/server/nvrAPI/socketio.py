from flask_socketio import SocketIO, emit
from .models import db, Room, Source, User, nvr_db_context
from threading import Thread
from flask import current_app

from calendarAPI.calendarSettings import create_calendar, delete_calendar, give_permissions
from driveAPI.startstop import start, stop, upload_file
from driveAPI.driveSettings import create_folder, move_file
import time

CAMPUS = 'dev'


@nvr_db_context
def start_timer(room_id: int) -> None:
    while not Room.query.get(room_id).free:
        Room.query.get(room_id).timestamp += 1
        db.session.commit()
        time.sleep(1)


@nvr_db_context
def stop_record(room_id, calendar_id, event_id):
    try:
        stop(current_app._get_current_object(), room_id, calendar_id, event_id)
    except Exception as e:
        pass
    finally:
        room = Room.query.get(room_id)
        room.free = True
        room.timestamp = 0
        db.session.commit()


def create_socketio(app):
    socketio = SocketIO(app,
                        cors_allowed_origins='http://127.0.0.1:8080',
                        logger=True, engineio_logger=True,
                        )

    @socketio.on('sound_change', namespace='/test')
    def sound_change(msg_json):
        room_id = msg_json['id']
        sound_type = msg_json['sound']

        room = Room.query.get(room_id)
        room.chosen_sound = sound_type
        db.session.commit()

        emit('sound_change', {'id': room.id,
                              'sound': sound_type}, broadcast=True)

    @socketio.on('start_rec', namespace='/test')
    def start_rec(msg_json):
        room_id = msg_json['id']
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

        # Thread(
        #     target=start,
        #     args=(current_app._get_current_object(), room_id)
        # ).start()

        emit('start_rec', {'id': room.id}, broadcast=True)

    @socketio.on('stop_rec', namespace='/test')
    def stop_rec(msg_json):
        room_id = msg_json['id']

        calendar_id = msg_json.get('calendar_id')
        event_id = msg_json.get('event_id')

        room = Room.query.get(room_id)

        if room.free:
            return "Already stoped", 401

        Thread(target=stop_record, args=(current_app._get_current_object(),
                                         room_id, calendar_id, event_id)).start()

        emit('stop_rec', {'id': room.id}, broadcast=True)

    @socketio.on('delete_room', namespace='/test')
    def delete_room(msg_json):
        room_id = msg_json['id']

        room = Room.query.get(room_id)

        Thread(target=delete_calendar, args=(
            room.calendar,), daemon=True).start()

        db.session.delete(room)
        db.session.commit()

        emit('delete_room', {'id': room.id, 'name': room.name}, broadcast=True)

    @socketio.on('add_room', namespace='/test')
    def add_room(msg_json):
        name = msg_json['name']

        room = Room(name=name)
        room.drive = create_folder(
            CAMPUS,
            name
        )
        room.sources = []
        db.session.add(room)
        db.session.commit()

        Thread(target=make_calendar, args=(
            current_app._get_current_object(), name), daemon=True).start()

        emit('add_room', {'room': room.to_dict()},
             broadcast=True)

    @nvr_db_context
    def make_calendar(name):
        room = Room(name=name)
        room.calendar = create_calendar(
            CAMPUS,
            name
        )
        db.session.commit()

    @socketio.on('edit_room', namespace='/test')
    def edit_room(msg_json):
        room_id = msg_json['id']
        room = Room.query.get(room_id)
        room.sources = []
        for s in msg_json['sources']:
            if s.get('id'):
                source = Source.query.get(s['id'])
            else:
                source = Source()
            room.sources.append(source)
            source.ip = s['ip']
            source.name = s['name']
            source.sound = s['sound'] if s['sound'] != False else None
            source.tracking = s.get('tracking')
            source.main_cam = s.get('main_cam')
            source.room_id = room_id

        db.session.commit()

        emit('edit_room', {'id': room.id, 'sources': [
             s.to_dict() for s in room.sources]}, broadcast=True)

    @socketio.on('delete_user', namespace='/test')
    def delete_user(msg_json):
        user = User.query.get(msg_json['id'])
        db.session.delete(user)
        db.session.commit()

        emit('delete_user', {'id': user.id}, broadcast=True)

    @socketio.on('change_role', namespace='/test')
    def change_role(msg_json):
        user = User.query.get(msg_json['id'])
        user.role = msg_json['role']
        db.session.commit()

        emit('change_role', {'id': user.id, 'role': user.role}, broadcast=True)

    @socketio.on('grant_access', namespace='/test')
    def grant_access(msg_json):
        user = User.query.get(msg_json['id'])
        user.access = True
        db.session.commit()

        Thread(target=give_permissions,
               args=(
                   current_app._get_current_object(), CAMPUS, user.email),
               daemon=True).start()

        emit('grant_access', {'id': user.id}, broadcast=True)

    return socketio
