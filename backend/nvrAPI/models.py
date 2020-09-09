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


class UserRecord(db.Model):
    __tablename__ = 'user_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    record_id = db.Column(db.Integer, db.ForeignKey('records.id'))

    user = db.relationship("User", backref=db.backref(
        "user_records", cascade="all, delete-orphan"))
    record = db.relationship("Record", backref=db.backref(
        "user_records", cascade="all, delete-orphan"))


class Record(db.Model):
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.String(100), nullable=False)
    end_time = db.Column(db.String(100), nullable=False)
    event_name = db.Column(db.String(200))
    event_id = db.Column(db.String(200))
    drive_file_url = db.Column(db.String(200))
    # Will be deleted later
    user_email = db.Column(db.String(200), nullable=False)
    room_name = db.Column(db.String(200), nullable=False)

    done = db.Column(db.Boolean, default=False)
    processing = db.Column(db.Boolean, default=False)
    error = db.Column(db.Boolean, default=False)

    # room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    # room = db.relationship("Room", back_populates='records')
    users = db.relationship("User", secondary="user_records")

    def update_from_calendar(self, **kwargs):
        self.event_id = kwargs.get('id')
        self.event_name = kwargs.get('summary')
        self.date = kwargs['start']['dateTime'].split('T')[0]
        self.start_time = kwargs['start']['dateTime'].split('T')[1][:5]
        self.end_time = kwargs['end']['dateTime'].split('T')[1][:5]
        self.room_name = kwargs['room_name']
        self.user_email = kwargs['creator']['email']

    def to_dict(self):
        return dict(id=self.id,
                    date=self.date,
                    start_time=self.start_time,
                    end_time=self.end_time,
                    event_name=self.event_name,
                    event_id=self.event_id,
                    drive_file_url=self.drive_file_url,
                    user_email=self.user_email,
                    room_name=self.room_name,
                    done=self.done,
                    processing=self.processing)


class Channel(db.Model):
    __tablename__ = 'channels'

    id = db.Column(db.String(100), primary_key=True)
    resource_id = db.Column(db.String(100))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), default=None)
    role = db.Column(db.String(50), default='user')
    email_verified = db.Column(db.Boolean, default=False)
    access = db.Column(db.Boolean, default=False)
    api_key = db.Column(db.String(255), unique=True)

    records = db.relationship("Record", secondary="user_records")

    def __init__(self, email, password=None):
        self.email = email
        if password:
            self.password = generate_password_hash(password, method='sha256')

    def update_pass(self, password):
        self.password = generate_password_hash(password, method='sha256')

    @classmethod
    def authenticate(cls, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')

        if not email or not password:
            return None

        user = cls.query.filter_by(email=email).first()
        if not user or not user.password or not check_password_hash(user.password, password):
            return None

        return user

    @classmethod
    def create_api_key(cls, user_id):
        if cls.query.get(user_id).api_key:
            return
        return uuid.uuid4().hex

    def get_token(self, token_expiration: int, key: str):
        """
        Creates verification token
        """
        return jwt.encode(
            {key: self.id,
             'exp': time() + token_expiration},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def delete_user_after_token_expiration(self, app, token_expiration: int) -> None:
        """
        Deletes user if token is expired
        """
        # TODO looks weird
        sleep(token_expiration)
        with app.app_context():
            user = User.query.get(self.id)
            if not user.email_verified:
                db.session.delete(user)
                db.session.commit()

    @staticmethod
    def verify_token(token: str, key: str):
        """
        Check if token is valid
        """
        try:
            id = jwt.decode(token,
                            current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])[key]
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
    name = db.Column(db.String(100), nullable=False, unique=True)
    tracking_state = db.Column(db.Boolean, default=False)
    ruz_id = db.Column(db.Integer)

    # records = db.relationship('Record', back_populates='room')
    sources = db.relationship('Source', backref='room', lazy=False)
    channel = db.relationship("Channel", backref="room", uselist=False)

    drive = db.Column(db.String(200))
    calendar = db.Column(db.String(200))
    stream_url = db.Column(db.String(300))

    sound_source = db.Column(db.String(100))
    main_source = db.Column(db.String(100))
    tracking_source = db.Column(db.String(100))
    screen_source = db.Column(db.String(100))

    auto_control = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    tracking_state=self.tracking_state,
                    sources=[source.to_dict() for source in self.sources],
                    drive=self.drive,
                    calendar=self.calendar,
                    stream_url=self.stream_url,
                    sound_source=self.sound_source,
                    main_source=self.main_source,
                    tracking_source=self.tracking_source,
                    screen_source=self.screen_source,
                    auto_control=self.auto_control)


class Source(db.Model):
    __tablename__ = 'sources'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='источник')
    ip = db.Column(db.String(200))
    port = db.Column(db.String(200))
    rtsp = db.Column(db.String(200), default='no')
    audio = db.Column(db.String(200))
    merge = db.Column(db.String(200))
    tracking = db.Column(db.String(200))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))

    def update(self, **kwargs):
        self.name = kwargs.get('name')
        self.ip = kwargs.get('ip')
        self.port = kwargs.get('port')
        self.rtsp = kwargs.get('rtsp')
        self.audio = kwargs.get('audio')
        self.merge = kwargs.get('merge')
        self.tracking = kwargs.get('tracking')
        self.room_id = kwargs.get('room_id')

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    ip=self.ip,
                    port=self.port,
                    rtsp=self.rtsp,
                    audio=self.audio,
                    merge=self.audio,
                    tracking=self.tracking,
                    room_id=self.room_id)
