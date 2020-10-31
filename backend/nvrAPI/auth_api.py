from flask import Blueprint

auth_api = Blueprint('auth_api', __name__)

@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(**data)

    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify({"error": 'Пользователь с данной почтой существует'}), 409

    token_expiration = 600
    try:
        send_verify_email(user, token_expiration)
        Thread(target=user.delete_user_after_token_expiration,
               args=(current_app._get_current_object(), token_expiration)).start()
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500

    return jsonify(user.to_dict()), 202


@api.route('/verify-email/<token>', methods=['POST'])
def verify_email(token):
    user = User.verify_token(token, 'verify_email')
    if not user:
        return render_template('msg_template.html',
                               msg={'title': 'Подтверждение почты',
                                    'text': "Время на подтверждение вышло. Зарегистрируйтесь ещё раз"},
                               url=NVR_CLIENT_URL), 404

    if user.email_verified:
        return render_template('msg_template.html',
                               msg={'title': 'Подтверждение почты',
                                    'text': "Почта уже подтверждена",
                                    },
                               url=NVR_CLIENT_URL), 409

    user.email_verified = True
    db.session.commit()

    try:
        send_access_request_email(
            [u.email for u in User.query.all() if u.role not in ['user', 'editor']], user)
    except Exception as e:
        traceback.print_exc()
        return "Server error", 500

    emit_event('new_user', {'user': user.to_dict()})

    return render_template('msg_template.html',
                           msg={'title': 'Подтверждение почты',
                                'text': "Подтверждение успешно, ожидайте одобрения администратора"},
                           url=NVR_CLIENT_URL), 202


@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.authenticate(**data)

    if not user:
        return jsonify({'error': "Неверные данные", 'authenticated': False}), 401

    if not user.email_verified:
        return jsonify({'error': 'Почта не подтверждена', 'authenticated': False}), 401

    if not user.access:
        return jsonify({'error': 'Администратор ещё не открыл доступ для этого аккаунта',
                        'authenticated': False}), 401

    token = jwt.encode({
        'sub': {'email': user.email, 'role': user.role},
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(weeks=12)},
        current_app.config['SECRET_KEY'])

    return jsonify({'token': token.decode('UTF-8')}), 202


@api.route('/google-login', methods=['POST'])
def glogin():
    data = request.get_json()
    token = data.get('token')
    if not token:
        return jsonify({'error': "Bad request"}), 400

    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), GOOGLE_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        email = idinfo['email']

    except ValueError:
        return jsonify({'error': "Bad token"}), 403

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        user.email_verified = True
        user.access = True

        db.session.add(user)
        db.session.commit()

    token = jwt.encode({
        'sub': {'email': user.email, 'role': user.role},
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(weeks=12)},
        current_app.config['SECRET_KEY'])

    return jsonify({'token': token.decode('UTF-8')}), 202

# RESET PASS

@api.route('/reset-pass/<email>', methods=['POST'])
def send_reset_pass(email):
    user = User.query.filter_by(email=str(email)).first()
    if not user:
        return jsonify({"error": "User doesn`t exist"}), 404

    token_expiration = 300
    try:
        send_reset_pass_email(user, token_expiration)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500

    return jsonify({"message": "Reset pass token generated"}), 200


@api.route('/reset-pass/<token>', methods=['PUT'])
@json_data_required
def reset_pass(token):
    data = request.get_json()

    new_pass = data.get('new_pass')
    if not new_pass:
        return jsonify({"error": "New password required"}), 400

    user = User.verify_token(token, 'reset_pass')
    if not user:
        return jsonify({"error": "Invalid token"}), 403

    user.update_pass(new_pass)
    db.session.commit()

    return jsonify({"message": "Password updated"}), 200
