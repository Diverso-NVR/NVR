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


google_api = Blueprint('google_api', __name__)

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


@google_api.route('/gcalendar-event/<room_name>', methods=['POST'])
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


@google_api.route('/gdrive-upload/<room_name>', methods=['POST'])
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


@google_api.route('/gconfigure/<string:room_name>', methods=['POST'])
@auth_required
@admin_or_editor_only
def create_drive_and_calendar(current_user, room_name):
    drive = create_folder(room_name)
    calendar = create_calendar(room_name)
    return jsonify({"drive": drive, "calendar": calendar}), 201