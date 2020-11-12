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
    # uuid.uuid4().hex  # for encryption and session management
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DB_URL = os.environ.get('DB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['nvr.autoreply@gmail.com']