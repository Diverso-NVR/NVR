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

source_api = Blueprint('source_api', __name__)

@source_api.route("/sources/", methods=['GET'])
@auth_required
def get_sources(current_user):
    return jsonify([s.to_dict() for s in Source.query.all()]), 200


@source_api.route("/sources/<path:ip>", methods=['POST', 'GET', 'DELETE', 'PUT'])
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
