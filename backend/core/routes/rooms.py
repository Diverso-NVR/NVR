"""Api for interacting with rooms"""


from threading import Thread
from pathlib import Path


from flask import Blueprint, jsonify, request, current_app, g

from ..socketio import emit_event
from ..apis.calendar_api import create_calendar, delete_calendar
from ..apis.drive_api import create_folder
from ..apis.ruz_api import get_room_ruzid
from ..models import Session, Room, Source, User, Record
from ..decorators import json_data_required, auth_required, admin_or_editor_only


api = Blueprint('rooms_api', __name__)

@api.route('/rooms/<room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
def create_room(current_user, room_name):
    if not room_name:
        return jsonify({"error": "Room name required"}), 400

    room = g.session.query(Room).filter_by(name=room_name).first()
    if room:
        return jsonify({"error": f"Room '{room_name}' already exist"}), 409

    room = Room(name=room_name)
    room.sources = []
    g.session.add(room)
    g.session.commit()

    emit_event('add_room', {'room': room.to_dict()})

    Thread(target=config_room, args=(
        current_app._get_current_object(), room_name)).start()

    return jsonify({'message': f"Started creating '{room_name}'"}), 204


def config_room(room_name):
    session = Session()

    users = session.query(User).all()

    room = session.query(Room).filter_by(name=room_name).first()
    room.drive = create_folder(room_name)
    room.calendar = create_calendar([user.email for user in users], room_name)
    room.ruz_id = get_room_ruzid(room_name)

    session.commit()
    session.close()


@api.route('/rooms/', methods=['GET'])
@auth_required
def get_rooms(current_user):
    return jsonify([r.to_dict() for r in g.session.query(Room).all()]), 200


@api.route('/rooms/<room_name>', methods=['GET'])
@auth_required
def get_room(current_user, room_name):
    room = g.session.query(Room).filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 400
    return jsonify(room.to_dict()), 200


@api.route('/rooms/<room_name>', methods=['DELETE'])
@auth_required
@admin_or_editor_only
def delete_room(current_user, room_name):
    room = g.session.query(Room).filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 400

    Thread(target=delete_calendar, args=(room.calendar,)).start()

    g.session.delete(room)
    g.session.commit()

    emit_event('delete_room', {'id': room.id, 'name': room.name})

    return jsonify({"message": "Room deleted"}), 200


@api.route("/rooms/<room_name>", methods=['PUT'])
@auth_required
@admin_or_editor_only
@json_data_required
def edit_room(current_user, room_name):
    post_data = request.get_json()

    room = g.session.query(Room).filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given 'room_name'"}), 400
    if not post_data.get('sources'):
        return jsonify({"error": "Sources array required"}), 400

    for s in post_data['sources']:
        if s.get('id'):
            source = g.session.query(Source).get(s['id'])
            source.update(**s)
        else:
            source = Source(**s)
            source.room_id = room.id
            g.session.add(source)

    g.session.commit()

    emit_event('edit_room', {room.to_dict()})

    return jsonify({"message": "Room edited"}), 200


@api.route('/set-source/<room_name>/<source_type>/<path:ip>', methods=['POST'])
@auth_required
@admin_or_editor_only
def room_settings(current_user, room_name, source_type, ip):
    room = g.session.query(Room).filter_by(name=str(room_name)).first()
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

    g.session.commit()

    emit_event('edit_room', {room.to_dict()})

    return jsonify({"message": "Source set"}), 200
