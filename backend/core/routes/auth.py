"""Api for interacting with auth and such things"""


import os
from datetime import datetime, timedelta
from threading import Thread

import traceback

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from ..socketio import emit_room

import jwt
from flask import Blueprint, jsonify, request, current_app, render_template, g

from ..email import send_verify_email, send_access_request_email, send_reset_pass_email
from ..models import User, Role
from ..decorators import json_data_required

api = Blueprint("auth_api", __name__)

NVR_CLIENT_URL = os.environ.get("NVR_CLIENT_URL")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")


@api.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    user = User(**data)
    user.role_id = g.session.query(Role).filter_by(name="user").first().id

    try:
        g.session.add(user)
        g.session.commit()
    except Exception:
        return jsonify({"error": "Пользователь с данной почтой существует"}), 409

    token_expiration = 600
    try:
        send_verify_email(user, token_expiration)
        Thread(
            target=user.delete_user_after_token_expiration,
            args=(current_app._get_current_object(), token_expiration),
        ).start()
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500

    return jsonify(user.to_dict()), 202


@api.route("/verify-email/<token>", methods=["POST", "GET"])
def verify_email(token):
    user = User.verify_token(g.session, token, "verify_email")
    if not user:
        return (
            render_template(
                "msg_template.html",
                msg={
                    "title": "Подтверждение почты",
                    "text": "Время на подтверждение вышло. Зарегистрируйтесь ещё раз",
                },
                url=NVR_CLIENT_URL,
            ),
            404,
        )

    if user.email_verified:
        return (
            render_template(
                "msg_template.html",
                msg={
                    "title": "Подтверждение почты",
                    "text": "Почта уже подтверждена",
                },
                url=NVR_CLIENT_URL,
            ),
            409,
        )

    user.email_verified = True
    g.session.commit()

    try:
        send_access_request_email(
            [
                u.email
                for u in g.session.query(User)
                .filter_by(organization_id=user.organization_id)
                .all()
                if u.role.name not in ["user", "editor"]
            ],
            user,
        )
    except Exception:
        traceback.print_exc()
        return "Server error", 500

    emit_room("new_user", {"user": user.to_dict()}, room=user.organization_id)

    return (
        render_template(
            "msg_template.html",
            msg={
                "title": "Подтверждение почты",
                "text": "Подтверждение успешно, ожидайте одобрения администратора",
            },
            url=NVR_CLIENT_URL,
        ),
        202,
    )


@api.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.authenticate(g.session, **data)

    if not user:
        return jsonify({"error": "Неверные данные", "authenticated": False}), 401

    if not user.email_verified:
        return jsonify({"error": "Почта не подтверждена", "authenticated": False}), 401

    if not user.access:
        return (
            jsonify(
                {
                    "error": "Администратор ещё не открыл доступ для этого аккаунта",
                    "authenticated": False,
                }
            ),
            401,
        )

    if user.banned:
        return (
            jsonify({"error": "Вам закрыт доступ к NVR", "authenticated": False}),
            403,
        )

    token = jwt.encode(
        {
            "sub": {
                "email": user.email,
                "role": user.role.name,
                "org_name": user.organization.name,
            },
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(weeks=12),
        },
        current_app.config["SECRET_KEY"],
    )

    g.session.commit()
    return jsonify({"token": token.decode("UTF-8")}), 202


@api.route("/google-login", methods=["POST"])
def glogin():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"error": "Bad request"}), 400

    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), GOOGLE_CLIENT_ID
        )

        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")
        email = idinfo["email"]
    except ValueError:
        return jsonify({"error": "Bad token"}), 403

    user = g.session.query(User).filter_by(email=email).first()
    if user and user.banned:
        return (
            jsonify({"error": "Вам закрыт доступ к NVR", "authenticated": False}),
            403,
        )

    if not user:
        user = User(email=email)
        user.email_verified = True
        user.access = True
        user.role_id = g.session.query(Role).filter_by(name="user").first().id
        g.session.add(user)

    token = jwt.encode(
        {
            "sub": {
                "email": user.email,
                "role": user.role.name,
                "org_name": user.organization.name,
            },
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(weeks=12),
        },
        current_app.config["SECRET_KEY"],
    )
    g.session.commit()

    return jsonify({"token": token.decode("UTF-8")}), 202


@api.route("/reset-pass/<email>", methods=["POST"])
def send_reset_pass(email):
    user = g.session.query(User).filter_by(email=str(email)).first()
    if not user:
        return jsonify({"error": "User doesn`t exist"}), 404

    token_expiration = 300
    try:
        send_reset_pass_email(user, token_expiration)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500

    return jsonify({"message": "Reset pass token generated"}), 200


@api.route("/reset-pass/<token>", methods=["PUT"])
@json_data_required
def reset_pass(token):
    data = request.get_json()

    new_pass = data.get("new_pass")
    if not new_pass:
        return jsonify({"error": "New password required"}), 400

    user = User.verify_token(g.session, token, "reset_pass")
    if not user:
        return jsonify({"error": "Invalid token"}), 403

    user.update_pass(new_pass)
    g.session.commit()

    return jsonify({"message": "Password updated"}), 200
