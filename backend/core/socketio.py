import logging
import os
from functools import wraps
from threading import Thread
from datetime import datetime

import requests
from flask import current_app, render_template
from flask_socketio import emit, Namespace

from flask_socketio import SocketIO

from .apis.calendar_api import create_calendar, delete_calendar
from .apis.drive_api import create_folder
from .email import send_email
from .models import Session, Room, Source, User


NVR_CLIENT_URL = os.environ.get("NVR_CLIENT_URL", "*")

socketio = SocketIO(message_queue="redis://", cors_allowed_origins=NVR_CLIENT_URL)


def emit_event(event, data):
    socketio.emit(event, data, broadcast=True, namespace="/websocket")


def log_info(f):
    @wraps(f)
    def wrapper(*args):
        # logging.getLogger("flask.app").info(
        #     f"Emitted function {f.__name__} with args: {args}"
        # )

        return f(*args)

    return wrapper


class NvrNamespace(Namespace):
    @log_info
    def emit_error(self, err):
        emit("error", {"error": err})

    @log_info
    def on_auto_control_change(self, msg_json):
        room_id = msg_json["id"]
        auto_control_enabled = msg_json["auto_control"]

        session = Session()
        room = session.query(Room).get(room_id)
        room.auto_control = auto_control_enabled
        session.commit()
        session.close()

        emit(
            "auto_control_change",
            {"id": room.id, "auto_control": room.auto_control, "room_name": room.name},
            broadcast=True,
        )

    @log_info
    def on_delete_room(self, msg_json):
        room_id = msg_json["id"]

        session = Session()
        room = session.query(Room).get(room_id)

        Thread(target=delete_calendar, args=(room.calendar,), daemon=True).start()

        session.delete(room)
        session.commit()
        session.close()

        emit("delete_room", {"id": room.id, "name": room.name}, broadcast=True)

    @log_info
    def on_add_room(self, msg_json):
        room_name = msg_json["name"]

        session = Session()

        room = Room(name=room_name)
        room.drive = create_folder(room_name)
        room.sources = []

        session.add(room)
        session.commit()
        session.close()

        Thread(
            target=NvrNamespace.make_calendar,
            args=(current_app._get_current_object(), room_name),
            daemon=True,
        ).start()

        emit("add_room", {"room": room.to_dict()}, broadcast=True)

    @staticmethod
    def make_calendar(room_name):
        session = Session()
        room = session.query(Room).filter_by(name=room_name).first()
        room.calendar = create_calendar(room_name)

        session.commit()
        session.close()

    @log_info
    def on_edit_room(self, msg_json):
        room_id = msg_json["id"]
        session = Session()
        room = session.query(Room).get(room_id)

        room.main_source = msg_json["main_source"]
        room.screen_source = msg_json["screen_source"]
        room.sound_source = msg_json["sound_source"]

        # add, update
        for s in msg_json["sources"]:
            if not s.get("id"):
                source = Source(**s)
                source.room_id = room_id
                session.add(source)
            else:
                source = session.query(Source).get(s["id"])
                source.update(**s)

        # delete
        updated_sources = [source.get("id") for source in msg_json["sources"]]
        for s in room.sources:
            if s.id not in updated_sources:
                session.delete(s)

        session.commit()
        session.close()

        emit("edit_room", {room.to_dict()}, broadcast=True)

    @log_info
    def on_delete_user(self, msg_json):
        session = Session()
        user = session.query(User).get(msg_json["id"])
        emit("delete_user", {"id": user.id}, broadcast=True)

        if user.access is False:
            send_email(
                "[NVR] Отказано в доступе",
                sender=current_app.config["ADMINS"][0],
                recipients=[user.email],
                html_body=render_template("email/access_deny.html", user=user),
            )
        session.delete(user)
        session.commit()
        session.close()

    @log_info
    def on_change_role(self, msg_json):
        session = Session()
        user = session.query(User).get(msg_json["id"])
        user.role = msg_json["role"]

        session.commit()
        session.close()
        emit("change_role", {"id": user.id, "role": user.role}, broadcast=True)

    @log_info
    def on_ban_user(self, msg_json):
        session = Session()
        user = session.query(User).get(msg_json["id"])
        emit("block_user", {"id": user.id}, broadcast=True)
        user.banned = True
        session.commit()
        session.close()

    @log_info
    def on_unblock_user(self, msg_json):
        session = Session()
        user = session.query(User).get(msg_json["id"])
        emit("unblock_user", {"id": user.id}, broadcast=True)
        user.banned = False
        session.commit()
        session.close()

    @log_info
    def on_kick_banned(self, msg_json):
        session = Session()
        email = msg_json["email"]
        user = session.query(User).filter_by(email=email).first()
        if user.banned == True:
            emit("kick_user", {"email": user.email}, broadcast=True)

        session.commit()
        session.close()
        emit("kick_banned", {"id": user.id}, broadcast=True)

    @log_info
    def on_check_online(self, msg_json):
        session = Session()
        email = msg_json["email"]
        user = session.query(User).filter_by(email=email).first()
        emit("show_online", user.to_dict(), broadcast=True)
        user.last_login = datetime.utcnow()
        session.commit()
        session.close()

    @log_info
    def on_logout_online(self, msg_json):
        session = Session()
        email = msg_json["email"]
        user = session.query(User).filter_by(email=email).first()
        emit("false_online", {"id": user.id}, broadcast=True)
        session.commit()
        session.close()

    @log_info
    def on_change_online(self, msg_json):
        session = Session()
        email = msg_json["email"]
        user = session.query(User).filter_by(email=email).first()
        if user.banned == True:
            emit("kick_user", {})

        session.commit()
        session.close()
        emit("change_online", {"id": user.id}, broadcast=True)

    @log_info
    def on_grant_access(self, msg_json):
        session = Session()
        user = session.query(User).get(msg_json["id"])
        user.access = True
        session.commit()
        session.close()

        emit("grant_access", {"id": user.id}, broadcast=True)

        send_email(
            "[NVR] Доступ открыт",
            sender=current_app.config["ADMINS"][0],
            recipients=[user.email],
            html_body=render_template(
                "email/access_approve.html", user=user, url=NVR_CLIENT_URL
            ),
        )
