"""Api for interacting with users"""


import uuid

from flask import Blueprint, jsonify, request, g

from ..socketio import emit_event

from ..models import User
from ..decorators import auth_required, admin_only, json_data_required
from ..email import send_registration_requests

from threading import Thread

api = Blueprint("users_api", __name__)


@api.route("/users", methods=["GET"])
@auth_required
@admin_only
def get_users(current_user):
    users = [
        u.to_dict()
        for u in g.session.query(User).filter(
            User.organization_id == current_user.organization_id
        )
        if u.email_verified
    ]
    return jsonify(users), 200


@api.route("/users/<user_id>", methods=["PUT"])
@auth_required
@admin_only
def grant_access(current_user, user_id):
    user = g.session.query(User).get(user_id)
    user.access = True
    g.session.commit()

    emit_event("grant_access", {"id": user.id})

    return jsonify({"message": "Access granted"}), 202


@api.route("/users/roles/<user_id>", methods=["PUT"])
@auth_required
@admin_only
def user_role(current_user, user_id):
    user = g.session.query(User).get(user_id)
    user.role = request.get_json()["role"]
    g.session.commit()
    emit_event("change_role", {"id": user.id, "role": user.role})
    return jsonify({"message": "User role changed"}), 200


@api.route("/users/<user_id>", methods=["DELETE"])
@auth_required
@admin_only
def delete_user(current_user, user_id):
    user = g.session.query(User).get(user_id)
    g.session.delete(user)
    g.session.commit()
    emit_event("delete_user", {"id": user.id})
    return jsonify({"message": "User deleted"}), 200


@api.route("/api-key/<email>", methods=["GET", "POST", "PUT", "DELETE"])
@auth_required
def manage_api_key(current_user, email):
    user = g.session.query(User).filter_by(email=email).first()
    if current_user.role == "user" or email != current_user.email:
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
    user = g.session.query(User).filter_by(email=user_email).first()
    return jsonify([u_rec.record.to_dict() for u_rec in user.records]), 200


@api.route("/users", methods=["POST"])
@auth_required
@admin_only
@json_data_required
def invite_users(current_user):
    organization_id = current_user.organization_id

    emails = request.get_json()["email_list"]
    new_users_role = request.get_json()["role"]

    if new_users_role == "admin":
        if current_user.role != "super_admin":
            return jsonify({"error": "not enough rights"}), 403

    # Format for emails_list:
    # [
    #  {'email': 'as@da.com'},
    #  {'email': 'sa@da.com'}
    # ]

    already_registred_emails = []
    new_users = []
    for email in emails:
        usr = User(email, organization_id)
        usr.role = new_users_role
        usr.email_verified = True
        usr.access = True
        try:
            g.session.add(user)
            g.session.commit()
        except Exception:
            already_registred_emails.append(email)

        # Если успешно добавился в бд, поставим таймер на удаление
        token_expiration = 600
        try:
            send_registration_requests(usr)
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
