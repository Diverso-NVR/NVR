"""
- settings for the flask application project
"""

import os
import uuid


class BaseConfig(object):
    """
    Config variables for app
    """
    DEBUG = False
    SECRET_KEY = 'supersecret'  # uuid.uuid4().hex  # for encryption and session management
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['nvr.autoreply@gmail.com']
