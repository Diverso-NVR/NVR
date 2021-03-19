"""Api for interacting with users"""


import uuid
import traceback
import json

from flask import Blueprint, jsonify, request, g, current_app

from ..models import User, Role
from ..decorators import auth_required, admin_only, json_data_required
from ..email import send_registration_requests

from threading import Thread

api = Blueprint("users_api", __name__)


@api.route("/users", methods=["GET"])
@auth_required
@admin_only
def get_users(current_user):
    # users = g.session.query(User).all()
    # roles = g.session.query(Role).all()
    # for usr in users:
    #     usr.role_id = g.session.query(Role).filter_by(name=usr.role).first().id
    # g.session.commit()

    users = [
        u.to_dict()
        for u in g.session.query(User).filter(
            User.organization_id == current_user.organization_id
        )
        if u.email_verified
    ]
    return jsonify(users), 200


@api.route("/api-key/<email>", methods=["GET", "POST", "PUT", "DELETE"])
@auth_required
def manage_api_key(current_user, email):
    user = g.session.query(User).filter_by(email=email).first()
    if current_user.role.name == "user" or email != current_user.email:
        return jsonify({"error": "Access error"}), 401

    if request.method == "POST":
        if user.api_key:
            return jsonify({"error": "Ключ API уже существует"}), 409

        user.api_key = uuid.uuid4().hex
        g.session.commit()

        return jsonify({"key": user.api_key}), 201

    if request.method == "GET":
        return jsonify({"key": user.api_key}), 200

    if request.method == "PUT":
        user.api_key = uuid.uuid4().hex
        g.session.commit()

        return jsonify({"key": user.api_key}), 202

    if request.method == "DELETE":
        user.api_key = None
        g.session.commit()

        return jsonify({"message": "API key deleted"}), 200


@api.route("/records/<user_email>", methods=["GET"])
@auth_required
def get_urls(current_user, user_email):
    if user_email != current_user.email:
        return jsonify({"error": "Access error"}), 403

    user = g.session.query(User).filter_by(email=user_email).first()
    return jsonify([u_rec.record.to_dict() for u_rec in user.records]), 200


@api.route("/users", methods=["POST"])
@auth_required
@admin_only
@json_data_required
def invite_users(current_user):
    organization_id = current_user.organization_id

    emails = request.get_json()["emails"]
    role = request.get_json()["role"]  # Роль должна быть одна и записана текстом
    role_id = g.session.query(Role).filter_by(name=role).first().id

    already_registred_emails = []
    for email in emails:
        user = User(email, organization_id)
        user.role_id = role_id
        user.email_verified = True
        user.access = True
        try:
            g.session.add(user)
            g.session.commit()
        except Exception:
            already_registred_emails.append(email)

        # Если успешно добавился в бд, поставим таймер на удаление
        token_expiration = 600
        try:
            send_registration_requests(user, token_expiration)
            Thread(
                target=user.delete_user_after_token_expiration,
                args=(current_app._get_current_object(), token_expiration),
            ).start()
        except Exception:
            traceback.print_exc()
            return jsonify({"error": "Server error"}), 500

    if len(already_registred_emails) > 0:
        return jsonify(
            {
                "message": "Some users have been already registred, for others emails have been sent",
                "registred_emails": f"{''.join(map(str, already_registred_emails))}",
            }
        )
    else:
        return jsonify({"message": "we have successfully sent emails"})


@api.route("/roles", methods=["GET"])
def get_all_roles():
    roles = g.session.query(Role).all()
    a = list(map(lambda role: role.to_dict(), roles))
    return json.dumps(a)
    return 0