"""
- Data classes for application
"""

from flask_sqlalchemy import SQLAlchemy
from flask import current_app


db = SQLAlchemy()


def nvr_db_context(func):
    """
    Decorator to provide functions access to db
    """
    def wrapper(app, *args):
        with app.app_context():
            return func(*args)
    return wrapper


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    free = db.Column(db.Boolean,  default=True)
    processing = db.Column(db.Boolean,  default=False)
    timestamp = db.Column(db.Integer,  default=0)
    chosen_sound = db.Column(db.String(100), default='enc')
    sources = db.relationship('Source', backref='room', lazy=False)
    drive = db.Column(db.String(200))
    calendar = db.Column(db.String(200))

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    free=self.free,
                    processing=self.processing,
                    timestamp=self.timestamp,
                    chosen_sound=self.chosen_sound,
                    sources=[source.to_dict() for source in self.sources],
                    drive=self.drive,
                    calendar=self.calendar)


class Source(db.Model):
    __tablename__ = 'sources'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(200))
    name = db.Column(db.String(100))
    sound = db.Column(db.String(100))
    tracking = db.Column(db.Boolean, default=False)
    main_cam = db.Column(db.Boolean, default=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))

    def to_dict(self):
        return dict(id=self.id,
                    ip=self.ip,
                    name=self.name,
                    sound=self.sound,
                    tracking=self.tracking,
                    main_cam=self.main_cam,
                    room_id=self.room_id)
