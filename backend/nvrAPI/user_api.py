from flask import Blueprint
user_api = Blueprint('user_api', __name__)

@api.route('/users', methods=['GET'])
@auth_required
@admin_only
def get_users(current_user):
    users = [u.to_dict() for u in User.query.all() if u.email_verified]
    return jsonify(users), 200


@api.route('/users/<user_id>', methods=['PUT'])
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


@api.route('/users/roles/<user_id>', methods=['PUT'])
@auth_required
@admin_only
def user_role(current_user, user_id):
    user = User.query.get(user_id)
    user.role = request.get_json()['role']
    db.session.commit()

    emit_event('change_role', {'id': user.id, 'role': user.role})

    return jsonify({"message": "User role changed"}), 200


@api.route('/users/<user_id>', methods=['DELETE'])
@auth_required
@admin_only
def delete_user(current_user, user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    emit_event('delete_user', {'id': user.id})

    return jsonify({"message": "User deleted"}), 200


@api.route('/api-key/<email>', methods=['GET', 'POST', 'PUT', 'DELETE'])
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
