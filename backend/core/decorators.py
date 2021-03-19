"""Decorators for NVR"""


from functools import wraps
import traceback
import jwt
from flask import jsonify, request, current_app
from sqlalchemy.orm import joinedload
from .models import User, Session


def auth_required(f):
    """
    Verification wrapper to make sure that user is logged in
    """

    @wraps(f)
    def _verify(*args, **kwargs):

        token = request.headers.get("Token", "")
        api_key = request.headers.get("key", "")

        invalid_msg = {"error": "Ошибка доступа", "autheticated": False}
        expired_msg = {"error": "Истёкшая сессия", "autheticated": False}

        session = Session()
        if token:
            try:
                data = jwt.decode(token, current_app.config["SECRET_KEY"])
                user = session.query(User).filter_by(email=data["sub"]["email"]).first()
                session.close()
                if not user:
                    return jsonify({"error": "User not found"}), 404
                if user.banned:
                    return jsonify({"error": "Access denied"}), 403
                return f(user, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify(expired_msg), 403
            except jwt.InvalidTokenError:
                return jsonify(invalid_msg), 403
            except Exception:
                traceback.print_exc()
                return jsonify({"error": "Server error"}), 500
        elif api_key:
            try:
                user = session.query(User).filter_by(api_key=api_key).first()
                session.close()
                if not user:
                    return jsonify({"error": "Wrong API key"}), 400
                if user.banned:
                    return jsonify({"error": "Access denied"}), 403
                return f(user, *args, **kwargs)
            except Exception:
                traceback.print_exc()
                return jsonify({"error": "Server error"}), 500

        return jsonify(invalid_msg), 403

    return _verify


def admin_only(f):
    @wraps(f)
    def wrapper(user, *args, **kwargs):
        if user.role.name in ["user", "editor"]:
            return jsonify({"error": "Access error"}), 401
        return f(user, *args, **kwargs)

    return wrapper


def admin_or_editor_only(f):
    @wraps(f)
    def wrapper(user, *args, **kwargs):
        if user.role.name == "user":
            return jsonify({"error": "Access error"}), 401
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
