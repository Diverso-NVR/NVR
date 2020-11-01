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

auth_api = Blueprint('user_api', __name__)

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

user_api = Blueprint('user_api', __name__)

@user_api.route('/users', methods=['GET'])
@auth_required
@admin_only
def get_users(current_user):
    users = [u.to_dict() for u in User.query.all() if u.email_verified]
    return jsonify(users), 200


@user_api.route('/users/<user_id>', methods=['PUT'])
@auth_required
@admin_only
def grant_access(current_user, user_id):
    user = User.query.get(user_id)
    user.access = True
    db.session.commit()

    Thread(target=give_permissions, args=(
        current_app._get_current_object(), user.email)).start()

    emit_event('grant_access', {'id': user.id})

    return jsonify({"message": "Access granted"}), 202


@user_api.route('/users/roles/<user_id>', methods=['PUT'])
@auth_required
@admin_only
def user_role(current_user, user_id):
    user = User.query.get(user_id)
    user.role = request.get_json()['role']
    db.session.commit()

    emit_event('change_role', {'id': user.id, 'role': user.role})

    return jsonify({"message": "User role changed"}), 200


@user_api.route('/users/<user_id>', methods=['DELETE'])
@auth_required
@admin_only
def delete_user(current_user, user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    emit_event('delete_user', {'id': user.id})

    return jsonify({"message": "User deleted"}), 200


@user_api.route('/api-key/<email>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@auth_required
def manage_api_key(current_user, email):
    user = User.query.filter_by(email=email).first()
    if current_user.role == 'user' or email != current_user.email:
        return jsonify({'error': "Access error"}), 401

    if request.method == 'POST':
        if user.api_key:
            return jsonify({'error': 'Ключ API уже существует'}), 409

        user.api_key = uuid.uuid4().hex
        db.session.commit()

        return jsonify({'key': user.api_key}), 201

    if request.method == 'GET':
        return jsonify({"key": user.api_key}), 200

    if request.method == 'PUT':
        user.api_key = uuid.uuid4().hex
        db.session.commit()

        return jsonify({'key': user.api_key}), 202

    if request.method == 'DELETE':
        user.api_key = None
        db.session.commit()

        return jsonify({'message': "API key deleted"}), 200
