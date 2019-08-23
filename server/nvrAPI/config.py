"""
- settings for the flask application project
"""

import os


class BaseConfig(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///nvr.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'nvr2019'  # for encryption and session managment
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['nvr.autoreply@gmail.com']
