"""Api for interacting with users"""


import uuid

from flask import Blueprint, jsonify, request, g

from ..models import User
from ..decorators import auth_required, admin_only

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
    if user_email != current_user.email:
        return jsonify({"error": "Access error"}), 403
        
    user = g.session.query(User).filter_by(email=user_email).first()
    return jsonify([u_rec.record.to_dict() for u_rec in user.records]), 200
