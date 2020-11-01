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

from .decorators import json_data_required, auth_required, admin_only, admin_or_editor_only

auth_api = Blueprint('auth_api', __name__)

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

merger_api = Blueprint('merger_api', __name__)



from flask import Blueprint
room_api = Blueprint('room_api', __name__)

@room_api.route('/rooms/<room_name>', methods=['POST'])
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


@room_api.route('/rooms/', methods=['GET'])
@auth_required
def get_rooms(current_user):
    return jsonify([r.to_dict() for r in Room.query.all()]), 200


@room_api.route('/rooms/<room_name>', methods=['GET'])
@auth_required
def get_room(current_user, room_name):
    room = Room.query.filter_by(name=str(room_name)).first()
    if not room:
        return jsonify({"error": "No room found with given room_name"}), 400
    return jsonify(room.to_dict()), 200


@room_api.route('/rooms/<room_name>', methods=['DELETE'])
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


@room_api.route("/rooms/<room_name>", methods=['PUT'])
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


@room_api.route('/set-source/<room_name>/<source_type>/<path:ip>', methods=['POST'])
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
