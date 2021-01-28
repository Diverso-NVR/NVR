"""Api for interacting with users"""


import uuid

from flask import Blueprint, jsonify, request, g

from ..socketio import emit_event

from ..models import User
from ..decorators import auth_required, admin_only

api = Blueprint("users_api", __name__)


@api.route("/users", methods=["GET"])
@auth_required
@admin_only
def get_users():
    users = [u.to_dict() for u in g.session.query(User).all() if u.email_verified]
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
