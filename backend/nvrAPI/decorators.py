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


def auth_required(f):
    """
    Verification wrapper to make sure that user is logged in
    """

    @wraps(f)
    def _verify(*args, **kwargs):
        token = request.headers.get('Token', '')
        api_key = request.headers.get('key', '')

        invalid_msg = {
            'error': 'Ошибка доступа',
            'autheticated': False
        }
        expired_msg = {
            'error': 'Истёкшая сессия',
            'autheticated': False
        }

        if token:
            try:
                data = jwt.decode(token, current_app.config['SECRET_KEY'])
                user = User.query.filter_by(email=data['sub']['email']).first()
                if not user:
                    return jsonify({'error': "User not found"}), 404
                return f(user, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify(expired_msg), 403
            except jwt.InvalidTokenError:
                return jsonify(invalid_msg), 403
            except Exception as e:
                traceback.print_exc()
                return jsonify({'error': "Server error"}), 500
        elif api_key:
            try:
                user = User.query.filter_by(api_key=api_key).first()
                if not user:
                    return jsonify({'error': "Wrong API key"}), 400
                return f(user, *args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                return jsonify({'error': "Server error"}), 500

        return jsonify(invalid_msg), 403

    return _verify


def admin_only(f):
    @wraps(f)
    def wrapper(user, *args, **kwargs):
        if user.role in ['user', 'editor']:
            return jsonify({'error': "Access error"}), 401 #403?
        return f(user, *args, **kwargs)

    return wrapper


def admin_or_editor_only(f):
    @wraps(f)
    def wrapper(user, *args, **kwargs):
        if user.role == 'user':
            return jsonify({'error': "Access error"}), 401 #мб 403
        return f(user, *args, **kwargs)

    return wrapper


def json_data_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        post_data = request.get_json()
        if not post_data:
            return jsonify({"error": "json data required"}), 400
        return f(*args, **kwargs)

    return wrapper
