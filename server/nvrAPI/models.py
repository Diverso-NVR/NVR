"""
- Data classes for application
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app
from time import time


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    email_verified = db.Column(db.Boolean, default=False)
    access = db.Column(db.Boolean, default=False)

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

    def get_verify_token(self, expires_in=600):
        return jwt.encode(
            {'verify_user': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_email_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['verify_user']
        except:
            return
        return User.query.get(id)

    def to_dict(self):
        return dict(id=self.id,
                    email=self.email,
                    role=self.role,
                    email_verified=self.email_verified,
                    access=self.access)


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    free = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.Integer, default=0)
    chosenSound = db.Column(db.String(100), default='enc')
    sources = db.relationship('Source', backref='room', lazy=False)
    drive = db.Column(db.String(200), nullable=False)
    calendar = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    free=self.free,
                    timestamp=self.timestamp,
                    chosenSound=self.chosenSound,
                    sources=[source.to_dict() for source in self.sources],
                    drive=self.drive,
                    calendar=self.calendar)


class Source(db.Model):
    __tablename__ = 'sources'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(200))
    name = db.Column(db.String(100))
    sound = db.Column(db.String(100))
    tracking = db.Column(db.Boolean, default=False,  nullable=False)
    mainCam = db.Column(db.Boolean, default=False,  nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))

    def to_dict(self):
        return dict(id=self.id,
                    ip=self.ip,
                    name=self.name,
                    sound=self.sound,
                    tracking=self.tracking,
                    mainCam=self.mainCam,
                    room_id=self.room_id)
