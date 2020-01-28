"""
- Data classes for application
"""

import uuid
from time import time, sleep

import jwt
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def nvr_db_context(func):
    """
    Decorator to provide functions access to db
    """

    def wrapper(app, *args, **kwargs):
        with app.app_context():
            return func(*args, **kwargs)

    return wrapper


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    email_verified = db.Column(db.Boolean, default=False)
    access = db.Column(db.Boolean, default=False)

    api_key = db.Column(db.String(255), unique=True)

    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password, method='sha256')

    @classmethod
    def authenticate(cls, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')

        if not email or not password:
            return None

        user = cls.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return None

        return user

    @classmethod
    def create_api_key(cls, user_id):
        if cls.query.get(user_id).api_key:
            return
        return uuid.uuid4().hex

    def get_verify_token(self, token_expiration: int):
        """
        Creates verification token
        """
        return jwt.encode(
            {'verify_user': self.id,
             'exp': time() + token_expiration},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def delete_user_after_token_expiration(self, app, token_expiration: int) -> None:
        """
        Deletes user if token is expired
        """
        sleep(token_expiration)
        with app.app_context():
            user = User.query.get(self.id)
            if not user.email_verified:
                db.session.delete(user)
                db.session.commit()

    @staticmethod
    def verify_email_token(token: str):
        """
        Check if token is valid
        """
        try:
            id = jwt.decode(token,
                            current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['verify_user']
        except:
            return
        return User.query.get(id)

    def to_dict(self):
        return dict(id=self.id,
                    email=self.email,
                    role=self.role,
                    email_verified=self.email_verified,
                    access=self.access,
                    api_key=self.api_key)


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    free = db.Column(db.Boolean, default=True)
    tracking_state = db.Column(db.Boolean, default=False)

    sound_source = db.Column(db.String(100), default='0')
    main_source = db.Column(db.String(100), default='0')
    tracking_source = db.Column(db.String(100), default='0')
    screen_source = db.Column(db.String(100), default='0')

    sources = db.relationship('Source', backref='room', lazy=False)
    drive = db.Column(db.String(200))
    calendar = db.Column(db.String(200))

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    free=self.free,
                    tracking_state=self.tracking_state,
                    sound_source=self.sound_source,
                    main_source=self.main_source,
                    tracking_source=self.tracking_source,
                    screen_source=self.screen_source,
                    sources=[source.to_dict() for source in self.sources],
                    drive=self.drive,
                    calendar=self.calendar)


class Source(db.Model):
    __tablename__ = 'sources'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(200), default='0')
    name = db.Column(db.String(100), default='источник')
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))

    def __init__(self, **kwargs):
        self.ip = kwargs.get('ip')
        self.name = kwargs.get('name')
        self.room_id = kwargs.get('room_id')

    def to_dict(self):
        return dict(id=self.id,
                    ip=self.ip,
                    name=self.name,
                    room_id=self.room_id)


class Stream(db.Model):
    __tablename__ = 'streams'

    url = db.Column(db.String(250), primary_key=True)
    pid = db.Column(db.Integer, unique=True, nullable=False)
