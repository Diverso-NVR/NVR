"""
- Data classes for application
"""

import os
import uuid
from datetime import datetime
from time import time, sleep

import jwt
from sqlalchemy import Column, String, Integer, Boolean, create_engine, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()
engine = create_engine(os.environ.get('SQLALCHEMY_DATABASE_URI'))
Session = sessionmaker(bind=engine)


class UserRecord(Base):
    __tablename__ = 'user_records'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    record_id = Column(Integer, ForeignKey('records.id'))

    user = relationship("User", backref=backref(
        "user_records", cascade="all, delete-orphan"))
    record = relationship("Record", backref=backref(
        "user_records", cascade="all, delete-orphan"))


class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    date = Column(String(100), nullable=False)
    start_time = Column(String(100), nullable=False)
    end_time = Column(String(100), nullable=False)
    event_name = Column(String(200))
    event_id = Column(String(200))
    drive_file_url = Column(String(200))
    # Will be deleted later
    user_email = Column(String(200), nullable=False)
    room_name = Column(String(200), nullable=False)

    done = Column(Boolean, default=False)
    processing = Column(Boolean, default=False)
    error = Column(Boolean, default=False)

    # room_id = Column(Integer, ForeignKey('rooms.id'))
    # room = relationship("Room", back_populates='records')
    users = relationship("User", secondary="user_records")

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


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(String(100), primary_key=True)
    resource_id = Column(String(100))
    room_id = Column(Integer, ForeignKey('rooms.id'))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), default=None)
    role = Column(String(50), default='user')
    email_verified = Column(Boolean, default=False)
    access = Column(Boolean, default=False)
    api_key = Column(String(255), unique=True)
    last_login = Column(DateTime, default=datetime.utcnow)

    records = relationship("Record", secondary="user_records")

    def __init__(self, email, password=None):
        self.email = email
        if password:
            self.password = generate_password_hash(password, method='sha256')

    def update_pass(self, password):
        self.password = generate_password_hash(password, method='sha256')

    @classmethod
    def authenticate(cls, session, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')

        if not email or not password:
            return None

        user = session.query(cls).filter_by(email=email).first()

        if not user or not user.password or not check_password_hash(user.password, password):
            return None

        return user

    @classmethod
    def create_api_key(cls, user_id):
        session = Session()
        api_key = session.query(cls).get(user_id).api_key
        session.close()

        if api_key:
            return
        return uuid.uuid4().hex

    def get_token(self, token_expiration: int, key: str):
        """
        Creates verification token
        """
        return jwt.encode(
            {key: self.id,
             'exp': time() + token_expiration},
            os.environ.get('SECRET_KEY'),
            algorithm='HS256').decode('utf-8')

    def delete_user_after_token_expiration(self, app, token_expiration: int) -> None:
        """
        Deletes user if token is expired
        """
        # TODO looks weird
        sleep(token_expiration)
        session = Session()
        user = session.query(User).get(self.id)
        if not user.email_verified:
            session.delete(user)
            session.commit()
            session.close()

    @staticmethod
    def verify_token(session: Session, token: str, key: str):
        """
        Check if token is valid
        """
        try:
            id = jwt.decode(token,
                            os.environ.get('SECRET_KEY'),
                            algorithms=['HS256'])[key]
        except:
            return

        user = session.query(User).get(id)
        return user

    def to_dict(self):
        return dict(id=self.id,
                    email=self.email,
                    role=self.role,
                    email_verified=self.email_verified,
                    access=self.access,
                    api_key=self.api_key,
                    last_login=self.last_login)


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    tracking_state = Column(Boolean, default=False)
    ruz_id = Column(Integer)

    # records = relationship('Record', back_populates='room')
    sources = relationship('Source', backref='room', lazy=False)
    channel = relationship("Channel", backref="room", uselist=False)

    drive = Column(String(200))
    calendar = Column(String(200))
    stream_url = Column(String(300))

    sound_source = Column(String(100))
    main_source = Column(String(100))
    tracking_source = Column(String(100))
    screen_source = Column(String(100))

    auto_control = Column(Boolean, default=True)

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


class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), default='источник')
    ip = Column(String(200))
    port = Column(String(200))
    rtsp = Column(String(200), default='no')
    audio = Column(String(200))
    merge = Column(String(200))
    tracking = Column(String(200))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    time_editing = Column(DateTime, default=datetime.utcnow)
    external_id = Column(String(200))

    def update(self, **kwargs):
        self.name = kwargs.get('name')
        self.ip = kwargs.get('ip')
        self.port = kwargs.get('port')
        self.rtsp = kwargs.get('rtsp')
        self.audio = kwargs.get('audio')
        self.merge = kwargs.get('merge')
        self.tracking = kwargs.get('tracking')
        self.room_id = kwargs.get('room_id')
        self.time_editing = datetime.utcnow()
        self.external_id = kwargs.get('external_id')

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    ip=self.ip,
                    port=self.port,
                    rtsp=self.rtsp,
                    audio=self.audio,
                    merge=self.audio,
                    tracking=self.tracking,
                    room_id=self.room_id,
                    time_editing=self.time_editing,
                    external_id=self.external_id)
